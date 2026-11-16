# Límites de la métrica de evaluación


## Qué mide

Compara las palabras de la respuesta con las de una referencia, después de pasar
ambos textos a minúsculas y quitar la puntuación. Cuenta también las repeticiones
(usa `Counter`, no conjuntos). Calcula precisión (qué parte de la respuesta está en la
referencia), cobertura (qué parte de la referencia aparece en la respuesta) y F1.


## Modos de falla conocidos

Observados en la revisión manual (`docs/revision_manual.json`):

- Una respuesta correcta pero larga puntúa bajo, porque las palabras de más bajan la
  precisión.
```
"¿Qué es Python?"  F1=0.30  precisión baja, cobertura alta
Referencia: Python es un lenguaje de programación interpretado.
Respuesta: lenguaje "de alto nivel, interpretado, de propósito general", más usos y adjetivos.
```
- Un sinónimo o un cambio de forma verbal baja el puntaje aunque el significado sea el mismo.
```
"¿Quién pintó la Mona Lisa?"  F1=0.75
Referencia: Leonardo da Vinci pintó la Mona Lisa.
Respuesta: La Mona Lisa fue pintada por Leonardo da Vinci.
("pintó" y "pintada" no coinciden, y "fue" y "por" suman palabras de más)

"¿Qué es una lista en Python?"  F1=0.45  ("modificable" frente a "mutable")
```
- Una respuesta con más de una fecha es difícil de juzgar solo con el número.
```
"¿Cuándo se creó Python?"  F1=0.56
Referencia: Python fue creado en 1991 por Guido van Rossum.
Respuesta: creado "a finales de la década de 1980", con su primera versión pública en 1991.
(en la revisión: factualmente "parcialmente")
```
- La métrica ignora el orden de las palabras. En esta muestra no causó problema, pero
  podría ocultar un cambio de sentido.
```
"¿Quién fue el primer presidente de Estados Unidos?"  F1=1.00
Referencia: George Washington fue el primer presidente de Estados Unidos.
Respuesta: El primer presidente de Estados Unidos fue George Washington.
```

Conocidos pero que no aparecieron en la muestra (probados con ejemplos construidos a mano):

- Datos incorrectos (fechas, cifras) pueden puntuar alto si el resto de la oración coincide.
```
F1("Python fue inventado en 1991","Python fue inventado en 1992")=0.8
```
- Las negaciones ausentes casi no bajan el puntaje, aunque inviertan el significado.
```
F1("Python NO fue inventado en 1992","Python fue inventado en 1992")=0.91
```


## Muestra revisada

10 casos: los 5 con menor F1 y los 5 con mayor F1, sobre 20 respuestas generadas el
2026-11-15 con Deepseek 4.1 Flash. Las 20 preguntas son cortas, con una respuesta clara,
y cada referencia se escribió a mano.

Resultado de la rúbrica (corrección factual, completitud, contradicción):
corrección factual "si" en 9 casos y "parcialmente" en 1; completitud "si" en los 10;
contradicción "no" en los 10. No hubo falsos positivos: los 5 de F1 más alto (todos 1.00)
resultaron correctos. Los 5 de F1 más bajo eran respuestas correctas o casi correctas
que puntuaron bajo por su longitud o su redacción.

Límite de la muestra: son preguntas de dato corto. No se probó con respuestas largas
ni con razonamientos.


## Recomendación de uso

- Usar F1 para comparar en volumen entre versiones del cliente o entre modelos, no para
  decidir si una respuesta individual es correcta.
- Con cobertura alta y precisión baja, lo más probable es una respuesta correcta pero
  larga: pedir respuestas breves en la instrucción mejora el puntaje.
- Revisar siempre a mano cualquier respuesta con fechas, cifras o nombres propios.
- Revisar a mano también los casos de F1 alto, no solo los de F1 bajo.
