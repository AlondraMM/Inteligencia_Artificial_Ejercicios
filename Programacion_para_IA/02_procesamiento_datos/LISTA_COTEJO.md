# Lista de cotejo · Unidad 2

## Sesión 1 · NumPy y vectorización (11 ejercicios)

- [ ] Se entregan ambas notebooks con los 11 ejercicios resueltos.
- [ ] El proyecto incorpora `select_warm_rounds` en `measurements/selection.py`: selecciona por temperatura norte, conserva las tres columnas, no modifica la entrada y rechaza valores no finitos.
- [ ] La notebook llama la función y comprueba los casos solicitados con `assert` y `try`/`except`; compara las medias y explica la selección vacía. No se crean pruebas con pytest.

## Sesión 2 · pandas (5 ejercicios)

- [ ] Se entrega la notebook con los cuatro ejercicios resueltos.
- [ ] Para el ejercicio 5, el proyecto añade `missing_age_by_class` en `titanic/analysis.py`, la llama desde `main.py` y genera `missing_age_by_class.csv` con conteos y proporciones por clase.
- [ ] Se adjunta el CSV; la notebook comprueba los conteos, las proporciones y un caso pequeño con `assert`, y explica el resultado. No se crean pruebas con pytest.

## Sesión 3 · PyTorch (5 ejercicios)

- [ ] Se entrega la notebook con los cuatro ejercicios resueltos.
- [ ] Para el ejercicio 5, el proyecto añade `proportion` a `label_summary` en `data_lab/inspection.py`, conserva las clases con conteo cero y actualiza el tipo de retorno para admitir `float`.
- [ ] Se adjunta `class_counts.csv` para 10 imágenes con lotes de 4; la notebook comprueba el caso indicado con `assert` y explica el efecto del lote y el límite. No se crean pruebas con pytest.

## Sesión 4 · Visualización (2 ejercicios)

- [ ] Se entrega la notebook con ambos ejercicios resueltos, gráficos visibles e interpretaciones.
