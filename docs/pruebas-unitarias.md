# Pruebas unitarias del cliente modular

Suite de `pytest` para `src/cliente.py`, en `tests/test_cliente.py`. Usa mocks para simular la API y el paso del tiempo, así que corre en menos de un segundo, sin gastar tokens ni depender del proveedor.

```
python -m pytest -v
```

`pytest.ini` apunta a `src/` para encontrar el módulo, así que se corre desde la raíz del repositorio. Resultado actual: **20 pruebas en verde en 0,09 s**.

La última corrida, con cada prueba ejecutada por separado (su comando y su resultado), está en [`resultado-pruebas.txt`](resultado-pruebas.txt). Para regenerarla, desde la raíz y con el venv activo:

```
{
  echo "Resultado de la suite de pruebas, una por una - $(date '+%Y-%m-%d %H:%M')"; echo
  python -m pytest --collect-only -q --color=no | grep '::' | while read -r prueba; do
    echo "\$ python -m pytest \"$prueba\" -v"
    python -m pytest "$prueba" -v --color=no 2>&1 | grep -E "PASSED|FAILED|ERROR| passed| failed"
    echo
  done
} > docs/resultado-pruebas.txt
```

## Checklist de la suite de pruebas

Cuatro funciones, cada una con sus escenarios por cubrir. No se trata de tener muchas pruebas: se trata de cubrir cada fila de esta tabla.

| Función | Escenario 1 | Escenario 2 | Escenario 3 |
|---|---|---|---|
| **`enviar_peticion`** | ✅ Respuesta exitosa (200) | ✅ `TimeoutError` (429, 5xx o sin conexión) | ✅ `ValueError` (401 / 403) |
| **`con_reintento`** | ✅ Reintenta en caso de timeout | ✅ Respeta backoff y jitter | ✅ Propaga error no reintentable |
| **`registrar_costo`** | ✅ Acumula costo correctamente | ✅ Maneja múltiples llamadas | ✅ Expone el costo total |
| **`consultar_modelo`** | ✅ Flujo completo exitoso | ✅ Integra reintento y costo | ✅ Maneja error final después de reintentos |

## Qué debe verificar la prueba

| Función | Qué se verifica | Pruebas |
|---|---|---|
| `enviar_peticion` | Que un 401 o 403 lance `ValueError`. Que un 429, un 5xx o una falla de conexión lance `TimeoutError`. Que una respuesta exitosa devuelva el JSON tal cual. Que un 400 no se reintente: sube como `HTTPError`. | `test_enviar_peticion_exito`, `test_enviar_peticion_limite_de_uso_o_error_del_proveedor` (429, 500, 503), `test_enviar_peticion_sin_conexion_es_reintentable`, `test_enviar_peticion_credencial_invalida` (401, 403), `test_enviar_peticion_error_400_no_se_reintenta` |
| `con_reintento` | Que reintente cuando la función protegida lanza `TimeoutError`. Que la espera siga el backoff (2 s, 4 s…) con jitter de hasta 10 % y respete el tope. Que no reintente ante otro tipo de excepción. Que, al agotar los intentos, deje propagarse la excepción original. | `test_con_reintento_reintenta_si_hay_timeout`, `test_con_reintento_respeta_backoff_y_jitter`, `test_con_reintento_respeta_el_tope_de_espera`, `test_con_reintento_no_reintenta_value_error`, `test_con_reintento_agota_intentos` |
| `registrar_costo` | Que calcule el costo correcto a partir de un `totalTokenCount` conocido. Que ese costo se sume a `costo_total_sesion`, también con varias llamadas. Que una respuesta sin `usageMetadata` no sume nada. | `test_registrar_costo_acumula`, `test_registrar_costo_maneja_multiples_llamadas`, `test_registrar_costo_sin_usage_metadata_no_suma` |
| `consultar_modelo` | Que devuelva el texto y registre el costo en el flujo exitoso. Que reintente y registre el costo una sola vez. Que convierta un `TimeoutError` agotado en `RuntimeError` sin sumar costo. Que un `ValueError` se propague sin cambios y sin reintentar. | `test_consultar_modelo_flujo_exitoso`, `test_consultar_modelo_integra_reintento_y_costo`, `test_consultar_modelo_convierte_timeout_agotado_en_runtime_error`, `test_consultar_modelo_propaga_value_error_sin_cambios` |

## Cómo se simula todo

- **La API:** `patch("cliente.requests.post")` reemplaza la llamada de red por una respuesta falsa con el `status_code` que se quiera probar.
- **El tiempo:** `patch("cliente.time.sleep")` evita esperas reales, y sus argumentos permiten comprobar cuánto se habría esperado en cada reintento.
- **Las capas internas:** en las pruebas de `consultar_modelo` se reemplaza `enviar_peticion` y se deja correr el código real de `con_reintento`, `registrar_costo` y `armar_peticion`. Así se prueba la integración del cliente y no el mock.
- **El estado compartido:** un fixture con `autouse=True` reinicia `costo_total_sesion` en 0 antes de cada prueba, para que una no contamine a la siguiente.

## Diferencias con la suite del Bloque 14

Se contrastó con el `test_cliente.py` del Bloque 14 y se completó lo que le faltaba:

- `test_con_reintento_no_reintenta_value_error` estaba vacío (solo tenía `return`). Aquí comprueba que la función se llama una sola vez y que nunca se duerme.
- Faltaba el 5xx, que ahora se prueba con 500 y 503, y la falla de conexión.
- Faltaban el backoff con jitter y su tope de espera. El Bloque 14 solo comprobaba que `sleep` se llamara una vez.
- `registrar_costo` tenía una sola prueba. Se agregaron las múltiples llamadas y la respuesta sin `usageMetadata`.
- `consultar_modelo` solo probaba el error. Se agregaron el flujo exitoso, la integración con reintento y costo, y que `ValueError` se propague sin cambios.
- No se incluyó un equivalente a `test_1.py`, que solo comprobaba `2 + 2 == 4`.

