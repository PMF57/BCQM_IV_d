#!/usr/bin/env python3
"""
BCQM IV_d B-series plotting script

Generates BCQM-style figures comparing A2/B1/B2/B3:
 - Fig_B_series_ratio_W100.png   (amplitude suppression vs N at W=100)
 - Fig_B_series_beta_vs_N.png    (beta_COM(N) vs N)
 - Fig_B_series_diagnostics_W100.png (Sv and kappa_eff vs N at W=100)
"""

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


# ---------------------------------------------------------------------
# 1. Config: where the runs live
# ---------------------------------------------------------------------

BASE = Path(__file__).resolve().parent
OUT_BASE = BASE / "outputs_bundles"

RUNS = {
    "A2 λ=0": {
        "label": r"$\lambda = 0$ (independent)",
        "path": OUT_BASE / "run_A2_independent",
        "lambda": 0.0,
    },
    "B1 λ=0.25": {
        "label": r"$\lambda = 0.25$",
        "path": OUT_BASE / "run_B1_shared_bias",
        "lambda": 0.25,
    },
    "B2 λ=0.5": {
        "label": r"$\lambda = 0.5$",
        "path": OUT_BASE / "run_B2_shared_bias_stronger",
        "lambda": 0.5,
    },
    "B3 λ=0.75": {
        "label": r"$\lambda = 0.75$",
        "path": OUT_BASE / "run_B3_shared_bias_75",
        "lambda": 0.75,
    },
}

# Choose which W_coh to slice for the “W=100” plots
W_SLICE = 100.0


# ---------------------------------------------------------------------
# 2. Helpers
# ---------------------------------------------------------------------

def parse_key(key: str):
    """Keys are of the form 'W20.0_N4' etc."""
    W_part, N_part = key.split("_")
    W = float(W_part[1:])
    N = int(N_part[1:])
    return W, N


def load_summary(run_path: Path):
    with open(run_path / "summary.json", "r", encoding="utf-8") as fh:
        return json.load(fh)


def bcqm_style(ax, title: str):
    """Apply BCQM IV-style plot cosmetics."""
    # Do NOT fiddle with global styles.
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, which="major", linestyle="--", linewidth=0.8)
    ax.minorticks_on()
    ax.set_title(title)


# ---------------------------------------------------------------------
# 3. Load all runs
# ---------------------------------------------------------------------

summaries = {}
for name, cfg in RUNS.items():
    summaries[name] = load_summary(cfg["path"])

# Check N and W grids from the first run
first_run = next(iter(summaries.values()))
Ws = sorted({parse_key(k)[0] for k in first_run})
Ns = sorted({parse_key(k)[1] for k in first_run})

print("W grid:", Ws)
print("N grid:", Ns)


# ---------------------------------------------------------------------
# 4. Figure B1: amplitude suppression vs N at W=100
# ---------------------------------------------------------------------

fig1, ax1 = plt.subplots(figsize=(8.5, 5.5))

for name, cfg in RUNS.items():
    summary = summaries[name]

    # Build A_single(W) from N=1
    A_single = {W: summary[f"W{W}_N1"]["A_mean"] for W in Ws}

    ratios = []
    for N in Ns:
        key = f"W{W_SLICE}_N{N}"
        A = summary[key]["A_mean"]
        ref = A_single[W_SLICE] / math.sqrt(N)
        ratios.append(A / ref)

    ax1.plot(
        Ns,
        ratios,
        marker="o",
        label=cfg["label"],
    )

ax1.set_xscale("log", base=2)
ax1.set_xticks(Ns)
ax1.get_xaxis().set_major_formatter(plt.ScalarFormatter())
ax1.get_xaxis().set_minor_formatter(plt.NullFormatter())
ax1.set_xlabel("Bundle size $N$")
ax1.set_ylabel(
    r"$A_{\mathrm{COM}}(W,N) / [A_{\mathrm{single}}(W)/\sqrt{N}]$"
)
bcqm_style(
    ax1,
    r"Fig. B1  COM amplitude suppression vs bundle size ($W_{\mathrm{coh}} = 100$)",
)
ax1.legend(frameon=False)
fig1.tight_layout()
fig1_path = OUT_BASE / "Fig_B_series_ratio_W100.png"
fig1.savefig(fig1_path, dpi=300)
print("Saved", fig1_path)


