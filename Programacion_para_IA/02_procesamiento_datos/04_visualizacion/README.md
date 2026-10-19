# Sesión 4: Visualización de datos

[Presentación de la sesión (PDF)](https://drive.google.com/file/d/19PdTA8ILRMk53OZG0Cddl8fo4GeTniYx/view?usp=drivesdk).

Una sesión breve para representar los resultados de Titanic y las imágenes de
CIFAR-10 con Matplotlib. Trabajaremos con un histograma, una comparación de
porcentajes y una cuadrícula de imágenes.

## Entrega de prácticas

La fecha límite para entregar las prácticas de la Unidad 2 es el **19 de octubre de 2026**.
Envía los entregables mediante el [formulario de entrega](https://docs.google.com/forms/d/e/1FAIpQLScOPQOB1sgjXsZbrealNcJ_U8Aa-bqtds5SozcSsRNSek7FxA/viewform?usp=publish-editor).

## Material y ejercicios

La [notebook u2_n5_visualizacion](./u2_n5_visualizacion.ipynb) introduce los ejemplos
y contiene **dos ejercicios**: ajustar los intervalos de un histograma y comparar
el porcentaje de edades ausentes por clase. Consulta los
[entregables en PRACTICA.md](./PRACTICA.md). `main.py` exporta los tres gráficos de ejemplo.

## Preparación

Necesitas las salidas de los proyectos de las sesiones 2 y 3. Si aún no existen,
ejecuta `uv sync --locked` y `uv run --locked python main.py` desde cada proyecto.
En la sesión 3, añade `--download` si todavía no tienes CIFAR-10.

Desde esta carpeta:

```bash
uv sync --locked
```

Abre [u2_n5_visualizacion.ipynb](./u2_n5_visualizacion.ipynb) en VS Code o
PyCharm con el entorno `.venv` de este proyecto; consulta las
[opciones de editor](../README.md#notebooks-locales).
Aquí usamos los archivos NumPy
ya exportados, por lo que no hace falta instalar PyTorch otra vez.

## Exportar los ejemplos

```bash
uv run --locked python main.py
```

El programa guarda `ages.png`, `survival.png` y `cifar_grid.png` en `outputs/`.
Otra ejecución reemplaza esas figuras. Las salidas están excluidas de Git.

[Fuentes oficiales](./FUENTES.md) · [Volver a la unidad](../README.md)
