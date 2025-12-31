# bcqm_bundles — BCQM IV_d bundle inertial-noise simulations

This repository contains the reference implementation for **Boundary-Condition
Quantum Mechanics IV_d** (“BCQM IV_d”), which studies inertial noise for
**bundles of primitive threads** within the Stage 1 BCQM programme.

BCQM IV_d builds on:

- **BCQM IV_b** — a W_coh-blind control model with β ≈ 0.
- **BCQM IV_c** — a single-thread soft-rudder model with W_coh-sensitive slips
  and a diffusive exponent β ≈ 1/2.

The code here implements the **bundle counterpart** to IV_c:

- multiple soft-rudder threads (“primitive threads”) per bundle,
- optional shared-bias coupling between threads,
- ensemble simulations over W_coh and bundle size N,
- extraction of centre-of-mass (COM) inertial-noise spectra and W_coh-scaling
  exponents β_COM.

The canonical A/B runs documented in the IV_d paper were generated with this
repository.

---

## 1. Repository layout

A typical layout looks like:

```text
bcqm_bundles/
├── bcqm_bundles/
│   ├── __init__.py
│   ├── cli.py
│   ├── simulate.py
│   ├── analyse.py
│   ├── config_schemas.py
│   └── persistence.py          # persistence-length helpers (if present)
├── configs/
│   ├── run_A1_regression.yml
│   ├── run_A2_independent.yml
│   ├── run_B1_shared_bias.yml
│   ├── run_B2_shared_bias_stronger.yml
│   ├── run_B3_shared_bias_75.yml
│   └── wcoh_bundle_scan_example.yml
├── outputs_bundles/
│   └── ...                     # created at runtime; not tracked in Git
├── scripts/
│   └── plot_b_series_with_persist.py
├── RUN_PLAN_IVd.tex            # optional run-plan document
├── README.md                   # this file
├── PROGRAMS.md or bcqm_bundles/README.md
├── pyproject.toml or setup.cfg
└── CITATION.cff
```

You can adapt names/paths to your actual repo structure; the key point is:

- `bcqm_bundles/` — Python package with the simulation and CLI logic.
- `configs/` — YAML configuration files for canonical runs.
- `outputs_bundles/` — auto-generated output directories (each run gets its own
  subfolder).
- `scripts/` — analysis/plotting helpers used for the IV_d figures.

---

## 2. Installation

### Requirements

- Python **3.10+** (earlier 3.9 may work but is not guaranteed).
- Standard scientific stack:
  - `numpy`
  - `scipy`
  - `pandas`
  - `pyyaml`
  - `matplotlib`

### Editable install

From the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate          # on macOS / Linux
# .venv\Scripts\activate         # on Windows

pip install --upgrade pip
pip install -e .
```

This makes `bcqm_bundles` importable and exposes the CLI as:

```bash
python3 -m bcqm_bundles.cli ...
```

---

## 3. Overview of the CLI

The main entry point is:

```bash
python3 -m bcqm_bundles.cli <command> [options]
```

Core commands:

- `run` — run one or more ensembles defined in a YAML config.
- `analyse` — post-process one or more output folders to extract amplitude
  scaling and fitted β exponents.

Use:

```bash
python3 -m bcqm_bundles.cli --help
python3 -m bcqm_bundles.cli run --help
python3 -m bcqm_bundles.cli analyse --help
```

for full option lists.

---

## 4. Canonical BCQM IV_d runs

The IV_d paper focuses on **A-series** and **B-series** runs:

### A-series: single-thread baseline and independent bundles

These reproduce / cross-check the IV_c baseline in the bcqm_bundles
implementation.

1. **Run A1 — single-thread regression**

   Config: `configs/run_A1_regression.yml`  
   Purpose: sanity check that the bcqm_bundles implementation of the soft-rudder
   kernel reproduces the IV_c single-thread scaling.

   ```bash
   python3 -m bcqm_bundles.cli run configs/run_A1_regression.yml
   python3 -m bcqm_bundles.cli analyse outputs_bundles/run_A1_regression
   ```

2. **Run A2 — independent bundles**

   Config: `configs/run_A2_independent.yml`  
   Purpose: bundles with N > 1 and **no inter-thread coupling** (λ = 0). Should
   show COM amplitude suppression ∝ N^{-1/2} with essentially unchanged β.

   ```bash
   python3 -m bcqm_bundles.cli run configs/run_A2_independent.yml
   python3 -m bcqm_bundles.cli analyse outputs_bundles/run_A2_independent
   ```

### B-series: shared-bias bundles

These introduce a **shared-bias coupling λ** between threads in a bundle and
scan N to see how COM noise and β_COM respond.

Example configs (adjust names to match your repo):

- `configs/run_B1_shared_bias.yml`  (λ = 0.25)
- `configs/run_B2_shared_bias_stronger.yml`  (λ = 0.5)
- `configs/run_B3_shared_bias_75.yml`  (λ = 0.75)

Example usage:

```bash
python3 -m bcqm_bundles.cli run configs/run_B1_shared_bias.yml
python3 -m bcqm_bundles.cli analyse outputs_bundles/run_B1_shared_bias

python3 -m bcqm_bundles.cli run configs/run_B2_shared_bias_stronger.yml
python3 -m bcqm_bundles.cli analyse outputs_bundles/run_B2_shared_bias_stronger

python3 -m bcqm_bundles.cli run configs/run_B3_shared_bias_75.yml
python3 -m bcqm_bundles.cli analyse outputs_bundles/run_B3_shared_bias_75
```

Each `run_*` config defines:

- a grid of W_coh values,
- a set of bundle sizes N,
- ensemble size and time-step parameters,
- glue parameters (λ, persistence-length, etc.),
- and the output directory name.

---

## 5. Outputs and analysis

Each run creates a subdirectory under `outputs_bundles/`, e.g.:

```text
outputs_bundles/
└── run_B2_shared_bias_stronger/
    ├── metadata.json
    ├── summary.json
    ├── trajectories_*.npy            # optional, may be omitted for large runs
    └── spectra/
        ├── accel_psd_W050_N04.npy
        ├── ...
        └── amplitude_scaling.csv
```

- `metadata.json` — echo of the configuration plus derived quantities (number of
  steps, etc.).
- `summary.json` — run-level diagnostics (β fits, error bars, persistence
  metrics, etc.).
- `spectra/` and `amplitude_scaling.csv` — inputs to figure-generation scripts.

The `analyse` command reads these and produces the `summary.json` and
`amplitude_scaling.csv` files used in the IV_d figures.

The helper script:

```bash
python3 scripts/plot_b_series_with_persist.py
```

can be used (after the B-series runs are complete) to reproduce the:

- amplitude vs W_coh plots,
- β_COM vs N plots,
- and persistence-vs-N diagnostics shown in the IV_d paper.

---

## 6. Reproducibility and RNG

The configs fix the random seed(s) used for:

- the bundle initial conditions,
- the soft-rudder slip / shared-bias draws.

If you keep the configs unchanged, re-running the commands above should reproduce
the published IV_d numbers (up to floating-point and library-version noise).

---

## 7. Licence and citation

- Licence: see `LICENSE` (fill with your preferred open licence).
- Citation: see `CITATION.cff` for a machine-readable citation that links the
  code to the BCQM IV_d paper and Zenodo record.

If you use this code in your own work, please cite both:

- the BCQM IV_d paper,
- and the bcqm_bundles code DOI (Zenodo archive).
