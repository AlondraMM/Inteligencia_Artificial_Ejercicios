"""CLI helpers."""

from __future__ import annotations

import argparse
import random
from pathlib import Path

from kmeans.dataset import Dataset, load_dataset

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SIX = ROOT / "data" / "six_points.yaml"
DEFAULT_BLOBS = ROOT / "data" / "blobs.yaml"


def build_parser(description: str, default: Path | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--data",
        type=Path,
        default=default or DEFAULT_SIX,
        help="YAML point cloud",
    )
    parser.add_argument("--seed", type=int, default=None, help="Override YAML seed")
    parser.add_argument("--k", type=int, default=None, help="Override YAML k")
    return parser


def load(args: argparse.Namespace) -> Dataset:
    return load_dataset(args.data)


def make_rng(data: Dataset, seed_override: int | None) -> random.Random:
    seed = seed_override if seed_override is not None else data.seed
    return random.Random(seed)
