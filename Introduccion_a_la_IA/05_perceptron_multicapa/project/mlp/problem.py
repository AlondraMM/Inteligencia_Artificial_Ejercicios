"""YAML problem: examples, architecture, optional hand-set weights."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from mlp.network import MLP


@dataclass(frozen=True)
class Example:
    x: tuple[float, ...]
    y: tuple[float, ...]


@dataclass(frozen=True)
class Problem:
    name: str
    hidden: int
    hidden_act: str
    out_act: str
    examples: tuple[Example, ...]
    epochs: int
    learning_rate: float
    seed: int
    weights: dict[str, Any] | None
    source: Path | None = None

    @property
    def n_in(self) -> int:
        return len(self.examples[0].x)

    @property
    def n_out(self) -> int:
        return len(self.examples[0].y)


def load_problem(path: str | Path) -> Problem:
    path = Path(path)
    with path.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    return parse_problem(raw, source=path)


def parse_problem(raw: dict[str, Any], source: Path | None = None) -> Problem:
    examples = []
    for row in raw.get("examples") or []:
        x = tuple(float(v) for v in row["x"])
        y = tuple(float(v) for v in row["y"])
        examples.append(Example(x, y))
    if not examples:
        raise ValueError("examples: need at least one {x, y}")
    n_in = len(examples[0].x)
    n_out = len(examples[0].y)
    for ex in examples:
        if len(ex.x) != n_in or len(ex.y) != n_out:
            raise ValueError("all examples must have the same x and y sizes")
    return Problem(
        name=str(raw.get("name") or "MLP problem"),
        hidden=int(raw.get("hidden") if raw.get("hidden") is not None else 2),
        hidden_act=str(raw.get("hidden_act") or "sigmoid"),
        out_act=str(raw.get("out_act") or "sigmoid"),
        examples=tuple(examples),
        epochs=int(raw["epochs"]) if raw.get("epochs") is not None else 4000,
        learning_rate=float(raw["learning_rate"]) if raw.get("learning_rate") is not None else 0.5,
        seed=int(raw["seed"]) if raw.get("seed") is not None else 1,
        weights=raw.get("weights"),
        source=source,
    )


def mlp_from_weights(problem: Problem) -> MLP:
    w = problem.weights or {}
    return MLP(
        W_h=[list(map(float, row)) for row in w["W_hidden"]],
        b_h=[float(v) for v in w["b_hidden"]],
        W_o=[list(map(float, row)) for row in w["W_out"]],
        b_o=[float(v) for v in w["b_out"]],
        hidden_act=problem.hidden_act,
        out_act=problem.out_act,
    )


def format_problem(problem: Problem) -> str:
    lines = [
        problem.name,
        "",
        f"Architecture:  {problem.n_in} → {problem.hidden} → {problem.n_out}",
        f"Activations:   hidden={problem.hidden_act}   out={problem.out_act}",
        f"Training:      epochs={problem.epochs}   η={problem.learning_rate}   seed={problem.seed}",
        f"Examples:      {len(problem.examples)}",
        "",
        f"{'x':<16}  y",
        "-" * 28,
    ]
    for ex in problem.examples:
        xs = ", ".join(f"{v:g}" for v in ex.x)
        ys = ", ".join(f"{v:g}" for v in ex.y)
        lines.append(f"[{xs}]{'':<{max(0, 14 - len(xs))}}  [{ys}]")
    if problem.weights:
        lines.append("")
        lines.append("Hand-set weights are in the YAML (used by 02_forward.py).")
    return "\n".join(lines)
