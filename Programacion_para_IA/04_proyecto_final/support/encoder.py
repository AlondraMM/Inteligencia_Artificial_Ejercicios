"""Embeddings compartidos y representación 50/50 de catálogo y reseñas.

El servidor crea un Encoder y construye el índice una vez. Cada consulta reutiliza
ese mismo modelo; no se guardan pesos ni vectores dentro del proyecto.
"""

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from sentence_transformers import SentenceTransformer

from support.data import (
    ProductRecord,
    ReviewRecord,
    prepare_catalog_texts,
    prepare_review_texts,
)
from support.settings import Settings


FloatArray = NDArray[np.float32]


def normalize_rows(vectors: FloatArray) -> FloatArray:
    """Normaliza una matriz sin convertir vectores nulos o inválidos en NaN."""
    if vectors.ndim != 2 or vectors.shape[1] == 0:
        raise ValueError("Los embeddings deben ser una matriz con columnas")
    if not np.isfinite(vectors).all():
        raise ValueError("Los embeddings deben contener valores finitos")
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    if np.any(norms == 0):
        raise ValueError("No se puede normalizar un embedding nulo")
    return np.asarray(vectors / norms, dtype=np.float32)


def combine_product_vectors(
    product_ids: Sequence[str],
    catalog_vectors: FloatArray,
    review_product_ids: Sequence[str],
    review_vectors: FloatArray,
) -> FloatArray:
    """Promedia por ID, normaliza la media y combina ambas fuentes al 50 %.

    La fila i del resultado pertenece a product_ids[i]. Las estrellas no
    intervienen: cada reseña con texto tiene el mismo peso dentro de su producto.
    """
    if not product_ids or len(set(product_ids)) != len(product_ids):
        raise ValueError("Se necesitan IDs de producto únicos")
    if catalog_vectors.ndim != 2 or catalog_vectors.shape[0] != len(product_ids):
        raise ValueError("El catálogo y los IDs de producto no están alineados")
    if review_vectors.ndim != 2 or review_vectors.shape[0] != len(review_product_ids):
        raise ValueError("Las reseñas y sus IDs de producto no están alineados")
    if catalog_vectors.shape[1] != review_vectors.shape[1]:
        raise ValueError("Catálogo y reseñas deben tener la misma dimensión")

    positions: dict[str, list[int]] = {product_id: [] for product_id in product_ids}
    for index, product_id in enumerate(review_product_ids):
        if product_id not in positions:
            raise ValueError(f"Reseña de un producto sin catálogo: {product_id}")
        positions[product_id].append(index)
    for product_id, indices in positions.items():
        if not indices:
            raise ValueError(f"El producto {product_id} no tiene reseñas con texto")

    catalog = normalize_rows(catalog_vectors)
    reviews = normalize_rows(review_vectors)
    review_means = np.stack([
        reviews[positions[product_id]].mean(axis=0) for product_id in product_ids
    ])
    review_summaries = normalize_rows(review_means)
    return normalize_rows(0.5 * catalog + 0.5 * review_summaries)


@dataclass(frozen=True)
class ProductIndex:
    """Matriz de productos e IDs alineados, conservada en memoria por el servidor."""

    product_ids: list[str]
    vectors: FloatArray
    review_counts: dict[str, int]
    review_ids: list[str]
    review_product_ids: list[str]


class Encoder:
    """Carga el modelo configurado una sola vez y codifica siempre con él."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model = SentenceTransformer(settings.model_name, device=settings.device)

    def encode(self, texts: Sequence[str]) -> FloatArray:
        """Codifica por lotes sin alterar el orden y devuelve vectores unitarios."""
        if not texts or any(not text.strip() for text in texts):
            raise ValueError("Se necesitan textos no vacíos para codificar")
        vectors = self.model.encode(
            list(texts),
            batch_size=self.settings.batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        result = normalize_rows(np.asarray(vectors, dtype=np.float32))
        if result.shape[0] != len(texts):
            raise ValueError("El modelo devolvió una cantidad inesperada de embeddings")
        return result

    def encode_query(self, query: str) -> FloatArray:
        """Devuelve el vector de una consulta usando el mismo modelo del índice."""
        if not query.strip():
            raise ValueError("query debe ser una cadena no vacía")
        return np.asarray(self.encode([query.strip()])[0], dtype=np.float32)

    def build_index(
        self,
        records: Sequence[ReviewRecord],
        products: Mapping[str, ProductRecord],
    ) -> ProductIndex:
        """Prepara catálogo y reseñas por separado una sola vez al iniciar."""
        catalog_texts, product_ids = prepare_catalog_texts(products)
        texts, review_ids, review_product_ids = prepare_review_texts(records)
        vectors = combine_product_vectors(
            product_ids,
            self.encode(catalog_texts),
            review_product_ids,
            self.encode(texts),
        )
        counts = Counter(record["product_id"] for record in records)
        return ProductIndex(
            product_ids=product_ids,
            vectors=vectors,
            review_counts={product_id: counts[product_id] for product_id in product_ids},
            review_ids=review_ids,
            review_product_ids=review_product_ids,
        )

