# Límites de la métrica de evaluación


## Qué mide

Coincidencia entre frases revisando palabras y la cantidad de ocurrencias.
Calcula precisión, cobertura, F1 .


## Modos de falla conocidos

- Sinónimos y paráfrasis correctas puntúan bajo.
```
F1("el auto es veloz","el vehiculo es rapido")=0.5
```
- Datos incorrectos (fechas, cifras) pueden puntuar alto si el
  resto de la oración coincide.
 ```
 P("Python fue inventado en 1991","Python fue inventado en 1992)=0.8
 ``` 
- Negaciones ausentes casi no bajan el puntaje, aunque
  inviertan el significado.
``` 
F1("Python NO fue inventado en 1992","Python fue inventado en 1992)=0.8 
```


## Muestra revisada

10 casos: los 5 con menor F1 y los 5 con mayor F1, sobre 40
respuestas generadas el 2026-08-10.


## Recomendación de uso

Usar F1 para comparar en volumen entre versiones del cliente.
Revisar siempre a mano cualquier respuesta con fechas, cifras
o nombres propios.