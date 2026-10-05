"""Modelo de Google AI para documentos y consultas."""

import logging
import time
from typing import Callable, TypeVar

from google import genai
from google.genai import errors, types


T = TypeVar("T")
logger = logging.getLogger(__name__)


def call_google(request: Callable[..., T], **kwargs) -> T:
    """Reintentar fallos transitorios sin repetir lotes ya completados."""
    for attempt in range(4):
        try:
            return request(**kwargs)
        except errors.APIError as exc:
            if attempt == 3 or exc.code not in {429, 500, 502, 503, 504}:
                raise
            delay = float(2 ** attempt)
            if exc.code == 429:
                payload = exc.details.get("error", exc.details)
                retry_info = next(
                    (item for item in payload.get("details", [])
                     if item.get("@type", "").endswith("RetryInfo")),
                    {},
                )
                try:
                    delay = float(retry_info["retryDelay"].removesuffix("s"))
                except (AttributeError, KeyError, TypeError, ValueError):
                    delay = 60.0
                # Acotamos las esperas incluso cuando Google no incluye RetryInfo.
                if not 0 <= delay <= 60:
                    raise
                delay = min(60.0, delay + 1.0)
            logger.warning("Google AI: error %s; reintento en %.1f s", exc.code, delay)
            time.sleep(delay)
    raise RuntimeError("No se completó la solicitud a Google AI")


class GoogleEmbedder:
    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=120000))
        self.model = model

    def embed(self, texts: list[str], *, is_query: bool = False) -> list[list[float]]:
        vectors: list[list[float]] = []
        task_type = "RETRIEVAL_QUERY" if is_query else "RETRIEVAL_DOCUMENT"
        for start in range(0, len(texts), 16):
            batch = texts[start : start + 16]
            response = call_google(
                self.client.models.embed_content,
                model=self.model,
                contents=batch,
                config=types.EmbedContentConfig(task_type=task_type),
            )
            embeddings = response.embeddings or []
            if len(embeddings) != len(batch):
                raise RuntimeError("Google AI devolvió un número inesperado de embeddings")
            for embedding in embeddings:
                if not embedding.values:
                    raise RuntimeError("Google AI devolvió un embedding vacío")
                vectors.append(list(embedding.values))
        return vectors
