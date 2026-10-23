import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

MODELO = "deepseek/deepseek-v4.1-flash"
URL = f"https://openrouter.ai/api/v1/chat/completions"
PRECIO_ENTRADA = 0.0342 # USD por millón de tokens
PRECIO_SALIDA = 0.1368  # USD por millón de tokens


def armar_peticion(instruccion, pregunta):
    if not pregunta or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía")
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("Falta OPENROUTER_API_KEY en el entorno o en .env")
    headers={
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    }
    body = {"model": MODELO, "messages": [{"role": "system", "content": instruccion},
                                          {"role": "user", "content": pregunta}]}
    return headers, body


def enviar_peticion(headers, body):
    try:
        respuesta = requests.post(URL, headers=headers, json=body, timeout=30)
    except requests.exceptions.RequestException:
        raise RuntimeError("No se pudo conectar con el servicio. Intenta de nuevo en unos segundos.")
    try:
        datos = respuesta.json()
    except ValueError:
        raise RuntimeError("La respuesta del servicio no llegó en el formato esperado.")
    if not respuesta.ok:
        mensaje = datos.get("error", {}).get("message", respuesta.reason)
        raise RuntimeError(f"El servicio respondió {respuesta.status_code}: {mensaje}")
    return datos


def extraer_texto(datos):
    try:
        return datos["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")


def extraer_metadata(datos):
    return datos.get("usage", {})


def calcular_costo(metadata, precio_entrada, precio_salida):
    tokens_entrada = metadata.get("prompt_tokens", 0)
    tokens_salida = metadata.get("completion_tokens", 0) + metadata.get("thoughtsTokenCount", 0)
    return (tokens_entrada * precio_entrada + tokens_salida * precio_salida) / 1_000_000


def obtener_dato_de_prueba(instruccion, pregunta):
    headers, body = armar_peticion(instruccion, pregunta)
    datos = enviar_peticion(headers, body)
    metadata = datos.get("usage", {})
    return extraer_texto(datos), metadata



#pregunta = "Confirma en una frase corta que esta conexión funciona y un emoji"
instruccion = "Eres un guía de viajes. Responde siempre en español, en máximo 3 líneas."
pregunta = "Como se llega de santiago a mendoza. Explicalo en un breve resumen."

print(" -- Verificando manejo de errores except -- ")
inicio = time.perf_counter()
try:
    resultado, metadata = obtener_dato_de_prueba(instruccion, pregunta)
    costo = calcular_costo(metadata, PRECIO_ENTRADA, PRECIO_SALIDA)
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