# ---------------------------------------------------------------------
# 5. Figure B2: beta_COM(N) vs N across runs
# ---------------------------------------------------------------------

fig2, ax2 = plt.subplots(figsize=(8.5, 5.5))

for name, cfg in RUNS.items():
    summary = summaries[name]
    beta_vals = []

    for N in Ns:
        # gather A(W) for this N
        As = np.array([summary[f"W{W}_N{N}"]["A_mean"] for W in Ws])
        logW = np.log10(np.array(Ws))
        logA = np.log10(As)
        m, c = np.polyfit(logW, logA, 1)
        beta = -m
        beta_vals.append(beta)

    ax2.plot(
        Ns,
        beta_vals,
        marker="o",
        label=cfg["label"],
    )

# diffusive ceiling reference line from IV_c
beta_ceiling = 0.5
ax2.axhline(beta_ceiling, linestyle="--", linewidth=0.8)

ax2.set_xscale("log", base=2)
ax2.set_xticks(Ns)
ax2.get_xaxis().set_major_formatter(plt.ScalarFormatter())
ax2.get_xaxis().set_minor_formatter(plt.NullFormatter())
ax2.set_xlabel("Bundle size $N$")
ax2.set_ylabel(r"$\beta_{\mathrm{COM}}(N)$")
bcqm_style(
    ax2,
    r"Fig. B2  Effective exponent $\beta_{\mathrm{COM}}(N)$ vs bundle size",
)
ax2.text(
    Ns[0] * 0.9,
    beta_ceiling + 0.01,
    r"diffusive ceiling ($\beta \approx 1/2$)",
    fontsize=9,
)
ax2.legend(frameon=False)
fig2.tight_layout()
fig2_path = OUT_BASE / "Fig_B_series_beta_vs_N.png"
fig2.savefig(fig2_path, dpi=300)
print("Saved", fig2_path)


# ---------------------------------------------------------------------
# 6. Figure B3: diagnostics (Sv and kappa_eff) at W=100
# ---------------------------------------------------------------------

fig3, (ax3a, ax3b) = plt.subplots(
    1, 2, figsize=(8.5, 5.5), sharex=True
)

for name, cfg in RUNS.items():
    summary = summaries[name]

    Sv_means = []
    kappa_vals = []

    for N in Ns:
        key = f"W{W_SLICE}_N{N}"
        d = summary[key]
        Sv_means.append(d["mean_Sv"])
        kappa_vals.append(d["kappa_eff"])

    ax3a.plot(Ns, Sv_means, marker="o", label=cfg["label"])
    ax3b.plot(Ns, kappa_vals, marker="o", label=cfg["label"])

for ax in (ax3a, ax3b):
    ax.set_xscale("log", base=2)
    ax.set_xticks(Ns)
    ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
    ax.get_xaxis().set_minor_formatter(plt.NullFormatter())
    bcqm_style(ax, "")

ax3a.set_xlabel("Bundle size $N$")
ax3b.set_xlabel("Bundle size $N$")
ax3a.set_ylabel(r"$\langle S_v \rangle$")
ax3b.set_ylabel(r"$\kappa_{\mathrm{eff}}$")
ax3a.set_title(
    r"Fig. B3a  Mean alignment $\langle S_v \rangle$ vs $N$"
    "\n"
    r"($W_{\mathrm{coh}} = 100$)"
)
ax3b.set_title(
    r"Fig. B3b  $\kappa_{\mathrm{eff}}$ vs $N$"
    "\n"
    r"($W_{\mathrm{coh}} = 100$)"
)

ax3a.legend(frameon=False)
# legend only on left to avoid clutter

fig3.tight_layout()
fig3_path = OUT_BASE / "Fig_B_series_diagnostics_W100.png"
fig3.savefig(fig3_path, dpi=300)
print("Saved", fig3_path)
