# Catálogo reproducible con MCP: nueve ejercicios resueltos

El proyecto consulta un catálogo local mediante Python y expone la misma búsqueda
como herramienta MCP por stdio. Incluye código, dos catálogos pequeños, nueve
pruebas, configuración y dependencias bloqueadas. Esta documentación conserva
los resultados de los cinco ejercicios de la práctica y los cuatro de calidad.

## Ejecutar la entrega

Descomprime `course-catalog-entrega.zip`, entra en su carpeta `course-catalog` y
ejecuta los comandos siguientes. Se requiere uv y, para las recetas, Make.
`uv sync --locked` reconstruye el entorno; la entrega no contiene `.venv`.

```bash
cd course-catalog
uv sync --locked
uv run --locked python main.py python
uv run --locked python client.py python
make check
```

El cliente inicia y detiene el servidor automáticamente. Para iniciar únicamente
el servidor: `uv run --locked python server.py`; queda esperando mensajes MCP
por stdin. Las recetas `make run`, `make client`, `make server` y `make sync`
equivalen a esas operaciones. `make format` modifica el formato; `make check`
comprueba lint, formato, tipos y pruebas. `.PHONY` evita confundir las recetas
con archivos del mismo nombre.

| Archivo | Responsabilidad |
|---|---|
| `catalog/search.py` | Modelo `Course`, validación, lectura y búsqueda. |
| `catalog/logging_config.py` | Niveles, formato y destinos de logging. |
| `main.py` | Argumentos de consola, salida JSON y códigos de salida. |
| `server.py` | Registro de `find_courses` y transporte MCP por stdio. |
| `client.py` | Descubrimiento y llamada de la herramienta en un proceso real. |
| `data/courses.json` | Catálogo predeterminado: tres cursos, dos de Python. |
| `data/extra_courses.json` | Copia ampliada: cuatro cursos, tres de Python. |
| `tests/` | Búsqueda, validación, consola y comunicación MCP real. |
| `pyproject.toml`, `uv.lock`, `.python-version` | Declaración y reproducción del entorno. |
| `Makefile` | Comandos de ejecución y comprobaciones de calidad. |

## Ejercicio 1: punto de entrada

```bash
uv run python -c "import main"
uv run --locked python -c "import server"
```

Ambos comandos terminaron con código **0**, stdout vacío y stderr vacío.
Importar `main` define sus funciones e importa sus dependencias; no ejecuta
`main()` porque la llamada está protegida por `if __name__ == "__main__":`.
Durante una importación, `__name__` vale `"main"`, por lo que no se procesa
ninguna consulta ni se abre el catálogo.

En `server.py`, `@mcp.tool()` sí registra `find_courses` al importar el módulo:
añade la función a las herramientas disponibles. El mismo guard
`if __name__ == "__main__":` protege la configuración de logging y
`mcp.run(transport="stdio")`. Registrar una herramienta prepara su descripción
y su función; iniciar el servidor abre el transporte y atiende llamadas.

## Ejercicio 2: datos y argumentos

`data/extra_courses.json` es una copia del catálogo original ampliada con:

```json
{"code": "PY03", "title": "Python automation with MCP", "hours": 14}
```

```bash
uv run --locked python main.py python --catalog data/extra_courses.json
uv run --locked python main.py python --catalog data/missing.json
```

La consulta a la copia terminó con código **0** y devolvió exactamente:

```json
[
  {"code": "PY01", "title": "Python foundations", "hours": 12},
  {"code": "PY02", "title": "Python for data analysis", "hours": 16},
  {"code": "PY03", "title": "Python automation with MCP", "hours": 14}
]
```

Su stderr incluyó `INFO | catalog.search | Search completed: 4 courses read, 3 matches`.
La ruta inexistente terminó con código **1**, stdout vacío y un mensaje
`ERROR | __main__ | Catalog search failed`, seguido del traceback de
`FileNotFoundError`. En una terminal, `echo $?` inmediatamente después del
comando permite consultar ese código.

