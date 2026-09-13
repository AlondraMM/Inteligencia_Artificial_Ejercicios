"""Pretty-print forward passes, weights, and training history."""

from __future__ import annotations

from mlp.network import Forward, MLP
from mlp.perceptron import Perceptron
from mlp.problem import Problem
from mlp.train import History, accuracy_mlp, accuracy_perceptron, mean_mse_mlp


def _fmt_vec(xs: list[float], digits: int = 3) -> str:
    return "[" + ", ".join(f"{v:.{digits}f}" for v in xs) + "]"


def format_weights(net: MLP) -> str:
    lines = ["W_hidden  (each row is one hidden unit over the inputs)"]
    for i, row in enumerate(net.W_h, 1):
        lines.append(f"  h{i}  w={_fmt_vec(row)}  b={net.b_h[i - 1]:.3f}")
    lines.append("W_out")
    for i, row in enumerate(net.W_o, 1):
        lines.append(f"  y{i}  w={_fmt_vec(row)}  b={net.b_o[i - 1]:.3f}")
    return "\n".join(lines)


def format_forward_row(snap: Forward, y: list[float] | None = None) -> str:
    bits = [
        f"x={_fmt_vec(snap.x, 0) if all(v in (0.0, 1.0) for v in snap.x) else _fmt_vec(snap.x)}",
        f"z_h={_fmt_vec(snap.z_h)}",
        f"h={_fmt_vec(snap.h)}",
        f"z_o={_fmt_vec(snap.z_o)}",
        f"ŷ={_fmt_vec(snap.yhat)}",
    ]
    if y is not None:
        bits.append(f"y={_fmt_vec(y, 0)}")
    return "  ".join(bits)


def format_truth_table(net: MLP, problem: Problem, title: str = "") -> str:
    lines = []
    if title:
        lines.append(title)
        lines.append("-" * 72)
    header = f"{'x':<12}  {'y':<8}  {'ŷ':<10}  {'class':<8}  hidden h"
    lines.append(header)
    for ex in problem.examples:
        snap = net.forward(list(ex.x))
        pred = 1 if snap.yhat[0] >= 0.5 else 0
        target = 1 if ex.y[0] >= 0.5 else 0
        mark = "ok" if pred == target else "miss"
        xs = " ".join(f"{v:g}" for v in ex.x)
        ys = " ".join(f"{v:g}" for v in ex.y)
        lines.append(
            f"{xs:<12}  {ys:<8}  {snap.yhat[0]:<10.3f}  {pred} {mark:<5}  {_fmt_vec(snap.h)}"
        )
    acc = accuracy_mlp(net, problem)
    lines.append(f"accuracy {acc:.0%}    mean MSE {mean_mse_mlp(net, problem):.4f}")
    return "\n".join(lines)


def format_perceptron_table(net: Perceptron, problem: Problem, title: str = "") -> str:
    from mlp.train import accuracy_perceptron, mean_mse_perceptron

    lines = []
    if title:
        lines.append(title)
        lines.append("-" * 56)
    lines.append(f"{'x':<12}  {'y':<8}  {'ŷ':<10}  class")
    for ex in problem.examples:
        yhat = net.predict(list(ex.x))
        pred = 1 if yhat[0] >= 0.5 else 0
        target = 1 if ex.y[0] >= 0.5 else 0
        mark = "ok" if pred == target else "miss"
        xs = " ".join(f"{v:g}" for v in ex.x)
        ys = " ".join(f"{v:g}" for v in ex.y)
        lines.append(f"{xs:<12}  {ys:<8}  {yhat[0]:<10.3f}  {pred} {mark}")
    lines.append(
        f"accuracy {accuracy_perceptron(net, problem):.0%}    "
        f"mean MSE {mean_mse_perceptron(net, problem):.4f}"
    )
    return "\n".join(lines)


def format_history(hist: History, every: int = 500) -> str:
    lines = [f"{'epoch':>8}  {'MSE':>10}  {'acc':>8}"]
    n = len(hist.losses)
    for i, (loss, acc) in enumerate(zip(hist.losses, hist.accuracies), 1):
        if i == 1 or i == n or i % every == 0:
            lines.append(f"{i:8d}  {loss:10.4f}  {acc:8.0%}")
    return "\n".join(lines)


def sparkline(values: list[float]) -> str:
    if not values:
        return ""
    lo, hi = min(values), max(values)
    span = hi - lo if hi > lo else 1.0
    blocks = "▁▂▃▄▅▆▇█"
    chars = []
    for v in values[:: max(1, len(values) // 40)]:
        idx = int(round((v - lo) / span * (len(blocks) - 1)))
        idx = max(0, min(len(blocks) - 1, idx))
        chars.append(blocks[idx])
    return "".join(chars)
