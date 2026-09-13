"""Vector helpers and activations (no NumPy: every multiply is visible)."""

from __future__ import annotations

import math
from typing import Callable


def dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def add(a: list[float], b: list[float]) -> list[float]:
    return [x + y for x, y in zip(a, b)]


def scale(a: list[float], s: float) -> list[float]:
    return [s * x for x in a]


def matvec(matrix: list[list[float]], vec: list[float]) -> list[float]:
    return [dot(row, vec) for row in matrix]


def outer(u: list[float], v: list[float]) -> list[list[float]]:
    return [[ui * vj for vj in v] for ui in u]


def transpose(matrix: list[list[float]]) -> list[list[float]]:
    return [list(col) for col in zip(*matrix)]


def zeros(n: int) -> list[float]:
    return [0.0] * n


def zeros2(rows: int, cols: int) -> list[list[float]]:
    return [[0.0] * cols for _ in range(rows)]


def sigmoid(z: float) -> float:
    z = max(-30.0, min(30.0, z))
    return 1.0 / (1.0 + math.exp(-z))


def sigmoid_prime(z: float) -> float:
    s = sigmoid(z)
    return s * (1.0 - s)


def tanh(z: float) -> float:
    return math.tanh(z)


def tanh_prime(z: float) -> float:
    t = math.tanh(z)
    return 1.0 - t * t


def relu(z: float) -> float:
    return z if z > 0.0 else 0.0


def relu_prime(z: float) -> float:
    return 1.0 if z > 0.0 else 0.0


def step(z: float) -> float:
    return 1.0 if z >= 0.0 else 0.0


def step_prime(z: float) -> float:
    """Zero almost everywhere; step nets are for hand-set weights, not SGD."""
    return 0.0


def identity(z: float) -> float:
    return z


def identity_prime(z: float) -> float:
    return 1.0


Activation = Callable[[float], float]

ACTIVATIONS: dict[str, tuple[Activation, Activation]] = {
    "sigmoid": (sigmoid, sigmoid_prime),
    "tanh": (tanh, tanh_prime),
    "relu": (relu, relu_prime),
    "step": (step, step_prime),
    "identity": (identity, identity_prime),
}


def apply(fn: Activation, zs: list[float]) -> list[float]:
    return [fn(z) for z in zs]


def get_activation(name: str) -> tuple[Activation, Activation]:
    if name not in ACTIVATIONS:
        raise ValueError(f"unknown activation {name!r}. Choose: {', '.join(sorted(ACTIVATIONS))}")
    return ACTIVATIONS[name]
