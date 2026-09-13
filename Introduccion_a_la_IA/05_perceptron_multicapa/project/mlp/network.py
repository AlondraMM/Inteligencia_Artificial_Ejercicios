"""One-hidden-layer MLP: forward, loss, backprop."""

from __future__ import annotations

import random
from dataclasses import dataclass

from mlp.activations import apply, get_activation, matvec, outer, transpose


@dataclass
class Forward:
    x: list[float]
    z_h: list[float]
    h: list[float]
    z_o: list[float]
    yhat: list[float]


@dataclass
class MLP:
    W_h: list[list[float]]
    b_h: list[float]
    W_o: list[list[float]]
    b_o: list[float]
    hidden_act: str = "sigmoid"
    out_act: str = "sigmoid"

    @property
    def n_in(self) -> int:
        return len(self.W_h[0]) if self.W_h else 0

    @property
    def n_hidden(self) -> int:
        return len(self.W_h)

    @property
    def n_out(self) -> int:
        return len(self.W_o)

    def forward(self, x: list[float]) -> Forward:
        f, _ = get_activation(self.hidden_act)
        g, _ = get_activation(self.out_act)
        z_h = [dot_row + b for dot_row, b in zip(matvec(self.W_h, x), self.b_h)]
        h = apply(f, z_h)
        z_o = [dot_row + b for dot_row, b in zip(matvec(self.W_o, h), self.b_o)]
        yhat = apply(g, z_o)
        return Forward(x=list(x), z_h=z_h, h=h, z_o=z_o, yhat=yhat)

    def predict(self, x: list[float]) -> list[float]:
        return self.forward(x).yhat

    def mse(self, x: list[float], y: list[float]) -> float:
        yhat = self.predict(x)
        return 0.5 * sum((a - b) ** 2 for a, b in zip(yhat, y))

    def backward(self, snap: Forward, y: list[float], lr: float) -> None:
        """SGD on L = ½ ‖ŷ − y‖². Updates weights in place."""
        _, f_p = get_activation(self.hidden_act)
        _, g_p = get_activation(self.out_act)
        dzo = [(yh - t) * g_p(z) for yh, t, z in zip(snap.yhat, y, snap.z_o)]
        dWo = outer(dzo, snap.h)
        dbo = dzo
        dh = matvec(transpose(self.W_o), dzo)
        dzh = [d * f_p(z) for d, z in zip(dh, snap.z_h)]
        dWh = outer(dzh, snap.x)
        dbh = dzh
        self.W_o = [[w - lr * g for w, g in zip(row, grow)] for row, grow in zip(self.W_o, dWo)]
        self.b_o = [b - lr * g for b, g in zip(self.b_o, dbo)]
        self.W_h = [[w - lr * g for w, g in zip(row, grow)] for row, grow in zip(self.W_h, dWh)]
        self.b_h = [b - lr * g for b, g in zip(self.b_h, dbh)]


def random_mlp(
    n_in: int,
    n_hidden: int,
    n_out: int,
    rng: random.Random,
    hidden_act: str = "sigmoid",
    out_act: str = "sigmoid",
    scale: float = 1.0,
) -> MLP:
    def rnd(rows: int, cols: int) -> list[list[float]]:
        return [[(rng.random() * 2 - 1) * scale for _ in range(cols)] for _ in range(rows)]

    return MLP(
        W_h=rnd(n_hidden, n_in),
        b_h=[(rng.random() * 2 - 1) * scale for _ in range(n_hidden)],
        W_o=rnd(n_out, n_hidden),
        b_o=[(rng.random() * 2 - 1) * scale for _ in range(n_out)],
        hidden_act=hidden_act,
        out_act=out_act,
    )
