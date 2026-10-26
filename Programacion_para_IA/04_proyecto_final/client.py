"""Descubrimiento y demostración de las tres herramientas MCP por HTTP local."""

from mcp import Client


SERVER_URL = "http://127.0.0.1:8000/mcp"


async def demonstrate() -> None:
    """Prueba respuestas normales, errores de entrada y recuperación de la sesión."""
    calls: list[tuple[str, dict[str, str | int | list[str]], bool]] = [
        (
            "search_products",
            {"query": "A portable waterproof Bluetooth speaker", "top_k": 3},
            False,
        ),
        ("analyze_product", {"product_id": "B0BCTJMN63"}, False),
        (
            "compare_products",
            {"product_ids": ["B0BCTJMN63", "B09MMWM2Y8"]},
            False,
        ),
        ("analyze_product", {"product_id": "UNKNOWN_PRODUCT"}, False),
        (
            "compare_products",
            {"product_ids": ["B0BCTJMN63", "UNKNOWN_PRODUCT"]},
            False,
        ),
        ("search_products", {"query": "delivery", "top_k": 0}, True),
        ("search_products", {"query": "   "}, True),
        ("analyze_product", {"product_id": "   "}, True),
        (
            "compare_products",
            {"product_ids": ["B0BCTJMN63", "B0BCTJMN63"]},
            True,
        ),
        (
            "search_products",
            {"query": "Comfortable headphones with good sound", "top_k": 2},
            False,
        ),
    ]
    async with Client(SERVER_URL) as client:
        tools = await client.list_tools()
        names = {tool.name for tool in tools.tools}
        print("Herramientas descubiertas:", sorted(names))
        required = {"search_products", "analyze_product", "compare_products"}
        if not required.issubset(names):
            raise RuntimeError(f"Faltan herramientas MCP: {sorted(required - names)}")

        for name, arguments, expected_error in calls:
            print(f"\n{name}: {arguments}")
            result = await client.call_tool(name, arguments)
            print("Error de herramienta:", result.is_error)
            print(result.model_dump_json(indent=2))
            if bool(result.is_error) != expected_error:
                raise RuntimeError(
                    f"Respuesta inesperada de {name}: "
                    f"se esperaba is_error={expected_error}"
                )
    print("\nDemostración completada: la sesión sigue funcionando tras los errores.")
