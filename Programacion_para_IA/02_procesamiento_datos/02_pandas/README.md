# Sesión 2: Tablas con pandas y paso a NumPy

[Presentación de la sesión (PDF)](https://drive.google.com/file/d/1fgePaMIGZf_aMCW_2T3xgsepiQbHjG82/view?usp=drivesdk).

En la sesión anterior, cada columna del arreglo representaba una sala y todas
contenían temperaturas. Titanic reúne números, texto y valores ausentes en una
misma tabla. Usaremos pandas para conservar los nombres de las columnas mientras
seleccionamos, limpiamos y agrupamos pasajeros. Al final extraeremos únicamente
las columnas numéricas que necesitaremos como matriz en la siguiente sesión.

## Entrega de prácticas

La fecha límite para entregar las prácticas de la Unidad 2 es el **19 de octubre de 2026**.
Envía los entregables mediante el [formulario de entrega](https://docs.google.com/forms/d/e/1FAIpQLScOPQOB1sgjXsZbrealNcJ_U8Aa-bqtds5SozcSsRNSek7FxA/viewform?usp=publish-editor).

## Recorrido

1. Abre [u2_n3_pandas_titanic.ipynb](./u2_n3_pandas_titanic.ipynb) en VS Code o PyCharm con el entorno de este proyecto.
2. Examina columnas, tipos, ausentes y filas repetidas.
3. Filtra, agrupa y crea una variable nueva sin perder las etiquetas.
4. Comprueba un `merge` sencillo y transforma las columnas numéricas a NumPy.
5. Ejecuta [main.py](./main.py) para generar los mismos datos preparados desde la terminal.

Los **ejercicios 1–4** se resuelven en la notebook. La
[práctica](./PRACTICA.md) contiene el ejercicio 5, que amplía el módulo y su
reporte. Consulta los entregables en [PRACTICA.md](./PRACTICA.md).

## Ejecutar

Desde esta carpeta:

```bash
uv sync --locked
```

Consulta las [opciones de editor](../README.md#notebooks-locales) para
seleccionar el entorno `.venv`.

La notebook utiliza [Titanic-Dataset.csv](./datasets/Titanic-Dataset.csv),
incluido en el repositorio. No requiere cuenta de Kaggle ni descarga durante la
clase. Para generar los archivos de salida:

```bash
uv run --locked python main.py
uv run --locked ruff check .
```

La aplicación escribe `passengers_prepared.csv`, `survival_by_group.csv`,
`missing_age_by_class.csv`, `features.npy` y `labels.npy` en `outputs/`.
`missing_age_by_class.csv` contiene el número de pasajeros y la proporción de
edades originalmente ausentes por clase, conservando también una clase ausente
si aparece en otra entrada. Los CSV mantienen nombres de columnas
y grupos; los archivos NumPy contienen una matriz numérica `(891, 4)` y un vector
de etiquetas `(891,)`. Son materiales para estudiar representación de datos, no
un conjunto de entrenamiento preparado para evaluar modelos.

La tabla de [fuentes](./FUENTES.md) reúne la documentación oficial usada en esta
sesión.

[Volver al contenido de la unidad](../README.md)

Las pruebas existentes se pueden ejecutar con `uv run --locked python -m pytest`
como apoyo opcional; no se pide crear pruebas para la práctica.
