"""Pretty-print points, Lloyd steps, elbow tables."""

from __future__ import annotations

from kmeans.dataset import Dataset
from kmeans.lloyd import KMeansResult, Step, sqdist


def cluster_name(j: int) -> str:
    return chr(ord("A") + j) if j < 26 else str(j)


def fmt_vec(xs: list[float] | tuple[float, ...], digits: int = 2) -> str:
    return "(" + ", ".join(f"{v:.{digits}f}" for v in xs) + ")"


def format_dataset(data: Dataset, max_rows: int = 12) -> str:
    sample_ids = list(data.ids)
    sample_X = list(data.X)
    omitted = 0
    if data.n > max_rows:
        sample_ids = list(data.ids[:8]) + list(data.ids[-2:])
        sample_X = list(data.X[:8]) + list(data.X[-2:])
        omitted = data.n - 10
    id_w = max(2, *(len(i) for i in sample_ids))
    feat_ws = []
    for d, name in enumerate(data.features):
        texts = [f"{x[d]:g}" for x in sample_X]
        feat_ws.append(max(len(name), *(len(t) for t in texts)))
    header = f"{'id':<{id_w}}  " + "  ".join(f"{n:<{w}}" for n, w in zip(data.features, feat_ws))
    lines = [data.name, "", header, "-" * len(header)]
    for i, (pid, x) in enumerate(zip(sample_ids, sample_X)):
        if omitted and i == 8:
            lines.append(f"... ({omitted} more points)")
        parts = [f"{x[d]:<{w}g}" for d, w in enumerate(feat_ws)]
        lines.append(f"{pid:<{id_w}}  " + "  ".join(parts))
    lines.append("")
    lines.append(f"n = {data.n}    dim = {data.dim}    k = {data.k}")
    lines.append(f"init = {data.init}    n_init = {data.n_init}    max_iter = {data.max_iter}    seed = {data.seed}")
    if data.centroids:
        mus = ", ".join(f"{cluster_name(j)} {fmt_vec(c)}" for j, c in enumerate(data.centroids))
        lines.append("given centroids: " + mus)
    if data.truth is not None:
        counts: dict[int, int] = {}
        for t in data.truth:
            counts[t] = counts.get(t, 0) + 1
        bits = ", ".join(f"{n} in group {g}" for g, n in sorted(counts.items()))
        lines.append(f"held-out truth (not given to k-means): {bits}")
    return "\n".join(lines)


def format_step(data: Dataset, step: Step, prev: Step | None) -> str:
    names = [cluster_name(j) for j in range(len(step.centroids))]
    used = "  ".join(f"μ{n} = {fmt_vec(c, 2)}" for n, c in zip(names, step.centroids))
    after = "  ".join(f"μ{n} = {fmt_vec(c, 2)}" for n, c in zip(names, step.updated))
    lines = [
        f"Iteration {step.t}",
        "-" * 72,
        "assign with  " + used,
    ]
    if step.t == 1:
        lines.append("Assignments from these centroids:")
    elif prev is not None:
        lines.append(f"{step.n_changed} point(s) changed cluster.")
    if data.n <= 12:
        lines.append("")
        col_w = max(4, *(len(i) for i in data.ids))
        header = f"{'id':<{col_w}}  {tuple_header(data.features):<16}  cluster"
        for n in names:
            header += f"  d²{n:>2}"
        lines.append(header)
        prev_labels = prev.labels if prev is not None else None
        for i, (pid, x, lab) in enumerate(zip(data.ids, data.X, step.labels)):
            mark = ""
            if prev_labels is not None and prev_labels[i] != lab:
                mark = f"  ← was {cluster_name(prev_labels[i])}"
            dists = "".join(f"  {sqdist(x, c):6.2f}" for c in step.centroids)
            lines.append(
                f"{pid:<{col_w}}  {fmt_vec(x, 0):<16}  {cluster_name(lab):^7}{dists}{mark}"
            )
    else:
        sizes = [step.labels.count(j) for j in range(len(step.centroids))]
        bits = ", ".join(f"{cluster_name(j)}: {n}" for j, n in enumerate(sizes))
        lines.append("cluster sizes: " + bits)
    lines.append("")
    lines.append("update     " + after)
    lines.append(f"J = {step.inertia:.4f}   (after the mean step; never increases)")
    return "\n".join(lines)


def tuple_header(features: tuple[str, ...]) -> str:
    return "(" + ", ".join(features) + ")"


def format_result(data: Dataset, result: KMeansResult) -> str:
    lines = [
        f"Converged in {result.n_iter} iteration(s)    J = {result.inertia:.4f}",
        "centroids: "
        + "  ".join(f"μ{cluster_name(j)} = {fmt_vec(c, 2)}" for j, c in enumerate(result.centroids)),
    ]
    return "\n".join(lines)


def sparkline(values: list[float]) -> str:
    if not values:
        return ""
    lo, hi = min(values), max(values)
    span = hi - lo if hi > lo else 1.0
    blocks = "▁▂▃▄▅▆▇█"
    chars = []
    for v in values:
        idx = int(round((v - lo) / span * (len(blocks) - 1)))
        idx = max(0, min(len(blocks) - 1, idx))
        chars.append(blocks[idx])
    return "".join(chars)


def format_choose_k(
    ks: list[int],
    inertias: list[float],
    sils: list[float | None],
    true_k: int | None,
) -> str:
    drops = [None]
    for i in range(1, len(inertias)):
        drops.append(inertias[i - 1] - inertias[i])
    # Heuristic elbow: last k where the drop is still large vs the next one.
    elbow = ks[0]
    if len(drops) >= 3:
        ratios = []
        for i in range(1, len(drops) - 1):
            nxt = drops[i + 1] if drops[i + 1] else 0.0
            ratios.append((drops[i] / nxt if nxt > 1e-12 else drops[i], i))
        elbow = ks[max(ratios, key=lambda t: t[0])[1]]
    sil_pairs = [(s, k) for k, s in zip(ks, sils) if s is not None]
    best_sil_k = max(sil_pairs, key=lambda t: t[0])[1] if sil_pairs else None

    lines = [
        f"{'k':>4}  {'J':>12}  {'ΔJ':>12}  {'silhouette':>12}  J",
        "-" * 72,
    ]
    bar_w = 18
    jmax = max(inertias) if inertias else 1.0
    for k, j, drop, sil in zip(ks, inertias, drops, sils):
        bar_n = max(1, int(round(j / jmax * bar_w))) if jmax else 1
        bar = "█" * bar_n
        drop_s = "           —" if drop is None else f"{drop:12.2f}"
        sil_s = "           —" if sil is None else f"{sil:12.3f}"
        marks = []
        if k == elbow:
            marks.append("codo")
        if best_sil_k is not None and k == best_sil_k:
            marks.append("max sil")
        if true_k is not None and k == true_k:
            marks.append("truth")
        tag = ("  ← " + ", ".join(marks)) if marks else ""
        lines.append(f"{k:4d}  {j:12.2f}  {drop_s}  {sil_s}  {bar}{tag}")
    lines.append("")
    lines.append(f"J sparkline (k = {ks[0]}…{ks[-1]}): {sparkline(inertias)}")
    extra = f"This file's k field is {true_k}." if true_k else ""
    lines.append(
        f"Codo (largest ΔJ relative to the next drop): k = {elbow}.  "
        + (f"Silhouette max: k = {best_sil_k}.  " if best_sil_k else "")
        + extra
    )
    return "\n".join(lines)
