# Documentación para profundizar

## Proyecto y reproducibilidad

- [Instalar uv](https://docs.astral.sh/uv/getting-started/installation/).
- [Trabajar con proyectos](https://docs.astral.sh/uv/guides/projects/).
- [Dependencias](https://docs.astral.sh/uv/concepts/projects/dependencies/).
- [Lockfile y sincronización](https://docs.astral.sh/uv/concepts/projects/sync/).
- [Punto de entrada de Python](https://docs.python.org/3/library/__main__.html).

## Logging y datos

- [Logging HOWTO](https://docs.python.org/3/howto/logging.html).
- [Loggers, handlers y formatters](https://docs.python.org/3/library/logging.html).
- [Modelos de Pydantic](https://docs.pydantic.dev/latest/concepts/models/).

## MCP local

- [SDK oficial de Python, versión 2](https://py.sdk.modelcontextprotocol.io/).
- [Ejecución y transporte stdio](https://py.sdk.modelcontextprotocol.io/run/).
- [Cliente Python](https://py.sdk.modelcontextprotocol.io/client/).
- [Transportes del cliente](https://py.sdk.modelcontextprotocol.io/client/transports/).
- [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector).
- [Conexión a un host](https://py.sdk.modelcontextprotocol.io/get-started/real-host/).

El proyecto declara `mcp>=2,<3`; `uv.lock` conserva la versión probada. Al consultar
otros ejemplos, verifica la versión: la línea 1.x usaba `FastMCP`, mientras que
esta práctica sigue `MCPServer` del SDK 2.x.

## Calidad

- [pytest](https://docs.pytest.org/en/stable/getting-started.html).
- [Ruff](https://docs.astral.sh/ruff/tutorial/).
- [mypy](https://mypy.readthedocs.io/en/stable/getting_started.html).
- [GNU Make](https://www.gnu.org/software/make/manual/make.html).
