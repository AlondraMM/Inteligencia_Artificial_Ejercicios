# Sesión 1: Python como cliente SQL y NoSQL

Conectaremos Python a un catálogo de documentos: primero como tabla SQLite y luego
como grafo Neo4j. El foco está en conexiones, consultas parametrizadas, resultados
y context managers; no en administrar bases de datos.

## Entrega de prácticas

La fecha límite para entregar las prácticas de la Unidad 3 es el **19 de octubre de 2026**.
Envía los entregables mediante el [formulario de entrega](https://docs.google.com/forms/d/e/1FAIpQLSd0_iF2IEHUsLu2WXZuq-GwOSBUTfPyKNV4ht_mbH070wxljg/viewform?usp=publish-editor).

## Material

- [Presentación (PDF)](https://drive.google.com/file/d/11EPsoBrk9rm0xkdjXOy0PuIkdz48iXc5/view?usp=drivesdk).

- [SQLite y pandas](./u3_n1_sqlite_pandas.ipynb): ejemplos y **3 ejercicios**.
- [Neo4j](./u3_n2_neo4j.ipynb): demostración opcional, sin ejercicios.
- [PRACTICA.md](./PRACTICA.md): entregables.
- [Fuentes oficiales](./FUENTES.md).

## Preparación

Abre esta carpeta como proyecto en VS Code o PyCharm y ejecuta:

```bash
uv sync --locked
```

Selecciona `.venv` como intérprete y kernel de las notebooks. En VS Code necesitas
las extensiones Python y Jupyter; en PyCharm usa la integración de notebooks.
SQLite forma parte de Python. `neo4j` instala el driver, no el servidor.

También puedes ejecutar los ejemplos SQL desde la terminal:

```bash
uv run --locked python main.py
```

Este comando y la primera celda de SQLite restauran el catálogo de seis documentos
en `outputs/documents.db`. La notebook añade el documento 7 durante la demostración.
La carpeta `outputs/` está excluida de Git.

## Neo4j Desktop (opcional)

Para seguir la segunda notebook, recomendamos [Neo4j Desktop](https://neo4j.com/download/).
No necesitas instalarlo para entregar la práctica.

1. Instala Desktop y crea una instancia local con una contraseña propia.
2. Inicia la instancia y verifica el nombre de la base; en el ejemplo usamos `neo4j`.
3. Copia la URI de conexión en `NEO4J_URI`; el ejemplo usa `neo4j://127.0.0.1:7687`.
4. Cambia `RUN_NEO4J = True` y ejecuta la notebook; `getpass()` solicitará la contraseña.

Los ejemplos usan etiquetas `LessonAuthor` y `LessonDocument`. `MERGE` permite
repetirlos sin duplicar los nodos y relaciones del catálogo proporcionado.
Si falla la conexión, comprueba que la instancia esté iniciada, que la URI y la
base coincidan con Desktop y que las credenciales sean correctas.

[Instalación oficial](https://neo4j.com/docs/desktop/current/installation/) ·
[Gestión de instancias](https://neo4j.com/docs/desktop/current/) ·
[Volver a la unidad](../README.md)