`--catalog` solo cambia la ruta de esa ejecución de `main.py`. La herramienta
MCP sigue llamando `search_courses(query)` con el catálogo predeterminado;
devuelve `PY01` y `PY02`. La ruta predeterminada se calcula desde el archivo
Python y funciona incluso si el directorio actual es otro.

## Ejercicio 3: niveles y destinos

```bash
uv run --locked python main.py python --log-level DEBUG
uv run --locked python main.py python --log-level INFO
uv run --locked python main.py python --log-level ERROR
uv run --locked python main.py python --log-level ERROR --log-file logs/app.log
```

Los cuatro comandos terminaron con código **0** y el mismo JSON de `PY01` y
`PY02` en stdout. Estos fueron los mensajes de consola, enviados a **stderr**:

| Nivel de consola | Resultado en stderr |
|---|---|
| DEBUG | `DEBUG ... Reading catalog: .../data/courses.json` e `INFO ... Search completed: 3 courses read, 2 matches`. |
| INFO | Solo `INFO ... Search completed: 3 courses read, 2 matches`. |
| ERROR | Vacío, porque la búsqueda terminó correctamente. |
| ERROR con archivo | Vacío; el archivo sí recibió los mensajes DEBUG e INFO. |

El archivo contenía estas dos líneas; la ruta absoluta corresponde a la copia
temporal usada para verificar la entrega:

```text
DEBUG | catalog.search | Reading catalog: /private/tmp/course-catalog-practice-5cbuzh8m/clean-verified/data/courses.json
INFO | catalog.search | Search completed: 3 courses read, 2 matches
```

El logger raíz acepta DEBUG. Cada handler filtra después: la consola aplica
`--log-level`, mientras el handler de archivo acepta DEBUG. Por eso ERROR en
consola no impide conservar DEBUG e INFO en el archivo. `StreamHandler()` usa
stderr de forma predeterminada. En `server.py`, stdout transporta los mensajes
MCP; imprimir logs o texto adicional allí podría romper el intercambio del
protocolo. El stdout del **cliente** muestra la respuesta recibida; no es el
stdout de transporte del servidor.

## Ejercicio 4: mejorar el diagnóstico

El mensaje INFO de `catalog/search.py` incluye el total de cursos validados
y la cantidad de coincidencias, utilizando argumentos de logging:

```python
logger.info(
    "Search completed: %d courses read, %d matches", len(courses), len(matches)
)
```

Los argumentos permiten al sistema de logging formar el mensaje cuando lo
necesita. El mensaje observado para `python` fue
`Search completed: 3 courses read, 2 matches`. Este cambio solo añade información
al diagnóstico: la consulta directa y la llamada MCP devolvieron los mismos
cursos, en el mismo orden. `tests/test_mcp.py` compara el contenido estructurado
MCP con los modelos serializados de `search_courses("python")` y comprueba que
el catálogo alternativo tiene tres coincidencias.

## Ejercicio 5: reproducción y llamada MCP

La verificación se realizó desde una copia limpia, inicialmente sin `.venv`,
logs ni cachés. `uv sync --locked` terminó con código **0**, creó un nuevo
entorno e instaló 39 paquetes; `uv.lock` permaneció sin cambios. Después se
ejecutaron las tres llamadas:

```bash
uv run --locked python client.py python
uv run --locked python client.py astronomy
uv run --locked python client.py "   "
```

Todas descubrieron exactamente `Tools: ['find_courses']`. La respuesta MCP
incluyó `result_type: "complete"` y estos resultados:

| Consulta | `structured_content` | `is_error` | Código de salida |
|---|---|---|---|
| `python` | `{"result": [{"code": "PY01", "title": "Python foundations", "hours": 12}, {"code": "PY02", "title": "Python for data analysis", "hours": 16}]}` | `false` | 0 |
| `astronomy` | `{"result": []}` | `false` | 0 |
| Tres espacios | `null` | `true` | 1 |

Para `python`, `content` contenía dos bloques de texto con los mismos cursos;
para `astronomy`, `content` fue `[]`. Para los espacios, el único bloque de
texto fue exactamente:

```text
Error executing tool find_courses: Cannot search the catalog. Check the query and server logs.
```

