"""CLI helpers."""

from __future__ import annotations

import argparse
import random
from pathlib import Path

from mlp.problem import Problem, load_problem

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_XOR = ROOT / "problems" / "xor.yaml"
DEFAULT_HAND = ROOT / "problems" / "xor_hand.yaml"


def build_parser(description: str, default: Path | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--problem", type=Path, default=default or DEFAULT_XOR, help="YAML MLP problem")
    parser.add_argument("--seed", type=int, default=None, help="Override YAML seed")
    parser.add_argument("--epochs", type=int, default=None, help="Override YAML epochs")
    return parser


def load(args: argparse.Namespace) -> Problem:
    return load_problem(args.problem)


def make_rng(problem: Problem, seed_override: int | None) -> random.Random:
    seed = seed_override if seed_override is not None else problem.seed
    return random.Random(seed)
