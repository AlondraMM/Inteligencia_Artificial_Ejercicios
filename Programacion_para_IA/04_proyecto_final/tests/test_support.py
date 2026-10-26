"""Comprueba matemáticas, relación entre IDs y entradas inválidas sin red."""

from collections.abc import Sequence
import gzip
import json
from math import cos, pi, sin, sqrt
from pathlib import Path
import tempfile
from typing import cast
import unittest

import numpy as np

from support.analysis import ProductService
from support.data import (
    ProductRecord,
    ReviewRecord,
    load,
    prepare_catalog_texts,
    prepare_review_texts,
    rows,
)
from support.encoder import FloatArray, ProductIndex, combine_product_vectors
from support.settings import load_settings


def product(product_id: str) -> ProductRecord:
    return {
        "product_id": product_id,
        "title": f"Product {product_id}",
        "features": ["waterproof", "portable"],
        "description": ["Bluetooth audio"],
        "categories": [],
        "family": "Audio",
    }


def write_jsonl(path: Path, records: Sequence[object]) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(record) + "\n")


class FixedEncoder:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def encode_query(self, query: str) -> FloatArray:
        self.queries.append(query)
        return np.array([1.0, 0.0], dtype=np.float32)


class EmbeddingTests(unittest.TestCase):
    def test_equal_source_weight_and_product_alignment(self) -> None:
        # Las reseñas están intercaladas y los productos no están ordenados.
        # A: catálogo a 0°, resumen de reseñas a 45° -> resultado a 22.5°.
        # B: catálogo a 90°, tres reseñas a 0° -> resultado a 45°.
        result = combine_product_vectors(
            ["B", "A"],
            np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.float32),
            ["A", "B", "A", "B", "B"],
            np.array([[0, 1], [1, 0], [1, 0], [1, 0], [1, 0]], dtype=np.float32),
        )
        expected = np.array([
            [sqrt(0.5), sqrt(0.5)],
            [cos(pi / 8), sin(pi / 8)],
        ])
        np.testing.assert_allclose(result, expected, atol=1e-6)
        np.testing.assert_allclose(np.linalg.norm(result, axis=1), 1, atol=1e-6)

    def test_incomplete_or_misaligned_embeddings_are_rejected(self) -> None:
        catalog = np.array([[1.0, 0.0]], dtype=np.float32)
        cases = [
            (["A"], ["A", "A"], catalog),
            (["A"], ["UNKNOWN"], catalog),
            (["A"], [], np.empty((0, 2), dtype=np.float32)),
            (["A", "A"], ["A"], catalog),
            (["A"], ["A"], np.array([[0.0, 0.0]], dtype=np.float32)),
            (["A"], ["A"], np.array([[np.nan, 0.0]], dtype=np.float32)),
        ]
        for product_ids, review_product_ids, reviews in cases:
            with self.subTest(product_ids=product_ids, review_ids=review_product_ids):
                with self.assertRaises(ValueError):
                    combine_product_vectors(product_ids, catalog, review_product_ids, reviews)


