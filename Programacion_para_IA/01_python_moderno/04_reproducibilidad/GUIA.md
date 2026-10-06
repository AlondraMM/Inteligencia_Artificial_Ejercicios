# De una función Python a un servidor MCP local

El proyecto consulta un catálogo de cursos. Construiremos primero una aplicación
que funciona desde la terminal y luego reutilizaremos su búsqueda mediante MCP.

## 1. Crear el proyecto

Instala uv desde las [instrucciones oficiales](https://docs.astral.sh/uv/getting-started/installation/).
Abre una terminal en tu carpeta de prácticas. `cd nombre` entra en una carpeta
y `cd ..` vuelve a la anterior. Crea el ejemplo fuera del proyecto de referencia:

```bash
uv init --no-package --python 3.13 --vcs none course-catalog
cd course-catalog
uv run python main.py
```

`--no-package` crea una aplicación que ejecutaremos como scripts. `--vcs none`
pospone la creación del repositorio Git. Python ejecuta el código y uv prepara
el entorno y sus dependencias. No necesitas activar `.venv` manualmente.

| Archivo o carpeta | Función |
|---|---|
| `main.py` | Punto de entrada de la aplicación de consola. |
| `pyproject.toml` | Nombre, compatibilidad y dependencias declaradas. |
| `.python-version` | Intérprete elegido para trabajar. |
| `uv.lock` | Versiones resueltas de dependencias directas y transitivas. |
| `.venv/` | Entorno local que uv puede reconstruir. |

`uv run` crea el entorno y el lockfile cuando hace falta. Comprueba el intérprete:

```bash
uv run python -c "import sys; print(sys.executable)"
```

## 2. Una función antes del protocolo

Reemplaza `main.py` por este ejemplo completo:

```python
def search_courses(query: str) -> list[str]:
    titles = ["Python foundations", "Python for data analysis", "Machine learning introduction"]
    matches = []
    for title in titles:
        if query.strip().casefold() in title.casefold():
            matches.append(title)
    return matches


def main() -> None:
    print(search_courses("python"))


if __name__ == "__main__":
    main()
```

`strip()` elimina espacios de los extremos y `casefold()` permite comparar sin
distinguir mayúsculas. Aquí la búsqueda es por una secuencia de caracteres en el
título. Todavía no validamos consultas vacías; lo añadiremos al extraer el módulo.

```bash
uv run python main.py
uv run python -c "import main"
```

El primer comando imprime dos títulos. El segundo importa el módulo sin ejecutar
la consulta. Python no llama automáticamente a una función llamada `main`:
la condición `if __name__ == "__main__"` decide cuándo hacerlo.

## 3. Archivo de datos y módulo reutilizable

```bash
uv add "pydantic>=2,<3"
uv tree
```

`uv add` actualiza las dependencias y su resolución. `uv tree` muestra también
las bibliotecas que estas necesitan. `json`, `pathlib` y `logging` pertenecen a
Python y no requieren `uv add`.

Crea `data/courses.json` copiando el [catálogo](./project/data/courses.json).
Crea la carpeta `catalog`, un `catalog/__init__.py` vacío y copia
[catalog/search.py](./project/catalog/search.py). Recorre el módulo:

- `Course` retoma Pydantic y exige un número positivo de horas.
- `search_courses` rechaza consultas vacías, carga el JSON y compara títulos.
- Si no encuentra cursos, devuelve `[]`. Un archivo ausente o inválido provoca
  una excepción: no equivale a una búsqueda sin coincidencias.

Un archivo `.py` es un módulo. `catalog` agrupa módulos en un paquete importable.
La ruta `Path(__file__).resolve().parents[1]` localiza la carpeta del proyecto a
partir del archivo del módulo. Así el catálogo no depende de dónde arranque un
cliente externo.

Sustituye temporalmente `main.py` por:

```python
from catalog.search import search_courses


def main() -> None:
    for course in search_courses("python"):
        print(course.model_dump_json())


if __name__ == "__main__":
    main()
```

Ejecuta y comprueba los códigos `PY01` y `PY02`. La función se puede usar sin MCP.

## 4. Logging y argumentos

Agrega `import logging` y esta configuración al principio de `main()`:

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s",
)
```

El módulo usa `logging.getLogger(__name__)` y emite eventos. La entrada del
programa configura sus destinos. Cambia INFO por DEBUG y compara los mensajes.

| Nivel | Ejemplo |
|---|---|
| DEBUG | Ruta del catálogo que se lee. |
| INFO | Cantidad de coincidencias de una consulta. |
| WARNING | Situación recuperable que merece atención; aquí no necesitamos emitir una. |
| ERROR | Consulta que no pudo completarse. |

Copia [logging_config.py](./project/catalog/logging_config.py) y reemplaza
`main.py` por la [versión de referencia](./project/main.py). `argparse` recibe
la consulta y opciones; `main` devuelve 0 al completar la búsqueda y 1 ante un
error. `raise SystemExit(main())` comunica ese resultado a la terminal.

```bash
uv run python main.py python
uv run python main.py python --log-level DEBUG
uv run python main.py python --log-level ERROR --log-file logs/app.log
uv run python main.py python --catalog data/missing.json
```

Un **handler** dirige mensajes a un destino; un **formatter** define cómo se ven.
El logger raíz acepta DEBUG. El handler de consola aplica el nivel solicitado,
y el archivo opcional recibe desde DEBUG. Por eso la tercera ejecución guarda
mensajes en el archivo aunque la consola no los muestre.

```bash
uv run python main.py python > result.json
```

El JSON sale por stdout. `StreamHandler` escribe en stderr, por lo que los logs
no contaminan el archivo. Dentro de `except`, `logger.exception` registra ERROR
con traceback. Consulta el código de salida inmediatamente con `echo $?` en
macOS/Linux o `$LASTEXITCODE` en PowerShell.

## 5. Exponer la función como herramienta MCP

MCP es un protocolo para que una aplicación descubra e invoque herramientas.
El **servidor** publica funciones; el **cliente** consulta cuáles están disponibles
y solicita su ejecución. Una aplicación de IA puede incorporar ese cliente.
Nuestro servidor realiza la búsqueda, sin generar una respuesta de lenguaje natural.

```bash
uv add "mcp>=2,<3"
```

Usaremos el SDK oficial versión 2. Algunos ejemplos antiguos importan FastMCP;
aquí seguimos su API actual, `MCPServer`. Copia [server.py](./project/server.py).
La parte central es:

```python
mcp = MCPServer("Course catalog")


