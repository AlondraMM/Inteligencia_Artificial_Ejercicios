"""Persistencia y búsqueda vectorial; Chroma nunca genera embeddings."""

import hashlib
from collections import Counter
from pathlib import Path

import chromadb
from chromadb.config import Settings

from app.chunk import Chunk


class ModelMismatchError(Exception):
    pass


class VectorStore:
    def __init__(self, path: Path, model: str):
        path.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(path), settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="rag_documents",
            metadata={"hnsw:space": "cosine", "embedding_model": model},
            embedding_function=None,
        )
        actual = (self.collection.metadata or {}).get("embedding_model")
        if actual != model:
            raise ModelMismatchError(
                f"El índice usa {actual or 'un modelo desconocido'}; configura EMBEDDING_MODEL={actual} "
                "o crea un índice nuevo."
            )

    def count(self) -> int:
        return self.collection.count()

    def list_sources(self) -> list[dict]:
        results = self.collection.get(include=["metadatas"])
        counts = Counter(metadata["source"] for metadata in results["metadatas"] or [])
        return [{"source": source, "chunks": counts[source]} for source in sorted(counts)]

    def source_count(self, source: str) -> int:
        return len(self.collection.get(where={"source": source}, include=[])["ids"])

    def delete_source(self, source: str) -> int:
        ids = self.collection.get(where={"source": source}, include=[])["ids"]
        if ids:
            self.collection.delete(ids=ids)
        return len(ids)

    def replace_source(self, source: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors) or not chunks:
            raise ValueError("Los chunks y embeddings deben tener la misma longitud")
        previous_ids = set(self.collection.get(where={"source": source}, include=[])["ids"])
        ids = [hashlib.sha256(f"{source}:{chunk.index}".encode()).hexdigest() for chunk in chunks]
        # Conservamos el documento anterior si Chroma rechaza los nuevos vectores.
        self.collection.upsert(
            ids=ids,
            documents=[chunk.text for chunk in chunks],
            embeddings=vectors,
            metadatas=[{
                "source": source,
                "chunk_index": chunk.index,
                "page": chunk.page or 0,
            } for chunk in chunks],
        )
        obsolete_ids = previous_ids - set(ids)
        if obsolete_ids:
            self.collection.delete(ids=list(obsolete_ids))

    def search(self, vector: list[float], top_k: int, source: str | None = None) -> list[dict]:
        available = self.source_count(source) if source is not None else self.count()
        if not available:
            return []
        results = self.collection.query(
            query_embeddings=[vector],
            n_results=min(top_k, available),
            where={"source": source} if source is not None else None,
            include=["documents", "metadatas", "distances"],
        )
        citations = []
        for index, (id_, document, metadata, distance) in enumerate(
            zip(results["ids"][0], results["documents"][0],
                results["metadatas"][0], results["distances"][0]), 1
        ):
            citations.append({
                "id": id_,
                "number": index,
                "source": metadata["source"],
                "text": document,
                "score": round(max(0.0, min(1.0, 1.0 - distance)), 4),
                "chunk_index": metadata["chunk_index"],
                "page": metadata["page"] or None,
            })
        return citations
