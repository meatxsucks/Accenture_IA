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

```
python src/consumir_gemini.py
python src/consumir_openrouter_Deepseek.py
python src/consumir_openrouter_Minimax.py
```

## Banco de prompts y pruebas de consistencia

El banco de prompts (`prompts/banco.py`) tiene tres prompts para la misma tarea de guía de viajes: `resumen_ruta`, `opciones_transporte` y `clasificar_consulta`. Cada script de prueba ejecuta cada prompt 3 veces contra la API real, intenta interpretar la respuesta como JSON con las claves esperadas, y guarda cuántas veces funcionó:

```
python prompts/test_consistencia_gemini.py
python prompts/test_consistencia_deepseek.py
python prompts/test_consistencia_minimax.py
```

Los resultados quedan en `prompts/registro_resultados_gemini.json`, `prompts/registro_resultados_deepseek.json` y `prompts/registro_resultados_minimax.json`. Estas pruebas hacen varias llamadas reales, así que consumen cuota de tu cuenta y pueden tardar un par de minutos.

## Estructura de carpetas

- `src/` : todo el código fuente del proyecto: `main.py` (punto de entrada) y un módulo de consumo de API por cada modelo.
- `prompts/` : el banco de prompts, los scripts de prueba de consistencia y sus registros de resultados.
- `docs/` : documentación técnica del proyecto (diagrama de arquitectura, decisión de arquitectura y capturas de evidencia).
- `tests/` : pruebas de tu código (las vas a usar más adelante en el programa, cuando el proyecto lo requiera).
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

