# k-means

Lloyd’s algorithm you can read line by line (no NumPy, no scikit-learn):
assign each point to the nearest centroid, replace each centroid by the mean.
The default cloud is the lecture example: **6 points, k = 2**, both seeds on
the left blob.

## Setup

```bash
cd "Clustering K-medias/project"
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows (PowerShell):

```powershell
cd "Clustering K-medias/project"
python3 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Later sessions: activate the venv again, then run the programs.
Deactivate with `deactivate`.

## Programs

| File | Role |
|---|---|
| `01_show_data.py` | Unlabeled points, k, init |
| `02_lloyd.py` | Assign / mean, iteration by iteration, inertia J |
| `03_choose_k.py` | Elbow (J vs k) and mean silhouette |
| `04_compare.py` | Scaling, k-means++ vs random, two moons |

```bash
python 01_show_data.py
python 02_lloyd.py
python 03_choose_k.py
python 04_compare.py
python 01_show_data.py --data data/blobs.yaml
python 02_lloyd.py --data data/blobs.yaml
python 03_choose_k.py --data data/six_points.yaml
python 04_compare.py --only scale
python 04_compare.py --only init
python 04_compare.py --only moons
```

## Edit the cloud

Open a file in `data/` (or copy one). Kinds:

**`points`** — list the lecture table yourself:

```yaml
name: Lecture 6 points
k: 2
kind: points
features: [x, y]
init: given          # given | random | k-means++
centroids:
  - [1.0, 1.0]
  - [2.0, 1.0]
points:
  - {id: P1, x: 1.0, y: 1.0}
```

**`blobs`** — Gaussian clouds (`centers`, `cluster_std`, `n_per_cluster`).

**`groups`** — one Gaussian per named feature (age vs income).

**`moons`** — two crescents (`n`, `noise`).

Optional knobs: `n_init`, `max_iter`, `seed`, `k_min` / `k_max` (for program 03).
A `cluster:` field on a point, or the generator’s group id, is **held-out
truth**: k-means does not see it; programs 03–04 use it only to score.

## What to expect

**`data/six_points.yaml`** (program 02) replays the lecture:

- Start: μA = (1, 1), μB = (2, 1) — both on the left cloud
- Iter 1: P2 stays B; update μA = (1.00, 1.50), μB = (6.75, 6.50)
- Iter 2: P2 moves to A; μA ≈ (1.33, 1.33), μB ≈ (8.33, 8.33), J ≈ 2.67
- A bad init was not fatal: the far cloud pulled a centroid

**`data/blobs.yaml`** (program 03) — three clouds. J drops hard until **k = 3**,
then flattens (elbow). Mean silhouette also peaks at **k = 3**.

**`04_compare.py`**

- Scale: without standardization, k-means follows **income**; with a
  StandardScaler (zero mean, unit variance, then inverse the centroids) it
  recovers the two **age** groups at 100%.
- Init: six well-separated clouds, `n_init = 1`. Random J is often ~470
  (a missed cloud); k-means++ is usually ~38. One unlucky ++ seed still
  happens — that is why you keep the best of several `n_init`.
- Moons: each crescent is split (~75% agreement). Voronoi cells are the
  wrong model; then DBSCAN / GMM / agglomerative.

scikit-learn does the same idea with `StandardScaler` + `KMeans` in a
`Pipeline` (see the lecture). This project is the algorithm, not the wrapper.
