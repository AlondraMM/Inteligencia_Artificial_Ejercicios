"""Punto de entrada para ejecutar el cliente de demostración."""

import asyncio
import sys

from client import SERVER_URL, demonstrate


if __name__ == "__main__":
    try:
        asyncio.run(demonstrate())
    except Exception:
        print(
            f"No se pudo completar la demostración. Comprueba que el servidor "
            f"esté listo en {SERVER_URL}. El detalle del error aparece abajo.",
            file=sys.stderr,
        )
        raise
