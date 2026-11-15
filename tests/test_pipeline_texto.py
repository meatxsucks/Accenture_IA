import pytest


from pipeline_texto import procesar_texto, limpiar_texto, coincidencia_tokens
from pipeline_texto import (
    procesar_texto, limpiar_texto, coincidencia_tokens,
    contar_coincidencias, calcular_precision_cobertura_f1,
)

def test_procesar_texto_normaliza_mayusculas_y_puntuacion():
    resultado = procesar_texto("El Cielo, es AZUL!")

    assert resultado == ["el", "cielo", "es", "azul"]


def test_procesar_texto_solo_puntuacion_devuelve_lista_vacia():
    resultado = procesar_texto("¡¡¡...!!!")

    assert resultado == []


def test_procesar_texto_colapsa_espacios_repetidos():
    assert procesar_texto("  hola    mundo  ") == ["hola", "mundo"]


def test_limpiar_texto_rechaza_entradas_que_no_son_texto():
    with pytest.raises(TypeError):
        limpiar_texto(123)


def test_coincidencia_tokens_textos_iguales_da_100_por_ciento():
    assert coincidencia_tokens("El cielo es azul.", "el cielo es azul") == 1.0


def test_coincidencia_tokens_parcial():
    # 3 de las 4 palabras de la referencia aparecen en la respuesta
    assert coincidencia_tokens("El cielo es azul.", "el cielo es verde") == 0.75


def test_coincidencia_tokens_referencia_vacia_da_cero_sin_dividir_por_cero():
    assert coincidencia_tokens("¡¡¡...!!!", "algo") == 0.0


def test_coincidencia_tokens_el_pipeline_alinea_ambos_lados():
    # En crudo ("Python," vs "python") no coincidirían; procesados, sí.
    assert coincidencia_tokens("Python, rápido.", "python rápido") == 1.0

# ---------- Bloque 16: precisión, cobertura y F1 ----------

def test_contar_coincidencias_respeta_repeticiones():
   assert contar_coincidencias(["el", "gato", "el", "gato"], ["el", "gato"]) == 2


def test_precision_cobertura_f1_ejemplo_calculado_a_mano():
    referencia = procesar_texto("El gato duerme en el sofá.")
    respuesta = procesar_texto("El gato duerme en el sillón todo el día.")

    resultado = calcular_precision_cobertura_f1(referencia, respuesta)

    assert contar_coincidencias(referencia, respuesta) == 5
    assert resultado["precision"] == pytest.approx(5 / 9)
    assert resultado["cobertura"] == pytest.approx(5 / 6)
    assert resultado["f1"] == pytest.approx(2 / 3)


def test_precision_cobertura_f1_textos_iguales_dan_uno():
    tokens = ["el", "gato", "duerme"]

    assert calcular_precision_cobertura_f1(tokens, tokens) == {
        "precision": 1.0, "cobertura": 1.0, "f1": 1.0,
    }


@pytest.mark.parametrize("referencia, respuesta", [([], ["a"]), (["a"], []), ([], [])])
def test_precision_cobertura_f1_con_lista_vacia_da_ceros(referencia, respuesta):
    assert calcular_precision_cobertura_f1(referencia, respuesta) == {
        "precision": 0.0, "cobertura": 0.0, "f1": 0.0,
    }


def test_respuesta_corta_tiene_precision_alta_y_cobertura_baja():
    referencia = ["el", "gato", "duerme", "en", "el", "sofá"]
    respuesta = ["el", "gato"]

    resultado = calcular_precision_cobertura_f1(referencia, respuesta)

    assert resultado["precision"] == 1.0
    assert resultado["cobertura"] == pytest.approx(2 / 6)


def test_respuesta_larga_tiene_cobertura_alta_y_precision_baja():
    referencia = ["el", "gato"]
    respuesta = ["el", "gato", "duerme", "en", "el", "sofá"]

    resultado = calcular_precision_cobertura_f1(referencia, respuesta)

    assert resultado["cobertura"] == 1.0
    assert resultado["precision"] == pytest.approx(2 / 6)