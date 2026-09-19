#!/usr/bin/env python3
"""Program 2: Lloyd — assign, then replace each centroid by the mean."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from kmeans.cli import DEFAULT_SIX, build_parser, load, make_rng  # noqa: E402
from kmeans.format import format_result, format_step  # noqa: E402
from kmeans.lloyd import fit_kmeans  # noqa: E402


def main() -> None:
    parser = build_parser("Run Lloyd iteration by iteration.", default=DEFAULT_SIX)
    args = parser.parse_args()
    data = load(args)
    k = args.k if args.k is not None else data.k
    rng = make_rng(data, args.seed)

    print(data.name)
    print()
    print("Each iteration: assign every point to the nearest μ_j, then μ_j ← mean of its points.")
    print("J = Σ_j Σ_{x in Cⱼ} ‖x − μ_j‖²   (always nonincreasing).")
    print()

    result = fit_kmeans(
        data.X,
        k,
        rng,
        init=data.init,
        given=data.centroids,
        n_init=data.n_init,
        max_iter=data.max_iter,
    )
    prev = None
    for step in result.history:
        print(format_step(data, step, prev))
        print()
        prev = step
    print(format_result(data, result))
    if data.init == "given" and data.n == 6:
        print()
        print("Lecture check: a bad start (both seeds on the left) still splits the two clouds.")


if __name__ == "__main__":
    main()
