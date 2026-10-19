# Práctica: NumPy y vectorización

Resuelve **11 ejercicios**: el 1–8 en la [notebook de exploración](./01-exploracion/u2_n1_arreglos_numpy.ipynb),
el 9 en una celda nueva de esa misma notebook y el 10–11 en la
[notebook de reporte](./02-reporte-mediciones/u2_n2_reporte_mediciones.ipynb).
Las instrucciones del 9 y la implementación del 11 se detallan aquí.

## Ejercicio 9: diferencias respecto de la media

Calcula la media de cada sala y réstala de `readings` sin un ciclo por ronda.
Comprueba la forma `(8, 3)` y que la media de cada columna de diferencias sea
aproximadamente cero. Explica cómo se alinean las formas `(8, 3)` y `(3,)`
y por qué no se resta la media general.

## Ejercicio 11: aplicación independiente

En `02-reporte-mediciones`, crea `measurements/selection.py` con
`select_warm_rounds(readings, threshold)`. Devuelve las filas cuya temperatura
norte sea mayor o igual al umbral, conserva las tres columnas y evita modificar
la entrada. Reutiliza la comprobación de matriz no vacía con tres columnas;
rechaza datos o umbrales no finitos con `ValueError`.

- Llama la función desde la notebook de reporte después de seleccionar filas completas.
- Con el archivo original y umbral `27`, comprueba
  `[[27, 29, 25], [28, 30, 26], [29, 31, 27]]`.
- Con umbral `100`, comprueba la forma `(0, 3)` y explica por qué no se calcula su media.
- Comprueba en la notebook el umbral exacto, ninguna coincidencia, valores no
  finitos y una selección que se pueda modificar sin cambiar el original. Usa
  `assert` para los resultados y `try`/`except` para los errores esperados.
- Compara las medias de la selección y del conjunto completo. Explica qué filas
  entraron en cada cálculo.

## Entregables

- Una copia de cada notebook con los ejercicios resueltos, resultados y explicaciones.
- El proyecto de reporte con el módulo nuevo.

Reinicia el kernel y ejecuta ambas notebooks. Comprueba que el proyecto se
reconstruya con `uv sync --locked`. Entrega el código y
los archivos de configuración, sin `.venv` ni cachés.
