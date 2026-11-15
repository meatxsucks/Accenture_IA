import re

from collections import Counter


def limpiar_texto(texto: str) -> str:
    """Normaliza el texto: minúsculas y sin puntuación."""
    if not isinstance(texto, str):
        tipo = type(texto).__name__
        raise TypeError(f"limpiar_texto espera str, no {tipo}")

    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def tokenizar(texto_limpio: str) -> list[str]:
    """Convierte texto limpio en una lista de tokens."""
    return texto_limpio.split()


def vectorizar(tokens: list[str]) -> Counter:
    """Cuenta cuántas veces aparece cada token."""
    return Counter(tokens)


def procesar_texto(texto: str) -> list[str]:
    """Limpia y tokeniza: es el pipeline completo para comparar textos."""
    texto_limpio = limpiar_texto(texto)
    return tokenizar(texto_limpio)


def coincidencia_tokens(referencia: str, respuesta: str) -> float:
    """Proporción de tokens de la referencia que también aparecen en la respuesta."""
    tokens_referencia = procesar_texto(referencia)
    tokens_respuesta = procesar_texto(respuesta)
    comunes = set(tokens_referencia) & set(tokens_respuesta)

    if tokens_referencia:
        return len(comunes) / len(set(tokens_referencia))
    return 0.0


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
