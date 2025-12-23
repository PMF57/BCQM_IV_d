"""Command-line interface for bcqm_bundles.

Usage examples
--------------
python -m bcqm_bundles.cli run configs/wcoh_bundle_scan.yml
python -m bcqm_bundles.cli analyse outputs_bundles/bundle_soft_rudder_v0
"""

from __future__ import annotations

import argparse
import json
import os
from glob import glob

from .config_schemas import load_config
from .simulate import run_all
from .analysis import analyse_pair


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="bcqm_bundles CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_run = subparsers.add_parser("run", help="run simulations for a config")
    p_run.add_argument("config", help="YAML config file")

    p_an = subparsers.add_parser("analyse", help="analyse an output directory")
    p_an.add_argument("output_dir", help="Output directory created by 'run'")

    args = parser.parse_args(argv)

    if args.command == "run":
        cfg = load_config(args.config)
        run_all(cfg)
    elif args.command == "analyse":
        out_dir = args.output_dir
        summary_path = os.path.join(out_dir, "summary.json")
        all_summaries = {}
        for pair_dir in sorted(glob(os.path.join(out_dir, "W*_N*"))):
            # Parse W and N from directory name W{W}_N{N}
            base = os.path.basename(pair_dir)
            try:
                w_str, n_str = base.split("_")
                W = float(w_str[1:])
                N = int(n_str[1:])
            except Exception:
                continue
            summary = analyse_pair(load_config_from_metadata(out_dir), pair_dir)
            key = f"W{W}_N{N}"
            all_summaries[key] = summary
        with open(summary_path, "w", encoding="utf-8") as fh:
            json.dump(all_summaries, fh, indent=2)
    else:
        parser.error(f"Unknown command {args.command!r}")


def load_config_from_metadata(out_dir: str):
    """Reconstruct a TopLevelConfig from metadata.json.

    For analysis, we need the analysis-related parameters. Rather than
    requiring the original YAML, we read metadata.json written by run_all.
    """
    from .config_schemas import (
        TopLevelConfig,
        EnsembleConfig,
        KernelConfig,
        SlipLawConfig,
        BundleCouplingConfig,
        PhaseDynamicsConfig,
        PhaseDynamicsParams,
        AnalysisConfig,
        PSDConfig,
        AmplitudeFitConfig,
        BetaFitConfig,
        KappaEffConfig,
        LifetimeConfig,
    )
    meta_path = os.path.join(out_dir, "metadata.json")
    with open(meta_path, "r", encoding="utf-8") as fh:
        meta = json.load(fh)

    ensemble = EnsembleConfig(**meta["ensemble"])

    slip = SlipLawConfig(**meta["kernel"]["slip_law"])
    kernel = KernelConfig(
        type=meta["kernel"]["type"],
        step_size=meta["kernel"]["step_size"],
        slip_law=slip,
    )

    bc = BundleCouplingConfig(**meta["bundle_coupling"])

    pd_params = PhaseDynamicsParams(**meta["phase_dynamics"]["params"])
    phase_dyn = PhaseDynamicsConfig(
        enabled=meta["phase_dynamics"]["enabled"],
        law=meta["phase_dynamics"]["law"],
        params=pd_params,
    )

    psd = PSDConfig(**meta["analysis"]["psd"])
    amp = AmplitudeFitConfig(**meta["analysis"]["amplitude_fit"])
    beta = BetaFitConfig(**meta["analysis"]["beta_fit"])
    kappa = KappaEffConfig(**meta["analysis"]["kappa_eff"])
    life = LifetimeConfig(**meta["analysis"]["lifetime"])
    analysis = AnalysisConfig(
        psd=psd, amplitude_fit=amp, beta_fit=beta, kappa_eff=kappa, lifetime=life
    )

    cfg = TopLevelConfig(
        model_name=meta["model_name"],
        output_dir=meta["output_dir"],
        random_seed=meta["random_seed"],
        wcoh_grid=meta["wcoh_grid"],
        bundle_sizes=meta["bundle_sizes"],
        ensemble=ensemble,
        kernel=kernel,
        bundle_coupling=bc,
        phase_dynamics=phase_dyn,
        analysis=analysis,
    )
    return cfg


if __name__ == "__main__":  # pragma: no cover
    main()
