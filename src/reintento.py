import time
from typing import Callable, Any
from consumir_gemini import obtener_dato_de_prueba

intentos_previos = 0


def enviar_peticion(cuerpo: dict) -> dict:
    global intentos_previos
    intentos_previos += 1
    if intentos_previos < 3:
        raise TimeoutError(
            "Límite de peticiones excedido. Hay que esperar y reintentar."
        )
    return {"contenido": "Respuesta simulada exitosa", "intento": intentos_previos}


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
            print(
                f"Intento {intento} de {intentos} falló por límite de uso. Reintentando..."
            )
            time.sleep(espera_segundos)


# cuerpo = {"contents": [{"parts": [{"text": "Hola"}]}]}
# respuesta = con_reintento(lambda: enviar_peticion(cuerpo))
# print(respuesta)

response = con_reintento(
    lambda: obtener_dato_de_prueba(
        "¿Cuál es la capital de Escocia? Dame solo el nombre", "", None
    )
)
