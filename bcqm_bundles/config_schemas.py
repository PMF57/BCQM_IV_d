"""Configuration loading and basic validation for bcqm_bundles.

We keep this deliberately lightweight: YAML in, nested dict out, with
a small number of helpers to fill defaults and sanity-check fields.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List

try:
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover
    yaml = None

@dataclass
class EnsembleConfig:
    n_ensembles: int = 50
    steps_per_wcoh: int = 1000


@dataclass
class SlipLawConfig:
    form: str = "power_law"
    alpha: float = 1.0
    k_prefactor: float = 2.0


@dataclass
class KernelConfig:
    type: str = "soft_rudder_bundle"
    step_size: float = 1.0
    slip_law: SlipLawConfig = field(default_factory=SlipLawConfig)


@dataclass
class BundleCouplingConfig:
    mode: str = "independent"  # "independent", "shared_bias", "strong_lock"
    coupling_strength: float = 0.0  # lambda in [0,1]


@dataclass
class PhaseDynamicsParams:
    base_rate: float = 1.0
    wcoh_scaling: str = "none"  # "none", "inverse", "sqrt_inverse"
    stability_weight: float = 0.5


@dataclass
class PhaseDynamicsConfig:
    enabled: bool = False
    law: str = "bundle_stability_v0"
    params: PhaseDynamicsParams = field(default_factory=PhaseDynamicsParams)


@dataclass
class PSDConfig:
    window: str = "hann"
    segment_length: int = 4096
    overlap: float = 0.5


@dataclass
class AmplitudeFitConfig:
    freq_min: float = 0.01
    freq_max: float = 0.1


@dataclass
class BetaFitConfig:
    log_wcoh_min: float = 1.0
    log_wcoh_max: float = 2.5


@dataclass
class KappaEffConfig:
    window_size: int = 1


@dataclass
class LifetimeConfig:
    f_min: float = 0.6
    evap_window: int = 20


@dataclass
class AnalysisConfig:
    psd: PSDConfig = field(default_factory=PSDConfig)
    amplitude_fit: AmplitudeFitConfig = field(default_factory=AmplitudeFitConfig)
    beta_fit: BetaFitConfig = field(default_factory=BetaFitConfig)
    kappa_eff: KappaEffConfig = field(default_factory=KappaEffConfig)
    lifetime: LifetimeConfig = field(default_factory=LifetimeConfig)


@dataclass
class TopLevelConfig:
    model_name: str
    output_dir: str
    random_seed: int = 12345
    wcoh_grid: List[float] = field(default_factory=list)
    bundle_sizes: List[int] = field(default_factory=list)
    ensemble: EnsembleConfig = field(default_factory=EnsembleConfig)
    kernel: KernelConfig = field(default_factory=KernelConfig)
    bundle_coupling: BundleCouplingConfig = field(default_factory=BundleCouplingConfig)
    phase_dynamics: PhaseDynamicsConfig = field(default_factory=PhaseDynamicsConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)


def _ensure_list(value: Any) -> list:
    if isinstance(value, list):
        return value
    return [value]


def load_config(path: str) -> TopLevelConfig:
    """Load YAML config from *path* and return a TopLevelConfig.

    This only does light sanity-checking; physics-level consistency
    (e.g. non-empty grids) is checked later in simulate.py.
    """
    if yaml is None:
        raise RuntimeError(
            "PyYAML is required to load configs. Please install 'pyyaml'."
        )

    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    # Basic required fields
    model_name = raw.get("model_name", "bundle_soft_rudder_v0")
    output_dir = raw.get("output_dir", "outputs_bundles/bundle_soft_rudder_v0")
    random_seed = int(raw.get("random_seed", 12345))

    wcoh_grid = _ensure_list(raw.get("wcoh_grid", []))
    bundle_sizes = _ensure_list(raw.get("bundle_sizes", []))

    # Ensemble
    ens_raw = raw.get("ensemble", {}) or {}
    ensemble = EnsembleConfig(
        n_ensembles=int(ens_raw.get("n_ensembles", 50)),
        steps_per_wcoh=int(ens_raw.get("steps_per_wcoh", 1000)),
    )

    # Kernel
    kern_raw = raw.get("kernel", {}) or {}
    slip_raw = kern_raw.get("slip_law", {}) or {}
    slip = SlipLawConfig(
        form=str(slip_raw.get("form", "power_law")),
        alpha=float(slip_raw.get("alpha", 1.0)),
        k_prefactor=float(slip_raw.get("k_prefactor", 2.0)),
    )
    kernel = KernelConfig(
        type=str(kern_raw.get("type", "soft_rudder_bundle")),
        step_size=float(kern_raw.get("step_size", 1.0)),
        slip_law=slip,
    )

    # Bundle coupling
    bc_raw = raw.get("bundle_coupling", {}) or {}
    bundle_coupling = BundleCouplingConfig(
        mode=str(bc_raw.get("mode", "independent")),
        coupling_strength=float(bc_raw.get("coupling_strength", 0.0)),
    )

    # Phase dynamics
    pd_raw = raw.get("phase_dynamics", {}) or {}
    pd_params_raw = pd_raw.get("params", {}) or {}
    pd_params = PhaseDynamicsParams(
        base_rate=float(pd_params_raw.get("base_rate", 1.0)),
        wcoh_scaling=str(pd_params_raw.get("wcoh_scaling", "none")),
        stability_weight=float(pd_params_raw.get("stability_weight", 0.5)),
    )
    phase_dynamics = PhaseDynamicsConfig(
        enabled=bool(pd_raw.get("enabled", False)),
        law=str(pd_raw.get("law", "bundle_stability_v0")),
        params=pd_params,
    )

    # Analysis
    an_raw = raw.get("analysis", {}) or {}

    psd_raw = an_raw.get("psd", {}) or {}
    psd = PSDConfig(
        window=str(psd_raw.get("window", "hann")),
        segment_length=int(psd_raw.get("segment_length", 4096)),
        overlap=float(psd_raw.get("overlap", 0.5)),
    )

    amp_raw = an_raw.get("amplitude_fit", {}) or {}
    amp = AmplitudeFitConfig(
        freq_min=float(amp_raw.get("freq_min", 0.01)),
        freq_max=float(amp_raw.get("freq_max", 0.1)),
    )

    beta_raw = an_raw.get("beta_fit", {}) or {}
    beta = BetaFitConfig(
        log_wcoh_min=float(beta_raw.get("log_wcoh_min", 1.0)),
        log_wcoh_max=float(beta_raw.get("log_wcoh_max", 2.5)),
    )

    kappa_raw = an_raw.get("kappa_eff", {}) or {}
    kappa = KappaEffConfig(
        window_size=int(kappa_raw.get("window_size", 1)),
    )

    life_raw = an_raw.get("lifetime", {}) or {}
    life = LifetimeConfig(
        f_min=float(life_raw.get("f_min", 0.6)),
        evap_window=int(life_raw.get("evap_window", 20)),
    )

    analysis = AnalysisConfig(
        psd=psd, amplitude_fit=amp, beta_fit=beta, kappa_eff=kappa, lifetime=life
    )

    cfg = TopLevelConfig(
        model_name=model_name,
        output_dir=output_dir,
        random_seed=random_seed,
        wcoh_grid=[float(x) for x in wcoh_grid],
        bundle_sizes=[int(n) for n in bundle_sizes],
        ensemble=ensemble,
        kernel=kernel,
        bundle_coupling=bundle_coupling,
        phase_dynamics=phase_dynamics,
        analysis=analysis,
    )

    return cfg
