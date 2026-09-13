#!/usr/bin/env python3
"""Program 4: perceptron (no hidden layer) vs MLP on the same data."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from mlp.cli import build_parser, load, make_rng  # noqa: E402
from mlp.format import format_perceptron_table, format_truth_table  # noqa: E402
from mlp.problem import format_problem  # noqa: E402
from mlp.train import accuracy_perceptron, train_mlp, train_perceptron  # noqa: E402


def main() -> None:
    parser = build_parser("Train a perceptron and an MLP on the same examples.")
    args = parser.parse_args()
    problem = load(args)
    epochs = args.epochs if args.epochs is not None else problem.epochs

    print(format_problem(problem))
    print()

    perc, _ = train_perceptron(problem, rng=make_rng(problem, args.seed), epochs=epochs)
    mlp, _ = train_mlp(problem, rng=make_rng(problem, args.seed), epochs=epochs)

    print(format_perceptron_table(perc, problem, "Perceptron  (no hidden layer)"))
    print()
    print(format_truth_table(mlp, problem, f"MLP  {problem.n_in}–{problem.hidden}–{problem.n_out}"))
    print()
    if accuracy_perceptron(perc, problem) < 1.0:
        print("This table is not linearly separable: the perceptron cannot get every point.")
        print("The hidden layer changes the representation; then the output can separate them.")
    else:
        print("This table is linearly separable: a perceptron (one plane) is enough.")


if __name__ == "__main__":
    main()
