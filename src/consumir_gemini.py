import os
import json
import requests
from dotenv import load_dotenv
  
load_dotenv()
  
def armar_peticion(pregunta):
     if not pregunta:
     	raise ValueError("La pregunta no puede estar vacía")
     api_key = os.getenv("GEMINI_API_KEY")
     modelo = "gemini-3.6-flash"
     url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
     body = {"contents": [{"parts": [{"text": pregunta}]}]}
     return url, body


def enviar_peticion(url, body):
     try:
     	respuesta = requests.post(url, json=body)
     except requests.exceptions.ConnectionError:
     	raise RuntimeError("No se pudo conectar con el servicio. Intenta de nuevo en unos segundos.")
     try:
     	return respuesta.json()
     except requests.exceptions.JSONDecodeError:
     	raise RuntimeError("La respuesta del servicio no llegó en el formato esperado.")

def extraer_texto(datos):
     try:
     	return datos["candidates"][0]["content"]["parts"][0]["text"]
     except (KeyError, IndexError):
     	raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")

def extraer_metadata(datos):
    metadata = datos.get("usageMetadata", {})
    return metadata

def obtener_dato_de_prueba(pregunta):
     url, body = armar_peticion(pregunta)
     datos = enviar_peticion(url,body)
     metadata = extraer_metadata(datos)   
     return extraer_texto(datos), metadata

pregunta = "Confirma en una frase corta que esta conexión funciona y un emoji"

print(" -- Verificando manejo de errores except -- ")

try:
     resultado, metadata = obtener_dato_de_prueba(pregunta)
     print(resultado)
     #print(json.dumps(metadata, indent=2, ensure_ascii=False))
     print(f"Tokens de entrada: {metadata.get('promptTokenCount', 'No informado')}")
     print(f"Tokens de salida: {metadata.get('candidatesTokenCount', 'No informado')}")
     print(f"Tokens de pensamiento: {metadata.get('thoughtsTokenCount', 'No informado')}")
     print(f"Total: {metadata.get('totalTokenCount', 'No informado')}")
except (ValueError, RuntimeError) as error:
     print("No se pudo completar la operación:", error)