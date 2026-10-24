import os
import time
import requests
import json
import re
from dotenv import load_dotenv

load_dotenv()

MODELO = "gemini-3.6-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent"
PRECIO_ENTRADA = 0.75 # USD por millón de tokens: copia el valor de la tabla oficial
PRECIO_SALIDA = 3.75      # USD por millón de tokens: copia el valor de la tabla oficial
response_schema = {
    "type": "OBJECT",
    "properties": {"response": {"type": "STRING"}},
    "required": ["response"]
}

def armar_peticion(pregunta: str, system_instruction: str, response_schema: dict | None = None) -> tuple[dict, dict]:
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta debe ser un texto no vacío")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta GEMINI_API_KEY en el entorno o en .env")
    headers = {"x-goog-api-key": api_key}
    body = {
    "system_instruction": {"parts": [{"text": system_instruction}]},
    "contents": [{"parts": [{"text": pregunta}]}],
    "generationConfig": {"responseMimeType": "application/json"},
    }

    if response_schema is not None:
        body["generationConfig"]["responseSchema"] = response_schema
    return headers, body


def enviar_peticion(headers: dict, body: dict) -> dict:
    try:
        respuesta = requests.post(URL, headers=headers, json=body, timeout=30)
    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"No se pudo conectar con el servicio: {error}")
    try:
        datos = respuesta.json()
    except ValueError:
        raise RuntimeError("La respuesta del servicio no llegó en el formato esperado.")
    if not respuesta.ok:
        mensaje = datos.get("error", {}).get("message", respuesta.reason)
        raise RuntimeError(f"El servicio respondió {respuesta.status_code}: {mensaje}")
    return datos


def extraer_texto(datos: dict) -> str:
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")


def extraer_metadata(datos: dict) -> dict:
    return datos.get("usageMetadata", {})


def calcular_costo(metadata: dict, precio_entrada: float, precio_salida: float) -> float:
    tokens_entrada = metadata.get("promptTokenCount", 0)
    # Los tokens de pensamiento se cobran como salida; confírmalo en la página de precios
    tokens_salida = metadata.get("candidatesTokenCount", 0) + metadata.get("thoughtsTokenCount", 0)
    return (tokens_entrada * precio_entrada + tokens_salida * precio_salida) / 1_000_000


def obtener_dato_de_prueba(pregunta: str, system_instruction: str, response_schema: dict | None = None) -> tuple[str, dict]:
    headers, body = armar_peticion(pregunta, system_instruction, response_schema)
    datos = enviar_peticion(headers, body)
    return extraer_texto(datos), extraer_metadata(datos)


def parsear_respuesta_json(texto: str, claves: tuple = ("response",)) -> dict:
    texto_limpio = texto.strip()
    texto_limpio = re.sub(r"^```(?:json)?\s*", "", texto_limpio)
    texto_limpio = re.sub(r"\s*```$", "", texto_limpio)
    try:
        datos = json.loads(texto_limpio)
    except json.JSONDecodeError:
        raise ValueError("La respuesta del modelo no es JSON válido.")
    if not isinstance(datos, dict) or any(clave not in datos for clave in claves):
        raise ValueError("La respuesta no tiene la estructura esperada.")
    return datos


def test_latencia(ciclos: int = 5) -> None:
    latencias = []
    for i in range(ciclos):
        headers, body = armar_peticion("Cuanto es 2 + 2? Dame solo el resultado", "Responde breve")
        inicio = time.perf_counter()
        enviar_peticion(headers, body)
        latencias.append(time.perf_counter() - inicio)
        print(f"Duración de la petición {i + 1}: {latencias[-1]:.2f} segundos")
    print(f"Latencia promedio después de {ciclos} ciclos: {sum(latencias) / len(latencias):.2f} segundos")


if __name__ == "__main__":
    pregunta = "Como se llega de santiago a mendoza. Explicalo en un breve resumen."
    casos = [
        ("Instrucción de una sola palabra", "Da respuestas de una sola palabra", None, False),
        ("Sin instrucción", "", None, False),
        ("JSON pedido en la instrucción", "Responde únicamente con un objeto JSON válido, sin texto adicional, con la clave 'response' (string).", None, True),
        ("JSON forzado con schema", "Eres un guía de viajes. Responde siempre en español, en máximo 3 líneas", response_schema, True),
    ]
    for nombre, system_instruction, schema, parsear in casos:
        print(f" -- {nombre} -- ")
        inicio = time.perf_counter()
        try:
            resultado, metadata = obtener_dato_de_prueba(pregunta, system_instruction, schema)
            costo = calcular_costo(metadata, PRECIO_ENTRADA, PRECIO_SALIDA)
            if parsear:
                resultado = parsear_respuesta_json(resultado)
            print(resultado)
            print(f"Tokens de entrada: {metadata.get('promptTokenCount', 'No informado')}")
            print(f"Tokens de salida: {metadata.get('candidatesTokenCount', 'No informado')}")
            print(f"Tokens de pensamiento: {metadata.get('thoughtsTokenCount', 'No informado')}")
            print(f"Total: {metadata.get('totalTokenCount', 'No informado')}")
            print(f"Costo estimado: ${costo:.6f}")
        except (ValueError, RuntimeError) as error:
            print("No se pudo completar la operación:", error)
        latencia = time.perf_counter() - inicio
        print(f"Latencia: {latencia:.2f} segundos")
