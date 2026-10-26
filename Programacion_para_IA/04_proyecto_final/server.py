"""Servidor MCP local; prepara datos y embeddings una vez durante el arranque."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging
from typing import Annotated

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

from support.analysis import ProductAnalysis, ProductComparison, ProductService, SearchResult
from support.data import load
from support.encoder import Encoder
from support.settings import DEFAULT_DATA_DIR, load_settings


def load_service() -> ProductService:
    """Carga la selección completa y construye el índice con el mismo modelo."""
    logger = logging.getLogger(__name__)
    records, products = load(DEFAULT_DATA_DIR)
    logger.info("Preparando %d productos y %d reseñas...", len(products), len(records))
    encoder = Encoder(load_settings())
    index = encoder.build_index(records, products)
    logger.info("Índice preparado: %s. El servidor está listo.", index.vectors.shape)
    return ProductService(records, products, encoder, index)


def create_server(service: ProductService | None = None) -> MCPServer[None]:
    """Crea el servidor; permite inyectar un servicio para comprobar el protocolo."""
    active_service = service

    @asynccontextmanager
    async def lifespan(_server: MCPServer[None]) -> AsyncIterator[None]:
        nonlocal active_service
        if active_service is None:
            active_service = load_service()
        yield None

    server: MCPServer[None] = MCPServer("Amazon reviews", lifespan=lifespan)

    def get_service() -> ProductService:
        if active_service is None:
            raise RuntimeError("El servicio todavía no se ha iniciado")
        return active_service

    @server.tool()
    def search_products(
        query: str,
        top_k: Annotated[int, Field(strict=True, ge=1, le=20)] = 5,
    ) -> list[SearchResult]:
        """Busca productos por catálogo y reseñas; usa consultas en inglés.

        La similitud es coseno, no una probabilidad ni una medida de calidad.
        review_count cuenta únicamente reseñas de la selección proporcionada.
        """
        try:
            return get_service().search_products(query, top_k)
        except ValueError as exc:
            raise ToolError(str(exc)) from exc

    @server.tool()
    def analyze_product(product_id: str) -> ProductAnalysis:
        """Cuenta estrellas y calcula media/mediana de las reseñas seleccionadas.

        Un producto desconocido devuelve ceros y media/mediana null.
        """
        try:
            return get_service().analyze_product(product_id)
        except ValueError as exc:
            raise ToolError(str(exc)) from exc

    @server.tool()
    def compare_products(product_ids: list[str]) -> ProductComparison:
        """Compara al menos dos IDs distintos y sus medias respecto al primero.

        Las diferencias son null si falta alguna de las medias necesarias.
        """
        try:
            return get_service().compare_products(product_ids)
        except ValueError as exc:
            raise ToolError(str(exc)) from exc

    return server


mcp = create_server()


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
