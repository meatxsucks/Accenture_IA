import json


if __name__ == "__main__":
    with open("docs/resultados_metricas.json", encoding="utf-8") as archivo:
        resultados = json.load(archivo)

    if len(resultados) < 10:
        print(f"Solo hay {len(resultados)} resultados: se necesitan al menos 10.")
        raise SystemExit(1)

    ordenados = sorted(resultados, key=lambda r: r["f1"])
    muestra = ordenados[:5] + ordenados[-5:]    # los 5 peores y los 5 mejores

    for n, caso in enumerate(muestra, start=1):
        print(f"--- Caso {n} (F1 {caso['f1']:.2f}) ---")
        print(f"Consulta:   {caso['consulta']}")
        print(f"Referencia: {caso['referencia']}")
        print(f"Respuesta:  {caso['respuesta']}")
        print()
