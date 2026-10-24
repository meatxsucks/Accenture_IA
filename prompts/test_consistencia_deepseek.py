import json
import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from banco import BANCO_DE_PROMPTS
from consumir_openrouter_Deepseek import armar_peticion, enviar_peticion, extraer_texto, parsear_respuesta_json

registro = {}

for prompt in BANCO_DE_PROMPTS:
    exitos = 0
    intentos = 3
    for intento in range(intentos):
        try:
            headers, body = armar_peticion(
                prompt["ejemplo_usuario"],
                prompt["system_instruction"],
            )
            respuesta = enviar_peticion(headers, body)
            texto = extraer_texto(respuesta)
            parsear_respuesta_json(texto, prompt["claves_esperadas"])
            exitos += 1
        except (ValueError, RuntimeError) as error:
            print(f"  intento {intento + 1} falló: {error}")
        time.sleep(1)
    print(f"{prompt['nombre']}: {exitos}/{intentos} respuestas válidas")
    registro[prompt["nombre"]] = {"exitos": exitos, "intentos": intentos}

ruta_registro = os.path.join(os.path.dirname(__file__), "registro_resultados_deepseek.json")
with open(ruta_registro, "w", encoding="utf-8") as archivo:
    json.dump(registro, archivo, indent=2, ensure_ascii=False)
