"""Kernel implementations: soft-rudder threads and bundle coupling.

This module implements:
  * single-thread soft-rudder updates with slip law q(W_coh),
  * bundle-level coupling modes: independent, shared_bias, strong_lock (test).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple
import numpy as np

from .config_schemas import KernelConfig, BundleCouplingConfig


@dataclass
class BundleState:
    """State of a bundle at a given step.

    Attributes
    ----------
    x : np.ndarray
        Positions of threads, shape (N,).
    v : np.ndarray
        Direction states of threads, each in {+1, -1}, shape (N,).
    """
    x: np.ndarray
    v: np.ndarray


def slip_probability(W_coh: float, kernel_cfg: KernelConfig) -> float:
    """Return slip probability q(W_coh) for the given kernel config.

    Currently only supports a simple power-law slip law:
        q(W) = k / W^alpha
    with a natural default alpha=1, k=2.
    """
    slip = kernel_cfg.slip_law
    if slip.form != "power_law":
        raise ValueError(f"Unsupported slip law form: {slip.form!r}")

    if W_coh <= 0:
        raise ValueError("W_coh must be positive")

    q = slip.k_prefactor / (W_coh ** slip.alpha)
    # Clip to [0, 1] for safety
    return float(np.clip(q, 0.0, 1.0))


def effective_stay_probability(
    W_coh: float,
    state: BundleState,
    kernel_cfg: KernelConfig,
    coupling_cfg: BundleCouplingConfig,
) -> np.ndarray:
    """Compute effective stay probabilities for each thread.

    Parameters
    ----------
    W_coh : float
        Coherence horizon for this run.
    state : BundleState
        Current bundle state (positions and directions).
    kernel_cfg : KernelConfig
        Kernel parameters, including base slip law.
    coupling_cfg : BundleCouplingConfig
        Bundle coupling parameters (mode, coupling_strength).

    Returns
    -------
    p_stay_eff : np.ndarray
        Effective stay probabilities per thread, shape (N,).
    """
    N = state.v.size
    q_base = slip_probability(W_coh, kernel_cfg)
    p_stay_base = 1.0 - q_base

    mode = coupling_cfg.mode
    lam = coupling_cfg.coupling_strength

    if mode == "independent" or N == 1:
        return np.full(N, p_stay_base, dtype=float)

    # Direction alignment indicator S_v
    S_v = float(abs(state.v.mean()))  # in [0, 1]

    if mode == "shared_bias":
        # Phenomenological interpolation: alignment increases stay probability.
        p_eff = p_stay_base + lam * S_v * (1.0 - p_stay_base)
        return np.full(N, float(np.clip(p_eff, 0.0, 1.0)), dtype=float)

    if mode == "strong_lock":
        # Extreme stabilisation test: more aggressive enhancement.
        # This is not meant as a physical BCQM kernel, only as a limit case.
        p_eff = p_stay_base + lam * (S_v ** 2) * (1.0 - p_stay_base)
        return np.full(N, float(np.clip(p_eff, 0.0, 1.0)), dtype=float)

    raise ValueError(f"Unknown bundle_coupling mode {mode!r}")


def step_soft_rudder_bundle(
    state: BundleState,
    W_coh: float,
    kernel_cfg: KernelConfig,
    coupling_cfg: BundleCouplingConfig,
    rng: np.random.Generator,
) -> Tuple[BundleState, int]:
    """Advance a bundle state by one step.

    Returns the new state and the number of threads that flipped.

    The position increment per step is v (step_size absorbed into units).
    """
    N = state.v.size
    p_stay_eff = effective_stay_probability(W_coh, state, kernel_cfg, coupling_cfg)
    # Draw uniform random numbers to decide flips
    u = rng.random(size=N)
    stay_mask = u < p_stay_eff
    flip_mask = ~stay_mask

    v_new = state.v.copy()
    v_new[flip_mask] *= -1
    x_new = state.x + v_new  # unit step size

    new_state = BundleState(x=x_new, v=v_new)
    n_flips = int(flip_mask.sum())
    return new_state, n_flips
