# Sesión 3: Tensores y datasets con PyTorch

[Presentación de la sesión (PDF)](https://drive.google.com/file/d/19Jbf46jSTM2edUpSugP48twTpEXfJVj4/view?usp=drivesdk).

Convertiremos las matrices de Titanic a tensores y después exploraremos imágenes
de CIFAR-10. Trabajaremos con muestras, etiquetas, transformaciones y lotes para
entender los datos que recibe una aplicación de aprendizaje automático. Al final,
convertiremos textos en embeddings y haremos una búsqueda por similitud.

## Entrega de prácticas

La fecha límite para entregar las prácticas de la Unidad 2 es el **19 de octubre de 2026**.
Envía los entregables mediante el [formulario de entrega](https://docs.google.com/forms/d/e/1FAIpQLScOPQOB1sgjXsZbrealNcJ_U8Aa-bqtds5SozcSsRNSek7FxA/viewform?usp=publish-editor).

## Contenido

| Orden | Tema | Material |
|---|---|---|
| 1 | Arreglos NumPy, tensores y memoria compartida | Notebook, sección 1 |
| 2 | Muestras, `TensorDataset` y `DataLoader` | Notebook, sección 2 |
| 3 | CIFAR-10, transformaciones y lectura de imágenes bajo demanda | Notebook, sección 3 |
| 4 | Ejes de un lote y normalización | Notebook, sección 4 |
| 5 | Exportar una selección para visualizarla | Notebook, sección 5 y `main.py` |
| 6 | Embeddings con SentenceTransformer y búsqueda con PyTorch | Notebook, sección 6 |

Los **ejercicios 1–4** están en
[u2_n4_tensores_datasets.ipynb](./u2_n4_tensores_datasets.ipynb).
El [ejercicio 5](./PRACTICA.md) amplía el resumen del proyecto. Consulta los entregables en
[PRACTICA.md](./PRACTICA.md).

## Preparación

Primero genera los archivos de la sesión 2 si todavía no tienes
`02_pandas/outputs/features.npy` y `labels.npy`. Desde esta carpeta:

```bash
cd ../02_pandas
uv sync --locked
uv run --locked python main.py
cd ../03_pytorch
```

Después prepara este proyecto y descarga CIFAR-10:

```bash
uv sync --locked
uv run --locked python main.py --download
```

La primera descarga obtiene el archivo completo de CIFAR-10 (unos 170 MB
comprimidos) y lo extrae en `data/`. Aunque usamos el conjunto de prueba, el
archivo de descarga incluye ambos conjuntos. Prepara la descarga antes de clase.
En ejecuciones posteriores puedes omitir `--download`; la notebook utiliza
los archivos locales y no intenta descargarlos.

La sección 6 utiliza `sentence-transformers`, incluida en las dependencias del
proyecto. La primera carga de `all-MiniLM-L6-v2` descarga los pesos del modelo;
requiere internet y después utiliza su caché local. Puedes preparar esa descarga
antes de clase:

```bash
uv run --locked python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device='cpu')"
```

Es un ejemplo guiado: se mantienen los cinco ejercicios de la práctica.

Como demostración complementaria, abre [Embeddings en CPU y CUDA en Colab](https://colab.research.google.com/drive/18C8kn_iWqNVayn9ZvcrX203rL4pKpPky).
Repite la búsqueda en GPU y compara tiempos con el mismo modelo y lote.
Es independiente de los archivos locales y no añade entregables.

Abre [u2_n4_tensores_datasets.ipynb](./u2_n4_tensores_datasets.ipynb) en VS Code
o PyCharm con el entorno `.venv` de este proyecto; consulta las
[opciones de editor](../README.md#notebooks-locales).

## Proyecto

```text
03_pytorch/
├── main.py
├── data_lab/
│   └── inspection.py
├── tests/
├── u2_n4_tensores_datasets.ipynb
├── PRACTICA.md
├── pyproject.toml
└── uv.lock
```

`main.py` coordina los argumentos, la carga y la escritura de archivos.
`data_lab/inspection.py` contiene la transformación de imágenes, el recorrido por
lotes y el conteo de etiquetas. La notebook muestra las operaciones antes de
reutilizar las funciones.

```bash
uv run --locked python main.py
uv run --locked python main.py --limit 10 --batch-size 4 --output-dir outputs/ten
uv run --locked ruff check .
uv run --locked ruff format --check .
```

`--limit` selecciona las primeras muestras del conjunto de prueba y `--batch-size`
cambia cuántas se cargan juntas. La aplicación conserva el último lote incompleto.
Una selección de 10 imágenes con lotes de 4 contiene 10 imágenes, no 8.

## Archivos para la siguiente sesión

Con los argumentos predeterminados, `outputs/` contiene:

| Archivo | Contenido |
|---|---|
| `images.npy` | 64 imágenes, forma `(64, 3, 32, 32)`, `float32`, escala `[0, 1]` |
| `labels.npy` | 64 identificadores de clase en el mismo orden, `int64` |
| `class_counts.csv` | Conteo y proporción de las diez clases dentro de esas 64 imágenes |
| `report.json` | Conjunto, selección, formas, tipos y nombres de clase |

La columna `proportion` divide el conteo de cada clase entre el total de
etiquetas seleccionadas; las clases sin muestras conservan conteo y proporción
cero. Cambiar el tamaño de lote conserva los conteos porque no se descarta
el último lote; cambiar `--limit` puede cambiar las clases que entran.

La selección conserva el orden del dataset y no pretende representar la
proporción de clases del conjunto completo. Repetir la ejecución en la misma
carpeta reemplaza estas salidas. Usa otra ruta con `--output-dir` para conservar
experimentos separados.

Los datos descargados, las salidas y las notebooks ejecutadas están ignorados
por Git. Los gráficos comparativos y las cuadrículas de imágenes se desarrollarán
en la sesión 4.

[Fuentes oficiales](./FUENTES.md) · [Volver a la unidad](../README.md)

Las pruebas existentes se pueden ejecutar con `uv run --locked python -m pytest`
como apoyo opcional; no se pide crear pruebas para la práctica.
