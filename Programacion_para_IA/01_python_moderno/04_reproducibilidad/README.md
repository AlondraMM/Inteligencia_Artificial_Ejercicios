# Sesión 4: Organización y reproducibilidad con uv y un servidor MCP local

Construiremos un catálogo de cursos que primero consultaremos como una función
Python y después como una herramienta MCP. El ejemplo permite trabajar con
módulos, dependencias, logging y reproducción del entorno.

## Presentación

[Organización y reproducibilidad con uv y un servidor MCP local (PDF)](https://drive.google.com/file/d/1L7z6CxmTSq6CT-fPHlxq593WCAa2HRcI/view?usp=drivesdk).

## Entrega de prácticas

La fecha límite para entregar las prácticas de la Unidad 1 es el **7 de octubre de 2026**.
Envía los entregables mediante el [formulario de entrega](https://docs.google.com/forms/d/e/1FAIpQLSdTJ2vU04VfIpw1Tst_T_0g0tlbE-n6ZI81nrG0RQJMReAtaQ/viewform?usp=publish-editor).

## Recorrido

1. Crear un proyecto con uv y ejecutar `main.py`.
2. Consultar un archivo JSON desde un módulo reutilizable.
3. Incorporar argumentos y logging.
4. Exponer la consulta mediante un servidor MCP local.
5. Conectar un cliente y reproducir el proyecto desde una copia limpia.

La [guía](./GUIA.md) construye el ejemplo por etapas. El
[proyecto de referencia](./project/README.md) contiene la implementación completa.
La sesión reúne **9 ejercicios**: cinco de la aplicación y cuatro de calidad
con pytest, Ruff, mypy y Makefile. [PRACTICA.md](./PRACTICA.md) reúne los
entregables y enlaza el bloque de [CALIDAD.md](./CALIDAD.md).

## Ejecutar la referencia

```bash
cd unidad-01-python-moderno/sesion-04-reproducibilidad/project
uv sync --locked
uv run --locked python main.py python
uv run --locked python client.py python
```

La primera consulta devuelve dos cursos directamente. La segunda inicia un
servidor local, descubre `find_courses`, la invoca mediante MCP y cierra la
conexión. Una búsqueda sin coincidencias devuelve una lista vacía.

[Documentación para profundizar](./FUENTES.md)
