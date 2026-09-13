"""Single-layer perceptron (no hidden units): ŷ = f(Wx + b)."""

from __future__ import annotations

import random
from dataclasses import dataclass

from mlp.activations import apply, get_activation, matvec, outer
from mlp.network import Forward


@dataclass
class Perceptron:
    W: list[list[float]]
    b: list[float]
    activation: str = "sigmoid"

    def forward(self, x: list[float]) -> Forward:
        f, _ = get_activation(self.activation)
        z = [dot_row + bi for dot_row, bi in zip(matvec(self.W, x), self.b)]
        yhat = apply(f, z)
        return Forward(x=list(x), z_h=[], h=[], z_o=z, yhat=yhat)

    def predict(self, x: list[float]) -> list[float]:
        return self.forward(x).yhat

    def mse(self, x: list[float], y: list[float]) -> float:
        yhat = self.predict(x)
        return 0.5 * sum((a - b) ** 2 for a, b in zip(yhat, y))

    def backward(self, snap: Forward, y: list[float], lr: float) -> None:
        _, f_p = get_activation(self.activation)
        dz = [(yh - t) * f_p(z) for yh, t, z in zip(snap.yhat, y, snap.z_o)]
        dW = outer(dz, snap.x)
        self.W = [[w - lr * g for w, g in zip(row, grow)] for row, grow in zip(self.W, dW)]
        self.b = [b - lr * g for b, g in zip(self.b, dz)]


def random_perceptron(n_in: int, n_out: int, rng: random.Random, activation: str = "sigmoid") -> Perceptron:
    W = [[rng.random() * 2 - 1 for _ in range(n_in)] for _ in range(n_out)]
    b = [rng.random() * 2 - 1 for _ in range(n_out)]
    return Perceptron(W=W, b=b, activation=activation)