@mcp.tool()
def find_courses(query: str) -> list[Course]:
    """Find courses by words in their title, ignoring letter case."""
    return search_courses(query)
```

Este fragmento muestra el registro; el archivo completo incluye los imports y
el manejo de errores. El decorador registra la función como herramienta. El SDK
usa anotaciones y docstring para describir su entrada, salida y propósito.
La función de búsqueda sigue dentro de `catalog/search.py`.

La versión completa captura errores de lectura y validación, registra su detalle
y comunica `ToolError` al cliente. El servidor puede atender otra consulta después.

```bash
uv run python server.py
```

El transporte **stdio** intercambia mensajes por stdin y stdout del proceso.
El servidor espera una petición MCP: no abre un puerto ni una página. No escribas
una búsqueda como texto libre en esa terminal. Detén esta prueba con Ctrl+C.
Durante el servicio, stdout pertenece al protocolo. Usa logging a stderr en
lugar de `print` para diagnosticar el servidor.

El SDK puede configurar el logger raíz al crear `MCPServer`. Nuestra configuración
reemplaza los handlers antes de arrancar, para evitar destinos duplicados y aplicar
el formato elegido. Importar `server` registra la herramienta, pero no inicia
el transporte, gracias a la condición final del archivo.

## 6. Hacer una llamada local

Copia [client.py](./project/client.py) y ejecuta:

```bash
uv run --locked python client.py python
uv run --locked python client.py astronomy
uv run --locked python client.py " "
```

El cliente inicia `server.py` con el mismo intérprete, descubre `find_courses` y
la llama. `async with` gestiona la conexión y `await` espera las respuestas,
retomando la sesión anterior. Al terminar cierra la conexión y el proceso servidor.
No necesitas arrancar `server.py` en otra terminal.

La primera llamada devuelve los cursos PY01 y PY02. La segunda termina con éxito
y una lista vacía. La tercera devuelve un resultado de herramienta con
`is_error: true` y el cliente termina con código 1. El JSON MCP incluye un sobre
con contenido y metadatos; no es idéntico al JSON de la aplicación de consola.

Los `print` de este archivo muestran resultados en la terminal del **cliente**.
No escriben en el stdout reservado del proceso **servidor**.

## 7. Inspeccionar la herramienta

[MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) permite
explorar la herramienta visualmente. Requiere Node.js y `npx`; es una alternativa
al cliente Python incluido. Desde el proyecto:

```bash
npx @modelcontextprotocol/inspector uv run --locked python server.py
```

Abre la URL local que muestra Inspector. Selecciona el transporte stdio y conecta
con el comando indicado. En Tools, lista las herramientas, selecciona
`find_courses` y envía `query` con el valor `python`. Compara con `astronomy` y
una cadena de espacios. Inspector inicia el servidor, igual que el cliente de
la etapa anterior. Al terminar, desconecta y detén Inspector con Ctrl+C.

Para un host compatible con stdio, el comando equivalente es:

```bash
uv --directory /ruta/absoluta/course-catalog run --locked python server.py
```

Usa tu ruta real. Cada host tiene su propio formato de configuración. Consulta
[conexión a un host](https://py.sdk.modelcontextprotocol.io/get-started/real-host/).

## 8. Reproducir el proyecto

```bash
uv sync --locked
uv run --locked python client.py python
```

`--locked` falla si `pyproject.toml` requiere cambiar el lockfile. `--frozen` omite
esa comprobación de vigencia. Un `uv sync` normal puede actualizar la resolución.

Versiona código, datos de muestra, README, `.python-version`, `pyproject.toml`
y `uv.lock`. Copia [.gitignore](./project/.gitignore) y excluye `.venv`, cachés,
logs y resultados. El lockfile fija dependencias, pero no guarda los datos ni
reproduce por sí solo todo el sistema operativo.

En la carpeta independiente de tu práctica, inicializa Git, revisa los archivos
antes de guardarlos y crea un commit. Si trabajas dentro del repositorio del curso,
usa ese repositorio en lugar de crear otro anidado. Desde la carpeta superior de
un proyecto independiente ya guardado:

```bash
git clone ./course-catalog course-catalog-check
cd course-catalog-check
uv sync --locked
uv run --locked python client.py python
```

El clon reconstruye `.venv` a partir del lockfile. Debe devolver los mismos dos
cursos. Continúa con [PRACTICA.md](./PRACTICA.md). El bloque final de
[calidad](./CALIDAD.md) usa el mismo proyecto. Las [fuentes oficiales](./FUENTES.md)
permiten profundizar en MCP y en la gestión de proyectos.