`astronomy` es una búsqueda válida sin coincidencias. Los espacios se normalizan
con `strip()` y forman una consulta vacía: se lanza
`ValueError("Query must not be blank")`, registrada en stderr y convertida en
error de herramienta. El cliente devuelve código 1 cuando `is_error` es verdadero.
La prueba MCP también consulta otra vez `python` después del error y verifica
que el mismo servidor sigue respondiendo.

`pyproject.toml` declara el proyecto, Python mínimo (`>=3.12`), dependencias
de ejecución y desarrollo, y configuración de herramientas. `uv.lock` conserva
versiones resueltas, dependencias transitivas y hashes; `--locked` exige que
coincida con la declaración. `.python-version` selecciona Python `3.13` para uv.
No fija por sí solo el parche exacto: la comprobación usó **3.13.3**. `.venv`
contiene rutas y archivos específicos de la instalación local; se reconstruye
desde estos archivos y no forma parte de la entrega.

Versiones comprobadas en la copia limpia:

| Herramienta | Versión |
|---|---|
| Python | 3.13.3 |
| MCP | 2.2.0 |
| Pydantic | 2.13.5 |
| mypy | 2.3.1 |
| pytest | 9.1.1 |
| Ruff | 0.16.8 |

## Ejercicio 6: horas negativas (calidad 1)

`test_negative_hours`, en `tests/test_catalog.py`, escribe un catálogo temporal
con `hours: -4`. Comprueba que la búsqueda lanza `ValidationError` y examina
el error: campo `hours`, tipo `greater_than`, valor rechazado `-4` y restricción
`{"gt": 0}`. Esto verifica la regla `Field(gt=0)`, además del caso previo con
cero horas. La prueba pasó en la ejecución completa.

## Ejercicio 7: fallo de consola (calidad 2)

`test_missing_catalog_has_error_exit_and_no_stdout`, en `tests/test_main.py`,
usa `subprocess.run`, `sys.executable` y `tmp_path`. Ejecuta el programa real
desde un directorio temporal con una ruta inexistente. Comprueba código **1**,
stdout exactamente vacío y stderr con `Catalog search failed`,
`FileNotFoundError` y la ruta solicitada. La prueba pasó. Otra prueba comprueba
que el catálogo predeterminado funciona desde fuera del proyecto.

## Ejercicio 8: falla y corrección de Ruff (calidad 3)

Se añadió temporalmente `import os` a `client.py` y se ejecutó:

```bash
uv run --locked ruff check client.py
```

El comando terminó con código **1** y mostró:

```text
F401 [*] `os` imported but unused
 --> client.py:5:8
Found 1 error.
[*] 1 fixable with the `--fix` option.
```

Se eliminó ese import. La comprobación completa posterior pasó; el fallo
deliberado no permanece en el código entregado.

## Ejercicio 9: calidad desde una copia limpia (calidad 4)

Tras reconstruir el entorno con `uv sync --locked`, se ejecutó `make check`
en la copia limpia. Código de salida **0**, stderr vacío y transcript guardado:

```text
uv run --locked ruff check .
All checks passed!
uv run --locked ruff format --check .
10 files already formatted
uv run --locked mypy --strict main.py server.py client.py catalog
Success: no issues found in 6 source files
uv run --locked python -m pytest
.........                                                                [100%]
9 passed in 1.13s
```

Ruff comprobó problemas de código; `ruff format --check` comprobó formato sin
modificar archivos. Mypy analizó tipos en modo estricto y pytest ejecutó las
pruebas, incluida la comunicación MCP por un proceso real. Si Make no está
instalado, se pueden ejecutar directamente los cuatro comandos del transcript.

El SHA-256 de `uv.lock` antes y después de la reproducción fue el mismo:

```text
7752f3c5314f2af1b2b97d89b3e1d25752a517302a530f563e94630f1df85f8b
```

El archivo de entrega contiene únicamente el proyecto reproducible: no incluye
`.venv`, logs, cachés ni archivos compilados. Los logs mostrados arriba son
evidencia conservada en este README; se generan de nuevo al usar `--log-file`.
