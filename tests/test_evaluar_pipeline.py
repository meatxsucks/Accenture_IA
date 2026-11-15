from evaluar_pipeline import coincidencia
from pipeline_texto import procesar_texto


def test_coincidencia_listas_iguales_da_100_por_ciento():
    assert coincidencia(["el", "cielo", "es", "azul"], ["el", "cielo", "es", "azul"]) == 1.0


def test_coincidencia_parcial():
    # 2 de las 4 palabras de la referencia aparecen en la respuesta
    assert coincidencia(["a", "b", "c", "d"], ["a", "b", "x"]) == 0.5


def test_coincidencia_sin_palabras_en_comun_da_cero():
    assert coincidencia(["a", "b"], ["x", "y"]) == 0.0


def test_coincidencia_referencia_vacia_da_cero_sin_dividir_por_cero():
    assert coincidencia([], ["a", "b"]) == 0.0


def test_coincidencia_respuesta_vacia_da_cero():
    assert coincidencia(["a", "b"], []) == 0.0


def test_coincidencia_ignora_palabras_repetidas():
    # Compara conjuntos: repetir "el" no cambia el resultado
    assert coincidencia(["el", "el", "gato"], ["el", "gato"]) == 1.0


def test_coincidencia_procesado_supera_al_crudo():
    referencia = "Python, es rápido."
    respuesta = "python es rápido"

    crudo = coincidencia(referencia.split(), respuesta.split())
    procesado = coincidencia(procesar_texto(referencia), procesar_texto(respuesta))

    assert crudo == 1 / 3      # solo "es" coincide tal cual
    assert procesado == 1.0    # tras limpiar, las 3 palabras coinciden
