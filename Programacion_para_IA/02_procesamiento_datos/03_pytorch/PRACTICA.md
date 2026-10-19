# Práctica: tensores y datasets

Resuelve **5 ejercicios**: el 1–4 en [la notebook](./u2_n4_tensores_datasets.ipynb)
y el 5 en el proyecto, según las instrucciones siguientes.

## Ejercicio 5: proporciones por clase

Amplía `label_summary` en `data_lab/inspection.py` con `proportion`: la fracción
de cada clase respecto de todas las etiquetas recibidas. Conserva `class_id`,
`class_name`, `count` y las clases con conteo cero. Actualiza el tipo de retorno
para admitir valores `float`.

Comprueba en la notebook, mediante `assert`, el resultado con etiquetas `[0, 0, 2, 2, 2]` y clases
`["class_a", "class_b", "class_c"]`: conteos `[2, 0, 3]`, proporciones
`[0.4, 0.0, 0.6]` y suma aproximadamente uno.

Ejecuta `uv run --locked python main.py --limit 10 --batch-size 4` y comprueba
la columna nueva en `class_counts.csv`. Conserva `shuffle=False` y
`drop_last=False`. Explica por qué cambiar el tamaño de lote conserva los
conteos y cambiar `limit` puede alterarlos.

## Entregables

- Una copia de la notebook con los ejercicios 1–4 resueltos y sus explicaciones.
- El proyecto con la función modificada.
- `class_counts.csv` y la explicación del denominador y los conteos, que puede ir
  en la notebook.

Ejecuta toda la notebook desde un kernel limpio y ejecuta el proyecto según el README.
Entrega el proyecto sin `.venv`, cachés ni la descarga de CIFAR-10; adjunta el CSV.
