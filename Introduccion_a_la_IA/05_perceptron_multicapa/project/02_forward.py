#!/usr/bin/env python3
"""Program 2: one forward pass per example (z, h, ŷ).

Default is the lecture XOR net with hand-set threshold weights.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from mlp.cli import DEFAULT_HAND, build_parser, load  # noqa: E402
from mlp.format import format_forward_row, format_truth_table, format_weights  # noqa: E402
from mlp.problem import format_problem  # noqa: E402
from mlp.train import build_for_forward  # noqa: E402


def main() -> None:
    parser = build_parser(
        "Forward pass: print pre-activations, hidden units, and ŷ.",
        default=DEFAULT_HAND,
    )
    args = parser.parse_args()
    problem = load(args)
    net = build_for_forward(problem)

    print(format_problem(problem))
    print()
    print(format_weights(net))
    print()
    print("Forward  (ŷ = g(V f(Wx + b) + c))")
    print("-" * 72)
    for ex in problem.examples:
        snap = net.forward(list(ex.x))
        print(format_forward_row(snap, list(ex.y)))
    print()
    print(format_truth_table(net, problem, "Truth table"))


if __name__ == "__main__":
    main()
