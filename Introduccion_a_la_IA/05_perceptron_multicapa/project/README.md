# Multilayer Perceptron

A **one-hidden-layer MLP** you can read line by line (no NumPy): forward
pass, MSE, backprop, SGD. The default task is **XOR**, the lecture example
a single perceptron cannot learn.

## Setup

```bash
cd "Perceptrón multicapa/project"
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows (PowerShell):

```powershell
cd "Perceptrón multicapa/project"
python3 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Later sessions: activate the venv again, then run the programs.
Deactivate with `deactivate`.

## Programs

| File | Role |
|---|---|
| `01_show_problem.py` | Data, architecture, η, epochs |
| `02_forward.py` | One forward pass: \(z\), \(h\), \(\hat y\) |
| `03_train.py` | SGD + backprop; loss and accuracy |
| `04_compare.py` | Perceptron vs MLP on the same table |

```bash
python 01_show_problem.py
python 02_forward.py
python 03_train.py
python 04_compare.py
python 03_train.py --problem problems/and.yaml
```

`02_forward.py` defaults to `problems/xor_hand.yaml` (lecture weights).
The others default to `problems/xor.yaml` (weights learned from scratch).

## Edit the problem

Open a file in `problems/` (or copy it):

```yaml
name: XOR
hidden: 2
hidden_act: sigmoid    # sigmoid | tanh | relu | step
out_act: sigmoid
epochs: 5000
learning_rate: 0.7
seed: 2

examples:
  - {x: [0, 0], y: [0]}
  - {x: [0, 1], y: [1]}
```

Optional `weights:` (used by program 02) are the lecture threshold net:

```yaml
hidden_act: step
out_act: step
weights:
  W_hidden:
    - [1.0, 1.0]      # h1 ≈ OR
    - [-1.0, -1.0]    # h2 ≈ NAND
  b_hidden: [-0.5, 1.5]
  W_out:
    - [1.0, 1.0]      # ŷ ≈ AND(h1, h2)
  b_out: [-1.5]
```

`step` is for that demo only: its derivative is 0, so do not train it with SGD.

## What to expect

**`xor_hand.yaml`** (program 02) — all four XOR points correct; hidden
units are OR and NAND.

**`xor.yaml`** (program 03) — loss falls; accuracy reaches **100%**.

**`04_compare.py`** on XOR — the perceptron misses at least one point;
the MLP gets all four.

**`and.yaml` / `or.yaml`** — linearly separable; even a perceptron can
learn them (`python 04_compare.py --problem problems/and.yaml`).
