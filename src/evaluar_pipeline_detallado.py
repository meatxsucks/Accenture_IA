from collections import Counter

from cliente import consultar_modelo
from pipeline_texto import (
    procesar_texto,
    calcular_precision_cobertura_f1,
    contar_coincidencias,
)


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


def explicar_metricas(tokens_ref: list[str], tokens_resp: list[str], prefijo: str) -> None:
    print(f"{prefijo} Tokens procesados referencia ({len(tokens_ref)}): {tokens_ref}")
    print(f"{prefijo} Tokens procesados respuesta ({len(tokens_resp)}): {tokens_resp}")

    unicos_ref = set(tokens_ref)
    unicos_comunes = unicos_ref & set(tokens_resp)
    print(f"{prefijo} Tokens únicos que coinciden: {len(unicos_comunes)} de {len(unicos_ref)} "
          )

    metricas = calcular_precision_cobertura_f1(tokens_ref, tokens_resp)
    if not tokens_ref or not tokens_resp:
        print(f"{prefijo} Una de las listas está vacía: P, C y F1 se devuelven en 0 sin calcular.")
        print()
        return

    freq_ref = Counter(tokens_ref)
    freq_resp = Counter(tokens_resp)
    print(f"{prefijo} Frecuencias referencia: {dict(freq_ref)}")
    print(f"{prefijo} Frecuencias respuesta: {dict(freq_resp)}")

    interseccion = freq_ref & freq_resp
    print(f"{prefijo} Tokens que coinciden (token: min(ref, resp)):")
    for token in sorted(interseccion):
        print(f"{prefijo}   '{token}': min({freq_ref[token]}, {freq_resp[token]}) = {interseccion[token]}")

    coincidencias = contar_coincidencias(tokens_ref, tokens_resp)
    print(f"{prefijo} Numerador (coincidencias) = suma de mínimos = {coincidencias}")
    print(f"{prefijo} Denominador precisión = tokens de la respuesta = {len(tokens_resp)}")
    print(f"{prefijo} Denominador cobertura = tokens de la referencia = {len(tokens_ref)}")

    p, c, f1 = metricas["precision"], metricas["cobertura"], metricas["f1"]
    print(f"{prefijo} Precisión = {coincidencias} / {len(tokens_resp)} = {p:.1%}")
    print(f"{prefijo} Cobertura = {coincidencias} / {len(tokens_ref)} = {c:.1%}")
    print(f"{prefijo} F1 = 2 * P * C / (P + C) = 2 * {p:.3f} * {c:.3f} / ({p:.3f} + {c:.3f}) = {f1:.1%}")
    if p + c == 0:
        print(f"{prefijo} P + C = 0 (ninguna coincidencia), por eso F1 es 0.")
    print()


if __name__ == "__main__":
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

        print(f"[Caso {i}] Pregunta: {pregunta}")
        print(f"[Caso {i}] Referencia: {referencia}")
        print(f"[Caso {i}] Respuesta: {respuesta}")
        print(f"[Caso {i}] Coincidencia texto crudo: {pct_crudo:.1%}")
        print(f"[Caso {i}] Coincidencia texto procesado: {pct_procesado:.1%}")
        print(f"[Caso {i}] Precisión: {metricas['precision']:.1%}")
        print(f"[Caso {i}] Cobertura: {metricas['cobertura']:.1%}")
        print(f"[Caso {i}] F1: {metricas['f1']:.1%}")
        print()

        print(f"[Caso {i}] --- Detalle del cálculo ---")
        explicar_metricas(tokens_ref, tokens_resp, f"[Caso {i}]")
