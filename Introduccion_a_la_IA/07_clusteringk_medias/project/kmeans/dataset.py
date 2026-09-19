"""Unlabeled points loaded from YAML (explicit list or a small generator)."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Dataset:
    name: str
    k: int
    features: tuple[str, ...]
    ids: tuple[str, ...]
    X: tuple[tuple[float, ...], ...]
    truth: tuple[int, ...] | None
    init: str
    centroids: tuple[tuple[float, ...], ...] | None
    n_init: int
    max_iter: int
    seed: int
    k_min: int
    k_max: int
    source: Path | None = None

    @property
    def n(self) -> int:
        return len(self.X)

    @property
    def dim(self) -> int:
        return len(self.features)


def load_dataset(path: str | Path) -> Dataset:
    path = Path(path)
    with path.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    return parse_dataset(raw, source=path)


def parse_dataset(raw: dict[str, Any], source: Path | None = None) -> Dataset:
    features = tuple(str(f) for f in (raw.get("features") or ["x", "y"]))
    if not features:
        raise ValueError("features: list the coordinate names")
    kind = str(raw.get("kind") or "points")
    seed = int(raw.get("seed", 0))
    rng = random.Random(seed)

    if kind == "points":
        ids, X, truth = _from_points(raw, features)
    elif kind == "blobs":
        ids, X, truth = _from_blobs(raw, features, rng)
    elif kind == "groups":
        ids, X, truth = _from_groups(raw, features, rng)
    elif kind == "moons":
        ids, X, truth = _from_moons(raw, rng)
    else:
        raise ValueError(f"unknown kind {kind!r} (points | blobs | groups | moons)")

    if not X:
        raise ValueError("need at least one point")
    dim = len(features)
    for i, x in enumerate(X):
        if len(x) != dim:
            raise ValueError(f"point {i + 1} has {len(x)} coords, expected {dim}")

    init = str(raw.get("init") or "k-means++")
    if init not in {"given", "random", "k-means++"}:
        raise ValueError("init must be given, random, or k-means++")

    centroids = None
    if raw.get("centroids"):
        centroids = tuple(tuple(float(v) for v in row) for row in raw["centroids"])
        for c in centroids:
            if len(c) != dim:
                raise ValueError("each centroid must have one value per feature")
        init = "given"

    k = int(raw.get("k") or (len(centroids) if centroids else 2))
    if k < 1:
        raise ValueError("k must be >= 1")
    k_min = int(raw.get("k_min", 1))
    k_max = int(raw.get("k_max", max(k, 8)))
    if k_min < 1 or k_max < k_min:
        raise ValueError("need 1 <= k_min <= k_max")

    n_init = int(raw.get("n_init", 1 if init == "given" else 10))
    max_iter = int(raw.get("max_iter", 100))
    return Dataset(
        name=str(raw.get("name") or "k-means data"),
        k=k,
        features=features,
        ids=tuple(ids),
        X=tuple(X),
        truth=tuple(truth) if truth is not None else None,
        init=init,
        centroids=centroids,
        n_init=max(1, n_init),
        max_iter=max(1, max_iter),
        seed=seed,
        k_min=k_min,
        k_max=k_max,
        source=source,
    )


def _from_points(
    raw: dict[str, Any], features: tuple[str, ...]
) -> tuple[list[str], list[tuple[float, ...]], tuple[int, ...] | None]:
    ids: list[str] = []
    X: list[tuple[float, ...]] = []
    truth_list: list[int] = []
    has_truth = False
    for i, row in enumerate(raw.get("points") or [], 1):
        ids.append(str(row.get("id") or f"P{i}"))
        X.append(tuple(float(row[f]) for f in features))
        if "cluster" in row:
            has_truth = True
            truth_list.append(int(row["cluster"]))
    truth = tuple(truth_list) if has_truth else None
    return ids, X, truth


def _from_blobs(
    raw: dict[str, Any], features: tuple[str, ...], rng: random.Random
) -> tuple[list[str], list[tuple[float, ...]], tuple[int, ...]]:
    centers = raw.get("centers") or []
    if not centers:
        raise ValueError("blobs: need centers")
    std = float(raw.get("cluster_std", 0.6))
    n_each = int(raw.get("n_per_cluster", 60))
    ids: list[str] = []
    X: list[tuple[float, ...]] = []
    truth: list[int] = []
    n = 0
    for j, center in enumerate(centers):
        c = [float(v) for v in center]
        if len(c) != len(features):
            raise ValueError("each blob center must have one value per feature")
        for _ in range(n_each):
            n += 1
            ids.append(f"P{n}")
            X.append(tuple(rng.gauss(mu, std) for mu in c))
            truth.append(j)
    return ids, X, tuple(truth)


def _from_groups(
    raw: dict[str, Any], features: tuple[str, ...], rng: random.Random
) -> tuple[list[str], list[tuple[float, ...]], tuple[int, ...]]:
    groups = raw.get("groups") or []
    if not groups:
        raise ValueError("groups: need at least one group")
    ids: list[str] = []
    X: list[tuple[float, ...]] = []
    truth: list[int] = []
    n = 0
    for j, g in enumerate(groups):
        count = int(g.get("n", 50))
        for _ in range(count):
            n += 1
            ids.append(f"P{n}")
            X.append(tuple(rng.gauss(float(g[f]), float(g[f"{f}_std"])) for f in features))
            truth.append(j)
    return ids, X, tuple(truth)


def _from_moons(
    raw: dict[str, Any], rng: random.Random
) -> tuple[list[str], list[tuple[float, ...]], tuple[int, ...]]:
    n = int(raw.get("n", 220))
    noise = float(raw.get("noise", 0.08))
    n_out = n // 2
    n_in = n - n_out
    X: list[tuple[float, ...]] = []
    truth: list[int] = []
    for i in range(n_out):
        t = math.pi * i / max(n_out - 1, 1)
        X.append((math.cos(t) + rng.gauss(0, noise), math.sin(t) + rng.gauss(0, noise)))
        truth.append(0)
    for i in range(n_in):
        t = math.pi * i / max(n_in - 1, 1)
        X.append((1 - math.cos(t) + rng.gauss(0, noise), 1 - math.sin(t) - 0.5 + rng.gauss(0, noise)))
        truth.append(1)
    order = list(range(n))
    rng.shuffle(order)
    ids = [f"P{i + 1}" for i in range(n)]
    return ids, [X[i] for i in order], tuple(truth[i] for i in order)
