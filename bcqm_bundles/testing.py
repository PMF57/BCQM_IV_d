"""Lightweight sanity checks for bcqm_bundles.

These are not full unit tests, but quick numerical checks that can be
run by hand to see if the implementation is broadly sane.
"""

from __future__ import annotations

import os
import tempfile

import numpy as np

from .config_schemas import TopLevelConfig, EnsembleConfig, KernelConfig, SlipLawConfig, BundleCouplingConfig, PhaseDynamicsConfig, PhaseDynamicsParams, AnalysisConfig
from .simulate import run_all
from .analysis import analyse_pair


def quick_independent_check() -> None:
    """Run a tiny independent-mode check (N=1,2) in a temp directory."""
    tmpdir = tempfile.mkdtemp(prefix="bcqm_bundles_test_")
    cfg = TopLevelConfig(
        model_name="test_independent",
        output_dir=os.path.join(tmpdir, "outputs"),
        random_seed=123,
        wcoh_grid=[10.0, 20.0],
        bundle_sizes=[1, 2],
        ensemble=EnsembleConfig(n_ensembles=5, steps_per_wcoh=100),
        kernel=KernelConfig(step_size=1.0, slip_law=SlipLawConfig(form="power_law", alpha=1.0, k_prefactor=2.0), type="soft_rudder_bundle"),
        bundle_coupling=BundleCouplingConfig(mode="independent", coupling_strength=0.0),
        phase_dynamics=PhaseDynamicsConfig(enabled=False, law="bundle_stability_v0", params=PhaseDynamicsParams()),
        analysis=AnalysisConfig(),
    )
    run_all(cfg)
    for W in cfg.wcoh_grid:
        for N in cfg.bundle_sizes:
            pair_dir = os.path.join(cfg.output_dir, f"W{int(W)}_N{N}")
            summary = analyse_pair(cfg, pair_dir)
            print(f"W={W}, N={N}, A_mean={summary['A_mean']:.3g}, kappa_eff={summary['kappa_eff']:.3g}")
