import os

import time

import requests

from dotenv import load_dotenv

from typing import Callable, Any

from cliente_api import armar_peticion, extraer_texto


load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-3.6-flash:generateContent"
)

headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}


def enviar_peticion(cuerpo: dict) -> dict:
    try:
        respuesta = requests.post(URL, json=cuerpo, headers=headers, timeout=30)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise TimeoutError("No se pudo contactar al proveedor. Puede ser momentáneo.")
    if respuesta.status_code in (401, 403):
        raise ValueError("Credencial inválida o sin permiso. Revisa tu GEMINI_API_KEY.")
    if respuesta.status_code == 429:
        segundos = respuesta.headers.get("Retry-After")
        mensaje = f"Límite excedido. Reintentar en {segundos}s." if segundos else "Límite excedido."
        raise TimeoutError(mensaje)
    if respuesta.status_code >= 500:
        raise TimeoutError("El proveedor no pudo procesar la petición. Hay que esperar y reintentar.")
    respuesta.raise_for_status()
    return respuesta.json()


def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_segundos: int = 2,
) -> Any:
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos:
                raise
            print(f"Intento {intento} de {intentos} falló por límite de uso. Reintentando...")
            time.sleep(espera_segundos)


COSTO_POR_1000_TOKENS = 0.002  # referencial, ajusta según el modelo que uses

costo_total_sesion = 0.0


def registrar_costo(respuesta: dict) -> float:
    global costo_total_sesion
    uso = respuesta.get("usageMetadata", {})
    total_tokens = uso.get("totalTokenCount", 0)
    costo_estimado = (total_tokens / 1000) * COSTO_POR_1000_TOKENS
    costo_total_sesion += costo_estimado
    return costo_estimado


def consultar_modelo(pregunta: str, system_instruction: str = "") -> str:
    _, cuerpo = armar_peticion(pregunta, system_instruction)
    try:
        respuesta = con_reintento(lambda: enviar_peticion(cuerpo))
    except TimeoutError:
        raise RuntimeError("El servicio no respondió tras varios intentos. Intenta más tarde.")
    registrar_costo(respuesta)
    return extraer_texto(respuesta)


if __name__ == "__main__":
    respuesta = consultar_modelo("¿Cuál es la capital de Chile?")
    print(respuesta)
    print(f"Costo acumulado de la sesión: ${costo_total_sesion:.5f}")
