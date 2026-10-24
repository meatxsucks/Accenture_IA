BANCO_DE_PROMPTS = [
    {
        "nombre": "resumen_ruta",
        "system_instruction": (
            "Eres un guía de viajes. Responde únicamente con un JSON con la clave "
            "'response' (string): un resumen en español de máximo 3 líneas."
        ),
        "ejemplo_usuario": "Como se llega de santiago a mendoza. Explicalo en un breve resumen.",
        "claves_esperadas": ["response"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {"response": {"type": "STRING"}},
            "required": ["response"],
        },
    },
    {
        "nombre": "opciones_transporte",
        "system_instruction": (
            "Eres un guía de viajes. Responde únicamente con un JSON con las claves "
            "'opciones' (lista de objetos con 'medio' y 'duracion', ambos string) "
            "y 'recomendacion' (string)."
        ),
        "ejemplo_usuario": "Como se llega de santiago a mendoza.",
        "claves_esperadas": ["opciones", "recomendacion"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "opciones": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "medio": {"type": "STRING"},
                            "duracion": {"type": "STRING"},
                        },
                        "required": ["medio", "duracion"],
                    },
                },
                "recomendacion": {"type": "STRING"},
            },
            "required": ["opciones", "recomendacion"],
        },
    },
    {
        "nombre": "clasificar_consulta",
        "system_instruction": (
            "Clasifica la consulta de un viajero. Responde únicamente con un JSON con las claves "
            "'categoria' ('ruta', 'alojamiento', 'clima' u 'otro') y 'confianza' (número de 0 a 1)."
        ),
        "ejemplo_usuario": "Que tiempo hara en Mendoza el fin de semana?",
        "claves_esperadas": ["categoria", "confianza"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "categoria": {"type": "STRING"},
                "confianza": {"type": "NUMBER"},
            },
            "required": ["categoria", "confianza"],
        },
    },
]
