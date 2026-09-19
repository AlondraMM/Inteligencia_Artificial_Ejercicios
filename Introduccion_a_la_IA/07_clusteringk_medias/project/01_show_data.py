#!/usr/bin/env python3
"""Program 1: print the unlabeled points (k-means never sees a y)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from kmeans.cli import build_parser, load  # noqa: E402
from kmeans.format import format_dataset  # noqa: E402


def main() -> None:
    parser = build_parser("Show a YAML point cloud.")
    args = parser.parse_args()
    data = load(args)
    print(format_dataset(data))
    print()
    print("Edit the YAML file, then rerun this program.")
    print("k-means only uses the coordinates. Any 'truth' groups are for you, not for Lloyd.")


if __name__ == "__main__":
    main()
