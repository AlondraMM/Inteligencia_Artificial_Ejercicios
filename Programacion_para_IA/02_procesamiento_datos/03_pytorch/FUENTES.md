# Documentación consultada

| Tema | Fuente oficial |
|---|---|
| Tensores, operaciones y dispositivos | [PyTorch: Tensors](https://docs.pytorch.org/tutorials/beginner/basics/tensorqs_tutorial.html) |
| Memoria compartida con NumPy | [torch.from_numpy](https://docs.pytorch.org/docs/stable/generated/torch.from_numpy.html) |
| Lectura de imágenes bajo demanda | [Dataset personalizado](https://docs.pytorch.org/tutorials/beginner/data_loading_tutorial.html) |
| Dataset y DataLoader | [Datasets & DataLoaders](https://docs.pytorch.org/tutorials/beginner/basics/data_tutorial.html) |
| TensorDataset, Subset y argumentos de carga | [torch.utils.data](https://docs.pytorch.org/docs/stable/data.html) |
| Semillas y límites de reproducibilidad | [Reproducibility](https://docs.pytorch.org/docs/stable/notes/randomness.html) |
| Tamaño, clases y particiones de CIFAR-10 | [Página de los autores](https://www.cs.toronto.edu/~kriz/cifar.html) |
| Acceso a CIFAR-10 con torchvision | [CIFAR10](https://docs.pytorch.org/vision/stable/generated/torchvision.datasets.CIFAR10.html) |
| Conversión de imágenes con v2 | [Transforming images](https://docs.pytorch.org/vision/stable/transforms.html) |
| Conversión de tipo y escala | [ToDtype](https://docs.pytorch.org/vision/stable/generated/torchvision.transforms.v2.ToDtype.html) |
| Normalización por canal | [Normalize](https://docs.pytorch.org/vision/stable/generated/torchvision.transforms.v2.Normalize.html) |
| Concatenación | [torch.cat](https://docs.pytorch.org/docs/stable/generated/torch.cat.html) |
| Conteo de etiquetas enteras | [torch.bincount](https://docs.pytorch.org/docs/stable/generated/torch.bincount.html) |
| Comprobación numérica | [torch.testing.assert_close](https://docs.pytorch.org/docs/stable/testing.html#torch.testing.assert_close) |

El [tutorial de CIFAR-10](https://docs.pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html#load-and-normalize-cifar10)
sirve como referencia para la carga y normalización. Esta sesión desarrolla
únicamente la preparación y exploración de los datos. Usa `transforms.v2`, la API
recomendada actualmente por torchvision, y separa la conversión a `[0, 1]` del
ejemplo de normalización a `[-1, 1]`.

Consulta: 27 de septiembre de 2026. Las versiones del proyecto están fijadas en
`uv.lock`.

## Embeddings y búsqueda textual

- [SentenceTransformer: dispositivos y encode](https://www.sbert.net/docs/package_reference/sentence_transformer/model.html).
- [PyTorch: ejecución asíncrona y medición en CUDA](https://docs.pytorch.org/docs/stable/notes/cuda.html#asynchronous-execution).
- [Colab: recursos y aceleradores](https://research.google.com/colaboratory/faq.html).

- [Modelo all-MiniLM-L6-v2: dimensiones y límites](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2).
- [Similitud textual](https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html).
- [Normalización por dimensión](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.normalize.html).
- [torch.topk](https://docs.pytorch.org/docs/stable/generated/torch.topk.html).

Consulta de esta sección: 3 de octubre de 2026.
