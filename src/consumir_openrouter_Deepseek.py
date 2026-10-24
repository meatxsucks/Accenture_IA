import os
import time
import requests
import json
import re
from dotenv import load_dotenv

load_dotenv()

MODELO = "deepseek/deepseek-v4.1-flash"
URL = f"https://openrouter.ai/api/v1/chat/completions"
PRECIO_ENTRADA = 0.0342 # USD por millón de tokens
PRECIO_SALIDA = 0.1368  # USD por millón de tokens
response_schema = {
    "type": "object",
    "properties": {"response": {"type": "string"}},
    "required": ["response"],
    "additionalProperties": False,
}

def armar_peticion(pregunta: str, system_instruction: str, response_schema: dict | None = None) -> tuple[dict, dict]:
    if not isinstance(pregunta, str) or not pregunta.strip():
            raise ValueError("La pregunta debe ser un texto no vacío")
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("Falta OPENROUTER_API_KEY en el entorno o en .env")
    headers={
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    }
    body = {"model": MODELO, "messages": [{"role": "system", "content": system_instruction},
                                                  {"role": "user", "content": pregunta}],
                "response_format": {"type": "json_object"}}
    if response_schema is not None:
        body["response_format"] = {
            "type": "json_schema",
            "json_schema": {"name": "respuesta", "strict": True, "schema": response_schema},
        }
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
        return datos["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")


def extraer_metadata(datos: dict) -> dict:
    return datos.get("usage", {})


def calcular_costo(metadata: dict, precio_entrada: float, precio_salida: float) -> float:
    tokens_entrada = metadata.get("prompt_tokens", 0)
    tokens_salida = metadata.get("completion_tokens", 0) + metadata.get("thoughtsTokenCount", 0)
    return (tokens_entrada * precio_entrada + tokens_salida * precio_salida) / 1_000_000


def obtener_dato_de_prueba(pregunta: str, system_instruction: str, response_schema: dict | None = None) -> tuple[str, dict]:
    headers, body = armar_peticion(pregunta, system_instruction, response_schema)
    datos = enviar_peticion(headers, body)
    metadata = datos.get("usage", {})
    return extraer_texto(datos), metadata

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
            print(f"Tokens de entrada: {metadata.get('prompt_tokens', 'No informado')}")
            print(f"Tokens de salida: {metadata.get('completion_tokens', 'No informado')}")
            print(f"Tokens de pensamiento: {metadata.get('thoughts_tokens', 'No informado')}")
            print(f"Total: {metadata.get('total_tokens', 'No informado')}")
            print(f"Costo estimado: ${costo:.6f}")
        except (ValueError, RuntimeError) as error:
            print("No se pudo completar la operación:", error)
        latencia = time.perf_counter() - inicio
        print(f"Latencia: {latencia:.2f} segundos")
