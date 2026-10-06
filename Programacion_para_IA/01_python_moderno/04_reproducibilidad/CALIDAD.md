# Calidad de código: pytest, Ruff, mypy y Makefile

Este bloque final trabaja sobre el catálogo ya construido. Puede continuarse
en otra sesión.

## Comprobaciones directas

Al construirlo desde cero, agrega las herramientas:

```bash
uv add --dev pytest ruff mypy
```

Copia la configuración de herramientas del `pyproject.toml` de referencia y
revisa [tests](./project/tests). Las pruebas de búsqueda comprueban normalización,
consultas vacías, ausencia de coincidencias y errores de archivo. La prueba MCP
arranca un proceso real, descubre la herramienta y verifica que el servidor
sigue respondiendo después de una consulta inválida.

```bash
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy --strict main.py server.py client.py catalog
uv run --locked python -m pytest
```

Ruff revisa estilo y problemas frecuentes. `format --check` no modifica archivos.
Mypy analiza los tipos sin ejecutar las consultas; `--strict` activa controles
adicionales. Pytest ejecuta los casos y comprueba sus resultados.

## Makefile

Copia el [Makefile](./project/Makefile). Sus recetas usan tabulaciones.
`check` reúne lint, formato, tipos y pruebas. `run` consulta sin MCP y `client`
hace una llamada al servidor. `.PHONY` evita confundir tareas con archivos.

```bash
make check
make run
make client
```

`make format` sí cambia el formato de archivos. Make no se instala con uv;
si no está disponible, usa los comandos directos anteriores. En Windows puedes
usar esos comandos desde PowerShell sin instalar Make.

## Ejercicios de calidad

1. Agrega una prueba de un catálogo cuyo curso tenga horas negativas.
2. Agrega una prueba de consola que compruebe código 1 y stdout vacío ante un
   archivo inexistente. Usa `subprocess.run` y un directorio temporal de pytest.
3. Introduce un import sin usar, observa la falla de Ruff y corrígelo.
4. Ejecuta todas las comprobaciones desde una copia limpia.

Entrega las pruebas y la configuración junto al proyecto.
Consulta las [fuentes oficiales](./FUENTES.md) para profundizar.
