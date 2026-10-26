"""Búsqueda vectorizada y estadísticas de las reseñas seleccionadas."""

from collections.abc import Mapping, Sequence
from typing import Protocol, TypedDict

import numpy as np

from support.data import ProductRecord, ReviewRecord
from support.encoder import FloatArray, ProductIndex


class QueryEncoder(Protocol):
    """Interfaz mínima del modelo ya cargado, compartido con la indexación."""

    def encode_query(self, query: str) -> FloatArray: ...


class SearchResult(TypedDict):
    product_id: str
    title: str
    similarity: float
    review_count: int


class ProductAnalysis(TypedDict):
    product_id: str
    title: str | None
    review_count: int
    rating_counts: dict[str, int]
    rating_proportions: dict[str, float]
    mean_rating: float | None
    median_rating: float | None


class ComparedProduct(ProductAnalysis):
    mean_difference_from_first: float | None


class ProductComparison(TypedDict):
    reference_product_id: str
    products: list[ComparedProduct]


def _product_id(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("product_id debe ser una cadena no vacía")
    return value.strip()


class ProductService:
    """Reutiliza el modelo y el índice, sin codificar el catálogo en cada llamada."""

    def __init__(
        self,
        records: Sequence[ReviewRecord],
        products: Mapping[str, ProductRecord],
        encoder: QueryEncoder,
        index: ProductIndex,
    ) -> None:
        self.products = products
        self.encoder = encoder
        self.index = index
        self._ratings: dict[str, list[float]] = {}
        for record in records:
            self._ratings.setdefault(record["product_id"], []).append(record["rating"])

    def search_products(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Ordena por coseno; la similitud no mide calidad ni probabilidad."""
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query debe ser una cadena no vacía")
        if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 20:
            raise ValueError("top_k debe ser un entero entre 1 y 20")
        query_vector = self.encoder.encode_query(query.strip())
        scores = self.index.vectors @ query_vector
        positions = np.argsort(-scores, kind="stable")[:top_k]
        results: list[SearchResult] = []
        for position in positions:
            product_id = self.index.product_ids[int(position)]
            results.append({
                "product_id": product_id,
                "title": self.products[product_id]["title"],
                "similarity": float(scores[position]),
                "review_count": int(self.index.review_counts.get(product_id, 0)),
            })
        return results

    def analyze_product(self, product_id: str) -> ProductAnalysis:
        """Resume solamente las reseñas de esta selección, incluso sin texto."""
        product_id = _product_id(product_id)
        ratings = np.asarray(self._ratings.get(product_id, []), dtype=np.float64)
        count = int(ratings.size)
        counts = np.bincount(ratings.astype(np.int64), minlength=6)[1:6]
        product = self.products.get(product_id)
        return {
            "product_id": product_id,
            "title": None if product is None else product["title"],
            "review_count": count,
            "rating_counts": {str(star): int(counts[star - 1]) for star in range(1, 6)},
            "rating_proportions": {
                str(star): float(counts[star - 1]) / count if count else 0.0
                for star in range(1, 6)
            },
            "mean_rating": float(np.mean(ratings)) if count else None,
            "median_rating": float(np.median(ratings)) if count else None,
        }

    def compare_products(self, product_ids: list[str]) -> ProductComparison:
        """Compara medias usando el primer ID como referencia."""
        if not isinstance(product_ids, list) or len(product_ids) < 2:
            raise ValueError("product_ids debe contener al menos dos IDs distintos")
        ids = [_product_id(value) for value in product_ids]
        if len(set(ids)) != len(ids):
            raise ValueError("Los IDs de product_ids deben ser distintos")
        summaries = [self.analyze_product(product_id) for product_id in ids]
        reference_mean = summaries[0]["mean_rating"]
        compared: list[ComparedProduct] = []
        for summary in summaries:
            mean = summary["mean_rating"]
            difference = (
                None if mean is None or reference_mean is None else mean - reference_mean
            )
            compared.append({**summary, "mean_difference_from_first": difference})
        return {"reference_product_id": ids[0], "products": compared}
