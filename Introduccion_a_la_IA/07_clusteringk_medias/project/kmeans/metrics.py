"""Inertia is in lloyd.py. Here: silhouette and agreement with a held-out labeling."""

from __future__ import annotations

from itertools import permutations

from kmeans.lloyd import euclid


def silhouette_samples(
    X: tuple[tuple[float, ...], ...],
    labels: list[int],
) -> list[float]:
    """s(i) = (b − a) / max(a, b) ∈ [−1, 1]. Singleton clusters get 0."""
    n = len(X)
    clusters: dict[int, list[int]] = {}
    for i, lab in enumerate(labels):
        clusters.setdefault(lab, []).append(i)
    scores = []
    for i, x in enumerate(X):
        own = labels[i]
        members = clusters[own]
        if len(members) <= 1:
            scores.append(0.0)
            continue
        a = sum(euclid(x, X[j]) for j in members if j != i) / (len(members) - 1)
        b = None
        for lab, idxs in clusters.items():
            if lab == own or not idxs:
                continue
            mean_d = sum(euclid(x, X[j]) for j in idxs) / len(idxs)
            if b is None or mean_d < b:
                b = mean_d
        if b is None:
            scores.append(0.0)
            continue
        denom = max(a, b)
        scores.append(0.0 if denom == 0 else (b - a) / denom)
    return scores


def silhouette_score(X: tuple[tuple[float, ...], ...], labels: list[int]) -> float:
    samples = silhouette_samples(X, labels)
    return sum(samples) / len(samples) if samples else 0.0


def cluster_accuracy(pred: list[int], truth: tuple[int, ...]) -> float:
    """Best match of predicted ids to truth ids (small k)."""
    pred_ids = sorted(set(pred))
    truth_ids = sorted(set(truth))
    n = len(pred)
    if not pred_ids or not truth_ids:
        return 0.0
    best = 0.0
    if len(pred_ids) <= len(truth_ids):
        for perm in permutations(truth_ids, len(pred_ids)):
            mapping = dict(zip(pred_ids, perm))
            ok = sum(mapping[p] == t for p, t in zip(pred, truth))
            best = max(best, ok / n)
    else:
        for perm in permutations(pred_ids, len(truth_ids)):
            mapping = dict(zip(perm, truth_ids))
            ok = sum(mapping.get(p, -1) == t for p, t in zip(pred, truth))
            best = max(best, ok / n)
    return best
