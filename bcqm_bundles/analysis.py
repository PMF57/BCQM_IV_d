"""Analysis utilities for bcqm_bundles.

Provides:
  * PSD estimation for acceleration time series,
  * extraction of A_COM in a frequency band,
  * flip statistics P(k) and kappa_eff,
  * summary alignment and lifetime statistics.
"""

from __future__ import annotations

import os
from typing import Dict, Tuple

import numpy as np

from .config_schemas import TopLevelConfig


def _hann_window(M: int) -> np.ndarray:
    n = np.arange(M)
    return 0.5 - 0.5 * np.cos(2.0 * np.pi * n / (M - 1))


def welch_psd(x: np.ndarray, fs: float, seg_len: int, overlap: float) -> Tuple[np.ndarray, np.ndarray]:
    """Simple Welch PSD estimator using numpy.fft.

    Parameters
    ----------
    x : np.ndarray
        1D time series.
    fs : float
        Sampling frequency (arbitrary units).
    seg_len : int
        Segment length.
    overlap : float
        Fractional overlap between segments, in [0, 1).

    Returns
    -------
    f : np.ndarray
        Frequencies.
    Pxx : np.ndarray
        One-sided PSD estimate.
    """
    x = np.asarray(x)
    N = x.size
    step = int(seg_len * (1.0 - overlap))
    if step <= 0:
        step = seg_len
    segments = []
    for start in range(0, N - seg_len + 1, step):
        seg = x[start:start+seg_len]
        segments.append(seg)
    if not segments:
        raise ValueError("Time series too short for given seg_len")

    window = _hann_window(seg_len)
    U = (window**2).sum()  # window power
    K = len(segments)
    psd_accum = None

    for seg in segments:
        segw = seg * window
        Xf = np.fft.rfft(segw)
        Pxx_seg = (1.0 / (fs * U)) * (np.abs(Xf) ** 2)
        if psd_accum is None:
            psd_accum = Pxx_seg
        else:
            psd_accum += Pxx_seg

    Pxx = psd_accum / K
    freqs = np.fft.rfftfreq(seg_len, d=1.0 / fs)
    return freqs, Pxx


def amplitude_from_band(freqs: np.ndarray, Pxx: np.ndarray, fmin: float, fmax: float) -> float:
    """Extract a scalar amplitude from a band of the PSD.

    We take the square root of the average power in [fmin, fmax].
    """
    mask = (freqs >= fmin) & (freqs <= fmax)
    if not np.any(mask):
        raise ValueError("No frequencies in requested band")
    band_power = Pxx[mask].mean()
    return float(np.sqrt(band_power))


def analyse_pair(
    cfg: TopLevelConfig,
    pair_dir: str,
) -> Dict[str, float]:
    """Analyse one (W_coh, N) pair directory.

    Expects a 'timeseries.npz' file created by simulate.run_all.
    Returns a small dictionary of summary quantities.
    """
    path = os.path.join(pair_dir, "timeseries.npz")
    data = np.load(path)

    acc = data["acceleration"]  # shape (n_ens, T)
    flips = data["flips"]       # shape (n_ens, steps)
    Sv = data["Sv"]             # shape (n_ens, steps)
    lifetimes = data["lifetimes"]
    survived = data["survived"]

    # PSD + amplitude (averaged over ensemble)
    fs = 1.0  # arbitrary units; only frequency band ratios matter
    seg_len = cfg.analysis.psd.segment_length
    overlap = cfg.analysis.psd.overlap
    fmin = cfg.analysis.amplitude_fit.freq_min
    fmax = cfg.analysis.amplitude_fit.freq_max

    amps = []
    for series in acc:
        freqs, Pxx = welch_psd(series, fs=fs, seg_len=seg_len, overlap=overlap)
        A = amplitude_from_band(freqs, Pxx, fmin=fmin, fmax=fmax)
        amps.append(A)
    A_mean = float(np.mean(amps))
    A_std = float(np.std(amps))

    # Flip statistics P(k) across ensemble and time
    maxN = flips.max() if flips.size > 0 else 0
    counts = np.bincount(flips.ravel(), minlength=maxN+1)
    total_steps = flips.size
    Pk = counts / total_steps if total_steps > 0 else counts.astype(float)

    P0 = float(Pk[0]) if Pk.size > 0 else 0.0
    P1 = float(Pk[1]) if Pk.size > 1 else 0.0

    eps = 1e-12
    if P1 < eps:
        kappa_eff = float("inf")
    else:
        kappa_eff = float(np.log((P0 + eps) / (P1 + eps)))

    # Alignment statistics
    mean_Sv = float(Sv.mean())
    std_Sv = float(Sv.std())

    # Lifetime statistics
    mean_life = float(lifetimes.mean())
    median_life = float(np.median(lifetimes))
    frac_survived = float(survived.mean())

    # Persistence-length statistics (if present)
    L_persist_mean = float("nan")
    L_persist_median = float("nan")
    if "L_persist_mean" in data.files:
        L_vals = data["L_persist_mean"]
        L_persist_mean = float(L_vals.mean())
        L_persist_median = float(np.median(L_vals))

    summary: Dict[str, float] = {
        "A_mean": A_mean,
        "A_std": A_std,
        "P0": P0,
        "P1": P1,
        "kappa_eff": kappa_eff,
        "mean_Sv": mean_Sv,
        "std_Sv": std_Sv,
        "mean_lifetime": mean_life,
        "median_lifetime": median_life,
        "frac_survived": frac_survived,
        "L_persist_mean": L_persist_mean,
        "L_persist_median": L_persist_median,
    }
    return summary