class SettingsTests(unittest.TestCase):
    def test_config_rejects_invalid_batches_and_empty_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "config.json"
            valid: dict[str, object] = {
                "model_name": " sentence-transformers/all-MiniLM-L6-v2 ",
                "batch_size": 32,
                "device": " cpu ",
            }
            path.write_text(json.dumps(valid), encoding="utf-8")
            settings = load_settings(path)
            self.assertEqual(settings.model_name, "sentence-transformers/all-MiniLM-L6-v2")
            self.assertEqual(settings.device, "cpu")
            self.assertEqual(settings.batch_size, 32)
            for field, value in (
                ("batch_size", True), ("batch_size", 0), ("batch_size", -1),
                ("batch_size", 2.5), ("batch_size", "32"),
                ("model_name", "  "), ("device", ""),
            ):
                with self.subTest(field=field, value=value):
                    path.write_text(json.dumps({**valid, field: value}), encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, field):
                        load_settings(path)

    def test_config_requires_object_and_all_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "config.json"
            for contents in ("[]", "{", '{"model_name": "model"}'):
                with self.subTest(contents=contents):
                    path.write_text(contents, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        load_settings(path)


class DataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.raw_products: list[dict[str, object]] = [
            {"parent_asin": "B", "title": "Speaker", "features": ["portable"],
             "description": ["waterproof"], "categories": [], "family": "Audio"},
            {"parent_asin": "A", "title": "Headphones", "features": [],
             "description": [], "categories": [], "family": "Audio"},
        ]
        self.raw_reviews: list[dict[str, object]] = [
            {"parent_asin": "A", "rating": 5, "text": " good sound ", "source_line": 91},
            {"parent_asin": "B", "rating": 1, "text": "   ", "source_line": 7},
            {"parent_asin": "A", "rating": 3, "text": "comfortable", "source_line": 23},
        ]
        write_jsonl(self.directory / "products.jsonl.gz", self.raw_products)
        write_jsonl(self.directory / "reviews.jsonl.gz", self.raw_reviews)

    def test_stable_source_ids_and_aligned_text_preparation(self) -> None:
        records, products = load(self.directory)
        self.assertEqual(len(records), 3)  # Una reseña sin texto conserva sus estrellas.
        self.assertEqual([record["review_id"] for record in records],
                         ["Electronics:91", "Electronics:7", "Electronics:23"])
        self.assertEqual(prepare_review_texts(records), (
            ["good sound", "comfortable"], ["Electronics:91", "Electronics:23"], ["A", "A"],
        ))
        self.assertEqual(prepare_catalog_texts(products), (
            ["Speaker portable waterproof", "Headphones"], ["B", "A"],
        ))

    def test_invalid_review_fields_are_rejected(self) -> None:
        for field, value in (
            ("rating", True), ("rating", 0), ("rating", 2.5),
            ("source_line", True), ("source_line", 0),
            ("parent_asin", "UNKNOWN"), ("text", 123),
        ):
            with self.subTest(field=field, value=value):
                changed = [{**self.raw_reviews[0], field: value}]
                write_jsonl(self.directory / "reviews.jsonl.gz", changed)
                with self.assertRaises(ValueError):
                    load(self.directory)

    def test_duplicate_ids_and_non_object_json_are_rejected(self) -> None:
        write_jsonl(self.directory / "reviews.jsonl.gz", [self.raw_reviews[0]] * 2)
        with self.assertRaisesRegex(ValueError, "duplicado"):
            load(self.directory)
        write_jsonl(self.directory / "products.jsonl.gz", [self.raw_products[0]] * 2)
        with self.assertRaisesRegex(ValueError, "duplicado"):
            load(self.directory)
        write_jsonl(self.directory / "products.jsonl.gz", [[]])
        with self.assertRaisesRegex(ValueError, "objeto JSON"):
            list(rows(self.directory / "products.jsonl.gz"))


class ProductServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.encoder = FixedEncoder()
        records: list[ReviewRecord] = [
            {"review_id": f"Electronics:{i}", "product_id": product_id,
             "text": "" if i == 1 else "review", "rating": float(rating)}
            for i, (product_id, rating) in enumerate(
                [("A", 1), ("A", 2), ("B", 2), ("A", 5), ("B", 4), ("A", 5)], start=1
            )
        ]
        index = ProductIndex(
            product_ids=["B", "A"],
            vectors=np.array([[0.6, 0.8], [1, 0]], dtype=np.float32),
            review_counts={"A": 4, "B": 2},
            review_ids=[],
            review_product_ids=[],
        )
        self.service = ProductService(records, {"B": product("B"), "A": product("A")},
                                      self.encoder, index)

    def test_rank_uses_matrix_row_ids_and_selected_review_count(self) -> None:
        results = self.service.search_products("  speaker  ", top_k=20)
        self.assertEqual([result["product_id"] for result in results], ["A", "B"])
        self.assertEqual([result["review_count"] for result in results], [4, 2])
        self.assertEqual(self.encoder.queries, ["speaker"])
        self.assertAlmostEqual(results[0]["similarity"], 1.0)
        self.assertAlmostEqual(results[1]["similarity"], 0.6, places=6)
        json.dumps(results, allow_nan=False)

    def test_ratings_include_blank_text_and_use_mean_and_median(self) -> None:
        analysis = self.service.analyze_product(" A ")
        self.assertEqual(analysis["review_count"], 4)
        self.assertEqual(analysis["rating_counts"], {"1": 1, "2": 1, "3": 0, "4": 0, "5": 2})
        self.assertEqual(analysis["rating_proportions"],
                         {"1": 0.25, "2": 0.25, "3": 0.0, "4": 0.0, "5": 0.5})
        self.assertEqual(analysis["mean_rating"], 3.25)
        self.assertEqual(analysis["median_rating"], 3.5)
        json.dumps(analysis, allow_nan=False)

    def test_unknown_product_has_zero_counts_and_null_statistics(self) -> None:
        analysis = self.service.analyze_product("UNKNOWN")
        self.assertEqual(analysis["review_count"], 0)
        self.assertEqual(list(analysis["rating_counts"].values()), [0] * 5)
        self.assertEqual(list(analysis["rating_proportions"].values()), [0.0] * 5)
        self.assertIsNone(analysis["mean_rating"])
        self.assertIsNone(analysis["median_rating"])
        self.assertIn('"mean_rating": null', json.dumps(analysis, allow_nan=False))

    def test_comparison_uses_first_mean_and_propagates_missing_values(self) -> None:
        result = self.service.compare_products(["A", "B", "UNKNOWN"])
        self.assertEqual(result["reference_product_id"], "A")
        self.assertEqual([item["mean_difference_from_first"] for item in result["products"]],
                         [0.0, -0.25, None])
        unknown_reference = self.service.compare_products(["UNKNOWN", "B"])
        self.assertTrue(all(item["mean_difference_from_first"] is None
                            for item in unknown_reference["products"]))
        json.dumps(result, allow_nan=False)

    def test_invalid_inputs_do_not_prevent_a_later_valid_call(self) -> None:
        for value in (0, 21, True, 2.0, "3"):
            with self.subTest(top_k=value):
                with self.assertRaisesRegex(ValueError, "top_k"):
                    self.service.search_products("speaker", cast(int, value))
        with self.assertRaisesRegex(ValueError, "query"):
            self.service.search_products("  ")
        with self.assertRaisesRegex(ValueError, "product_id"):
            self.service.analyze_product("  ")
        for ids in ([], ["A"], ["A", "A"], ["A", " A "], ["A", "  "]):
            with self.subTest(ids=ids):
                with self.assertRaises(ValueError):
                    self.service.compare_products(ids)
        self.assertEqual(len(self.service.search_products("speaker", 1)), 1)
        self.assertEqual(self.service.analyze_product("A")["review_count"], 4)


if __name__ == "__main__":
    unittest.main()
