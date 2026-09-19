#!/usr/bin/env python3
"""Program 3: choose k with the elbow (J) and the mean silhouette."""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from kmeans.cli import DEFAULT_BLOBS, load  # noqa: E402
from kmeans.format import format_choose_k, format_dataset  # noqa: E402
from kmeans.lloyd import fit_kmeans  # noqa: E402
from kmeans.metrics import silhouette_score  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Elbow (J vs k) and silhouette vs k.")
    parser.add_argument("--data", type=Path, default=DEFAULT_BLOBS, help="YAML point cloud")
    parser.add_argument("--seed", type=int, default=None, help="Override YAML seed")
    parser.add_argument("--k-min", type=int, default=None)
    parser.add_argument("--k-max", type=int, default=None)
    args = parser.parse_args()
    data = load(args)
    k_min = args.k_min if args.k_min is not None else data.k_min
    k_max = args.k_max if args.k_max is not None else min(data.k_max, data.n)
    seed = args.seed if args.seed is not None else data.seed

    print(format_dataset(data, max_rows=10))
    print()
    print("J always falls as k grows, so you cannot pick k by minimizing J.")
    print("Elbow: look for the k where the drop in J flattens.")
    print("Silhouette (k ≥ 2): mean of s(i) = (b − a) / max(a, b). Higher is better.")
    print()

    ks: list[int] = []
    inertias: list[float] = []
    sils: list[float | None] = []
    for k in range(k_min, k_max + 1):
        rng = random.Random(seed + 17 * k)
        result = fit_kmeans(
            data.X,
            k,
            rng,
            init="k-means++" if data.init == "given" else data.init,
            given=None,
            n_init=data.n_init,
            max_iter=data.max_iter,
        )
        ks.append(k)
        inertias.append(result.inertia)
        sils.append(None if k < 2 else silhouette_score(data.X, result.labels))

    true_k = data.k if data.truth is not None else None
    print(format_choose_k(ks, inertias, sils, true_k))


if __name__ == "__main__":
    main()
