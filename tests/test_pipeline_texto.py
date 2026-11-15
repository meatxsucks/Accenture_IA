import pytest

from pipeline_texto import procesar_texto, limpiar_texto, coincidencia_tokens


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
