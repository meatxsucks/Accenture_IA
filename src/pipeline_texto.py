import re

from collections import Counter


def limpiar_texto(texto: str) -> str:
    if not isinstance(texto, str):
        tipo = type(texto).__name__
        raise TypeError(f"limpiar_texto espera str, no {tipo}")

    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def tokenizar(texto_limpio: str) -> list[str]:
    return texto_limpio.split()


def vectorizar(tokens: list[str]) -> Counter:
    return Counter(tokens)


def procesar_texto(texto: str) -> list[str]:
    texto_limpio = limpiar_texto(texto)
    return tokenizar(texto_limpio)


def coincidencia_tokens(referencia: str, respuesta: str) -> float:
    tokens_referencia = procesar_texto(referencia)
    tokens_respuesta = procesar_texto(respuesta)
    comunes = set(tokens_referencia) & set(tokens_respuesta)

    if tokens_referencia:
        return len(comunes) / len(set(tokens_referencia))
    return 0.0

def contar_coincidencias(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> int:
    conteo_referencia = Counter(tokens_referencia)
    conteo_respuesta = Counter(tokens_respuesta)
    interseccion = conteo_referencia & conteo_respuesta
    return sum(interseccion.values())

def calcular_precision_cobertura_f1(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> dict[str, float]:
    if not tokens_referencia or not tokens_respuesta:
        return {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

    coincidencias = contar_coincidencias(tokens_referencia, tokens_respuesta)

    precision = coincidencias / len(tokens_respuesta)
    cobertura = coincidencias / len(tokens_referencia)

    if precision + cobertura == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * cobertura / (precision + cobertura)

    return {"precision": precision, "cobertura": cobertura, "f1": f1}

def calcular_metricas(texto_referencia: str, texto_respuesta: str) -> dict[str, float]:
    return calcular_precision_cobertura_f1(
        procesar_texto(texto_referencia), procesar_texto(texto_respuesta)
    )


def resumir_metricas(resultados: list[dict[str, float]]) -> dict[str, float]:
    if not resultados:
        return {"precision_promedio": 0.0, "cobertura_promedio": 0.0, "f1_promedio": 0.0}

    n = len(resultados)
    return {
        "precision_promedio": sum(r["precision"] for r in resultados) / n,
        "cobertura_promedio": sum(r["cobertura"] for r in resultados) / n,
        "f1_promedio": sum(r["f1"] for r in resultados) / n,
    }

if __name__ == "__main__":
    texto = "El gato, el perro y el gato corren.!"
    texto_limpio = limpiar_texto(texto)
    tokens = tokenizar(texto_limpio)

    print("Texto limpio:", texto_limpio)
    print("Tokens:", tokens)
    print("Conteo:", vectorizar(tokens))

    referencia = "El cielo es azul."
    respuesta = "el cielo es azul"
    print("Textos a comparar:", referencia, ";", respuesta)
    print(f"Coincidencia: {coincidencia_tokens(referencia, respuesta):.0%}")
