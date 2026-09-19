"""Standardize each column: zero mean, unit variance (sklearn StandardScaler, ddof=0)."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class StandardScaler:
    mean: tuple[float, ...]
    scale: tuple[float, ...]

    def transform(self, X: tuple[tuple[float, ...], ...]) -> tuple[tuple[float, ...], ...]:
        return tuple(
            tuple((x[d] - self.mean[d]) / self.scale[d] for d in range(len(self.mean)))
            for x in X
        )

    def inverse(self, X: list[list[float]] | tuple[tuple[float, ...], ...]) -> list[list[float]]:
        return [
            [row[d] * self.scale[d] + self.mean[d] for d in range(len(self.mean))]
            for row in X
        ]


def fit_standard_scaler(X: tuple[tuple[float, ...], ...]) -> StandardScaler:
    n = len(X)
    dim = len(X[0])
    mean = tuple(sum(x[d] for x in X) / n for d in range(dim))
    var = tuple(sum((x[d] - mean[d]) ** 2 for x in X) / n for d in range(dim))
    scale = tuple(math.sqrt(v) if v > 0 else 1.0 for v in var)
    return StandardScaler(mean=mean, scale=scale)
