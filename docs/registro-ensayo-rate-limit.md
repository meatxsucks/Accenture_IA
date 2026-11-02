# Registro del ensayo de rate limit

Ensayo del Bloque 13: peticiones seguidas, sin espera entre llamadas, con el backoff exponencial (2 s base, jitter de hasta 10 %, 3 intentos) y el registro de costo por operación.

## Deepseek (`python src/cliente_deepseek.py`)

| | Corrida 1 |
|---|---|
| Fecha | 2026-11-01 |
| Peticiones enviadas | 10 |
| Petición donde apareció el primer 429 | ninguna |
| Esperas observadas | ninguna, no hubo reintentos |
| Terminaron con éxito | 10 |
| Fallaron definitivamente | 0 |
| Costo total del ensayo | $0.00371 |
| Motivo del fallo | no hubo fallos |

## Minimax (`python src/cliente_minimax.py`)

| | Corrida 1 |
|---|---|
| Fecha | 2026-11-01 |
| Peticiones enviadas | 10 |
| Petición donde apareció el primer 429 | ninguna |
| Esperas observadas | ninguna, no hubo reintentos |
| Terminaron con éxito | 10 |
| Fallaron definitivamente | 0 |
| Costo total del ensayo | $0.00480 |
| Motivo del fallo | no hubo fallos |

## Gemini (`python src/cliente_gemini.py`)

| | Corrida 1 | Corrida 2 |
|---|---|---|
| Fecha | 2026-11-01 | 2026-11-01 |
| Peticiones enviadas | 10 | 3 |
| Petición donde apareció el primer reintento | la número 1 | la número 1 |
| Esperas observadas | 2,0 a 2,2 s y 4,1 a 4,3 s | 2,0 a 2,1 s y 4,1 a 4,2 s |
| Terminaron con éxito | 4 | 0 |
| Fallaron definitivamente | 6 | 3 |
| Costo total del ensayo | $0.00279 | $0.00000 |
| Motivo del fallo | no registrado | `Límite excedido.` (429) |

- El backoff creció con jitter en las dos corridas (unos 2 s, luego unos 4 s).
- El costo se registró únicamente en las peticiones que llegaron a completarse. Las que agotaron sus reintentos terminaron en `RuntimeError: El servicio no respondió tras varios intentos` y no sumaron nada.
- En la corrida 1 el mensaje de reintento todavía no mostraba el motivo. En la corrida 2 sí, y confirmó un 429 real. El proveedor no envió el encabezado `Retry-After`.
- En la corrida 2 el 429 apareció desde la primera petición, porque la cuota ya estaba agotada por las corridas anteriores del mismo día. Hay que dejar pasar tiempo antes de repetir.
