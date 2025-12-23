"""Phase dynamics for bundles (optional, ħ-emergent).

All laws here must be dimensionless and may only depend on:
  * W_coh,
  * bundle size N,
  * alignment indicators,
  * a small set of dimensionless parameters.

No hbar, physical energies, or exp(-i E dt / hbar) are allowed here.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .config_schemas import PhaseDynamicsConfig
from .kernels import BundleState


@dataclass
class PhaseState:
    """Phase state for a bundle.

    theta has shape (N,) with values in [0, 2π).
    """
    theta: np.ndarray


def bundle_alignment_v(state: BundleState) -> float:
    """Return direction alignment S_v in [0, 1]."""
    return float(abs(state.v.mean()))


def update_phases(
    phase_state: PhaseState,
    bundle_state: BundleState,
    W_coh: float,
    cfg: PhaseDynamicsConfig,
) -> PhaseState:
    """Update phases for one step according to the chosen law.

    If cfg.enabled is False, phases are left unchanged.
    """
    theta = phase_state.theta
    if not cfg.enabled:
        return phase_state

    law = cfg.law
    params = cfg.params
    S_v = bundle_alignment_v(bundle_state)

    if law == "bundle_stability_v0":
        # Simple example: Δθ = ω0 * f_W(W_coh) * (1 + λ_stab S_v)
        if params.wcoh_scaling == "none":
            f_W = 1.0
        elif params.wcoh_scaling == "inverse":
            f_W = 1.0 / W_coh
        elif params.wcoh_scaling == "sqrt_inverse":
            f_W = 1.0 / (W_coh ** 0.5)
        else:
            raise ValueError(f"Unknown wcoh_scaling {params.wcoh_scaling!r}")

        delta_theta = params.base_rate * f_W * (1.0 + params.stability_weight * S_v)
        theta_new = (theta + delta_theta) % (2.0 * np.pi)
        return PhaseState(theta=theta_new)

    raise ValueError(f"Unknown phase dynamics law {law!r}")
