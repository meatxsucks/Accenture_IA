# Accenture_IA — Especialización en Desarrollo con IA Generativa (Accenture)

Esta es la primera miniaplicación del programa: un cliente en Python que envía una pregunta a un modelo de lenguaje a través de su API, le indica con un prompt de sistema cómo debe responder, y procesa la respuesta como JSON para que el código pueda leerla directamente. Se probó con tres modelos (Gemini 3.6 Flash, Deepseek 4.1 Flash y Minimax 3.1 Flash), y la decisión de cuál usar está documentada en `docs/decision-arquitectura.md`.

## Cómo empezar

Estos pasos se completan en orden, desde un clon limpio del repositorio:

1. Clona el repositorio y entra a la carpeta: `git clone git@github.com:meatxsucks/Accenture_IA.git` y luego `cd Accenture_IA`.
2. Crea tu entorno virtual de Python (por ejemplo, con `venv`) y actívalo. El proyecto se probó con Python 3.14.
3. Instala las dependencias con `pip install -r requirements.txt`.
4. Copia `.env.example` a un archivo nuevo llamado `.env`, y completa ahí tus credenciales reales (llaves de API): `GEMINI_API_KEY` para Gemini y `OPENROUTER_API_KEY` para Deepseek y Minimax. El archivo `.env` nunca se sube al repositorio: ya está excluido en `.gitignore`.

## Cómo ejecutarlo

Con el entorno virtual activo, desde la raíz del repositorio:

```
python src/main.py
```

Este comando hace una pregunta real a Gemini ("¿Cuál es la capital de Inglaterra?") y muestra la respuesta ya convertida a un diccionario de Python. Después prueba con una pregunta vacía, para mostrar cómo la aplicación maneja el error sin detenerse. El resultado esperado es parecido a este (el texto exacto de la respuesta puede variar):

```
{'response': 'La capital de Inglaterra es Londres.'}
No se pudo completar la operación: La pregunta debe ser un texto no vacío
```

Cada modelo tiene además su propio script, que corre cuatro casos (instrucción de una sola palabra, sin instrucción, JSON pedido en la instrucción y JSON forzado con un esquema) y muestra los tokens usados, el costo estimado y la latencia:

Los módulos de cada modelo viven en `src/proveedores_ia/`, que es un paquete: se ejecutan con `-m` desde la carpeta `src`.

```
cd src
python -m proveedores_ia.consumir_gemini
python -m proveedores_ia.consumir_openrouter_Deepseek
python -m proveedores_ia.consumir_openrouter_Minimax
```

## Clientes modulares con reintento

Cada modelo tiene un cliente que expone una sola función, `consultar_modelo(pregunta, system_instruction="")`. Por dentro arma la petición, la envía con reintento y devuelve el texto de la respuesta, de modo que quien lo usa no necesita conocer cómo se manejan los errores:

```
cd src
python -m proveedores_ia.cliente_gemini
python -m proveedores_ia.cliente_deepseek
python -m proveedores_ia.cliente_minimax
```

Los errores del proveedor se clasifican en `enviar_peticion` (dentro de cada `consumir_*.py`) y se tratan así:

| Respuesta del proveedor | Excepción | ¿Se reintenta? |
|---|---|---|
| 401 o 403 (credencial inválida o sin permiso) | `ValueError` | No, falla de inmediato |
| 429 (límite de uso) | `TimeoutError`, con los segundos de `Retry-After` si el proveedor los informa | Sí |
| 5xx (el proveedor no pudo procesar la petición) | `TimeoutError` | Sí |

Cada cliente es autocontenido: trae su propio `enviar_peticion` y su propio `con_reintento`. `con_reintento` reintenta hasta 3 veces, solo ante `TimeoutError`, y la espera crece en cada intento (backoff exponencial: 2 s, 4 s…, con un tope de 30 s y un jitter aleatorio de hasta 10 %). Si se agotan los intentos, `consultar_modelo` lo convierte en un `RuntimeError` con un mensaje claro: "El servicio no respondió tras varios intentos. Intenta más tarde."

Cada cliente registra además el costo estimado de cada operación exitosa (`registrar_costo`) y lo acumula en `costo_total_sesion`. Una petición que agota sus reintentos no suma costo. El ensayo de rate limit está documentado en `docs/registro-ensayo-rate-limit.md`.

## Pruebas unitarias

```
python -m pytest -v
```

