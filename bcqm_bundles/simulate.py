"""Simulation driver for bcqm_bundles.

This module implements the core loop:
  - for each (W_coh, N) pair,
  - run an ensemble of bundles for M steps,
  - record COM acceleration, flip statistics, alignment indicators, lifetimes.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from typing import Dict, Tuple

import numpy as np


def _compute_persistence_lengths(dir_sign: np.ndarray) -> tuple[float, float]:
    """Compute mean and median run lengths of COM direction sign.

    Parameters
    ----------
    dir_sign : np.ndarray
        1D array of integers in {-1, 0, +1} giving the COM direction per hop.
        Zeros are treated as breaks (they terminate any ongoing run but do not
        start a new one).

    Returns
    -------
    (mean_run, median_run) : tuple of floats
        Mean and median run length in hops. Returns (0.0, 0.0) if there are
        no non-zero runs.
    """
    runs = []
    current = 0
    length = 0
    for s in dir_sign:
        if s == 0:
            if length > 0:
                runs.append(length)
                length = 0
                current = 0
            continue
        if s == current:
            length += 1
        else:
            if length > 0:
                runs.append(length)
            current = int(s)
            length = 1
    if length > 0:
        runs.append(length)
    if not runs:
        return 0.0, 0.0
    arr = np.asarray(runs, dtype=float)
    mean_run = float(arr.mean())
    median_run = float(np.median(arr))
    return mean_run, median_run


from .config_schemas import TopLevelConfig
from .kernels import BundleState, step_soft_rudder_bundle, slip_probability, BundleCouplingConfig, KernelConfig
from .phase_dynamics import PhaseState, update_phases


def _init_rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def _init_bundle_state(N: int, rng: np.random.Generator) -> BundleState:
    # Start with all threads at x=0, random directions ±1
    v0 = rng.choice([-1, 1], size=N)
    x0 = np.zeros(N, dtype=float)
    return BundleState(x=x0, v=v0)


def _init_phase_state(N: int, rng: np.random.Generator) -> PhaseState:
    theta0 = rng.uniform(0.0, 2.0 * np.pi, size=N)
    return PhaseState(theta=theta0)


def run_ensemble_for_pair(
    cfg: TopLevelConfig,
    W_coh: float,
    N: int,
    seed_offset: int = 0,
) -> Dict[str, np.ndarray]:
    """Run an ensemble for a single (W_coh, N) pair.

    Returns a dictionary of time series and per-step statistics.
    """
    rng = _init_rng(cfg.random_seed + seed_offset + int(W_coh) + N)

    n_ens = cfg.ensemble.n_ensembles
    steps = int(cfg.ensemble.steps_per_wcoh * W_coh)

    # Pre-allocate arrays for aggregated statistics
    # We'll keep acceleration per ensemble, then average in analysis.
    acc_all = np.zeros((n_ens, steps - 1), dtype=float)
    flips_all = np.zeros((n_ens, steps), dtype=int)
    Sv_all = np.zeros((n_ens, steps), dtype=float)

    if cfg.phase_dynamics.enabled:
        Stheta_all = np.zeros((n_ens, steps), dtype=float)
    else:
        Stheta_all = None

    lifetimes = np.zeros(n_ens, dtype=int)
    survived = np.zeros(n_ens, dtype=bool)

    # Persistence-length statistics (per-ensemble)
    # L_persist_* are in hop units (number of steps with approximately
    # constant COM direction).
    L_persist_mean_all = np.zeros(n_ens, dtype=float)
    L_persist_median_all = np.zeros(n_ens, dtype=float)

    # Lifetime parameters
    f_min = cfg.analysis.lifetime.f_min
    evap_window = cfg.analysis.lifetime.evap_window

    for e in range(n_ens):
        state = _init_bundle_state(N, rng)
        phase_state = _init_phase_state(N, rng)

        X = np.zeros(steps, dtype=float)
        V = np.zeros(steps, dtype=float)
        Sv = np.zeros(steps, dtype=float)
        Sth = np.zeros(steps, dtype=float) if cfg.phase_dynamics.enabled else None
        flips = np.zeros(steps, dtype=int)
        # COM direction sign per step: -1, 0, or +1
        dir_sign = np.zeros(steps, dtype=int)

        evaporated_step = None

        for t in range(steps):
            # Record COM position & alignment before step
            X[t] = state.x.mean()
            mean_v = state.v.mean()
            Sv[t] = abs(mean_v)
            # Direction sign: -1 for predominantly negative, +1 for positive, 0 if exactly balanced
            if mean_v > 0:
                dir_sign[t] = 1
            elif mean_v < 0:
                dir_sign[t] = -1
            else:
                dir_sign[t] = 0
            if cfg.phase_dynamics.enabled:
                # Phase alignment indicator
                Sth[t] = abs(np.exp(1j * phase_state.theta).mean())

            # Advance one step
            state, n_flips = step_soft_rudder_bundle(
                state,
                W_coh=W_coh,
                kernel_cfg=cfg.kernel,
                coupling_cfg=cfg.bundle_coupling,
                rng=rng,
            )
            flips[t] = n_flips

            # Update phases
            phase_state = update_phases(
                phase_state,
                bundle_state=state,
                W_coh=W_coh,
                cfg=cfg.phase_dynamics,
            )

        # Derive velocities and accelerations for this ensemble member
        V[:-1] = np.diff(X)
        a = np.diff(V)  # length steps-2
        acc_all[e, :] = a
        flips_all[e, :] = flips
        Sv_all[e, :] = Sv
        if cfg.phase_dynamics.enabled:
            Stheta_all[e, :] = Sth

        # Persistence length statistics for this ensemble member
        L_mean, L_median = _compute_persistence_lengths(dir_sign)
        L_persist_mean_all[e] = L_mean
        L_persist_median_all[e] = L_median

        # Lifetime / evaporation
        # Define "aligned" as Sv >= f_min; evaporated when Sv < f_min for
        # evap_window consecutive steps.
        below = Sv < f_min
        run_length = 0
        ev_step = None
        for t in range(steps):
            if below[t]:
                run_length += 1
                if run_length >= evap_window:
                    ev_step = t
                    break
            else:
                run_length = 0
        if ev_step is None:
            lifetimes[e] = steps
            survived[e] = True
        else:
            lifetimes[e] = ev_step
            survived[e] = False

    result: Dict[str, np.ndarray] = {
        "acceleration": acc_all,
        "flips": flips_all,
        "Sv": Sv_all,
        "lifetimes": lifetimes,
        "survived": survived,
        "L_persist_mean": L_persist_mean_all,
        "L_persist_median": L_persist_median_all,
    }
    if cfg.phase_dynamics.enabled and Stheta_all is not None:
        result["Stheta"] = Stheta_all
    return result


def write_metadata(cfg: TopLevelConfig, out_dir: str) -> None:
    """Write a simple metadata.json file with config and basic info.

    We do not attempt to query git here; a commit hash can be added manually
    or by a wrapper script if needed.
    """
    meta = {
        "model_name": cfg.model_name,
        "output_dir": cfg.output_dir,
        "random_seed": cfg.random_seed,
        "wcoh_grid": cfg.wcoh_grid,
        "bundle_sizes": cfg.bundle_sizes,
        "ensemble": asdict(cfg.ensemble),
        "kernel": asdict(cfg.kernel),
        "bundle_coupling": asdict(cfg.bundle_coupling),
        "phase_dynamics": {
            "enabled": cfg.phase_dynamics.enabled,
            "law": cfg.phase_dynamics.law,
            "params": asdict(cfg.phase_dynamics.params),
        },
        "analysis": {
            "psd": asdict(cfg.analysis.psd),
            "amplitude_fit": asdict(cfg.analysis.amplitude_fit),
            "beta_fit": asdict(cfg.analysis.beta_fit),
            "kappa_eff": asdict(cfg.analysis.kappa_eff),
            "lifetime": asdict(cfg.analysis.lifetime),
        },
    }
    os.makedirs(out_dir, exist_ok=True)
    meta_path = os.path.join(out_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)


def run_all(cfg: TopLevelConfig) -> None:
    """Run simulations for all (W_coh, N) pairs in cfg.

    Saves one NumPy .npz file per pair, plus a metadata.json in the
    top-level output directory.
    """
    out_dir = cfg.output_dir
    os.makedirs(out_dir, exist_ok=True)
    write_metadata(cfg, out_dir)

    for W_coh in cfg.wcoh_grid:
        for N in cfg.bundle_sizes:
            pair_dir = os.path.join(out_dir, f"W{int(W_coh)}_N{N}")
            os.makedirs(pair_dir, exist_ok=True)
            data = run_ensemble_for_pair(cfg, W_coh=W_coh, N=N)
            out_path = os.path.join(pair_dir, "timeseries.npz")
            np.savez_compressed(out_path, **data)
