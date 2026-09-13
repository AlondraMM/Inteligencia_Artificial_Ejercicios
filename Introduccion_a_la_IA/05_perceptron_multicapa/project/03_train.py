#!/usr/bin/env python3
"""Program 3: train the MLP with SGD + backprop."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from mlp.cli import build_parser, load, make_rng  # noqa: E402
from mlp.format import format_history, format_truth_table, format_weights, sparkline  # noqa: E402
from mlp.problem import format_problem  # noqa: E402
from mlp.train import train_mlp  # noqa: E402


def main() -> None:
    parser = build_parser("Train a one-hidden-layer MLP (MSE + backprop).")
    args = parser.parse_args()
    problem = load(args)
    rng = make_rng(problem, args.seed)
    epochs = args.epochs if args.epochs is not None else problem.epochs

    print(format_problem(problem))
    if args.epochs is not None:
        print(f"Override:      epochs={epochs}")
    print()

    net, hist = train_mlp(problem, rng=rng, epochs=epochs)
    print(format_history(hist, every=max(1, epochs // 10)))
    print()
    print("MSE over epochs:  " + sparkline(hist.losses))
    print()
    print(format_weights(net))
    print()
    print(format_truth_table(net, problem, "After training"))


if __name__ == "__main__":
    main()
