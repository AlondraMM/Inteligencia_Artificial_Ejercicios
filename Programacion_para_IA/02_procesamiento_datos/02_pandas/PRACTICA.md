# Práctica: tablas con pandas

Resuelve **5 ejercicios**: el 1–4 en [la notebook](./u2_n3_pandas_titanic.ipynb)
y el 5 en el proyecto, según las instrucciones siguientes.

## Ejercicio 5: edades ausentes por clase

En `titanic/analysis.py`, añade `missing_age_by_class(prepared)`: una fila por
`Pclass`, con `passengers` y `missing_age_rate`. Reutiliza `age_missing` y agrupa
con `dropna=False`.

Llama la función desde `main.py` y guarda `outputs/missing_age_by_class.csv`.
Comprueba que los conteos sumen 891 y las proporciones estén entre cero y uno.
Comprueba también la función en la notebook con datos pequeños construidos por ti
y `assert`. Explica en dos o tres
frases qué aporta la proporción por clase frente al total de 177 edades ausentes,
sin interpretar la asociación como una causa.

## Entregables

- Una copia de la notebook con los ejercicios 1–4 resueltos y sus explicaciones.
- El proyecto con la función, su llamada del ejercicio 5.
- `missing_age_by_class.csv` y la explicación solicitada, que puede ir en la notebook.

Ejecuta toda la notebook desde un kernel limpio y ejecuta el proyecto según el README.
Entrega el proyecto sin `.venv` ni cachés; adjunta el CSV como evidencia.
