"""Lectura del subconjunto de Amazon y preparación de textos con sus IDs."""

from collections.abc import Iterator, Mapping, Sequence
import gzip
import json
from pathlib import Path
from typing import TypedDict, cast


class ReviewRecord(TypedDict):
    """Una reseña seleccionada; sus estrellas se conservan para el análisis."""

    review_id: str
    product_id: str
    text: str
    rating: float


class ProductRecord(TypedDict):
    """Catálogo de un producto, relacionado por ``parent_asin``."""

    product_id: str
    title: str
    features: list[str]
    description: list[str]
    categories: list[str]
    family: str


def ensure_data(directory: Path) -> None:
    """Comprueba que estén los dos archivos proporcionados, sin descargarlos."""
    for filename in ("reviews.jsonl.gz", "products.jsonl.gz"):
        path = directory / filename
        if not path.is_file():
            raise FileNotFoundError(f"Falta el archivo del dataset: {path}")


def rows(path: Path) -> Iterator[tuple[int, dict[str, object]]]:
    """Lee objetos JSONL y conserva el número de línea del archivo pequeño."""
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line_number, text in enumerate(stream, start=1):
            if not text.strip():
                continue
            try:
                record: object = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"JSON inválido en {path.name}, línea {line_number}: {exc.msg}"
                ) from exc
            if not isinstance(record, dict):
                raise ValueError(
                    f"Se esperaba un objeto JSON en {path.name}, línea {line_number}"
                )
            # Las claves de un objeto JSON siempre son cadenas.
            yield line_number, cast(dict[str, object], record)


def _required_text(value: object, field: str, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} debe ser texto no vacío en {location}")
    return value


def _text_list(value: object, field: str, location: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field} debe ser una lista de textos en {location}")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{field} debe ser una lista de textos en {location}")
        result.append(item)
    return result


def load(directory: Path) -> tuple[list[ReviewRecord], dict[str, ProductRecord]]:
    """Carga y valida los archivos completos, relacionándolos por ID de producto.

    No se descartan reseñas por sus estrellas o texto. Los textos vacíos solamente
    se excluyen después al preparar los embeddings, no de las estadísticas.
    """
    ensure_data(directory)
    products: dict[str, ProductRecord] = {}
    for line_number, product in rows(directory / "products.jsonl.gz"):
        location = f"products.jsonl.gz, línea {line_number}"
        product_id = _required_text(product.get("parent_asin"), "parent_asin", location)
        if product_id in products:
            raise ValueError(f"ID de producto duplicado {product_id!r} en {location}")
        products[product_id] = {
            "product_id": product_id,
            "title": _required_text(product.get("title"), "title", location),
            "features": _text_list(product.get("features"), "features", location),
            "description": _text_list(product.get("description"), "description", location),
            "categories": _text_list(product.get("categories"), "categories", location),
            "family": _required_text(product.get("family"), "family", location),
        }

    records: list[ReviewRecord] = []
    review_ids: set[str] = set()
    for line_number, review in rows(directory / "reviews.jsonl.gz"):
        location = f"reviews.jsonl.gz, línea {line_number}"
        product_id = _required_text(review.get("parent_asin"), "parent_asin", location)
        if product_id not in products:
            raise ValueError(f"Producto sin catálogo {product_id!r} en {location}")
        rating = review.get("rating")
        if (
            isinstance(rating, bool)
            or not isinstance(rating, (int, float))
            or rating not in (1, 2, 3, 4, 5)
        ):
            raise ValueError(f"rating debe ser un número de 1 a 5 en {location}")
        text = review.get("text")
        if text is None:
            text = ""
        if not isinstance(text, str):
            raise ValueError(f"text debe ser una cadena en {location}")
        source_line = review.get("source_line")
        if (
            isinstance(source_line, bool)
            or not isinstance(source_line, int)
            or source_line < 1
        ):
            raise ValueError(f"source_line debe ser un entero positivo en {location}")
        review_id = f"Electronics:{source_line}"
        if review_id in review_ids:
            raise ValueError(f"ID de reseña duplicado {review_id!r} en {location}")
        review_ids.add(review_id)
        records.append({
            "review_id": review_id,
            "product_id": product_id,
            "text": text,
            "rating": float(rating),
        })
    return records, products


def prepare_review_texts(
    records: Sequence[ReviewRecord],
) -> tuple[list[str], list[str], list[str]]:
    """Devuelve textos no vacíos, IDs de reseña e IDs de producto alineados."""
    texts: list[str] = []
    review_ids: list[str] = []
    review_product_ids: list[str] = []
    for record in records:
        text = record["text"].strip()
        if text:
            texts.append(text)
            review_ids.append(record["review_id"])
            review_product_ids.append(record["product_id"])
    return texts, review_ids, review_product_ids


def prepare_catalog_texts(
    products: Mapping[str, ProductRecord],
) -> tuple[list[str], list[str]]:
    """Devuelve título + características + descripción e IDs en el mismo orden."""
    texts: list[str] = []
    product_ids: list[str] = []
    for product_id, product in products.items():
        parts = (
            product["title"].strip(),
            " ".join(product["features"]),
            " ".join(product["description"]),
        )
        texts.append(" ".join(part for part in parts if part).strip())
        product_ids.append(product_id)
    return texts, product_ids
