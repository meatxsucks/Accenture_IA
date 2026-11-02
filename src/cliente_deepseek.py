import time

import requests

from cprint import cprint

from typing import Callable, Any

from consumir_openrouter_Deepseek import URL, armar_peticion, extraer_texto


def enviar_peticion(headers: dict, cuerpo: dict) -> dict:
    try:
        respuesta = requests.post(URL, json=cuerpo, headers=headers, timeout=30)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise TimeoutError("No se pudo contactar al proveedor. Puede ser momentáneo.")
    if respuesta.status_code in (401, 403):
        raise ValueError("Credencial inválida o sin permiso. Revisa tu OPENROUTER_API_KEY.")
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
    uso = respuesta.get("usage", {})
    total_tokens = uso.get("total_tokens", 0)
    costo_estimado = (total_tokens / 1000) * COSTO_POR_1000_TOKENS
    costo_total_sesion += costo_estimado
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
    respuesta = consultar_modelo(
        "¿Cuál es la capital de Chile?",
        "Responde únicamente con un objeto JSON válido con la clave 'response' (string), en español.",
    )
    print(respuesta)
    print(f"Costo acumulado de la sesión: ${costo_total_sesion:.5f}")
