"""API HTTP del sistema RAG. OpenAPI disponible en /docs."""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from google.genai.errors import APIError
from pydantic import BaseModel, Field

from app.chunk import split_document
from app.embed import GoogleEmbedder
from app.generate import ABSTENTION, generate_answer
from app.store import ModelMismatchError, VectorStore


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
GENERATION_MODEL = os.getenv("GENERATION_MODEL", "gemini-3.6-flash")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
MIN_SCORE = float(os.getenv("MIN_SCORE", "0.55"))
CHUNK_WORDS = int(os.getenv("CHUNK_WORDS", "250"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
CHROMA_PATH = ROOT / os.getenv("CHROMA_PATH", "chroma")
MAX_FILE_BYTES = 10 * 1024 * 1024

app = FastAPI(title="AstroBot — RAG de astronomía", version="1.0.0")


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=4, ge=1, le=10)
    source: str | None = Field(default=None, description="Consultar solo un documento indexado")


def get_store() -> VectorStore:
    try:
        return VectorStore(CHROMA_PATH, EMBEDDING_MODEL)
    except ModelMismatchError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


def require_key() -> str:
    if not GOOGLE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Falta GOOGLE_API_KEY en .env. Obtén una clave en Google AI Studio.",
        )
    return GOOGLE_API_KEY


def google_failure(exc: Exception, message: str) -> HTTPException:
    if isinstance(exc, APIError) and exc.code == 429:
        return HTTPException(
            429, "Google AI agotó la cuota disponible. Espera y revisa los límites de tu proyecto en AI Studio."
        )
    return HTTPException(502, message)


@app.get("/health", summary="Estado de la API y del índice")
def health() -> dict:
    store = get_store()
    return {
        "status": "ok",
        "index_chunks": store.count(),
        "key_configured": bool(GOOGLE_API_KEY),
        "embedding_model": EMBEDDING_MODEL,
        "generation_model": GENERATION_MODEL,
    }


@app.post("/ingest", summary="Indexar archivos PDF, Markdown o texto")
async def ingest(files: list[UploadFile] = File(...)) -> dict:
    key = require_key()
    store = get_store()
    if not files:
        raise HTTPException(400, "Selecciona al menos un archivo")
    prepared = []
    seen = set()
    for file in files:
        source = Path(file.filename or "").name
        if not source or source in seen:
            raise HTTPException(400, "Cada archivo debe tener un nombre único")
        seen.add(source)
        content = await file.read(MAX_FILE_BYTES + 1)
        if len(content) > MAX_FILE_BYTES:
            raise HTTPException(413, f"{source} supera el límite de 10 MB")
        try:
            chunks = split_document(source, content, CHUNK_WORDS, CHUNK_OVERLAP)
        except ValueError as exc:
            raise HTTPException(400, f"{source}: {exc}") from exc
        prepared.append((source, chunks))
    embedder = GoogleEmbedder(key, EMBEDDING_MODEL)
    try:
        # Calculamos los vectores antes de alterar el índice persistente.
        vectors_by_source = [embedder.embed([chunk.text for chunk in chunks]) for _, chunks in prepared]
    except Exception as exc:
        raise google_failure(exc, "No se pudieron generar embeddings con Google AI") from exc
    for (source, chunks), vectors in zip(prepared, vectors_by_source):
        store.replace_source(source, chunks, vectors)
    return {
        "documents_indexed": len(prepared),
        "chunks_indexed": sum(len(chunks) for _, chunks in prepared),
        "index_chunks": store.count(),
        "sources": [source for source, _ in prepared],
    }


@app.get("/documents", summary="Listar documentos indexados y sus chunks")
def documents() -> dict:
    store = get_store()
    sources = store.list_sources()
    return {
        "documents": sources,
        "documents_count": len(sources),
        "index_chunks": store.count(),
    }


@app.delete("/documents/{source}", summary="Borrar un documento del índice")
def delete_document(source: str) -> dict:
    store = get_store()
    deleted = store.delete_source(source)
    if not deleted:
        raise HTTPException(404, "El documento no está indexado")
    return {"source": source, "chunks_deleted": deleted, "index_chunks": store.count()}


@app.post("/query", summary="Preguntar con recuperación y citas")
def query(body: QueryRequest) -> dict:
    question = body.question.strip()
    if not question:
        raise HTTPException(400, "La pregunta no puede estar en blanco")
    if body.source is not None and not body.source.strip():
        raise HTTPException(400, "El documento de consulta no puede estar en blanco")
    store = get_store()
    if body.source is not None and not store.source_count(body.source):
        raise HTTPException(404, "El documento no está indexado")
    if store.count() == 0:
        return {"answer": ABSTENTION, "citations": [], "abstained": True}
    key = require_key()
    try:
        vector = GoogleEmbedder(key, EMBEDDING_MODEL).embed([question], is_query=True)[0]
    except Exception as exc:
        raise google_failure(exc, "No se pudo generar el embedding de la pregunta") from exc
    citations = store.search(vector, body.top_k, source=body.source)
    if not citations or citations[0]["score"] < MIN_SCORE:
        return {"answer": ABSTENTION, "citations": citations, "abstained": True}
    try:
        answer, abstained = generate_answer(key, GENERATION_MODEL, question, citations)
    except Exception as exc:
        raise google_failure(exc, "No se pudo generar la respuesta con Gemini") from exc
    return {"answer": answer, "citations": citations, "abstained": abstained}
