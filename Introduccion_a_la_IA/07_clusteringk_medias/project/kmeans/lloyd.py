"""Lloyd's algorithm: assign to nearest centroid, replace each centroid by the mean."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field


def sqdist(a: list[float] | tuple[float, ...], b: list[float] | tuple[float, ...]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b))


def euclid(a: list[float] | tuple[float, ...], b: list[float] | tuple[float, ...]) -> float:
    return math.sqrt(sqdist(a, b))


def inertia(
    X: list[tuple[float, ...]] | tuple[tuple[float, ...], ...],
    labels: list[int],
    centroids: list[list[float]],
) -> float:
    return sum(sqdist(X[i], centroids[labels[i]]) for i in range(len(X)))


def assign(
    X: list[tuple[float, ...]] | tuple[tuple[float, ...], ...],
    centroids: list[list[float]],
) -> list[int]:
    labels = []
    for x in X:
        best_j, best_d = 0, sqdist(x, centroids[0])
        for j in range(1, len(centroids)):
            d = sqdist(x, centroids[j])
            if d < best_d:
                best_j, best_d = j, d
        labels.append(best_j)
    return labels


def _mean(points: list[tuple[float, ...]], dim: int) -> list[float]:
    n = len(points)
    return [sum(p[d] for p in points) / n for d in range(dim)]


def update(
    X: list[tuple[float, ...]] | tuple[tuple[float, ...], ...],
    labels: list[int],
    k: int,
    rng: random.Random,
) -> list[list[float]]:
    dim = len(X[0])
    groups: list[list[tuple[float, ...]]] = [[] for _ in range(k)]
    for x, lab in zip(X, labels):
        groups[lab].append(x)
    centroids: list[list[float] | None] = [None] * k
    for j in range(k):
        if groups[j]:
            centroids[j] = _mean(groups[j], dim)
    filled = [c for c in centroids if c is not None]
    for j in range(k):
        if centroids[j] is not None:
            continue
        if filled:
            farthest = max(X, key=lambda x: min(sqdist(x, c) for c in filled))
            centroids[j] = list(farthest)
        else:
            centroids[j] = list(X[rng.randrange(len(X))])
        filled.append(centroids[j])
    return [c if c is not None else list(X[0]) for c in centroids]


def init_random(X: tuple[tuple[float, ...], ...], k: int, rng: random.Random) -> list[list[float]]:
    idx = list(range(len(X)))
    rng.shuffle(idx)
    chosen = sorted(idx[:k])  # stable order for reading
    return [list(X[i]) for i in chosen]


def init_kmeans_pp(X: tuple[tuple[float, ...], ...], k: int, rng: random.Random) -> list[list[float]]:
    """Arthur & Vassilvitskii 2007: next seed with probability ∝ D(x)²."""
    n = len(X)
    centroids = [list(X[rng.randrange(n)])]
    while len(centroids) < k:
        weights = [min(sqdist(x, c) for c in centroids) for x in X]
        total = sum(weights)
        if total <= 0:
            leftover = [list(X[i]) for i in range(n) if list(X[i]) not in centroids]
            centroids.append(leftover[0] if leftover else list(X[rng.randrange(n)]))
            continue
        pick = rng.random() * total
        acc = 0.0
        chosen = None
        for x, w in zip(X, weights):
            acc += w
            if acc >= pick:
                chosen = list(x)
                break
        centroids.append(chosen if chosen is not None else list(X[-1]))
    return centroids


def initial_centroids(
    X: tuple[tuple[float, ...], ...],
    k: int,
    rng: random.Random,
    init: str,
    given: tuple[tuple[float, ...], ...] | None,
) -> list[list[float]]:
    if init == "given":
        if not given:
            raise ValueError("init: given needs centroids in the YAML")
        if len(given) != k:
            raise ValueError(f"init: given {len(given)} centroids, k={k}")
        return [list(c) for c in given]
    if init == "random":
        return init_random(X, k, rng)
    if init == "k-means++":
        return init_kmeans_pp(X, k, rng)
    raise ValueError(f"unknown init {init!r}")


@dataclass
class Step:
    t: int
    centroids: list[list[float]]
    updated: list[list[float]]
    labels: list[int]
    inertia: float
    n_changed: int


@dataclass
class KMeansResult:
    centroids: list[list[float]]
    labels: list[int]
    inertia: float
    n_iter: int
    history: list[Step] = field(default_factory=list)


def lloyd(
    X: tuple[tuple[float, ...], ...],
    centroids: list[list[float]],
    max_iter: int,
    rng: random.Random,
) -> KMeansResult:
    k = len(centroids)
    prev_labels: list[int] | None = None
    hist: list[Step] = []
    for t in range(1, max_iter + 1):
        labels = assign(X, centroids)
        n_changed = len(X) if prev_labels is None else sum(a != b for a, b in zip(prev_labels, labels))
        if prev_labels is not None and n_changed == 0:
            break
        updated = update(X, labels, k, rng)
        hist.append(
            Step(
                t=t,
                centroids=[c[:] for c in centroids],
                updated=[c[:] for c in updated],
                labels=list(labels),
                inertia=inertia(X, labels, updated),
                n_changed=n_changed,
            )
        )
        prev_labels = labels
        centroids = updated
    last = hist[-1]
    return KMeansResult(
        centroids=last.updated,
        labels=last.labels,
        inertia=last.inertia,
        n_iter=last.t,
        history=hist,
    )


def fit_kmeans(
    X: tuple[tuple[float, ...], ...],
    k: int,
    rng: random.Random,
    init: str = "k-means++",
    given: tuple[tuple[float, ...], ...] | None = None,
    n_init: int = 10,
    max_iter: int = 100,
) -> KMeansResult:
    """Several seeds; keep the run with the smallest J (lecture: n_init)."""
    if init == "given":
        n_init = 1
    best: KMeansResult | None = None
    base = rng.randint(0, 10**9)
    for trial in range(n_init):
        trial_rng = random.Random(base + trial)
        start = initial_centroids(X, k, trial_rng, init, given)
        result = lloyd(X, start, max_iter, trial_rng)
        if best is None or result.inertia < best.inertia:
            best = result
    assert best is not None
    return best
