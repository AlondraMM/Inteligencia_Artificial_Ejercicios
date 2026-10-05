"""Lectura de documentos y partición reproducible por palabras."""

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


ALLOWED_SUFFIXES = {".txt", ".md", ".pdf"}


@dataclass(frozen=True)
class Chunk:
    source: str
    index: int
    text: str
    page: int | None = None


def extract_pages(filename: str, content: bytes) -> list[tuple[int | None, str]]:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise ValueError(f"Formato no admitido: {suffix or '(sin extensión)'}")
    if suffix == ".pdf":
        try:
            reader = PdfReader(BytesIO(content))
            pages = [(number, page.extract_text() or "") for number, page in enumerate(reader.pages, 1)]
        except Exception as exc:
            raise ValueError("No se pudo leer el PDF") from exc
        if not any(text.strip() for _, text in pages):
            raise ValueError("El PDF no contiene texto extraíble")
        return pages
    try:
        return [(None, content.decode("utf-8-sig"))]
    except UnicodeDecodeError as exc:
        raise ValueError("El archivo de texto debe estar codificado en UTF-8") from exc


def split_document(filename: str, content: bytes, size: int, overlap: int) -> list[Chunk]:
    if size < 1 or overlap < 0 or overlap >= size:
        raise ValueError("CHUNK_WORDS debe ser positivo y CHUNK_OVERLAP menor")
    chunks: list[Chunk] = []
    step = size - overlap
    for page, text in extract_pages(filename, content):
        words = text.split()
        for start in range(0, len(words), step):
            window = words[start : start + size]
            if not window:
                break
            chunks.append(Chunk(filename, len(chunks), " ".join(window), page))
            if start + size >= len(words):
                break
    if not chunks:
        raise ValueError("El documento está vacío")
    return chunks
