"""SGD training loops."""

from __future__ import annotations

import random
from dataclasses import dataclass

from mlp.network import MLP, random_mlp
from mlp.perceptron import Perceptron, random_perceptron
from mlp.problem import Problem, mlp_from_weights


@dataclass
class History:
    losses: list[float]
    accuracies: list[float]


def _threshold(yhat: list[float]) -> list[float]:
    return [1.0 if v >= 0.5 else 0.0 for v in yhat]


def accuracy_mlp(net: MLP, problem: Problem) -> float:
    ok = 0
    for ex in problem.examples:
        pred = _threshold(net.predict(list(ex.x)))
        if pred == [1.0 if v >= 0.5 else 0.0 for v in ex.y]:
            ok += 1
    return ok / len(problem.examples)


def accuracy_perceptron(net: Perceptron, problem: Problem) -> float:
    ok = 0
    for ex in problem.examples:
        pred = _threshold(net.predict(list(ex.x)))
        if pred == [1.0 if v >= 0.5 else 0.0 for v in ex.y]:
            ok += 1
    return ok / len(problem.examples)


def mean_mse_mlp(net: MLP, problem: Problem) -> float:
    return sum(net.mse(list(ex.x), list(ex.y)) for ex in problem.examples) / len(problem.examples)


def mean_mse_perceptron(net: Perceptron, problem: Problem) -> float:
    return sum(net.mse(list(ex.x), list(ex.y)) for ex in problem.examples) / len(problem.examples)


def train_mlp(problem: Problem, rng: random.Random | None = None, epochs: int | None = None) -> tuple[MLP, History]:
    rng = rng or random.Random(problem.seed)
    net = random_mlp(problem.n_in, problem.hidden, problem.n_out, rng, problem.hidden_act, problem.out_act)
    n_epochs = problem.epochs if epochs is None else epochs
    hist = History([], [])
    examples = list(problem.examples)
    for _ in range(n_epochs):
        rng.shuffle(examples)
        for ex in examples:
            snap = net.forward(list(ex.x))
            net.backward(snap, list(ex.y), problem.learning_rate)
        hist.losses.append(mean_mse_mlp(net, problem))
        hist.accuracies.append(accuracy_mlp(net, problem))
    return net, hist


def train_perceptron(problem: Problem, rng: random.Random | None = None, epochs: int | None = None) -> tuple[Perceptron, History]:
    rng = rng or random.Random(problem.seed)
    net = random_perceptron(problem.n_in, problem.n_out, rng, problem.out_act)
    n_epochs = problem.epochs if epochs is None else epochs
    hist = History([], [])
    examples = list(problem.examples)
    for _ in range(n_epochs):
        rng.shuffle(examples)
        for ex in examples:
            snap = net.forward(list(ex.x))
            net.backward(snap, list(ex.y), problem.learning_rate)
        hist.losses.append(mean_mse_perceptron(net, problem))
        hist.accuracies.append(accuracy_perceptron(net, problem))
    return net, hist


def build_for_forward(problem: Problem) -> MLP:
    if problem.weights:
        return mlp_from_weights(problem)
    rng = random.Random(problem.seed)
    return random_mlp(problem.n_in, problem.hidden, problem.n_out, rng, problem.hidden_act, problem.out_act)
