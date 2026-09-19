#!/usr/bin/env python3
"""Program 4: scaling, k-means++ vs random, and a shape k-means cannot cut."""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from kmeans.dataset import load_dataset  # noqa: E402
from kmeans.format import cluster_name, fmt_vec  # noqa: E402
from kmeans.lloyd import fit_kmeans  # noqa: E402
from kmeans.metrics import cluster_accuracy  # noqa: E402
from kmeans.scale import fit_standard_scaler  # noqa: E402

DATA = ROOT / "data"


def _means_by_cluster(X, labels, k, dim):
    sums = [[0.0] * dim for _ in range(k)]
    counts = [0] * k
    for x, lab in zip(X, labels):
        counts[lab] += 1
        for d in range(dim):
            sums[lab][d] += x[d]
    out = []
    for j in range(k):
        if counts[j] == 0:
            out.append([0.0] * dim)
        else:
            out.append([s / counts[j] for s in sums[j]])
    return out, counts


def scaling_demo() -> None:
    data = load_dataset(DATA / "age_income.yaml")
    rng = random.Random(data.seed)
    raw = fit_kmeans(data.X, data.k, rng, init="k-means++", n_init=data.n_init, max_iter=data.max_iter)

    scaler = fit_standard_scaler(data.X)
    Xs = scaler.transform(data.X)
    rng = random.Random(data.seed)
    scaled = fit_kmeans(Xs, data.k, rng, init="k-means++", n_init=data.n_init, max_iter=data.max_iter)
    cents_orig = scaler.inverse(scaled.centroids)

    print("1. Scale the variables")
    print("-" * 72)
    print(data.name)
    print("Two age groups, similar income. Euclidean distance without scaling is dominated by income.")
    print()
    print(f"{'':<22}  {'mean age':>12}  {'mean income':>14}  {'size':>6}  vs age groups")
    raw_means, raw_n = _means_by_cluster(data.X, raw.labels, data.k, data.dim)
    for j in range(data.k):
        print(
            f"raw k-means {cluster_name(j):<10}  {raw_means[j][0]:12.1f}  {raw_means[j][1]:14.0f}  "
            f"{raw_n[j]:6d}"
        )
    print(f"{'raw J':<22}  {raw.inertia:12.3g}                    accuracy {cluster_accuracy(raw.labels, data.truth):.0%}")
    print()
    for j in range(data.k):
        print(
            f"scaled {cluster_name(j):<14}  {cents_orig[j][0]:12.1f}  {cents_orig[j][1]:14.0f}  "
            f"{scaled.labels.count(j):6d}"
        )
    print(
        f"{'scaled J (on z-scores)':<22}  {scaled.inertia:12.3g}                    "
        f"accuracy {cluster_accuracy(scaled.labels, data.truth):.0%}"
    )
    print()
    print("Centroids on the scaled run are mapped back to age and income (inverse of the scaler).")
    print("Practice: standardize, fit k-means, then talk about μ in the original units.")


def init_demo() -> None:
    data = load_dataset(DATA / "grid_blobs.yaml")
    print("2. Initialization: random vs k-means++")
    print("-" * 72)
    print(f"{data.name}   n = {data.n}   k = {data.k}   n_init = 1 (one seed each)")
    print("Six well-separated clouds. A random draw of 6 seeds can put two in one cloud and miss another.")
    print()
    print(f"{'trial':>6}  {'random J':>12}  {'k-means++ J':>12}")
    random_js = []
    plus_js = []
    for trial in range(8):
        r1 = fit_kmeans(data.X, data.k, random.Random(20 + trial), init="random", n_init=1, max_iter=data.max_iter)
        r2 = fit_kmeans(data.X, data.k, random.Random(20 + trial), init="k-means++", n_init=1, max_iter=data.max_iter)
        random_js.append(r1.inertia)
        plus_js.append(r2.inertia)
        print(f"{trial:6d}  {r1.inertia:12.2f}  {r2.inertia:12.2f}")
    print(
        f"{'mean':>6}  {sum(random_js) / len(random_js):12.2f}  {sum(plus_js) / len(plus_js):12.2f}"
    )
    print()
    print("k-means++ spreads the first seeds (probability ∝ D(x)²). Still run n_init > 1 and keep min J.")


def moons_demo() -> None:
    data = load_dataset(DATA / "moons.yaml")
    rng = random.Random(data.seed)
    result = fit_kmeans(data.X, data.k, rng, init="k-means++", n_init=data.n_init, max_iter=data.max_iter)
    acc = cluster_accuracy(result.labels, data.truth)
    print("3. When k-means fails")
    print("-" * 72)
    print(data.name)
    print("True groups are two interlocking crescents. k-means cuts space into Voronoi cells.")
    print()
    print(f"{'true moon':<12}  {'k-means A':>10}  {'k-means B':>10}")
    for g in (0, 1):
        row = [sum(t == g and p == j for t, p in zip(data.truth, result.labels)) for j in (0, 1)]
        print(f"{g:<12}  {row[0]:10d}  {row[1]:10d}")
    print()
    print(f"agreement with the true moons (best label permutation): {acc:.0%}")
    print(f"J = {result.inertia:.3f}   centroids: " + "  ".join(fmt_vec(c) for c in result.centroids))
    print()
    print("Each crescent is split. Compact Euclidean balls are the wrong model here.")
    print("Then you try DBSCAN / HDBSCAN (density), GMM (ellipses), or agglomerative (hierarchy).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaling, initialization, and a k-means failure.")
    parser.add_argument(
        "--only",
        choices=("scale", "init", "moons", "all"),
        default="all",
        help="Run one demo (default: all three)",
    )
    args = parser.parse_args()
    demos = {
        "scale": scaling_demo,
        "init": init_demo,
        "moons": moons_demo,
    }
    names = list(demos) if args.only == "all" else [args.only]
    for i, name in enumerate(names):
        if i:
            print()
            print()
        demos[name]()


if __name__ == "__main__":
    main()
