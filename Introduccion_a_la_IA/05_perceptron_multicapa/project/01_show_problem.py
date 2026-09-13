#!/usr/bin/env python3
"""Program 1: print the problem (data, architecture, training knobs)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from mlp.cli import build_parser, load  # noqa: E402
from mlp.problem import format_problem  # noqa: E402


def main() -> None:
    parser = build_parser("Show a YAML MLP problem.")
    args = parser.parse_args()
    print(format_problem(load(args)))
    print()
    print("Edit the YAML file, then rerun this program.")


if __name__ == "__main__":
    main()
