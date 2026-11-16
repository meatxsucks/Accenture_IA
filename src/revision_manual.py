import json


revision_manual = [
    {
        "consulta": "¿Qué es Python?",
        "f1": 0.30,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "correcta pero muy larga: agrega usos que no están en la referencia lo que baja la precisión",
    },
    {
        "consulta": "¿Qué es una lista en Python?",
        "f1": 0.45,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "dice 'mutable' en vez de 'modificable' que es un sinonimo y agrega corchetes y tipos lo que es correcto aunqe baja la precisión",
    },
    {
        "consulta": "¿Cuándo se creó Python?",
        "f1": 0.56,
        "correccion_factual": "parcialmente",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "ubica la creación a fines de los 80 y la publicación en 1991, por lo que menciona dos fechas y no coincide del todo con la referencia",
    },
    {
        "consulta": "¿Quién pintó la Mona Lisa?",
        "f1": 0.75,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "mismo dato pero de forma pasiva, el cambio de estructura baja el F1 aunque el significado sigue siendo el mismo",
    },
    {
        "consulta": "¿Quién escribió Don Quijote de la Mancha?",
        "f1": 0.80,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "Al igual que el caso anterior, mismo dato pero de forma pasiva, el cambio de estructura baja el F1 aunque el significado sigue siendo el mismo",
    },
    {
        "consulta": "¿Cuál es el planeta más grande del sistema solar?",
        "f1": 1.00,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "idéntica a la referencia; el F1 alto es correcto",
    },
    {
        "consulta": "¿En qué año comenzó la Segunda Guerra Mundial?",
        "f1": 1.00,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "idéntica a la referencia; el F1 alto es correcto",
    },
    {
        "consulta": "¿Cuál es el idioma oficial de Brasil?",
        "f1": 1.00,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "idéntica a la referencia; el F1 alto es correcto",
    },
    {
        "consulta": "¿Quién fue el primer presidente de Estados Unidos?",
        "f1": 1.00,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "mismas palabras en otro orden; la métrica ignora el orden, aquí no importa porque el significado se mantiene",
    },
    {
        "consulta": "¿Cuántos grados mide un ángulo recto?",
        "f1": 1.00,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "idéntica a la referencia; el F1 alto es correcto",
    },
]


if __name__ == "__main__":
    with open("docs/revision_manual.json", "w", encoding="utf-8") as archivo:
        json.dump(revision_manual, archivo, indent=2, ensure_ascii=False)

    print(f"Guardadas {len(revision_manual)} revisiones en docs/revision_manual.json")