La suite de `pytest` vive en `tests/` y cubre `enviar_peticion`, `con_reintento`, `registrar_costo` y `consultar_modelo` de `src/cliente.py`, además del pipeline de texto. Usa mocks para la API y para `time.sleep`, así que corre en menos de un segundo y no gasta tokens. `pytest.ini` apunta a `src/`, por eso se ejecuta desde la raíz del repositorio. El detalle de qué se prueba está en `docs/pruebas-unitarias.md`, y la salida de cada prueba en `docs/resultado-pruebas.txt`.

## Pipeline de texto y métricas

`src/pipeline_texto.py` limpia y tokeniza texto (`limpiar_texto`, `tokenizar`, `procesar_texto`) y calcula precisión, cobertura y F1 entre una referencia y una respuesta (`calcular_precision_cobertura_f1` y `calcular_metricas`), contando las repeticiones de cada palabra. Con eso se evalúan respuestas reales del cliente:

```
python src/evaluar_pipeline.py     # 3 preguntas con Gemini: coincidencia en crudo y procesada, precisión, cobertura, F1 y un resumen
python src/generar_resultados.py   # 20 preguntas con Deepseek; guarda docs/resultados_metricas.json
python src/muestra_revision.py     # muestra los 5 casos de menor F1 y los 5 de mayor F1, para revisarlos a mano
python src/revision_manual.py      # guarda la revisión manual (rúbrica de tres preguntas) en docs/revision_manual.json
```

`generar_resultados.py` hace 20 llamadas reales a la API. La revisión manual y sus hallazgos están documentados en `docs/limites_metrica.md`: qué mide la métrica, en qué casos falla, cómo se eligió la muestra revisada y cuándo conviene confiar en el número.

## Banco de prompts y pruebas de consistencia

El banco de prompts (`prompts/banco.py`) tiene tres prompts para la misma tarea de guía de viajes: `resumen_ruta`, `opciones_transporte` y `clasificar_consulta`. Cada script de prueba ejecuta cada prompt 3 veces contra la API real, intenta interpretar la respuesta como JSON con las claves esperadas, y guarda cuántas veces funcionó:

```
python prompts/test_consistencia_gemini.py
python prompts/test_consistencia_deepseek.py
python prompts/test_consistencia_minimax.py
```

Los resultados quedan en `prompts/registro_resultados_gemini.json`, `prompts/registro_resultados_deepseek.json` y `prompts/registro_resultados_minimax.json`. Estas pruebas hacen varias llamadas reales, así que consumen cuota de tu cuenta y pueden tardar un par de minutos.

## Estructura de carpetas

- `src/` : todo el código fuente del proyecto: `main.py` (punto de entrada), `cliente.py` y `cliente_api.py` (el cliente modular base), `pipeline_texto.py` (limpieza, tokenización y métricas), los scripts de evaluación (`evaluar_pipeline.py`, `generar_resultados.py`, `muestra_revision.py` y `revision_manual.py`) y `proveedores_ia/`, con el módulo de consumo (`consumir_*.py`) y el cliente modular (`cliente_*.py`) de cada modelo.
- `prompts/` : el banco de prompts, los scripts de prueba de consistencia y sus registros de resultados.
- `docs/` : documentación técnica del proyecto: diagramas de arquitectura y de manejo de errores, decisión de arquitectura, registro del ensayo de rate limit, documentación de las pruebas, el documento de límites de la métrica, los resultados y la revisión manual (`.json`) y capturas de evidencia.
- `tests/` : la suite de `pytest` del cliente modular y del pipeline de texto. `pytest.ini` en la raíz le indica dónde está el código.
- `requirements.txt` : dependencias de Python del proyecto, para que cualquier otra persona pueda reconstruir tu entorno con un solo comando.
- `.env.example` : plantilla de las variables de entorno que el proyecto necesita, sin valores reales. Tu archivo `.env` real (con tus credenciales) nunca se commitea.
- `.gitignore` : le dice a Git qué archivos y carpetas ignorar (entre ellos, tu entorno virtual y tu archivo `.env`).


## Pruebas de sistema

Para comprobar que el repositorio funciona desde cero, clónalo en una carpeta limpia y sigue los pasos de instalación y ejecución:

```
rm -rf prueba_gate1
mkdir prueba_gate1
cd prueba_gate1
git clone git@github.com:meatxsucks/Accenture_IA.git prueba-gate1
cd prueba-gate1
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 src/main.py
```

Antes de ejecutar `src/main.py`, completa el archivo `.env` con tus llaves de API.

