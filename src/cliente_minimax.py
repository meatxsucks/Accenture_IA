import time

import random

import requests

from cprint import cprint

from typing import Callable, Any

from consumir_openrouter_Minimax import URL, armar_peticion, extraer_texto


def enviar_peticion(headers: dict, cuerpo: dict) -> dict:
    try:
        respuesta = requests.post(URL, json=cuerpo, headers=headers, timeout=30)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as error:
        raise TimeoutError(f"No se pudo contactar al proveedor ({type(error).__name__}). Puede ser momentáneo.")
    if respuesta.status_code in (401, 403):
        raise ValueError("Credencial inválida o sin permiso. Revisa tu OPENROUTER_API_KEY.")
    if respuesta.status_code == 429:
        segundos = respuesta.headers.get("Retry-After")
        mensaje = f"Límite excedido. Reintentar en {segundos}s." if segundos else "Límite excedido."
        raise TimeoutError(mensaje)
    if respuesta.status_code >= 500:
        raise TimeoutError(f"El proveedor no pudo procesar la petición (HTTP {respuesta.status_code}). Hay que esperar y reintentar.")
    respuesta.raise_for_status()
    return respuesta.json()


def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_base: float = 2,
    espera_maxima: float = 30,
) -> Any:
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError as error:
            if intento == intentos:
                raise
            espera = min(espera_base * (2 ** (intento - 1)), espera_maxima)
            espera_con_jitter = espera + random.uniform(0, espera * 0.1)
            print(f"Intento {intento} de {intentos} falló ({error}). Reintentando en {espera_con_jitter:.1f}s...")
            time.sleep(espera_con_jitter)


COSTO_POR_1000_TOKENS = 0.002  # referencial, ajusta según el modelo que uses

costo_total_sesion = 0.0


def registrar_costo(respuesta: dict) -> float:
    global costo_total_sesion
    uso = respuesta.get("usage", {})
    total_tokens = uso.get("total_tokens", 0)
    costo_estimado = (total_tokens / 1000) * COSTO_POR_1000_TOKENS
    costo_total_sesion += costo_estimado
    print(f"Operación: {total_tokens} tokens, costo estimado: ${costo_estimado:.5f} (acumulado: ${costo_total_sesion:.5f})")
    return costo_estimado


def consultar_modelo(pregunta: str, system_instruction: str = "") -> str:
    headers, cuerpo = armar_peticion(pregunta, system_instruction)
    try:
        respuesta = con_reintento(lambda: enviar_peticion(headers, cuerpo))
    except TimeoutError:
        raise RuntimeError("El servicio no respondió tras varios intentos. Intenta más tarde.")
    uso = respuesta.get("usage", {})
    cprint.ok("Tokens prompt:", uso.get("prompt_tokens"))
    cprint.ok("Tokens candidates:", uso.get("completion_tokens"))
    cprint.ok("Tokens total:", uso.get("total_tokens"))
    registrar_costo(respuesta)
    return extraer_texto(respuesta)


if __name__ == "__main__":
    for i in range(10):
        try:
            respuesta = consultar_modelo(f"Pregunta de prueba número {i}", "Responde únicamente con un objeto JSON válido con la clave 'response' (string), en español.")
            print(f"Respuesta {i}: {respuesta[:40]}...")
        except RuntimeError as error:
            print(f"Respuesta {i} falló definitivamente: {error}")

    print(f"Costo total del ensayo: ${costo_total_sesion:.5f}")
