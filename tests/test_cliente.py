from unittest.mock import patch, Mock

import pytest
import requests

import cliente
from cliente import enviar_peticion, con_reintento, registrar_costo, consultar_modelo


RESPUESTA_EXITOSA = {
    "candidates": [{"content": {"parts": [{"text": "Santiago"}]}}],
    "usageMetadata": {
        "promptTokenCount": 8,
        "candidatesTokenCount": 18,
        "totalTokenCount": 1000,
    },
}


@pytest.fixture(autouse=True)
def reiniciar_costo_total():
    cliente.costo_total_sesion = 0
    yield


# ---------- enviar_peticion ----------

def test_enviar_peticion_exito():
    respuesta_falsa = Mock(status_code=200)
    respuesta_falsa.json.return_value = {"texto": "respuesta simulada"}

    with patch("cliente.requests.post", return_value=respuesta_falsa):
        resultado = enviar_peticion({"pregunta": "test"})

    assert resultado == {"texto": "respuesta simulada"}


@pytest.mark.parametrize("codigo", [429, 500, 503])
def test_enviar_peticion_limite_de_uso_o_error_del_proveedor(codigo):
    respuesta_falsa = Mock(status_code=codigo)

    with patch("cliente.requests.post", return_value=respuesta_falsa):
        with pytest.raises(TimeoutError):
            enviar_peticion({"pregunta": "test"})


def test_enviar_peticion_sin_conexion_es_reintentable():
    with patch("cliente.requests.post", side_effect=requests.exceptions.ConnectionError):
        with pytest.raises(TimeoutError):
            enviar_peticion({"pregunta": "test"})


@pytest.mark.parametrize("codigo", [401, 403])
def test_enviar_peticion_credencial_invalida(codigo):
    respuesta_falsa = Mock(status_code=codigo)

    with patch("cliente.requests.post", return_value=respuesta_falsa):
        with pytest.raises(ValueError):
            enviar_peticion({"pregunta": "test"})


def test_enviar_peticion_error_400_no_se_reintenta():
    respuesta_falsa = Mock(status_code=400)
    respuesta_falsa.raise_for_status.side_effect = requests.exceptions.HTTPError("400")

    with patch("cliente.requests.post", return_value=respuesta_falsa):
        with pytest.raises(requests.exceptions.HTTPError):
            enviar_peticion({"pregunta": "test"})


# ---------- con_reintento ----------

def test_con_reintento_reintenta_si_hay_timeout():
    llamadas = {"n": 0}

    def falla_una_vez():
        llamadas["n"] += 1
        if llamadas["n"] == 1:
            raise TimeoutError("simulado")
        return "ok"

    with patch("cliente.time.sleep") as sleep_falso:
        resultado = con_reintento(falla_una_vez)

    assert resultado == "ok"
    assert llamadas["n"] == 2
    sleep_falso.assert_called_once()


def test_con_reintento_respeta_backoff_y_jitter():
    llamadas = {"n": 0}

    def falla_dos_veces():
        llamadas["n"] += 1
        if llamadas["n"] <= 2:
            raise TimeoutError("simulado")
        return "ok"

    with patch("cliente.time.sleep") as sleep_falso:
        con_reintento(falla_dos_veces, espera_base=2)

    primera, segunda = [llamada.args[0] for llamada in sleep_falso.call_args_list]
    assert 2 <= primera <= 2 * 1.1   # base 2 s, jitter de hasta 10 %
    assert 4 <= segunda <= 4 * 1.1   # el backoff se duplica


def test_con_reintento_respeta_el_tope_de_espera():
    def siempre_falla():
        raise TimeoutError("simulado")

    with patch("cliente.time.sleep") as sleep_falso:
        with pytest.raises(TimeoutError):
            con_reintento(siempre_falla, intentos=3, espera_base=20, espera_maxima=30)

    segunda = sleep_falso.call_args_list[1].args[0]
    assert 30 <= segunda <= 30 * 1.1   # 20 * 2 = 40 se corta en 30


def test_con_reintento_no_reintenta_value_error():
    llamadas = {"n": 0}

    def credencial_invalida():
        llamadas["n"] += 1
        raise ValueError("credencial inválida")

    with patch("cliente.time.sleep") as sleep_falso:
        with pytest.raises(ValueError):
            con_reintento(credencial_invalida)

    assert llamadas["n"] == 1
    sleep_falso.assert_not_called()


def test_con_reintento_agota_intentos():
    llamadas = {"n": 0}

    def siempre_falla():
        llamadas["n"] += 1
        raise TimeoutError("simulado")

    with patch("cliente.time.sleep"):
        with pytest.raises(TimeoutError, match="simulado"):
            con_reintento(siempre_falla, intentos=3)

    assert llamadas["n"] == 3


# ---------- registrar_costo ----------

def test_registrar_costo_acumula():
    costo = registrar_costo({"usageMetadata": {"totalTokenCount": 1000}})

    assert costo == cliente.COSTO_POR_1000_TOKENS
    assert cliente.costo_total_sesion == cliente.COSTO_POR_1000_TOKENS


def test_registrar_costo_maneja_multiples_llamadas():
    registrar_costo({"usageMetadata": {"totalTokenCount": 1000}})
    registrar_costo({"usageMetadata": {"totalTokenCount": 500}})

    esperado = cliente.COSTO_POR_1000_TOKENS * 1.5
    assert cliente.costo_total_sesion == pytest.approx(esperado)


def test_registrar_costo_sin_usage_metadata_no_suma():
    costo = registrar_costo({})

    assert costo == 0
    assert cliente.costo_total_sesion == 0


# ---------- consultar_modelo ----------

def test_consultar_modelo_flujo_exitoso():
    with patch("cliente.enviar_peticion", return_value=RESPUESTA_EXITOSA):
        texto = consultar_modelo("¿Capital de Chile?")

    assert texto == "Santiago"
    assert cliente.costo_total_sesion == cliente.COSTO_POR_1000_TOKENS


def test_consultar_modelo_integra_reintento_y_costo():
    with patch("cliente.time.sleep"), patch(
        "cliente.enviar_peticion",
        side_effect=[TimeoutError("simulado"), TimeoutError("simulado"), RESPUESTA_EXITOSA],
    ) as enviar_falso:
        texto = consultar_modelo("¿Capital de Chile?")

    assert texto == "Santiago"
    assert enviar_falso.call_count == 3
    # El costo se registra una sola vez: solo la petición exitosa lo suma.
    assert cliente.costo_total_sesion == cliente.COSTO_POR_1000_TOKENS


def test_consultar_modelo_convierte_timeout_agotado_en_runtime_error():
    with patch("cliente.time.sleep"), patch(
        "cliente.enviar_peticion", side_effect=TimeoutError("simulado")
    ):
        with pytest.raises(RuntimeError, match="no respondió"):
            consultar_modelo("¿Capital de Chile?")

    assert cliente.costo_total_sesion == 0   # una petición fallida no suma costo


def test_consultar_modelo_propaga_value_error_sin_cambios():
    with patch("cliente.enviar_peticion", side_effect=ValueError("credencial inválida")) as enviar_falso:
        with pytest.raises(ValueError, match="credencial inválida"):
            consultar_modelo("¿Capital de Chile?")

    assert enviar_falso.call_count == 1   # no se reintentó
