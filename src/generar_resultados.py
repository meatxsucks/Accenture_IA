import json

from proveedores_ia.cliente_deepseek import consultar_modelo
from proveedores_ia.consumir_openrouter_Deepseek import parsear_respuesta_json
from pipeline_texto import calcular_metricas


# Pregunta y referencia.
CASOS = [
    ("¿Qué es Python?", "Python es un lenguaje de programación interpretado."),
    ("¿Cuál es la capital de Chile?", "Santiago es la capital de Chile."),
    ("¿Cuándo se creó Python?", "Python fue creado en 1991 por Guido van Rossum."),
    ("¿Quién escribió Don Quijote de la Mancha?", "Miguel de Cervantes escribió Don Quijote de la Mancha."),
    ("¿Cuántos planetas tiene el sistema solar?", "El sistema solar tiene ocho planetas."),
    ("¿Cuál es el río más largo de Sudamérica?", "El río Amazonas es el más largo de Sudamérica."),
    ("¿En qué año llegó el hombre a la Luna?", "El hombre llegó a la Luna en 1969."),
    ("¿Cuál es el océano más grande del mundo?", "El océano Pacífico es el más grande del mundo."),
    ("¿Qué gas necesitan las plantas para la fotosíntesis?", "Las plantas necesitan dióxido de carbono para la fotosíntesis."),
    ("¿Cuál es la capital de Argentina?", "Buenos Aires es la capital de Argentina."),
    ("¿Quién pintó la Mona Lisa?", "Leonardo da Vinci pintó la Mona Lisa."),
    ("¿Cuántos días tiene un año bisiesto?", "Un año bisiesto tiene 366 días."),
    ("¿Cuál es la fórmula química del agua?", "La fórmula química del agua es H2O."),
    ("¿Qué es una lista en Python?", "Una lista es una colección ordenada y modificable."),
    ("¿Cuál es el planeta más grande del sistema solar?", "Júpiter es el planeta más grande del sistema solar."),
    ("¿En qué año comenzó la Segunda Guerra Mundial?", "La Segunda Guerra Mundial comenzó en 1939."),
    ("¿Cuál es el idioma oficial de Brasil?", "El idioma oficial de Brasil es el portugués."),
    ("¿Quién fue el primer presidente de Estados Unidos?", "George Washington fue el primer presidente de Estados Unidos."),
    ("¿Qué cordillera cruza Chile de norte a sur?", "La cordillera de los Andes recorre Chile de norte a sur."),
    ("¿Cuántos grados mide un ángulo recto?", "Un ángulo recto mide 90 grados."),
]
INSTRUCCION = "Responde únicamente con un objeto JSON válido con la clave 'response' (string), en una sola frase, en español."


if __name__ == "__main__":
    resultados = []

    for i, (consulta, referencia) in enumerate(CASOS, start=1):
        try:
            respuesta = parsear_respuesta_json(consultar_modelo(consulta, INSTRUCCION))["response"]
        except RuntimeError as error:
            print(f"[Caso {i}] No se pudo obtener respuesta: {error}")
            continue

        metricas = calcular_metricas(referencia, respuesta)
        resultados.append({
            "consulta": consulta,
            "referencia": referencia,
            "respuesta": respuesta,
            **metricas,
        })
        print(f"[Caso {i}] F1: {metricas['f1']:.1%}")

    with open("docs/resultados_metricas.json", "w", encoding="utf-8") as archivo:
        json.dump(resultados, archivo, indent=2, ensure_ascii=False)

    print(f"Guardados {len(resultados)} de {len(CASOS)} resultados en docs/resultados_metricas.json")
