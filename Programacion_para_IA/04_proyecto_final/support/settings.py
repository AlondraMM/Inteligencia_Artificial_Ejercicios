"""Carga y validación de la configuración compartida del modelo de embeddings."""

from dataclasses import dataclass
import json
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_DIR / "config.json"
DEFAULT_DATA_DIR = PROJECT_DIR / "datasets"


def _non_empty_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} debe ser una cadena no vacía")
    return value.strip()


def _positive_integer(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field} debe ser un entero positivo")
    return value


@dataclass(frozen=True)
class Settings:
    """Parámetros del único modelo utilizado para catálogo, reseñas y consultas."""

    model_name: str
    batch_size: int
    device: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "model_name", _non_empty_string(self.model_name, "model_name")
        )
        _positive_integer(self.batch_size, "batch_size")
        object.__setattr__(self, "device", _non_empty_string(self.device, "device"))


def load_settings(path: Path | None = None) -> Settings:
    """Lee config.json sin depender del directorio desde el que se ejecute Python.

    Los tres campos son obligatorios. El dispositivo se pasa al modelo, que
    comprueba su disponibilidad al cargarlo (por ejemplo, cpu, cuda o mps).
    """
    config_path = DEFAULT_CONFIG_PATH if path is None else path
    with config_path.open("r", encoding="utf-8") as stream:
        try:
            config: object = json.load(stream)
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSON inválido en {config_path}: {exc.msg}") from exc

    if not isinstance(config, dict):
        raise ValueError("La configuración debe ser un objeto JSON")

    return Settings(
        model_name=_non_empty_string(config.get("model_name"), "model_name"),
        batch_size=_positive_integer(config.get("batch_size"), "batch_size"),
        device=_non_empty_string(config.get("device"), "device"),
    )
