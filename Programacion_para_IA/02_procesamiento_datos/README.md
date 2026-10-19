# Unidad 2: Procesamiento y representación de datos para IA

Trabajaremos con arreglos, tablas, tensores y visualizaciones para preparar datos,
comprobar sus transformaciones y explorar sus características. Las notebooks
servirán para experimentar y explicar resultados; los proyectos con `uv`
permitirán repetir el procesamiento desde la terminal.

## Entrega de prácticas

Consulta la [lista de cotejo](./LISTA_COTEJO.md) para revisar los entregables y sus resultados esperados.

La fecha límite para entregar las prácticas de la Unidad 2 es el **19 de octubre de 2026**.
Envía los entregables mediante el [formulario de entrega](https://docs.google.com/forms/d/e/1FAIpQLScOPQOB1sgjXsZbrealNcJ_U8Aa-bqtds5SozcSsRNSek7FxA/viewform?usp=publish-editor).

## Contenido

| Sesión | Tema | Trabajo principal |
|---|---|---|
| 1 | [NumPy y vectorización](./sesion-01-numpy/README.md) | Formas, tipos, selección, vistas, operaciones vectorizadas y broadcasting con mediciones. |
| 2 | [pandas y paso a NumPy](./sesion-02-pandas/README.md) | Cargar, limpiar, agrupar y unir datos de Titanic; extraer una matriz numérica. |
| 3 | [PyTorch y datasets](./sesion-03-pytorch/README.md) | Tensores, `Dataset`, `DataLoader`, CIFAR-10 por lotes y embeddings de texto. |
| 4 | [Visualización](./sesion-04-visualizacion/README.md) | Histogramas, porcentajes por grupo y cuadrículas de imágenes con Matplotlib. |

Las notebooks se numeran de forma continua dentro de la unidad: `u2_n1`,
`u2_n2`, `u2_n3`, etc.

## Notebooks locales

Abre la carpeta del proyecto indicado en el README de la sesión y ejecuta
`uv sync --locked` en su terminal. La sesión 1 tiene dos proyectos, cada uno con
su propia `.venv`. Abre la notebook desde el enlace del README y usa el entorno
de ese proyecto como kernel. Cada proyecto incluye `ipykernel` y `pip` para la
integración con el editor; reiniciar el kernel borra las variables que habían
quedado en memoria.

### VS Code (recomendado)

Instala las extensiones **Python** y **Jupyter**. En la esquina superior derecha
de la notebook, elige **Select Kernel → Python Environments → `.venv`**. Si no
aparece, usa **Select Another Kernel** y selecciona `.venv/bin/python` en
macOS/Linux o `.venv/Scripts/python.exe` en Windows.

[Notebooks en VS Code](https://code.visualstudio.com/docs/datascience/jupyter-notebooks) ·
[uv con VS Code](https://docs.astral.sh/uv/guides/integration/jupyter/#using-jupyter-from-vs-code)

### PyCharm

Abre la carpeta del proyecto en PyCharm. En **Python Interpreter**, selecciona
**Add Interpreter → Add Local Interpreter → uv** y elige la `.venv` existente.
Abre la notebook desde el enlace del README y ejecuta una celda; PyCharm puede
iniciar la ejecución local con ese intérprete. Si cambia de proyecto, selecciona
la `.venv` correspondiente. Si la notebook no se abre correctamente, comprueba
que el complemento **Markdown** esté habilitado en PyCharm.

[Notebooks en PyCharm](https://www.jetbrains.com/help/pycharm/jupyter-notebook-support.html) ·
[Entornos uv en PyCharm](https://www.jetbrains.com/help/pycharm/uv.html)

## Ejercicios

La [sesión 1](./sesion-01-numpy/README.md) tiene ejercicios en las notebooks y
una práctica de aplicación. La [sesión 2](./sesion-02-pandas/README.md) tiene
ejercicios en su notebook y en `PRACTICA.md`. La
[sesión 3](./sesion-03-pytorch/README.md) combina ejercicios de tensores en su
notebook y una ampliación del resumen por clase en `PRACTICA.md`. La [sesión 4](./sesion-04-visualizacion/README.md) contiene dos ejercicios
de visualización en su notebook. Cada README de sesión explica dónde resolverlos y cómo ejecutar sus materiales.

## Producto de la unidad

El trabajo avanza desde una matriz de mediciones hasta una tabla con etiquetas,
una selección de variables numéricas y formas de examinar los datos. Los archivos
generados en la sesión 2 permiten retomar la representación numérica en PyTorch y
la tabla preparada en visualización.
