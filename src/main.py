from consumir_gemini import obtener_dato_de_prueba, parsear_respuesta_json, response_schema

for pregunta in ["¿Cuál es la capital de Inglaterra?", "   "]:
    try:
        texto, metadata = obtener_dato_de_prueba(pregunta, "Responde en español, en una frase.", response_schema)
        print(parsear_respuesta_json(texto))
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)
