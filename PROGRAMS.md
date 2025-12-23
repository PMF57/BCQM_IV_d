# bcqm_bundles programs overview

This document describes the **internal structure** of the `bcqm_bundles` Python
package: which modules exist, what they do, and how they fit together.

The main entry point is the CLI:

```bash
python3 -m bcqm_bundles.cli ...
```

but you can also import the modules directly for ad hoc experiments.

---

## Module map

### `bcqm_bundles.cli`

**Role:** Command-line interface and top-level orchestration.

Main features:

- Parses command-line arguments using `argparse`.
- Loads YAML configs via `config_schemas.load_config`.
- Dispatches to:
  - `simulate.run_all(cfg)` for the `run` command,
  - `analyse.run_analysis(cfg_or_paths)` for the `analyse` command.

Typical entry points:

- `main()` — wired to `python -m bcqm_bundles.cli`.
- `add_run_subparser(subparsers)` — defines options for the `run` command.
- `add_analyse_subparser(subparsers)` — defines options for the `analyse` command.

---

### `bcqm_bundles.config_schemas`

**Role:** Validate and normalise YAML configuration files.

Key responsibilities:

- Define the expected structure of config files, e.g.:

  ```yaml
  run_id: run_B2_shared_bias_50
  output_dir: outputs_bundles/run_B2_shared_bias_50
  random_seed: 123456
  n_steps: 2000
  dt: 0.1
  ensemble_size: 256

  W_coh_grid: [5.0, 10.0, 20.0, 40.0, 80.0, 160.0]
  N_grid: [1, 2, 4, 8, 16, 32]

  lambda_shared: 0.5
  persistence_length: 10.0
  ```

- Provide a single function:

  ```python
  cfg = load_config(path: str) -> dict
  ```

  which:
  - reads the YAML file,
  - applies defaults,
  - checks for invalid keys / types,
  - and returns a clean Python dictionary used by `simulate` and `analyse`.

If you add new configuration options (e.g. a new glue parameter), you should:

1. Extend the schema / defaults here.
2. Teach `simulate` and `analyse` how to interpret the new fields.

---

### `bcqm_bundles.simulate`

**Role:** Run the actual event-chain simulations for all `(W_coh, N)` pairs in a run.

Core concepts:

- A **primitive thread** follows the IV_c-style **soft-rudder** dynamics
  (telegraph-like process with W_coh-sensitive slip probabilities).
- A **bundle** is a collection of `N` threads whose directions are coupled by a
  shared-bias parameter `lambda_shared` and possibly a persistence-length scale.
- For each `(W_coh, N)` pair, we run an **ensemble** of independent bundles and
  record the acceleration time series for the bundle COM.

Important functions:

- `run_all(cfg: dict) -> None`  
  Top-level driver used by the CLI `run` command. It:

  - iterates over `W_coh` and `N` grids,
  - calls `run_ensemble_for_pair` for each pair,
  - writes all outputs into `cfg["output_dir"]`,
  - and creates a `metadata.json` summarising the run.

- `run_ensemble_for_pair(cfg, W_coh: float, N: int) -> dict`  
  Runs the acceleration time series for `ensemble_size` bundles at fixed
  `(W_coh, N)`, returning a dictionary of raw arrays which is then written to
  disk:

  - `acc_all[e, t]` — acceleration for ensemble index `e` at time step `t`,
  - optional diagnostics (e.g. alignment, flip counts),
  - and the computed persistence length if enabled.

- Internal helpers:

  - `step_soft_rudder(...)` — update rule for a single thread’s direction and
    position.
  - `apply_shared_bias(...)` — implement the glue rule between threads in a
    bundle (λ, persistence-length, etc.).
  - `compute_com_acceleration(...)` — aggregate thread accelerations into COM
    accelerations.

---

### `bcqm_bundles.analyse`

**Role:** Post-process the simulation outputs and extract quantities used in IV_d.

Typical usage via CLI:

```bash
python3 -m bcqm_bundles.cli analyse outputs_bundles/run_B2_shared_bias_50
```

Key tasks:

- Load `metadata.json` and all per-(W_coh,N) spectra from the output directory.
- For each `(W_coh, N)` pair:
  - compute the acceleration power spectral density (PSD),
  - extract a characteristic amplitude `A(W_coh, N)`,
  - compute alignment and flip-coherence diagnostics if available.
- Fit power-law scalings:
  - `A(W_coh, N) ~ W_coh^{-β_COM(N)}` for each bundle size N,
  - storing the fitted `β_COM(N)` and error bars.
- Write:
  - `amplitude_scaling.csv` — W_coh vs A for each N,
  - `summary.json` — including fitted β values and diagnostics,
  - optionally a `RUN_REPORT_*.md` template summarising the run.

Important functions (names may vary slightly):

- `analyse_run(output_dir: str) -> None`
- `fit_amplitude_scaling(dataframe) -> dict`

---

### `bcqm_bundles.persistence` (if present)

**Role:** Shared utilities for persistence-length calculations.

Typical features:

- Convert flip statistics or autocorrelation functions into a **persistence
  length** (in steps or in units of W_coh).
- Provide helper functions used by both `simulate` (to track persistence
  during the run) and `analyse` (to aggregate and average it).

---

## Helper scripts

### `scripts/plot_b_series_with_persist.py`

**Role:** Generate the IV_d “B-series” figures.

This script:

- reads the `summary.json` and `amplitude_scaling.csv` files from the B-series
  runs (B1/B2/B3),
- produces:
  - amplitude vs W_coh plots,
  - β_COM vs N plots,
  - persistence vs N plots,
- and saves them into a `figures/` folder ready for inclusion in the IV_d paper.

Typical usage, from the repo root:

```bash
python3 scripts/plot_b_series_with_persist.py
```

You may need to adjust hard-coded paths inside the script if your
`outputs_bundles/` layout differs.

---

## Extending the code

If you want to experiment with new glue laws or observables:

1. **Add new config options** in `config_schemas.py`.
2. **Implement the dynamics** in `simulate.py` (e.g. a new `apply_shared_bias`
   variant).
3. **Extend the analysis** in `analyse.py` if you introduce new observables.
4. Optionally add new configs under `configs/` (e.g. `run_C1_new_glue.yml`)
   and new plotting scripts under `scripts/`.

Keep the canonical A/B configs unchanged if you want to preserve the ability to
reproduce the published IV_d results.
