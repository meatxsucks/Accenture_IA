from cliente import consultar_modelo
from pipeline_texto import procesar_texto, calcular_precision_cobertura_f1, resumir_metricas


CASOS = [
    ("¿Qué es Python?",
     "Python es un lenguaje de programación interpretado."),
    ("¿Cuál es la capital de Chile?",
     "Santiago es la capital de Chile."),
    ("¿Qué es la fotosíntesis?",
     "Es el proceso por el cual las plantas convierten la luz en energía."),
]

def coincidencia(tokens_ref: list[str], tokens_resp: list[str]) -> float:
    if not tokens_ref:
        return 0.0
    comunes = set(tokens_ref) & set(tokens_resp)
    return len(comunes) / len(set(tokens_ref))


if __name__ == "__main__":
    resultados = []

    for i, (pregunta, referencia) in enumerate(CASOS, start=1):
        try:
            respuesta = consultar_modelo(pregunta, "Responde en una sola frase.")
        except RuntimeError as error:
            print(f"[Caso {i}] No se pudo obtener respuesta: {error}")
            continue

        tokens_ref = procesar_texto(referencia)
        tokens_resp = procesar_texto(respuesta)

        pct_crudo = coincidencia(referencia.split(), respuesta.split())
        pct_procesado = coincidencia(tokens_ref, tokens_resp)
        metricas = calcular_precision_cobertura_f1(tokens_ref, tokens_resp)
        resultados.append({"caso": i, **metricas})

        print(f"[Caso {i}] Pregunta: {pregunta}")
        print(f"[Caso {i}] Referencia: {referencia}")
        print(f"[Caso {i}] Respuesta: {respuesta}")
        print(f"[Caso {i}] Coincidencia texto crudo: {pct_crudo:.1%}")
        print(f"[Caso {i}] Coincidencia texto procesado: {pct_procesado:.1%}")
        print(f"[Caso {i}] Precisión: {metricas['precision']:.1%}")
        print(f"[Caso {i}] Cobertura: {metricas['cobertura']:.1%}")
        print(f"[Caso {i}] F1: {metricas['f1']:.1%}")
        print()

    if resultados:
        resumen = resumir_metricas(resultados)
        peor = min(resultados, key=lambda r: r["f1"])
        print(f"[Resumen] Casos evaluados: {len(resultados)} de {len(CASOS)}")
        print(f"[Resumen] Precisión promedio: {resumen['precision_promedio']:.1%}")
        print(f"[Resumen] Cobertura promedio: {resumen['cobertura_promedio']:.1%}")
        print(f"[Resumen] F1 promedio: {resumen['f1_promedio']:.1%}")
        print(f"[Resumen] Peor caso: Caso {peor['caso']} (F1: {peor['f1']:.1%})")
