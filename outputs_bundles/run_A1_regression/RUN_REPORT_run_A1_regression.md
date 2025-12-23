# BCQM IV_d Run Report

## 1. Run identification

- **Project:** BCQM IV_d – bundle / COM inertial noise
- **Run label:** `run_A1_regression`
- **Output directory:** `outputs_bundles/run_A1_regression`
- **Config file used:** `configs/run_A1_regression.yml`
- **Date run:** (fill in)
- **Code version:**
  - `bcqm_bundles` version: v0.3
  - git commit: (fill in, if applicable)
- **Machine / environment (optional):**
  - Python: (e.g. `python3 --version`)
  - OS: (e.g. macOS)

---

## 2. Purpose of this run

Run A1: single-thread regression to BCQM IV_c.
- Confirm that N = 1 in the bundle code reproduces the soft-rudder behaviour.
- Check that COM acceleration noise amplitude A(W_coh) decreases with W_coh
  in a way consistent with the IV_c diffusive baseline.

---

## 3. Key configuration parameters

- **W_coh grid:** [10.0, 20.0, 50.0, 100.0]
- **Bundle sizes N:** [1]
- **Ensemble:**
  - n_ensembles = 50
  - steps_per_wcoh = 1000
- **Kernel:**
  - type: soft_rudder_bundle
  - step_size: 1.0
  - slip law: form = power_law, alpha = 1.0, k_prefactor = 2.0  # q(W) = k / W^alpha
- **Bundle coupling:**
  - mode: independent
  - coupling_strength = 0.0
- **Phase dynamics:**
  - enabled: False
  - law: bundle_stability_v0
  - params: {'base_rate': 1.0, 'wcoh_scaling': 'none', 'stability_weight': 0.5}
- **Analysis:**
  - PSD: window = hann, segment_length = 512, overlap = 0.5
  - Amplitude band: freq_min = 0.01, freq_max = 0.1
  - Lifetime thresholds: f_min = 0.6, evap_window = 20

---

## 4. Run status

- [x] Run completed without errors
- [ ] Warnings / anomalies

**Notes on the run:**

> First proper A1 regression run with N = 1 only. All files generated as expected.


---

## 5. Summary of `summary.json` results

### 5.1 COM amplitude and W_coh scaling (N = 1)

- W = 10: A_mean ≈ 0.5727, A_std ≈ 0.0095
- W = 20: A_mean ≈ 0.5291, A_std ≈ 0.0073
- W = 50: A_mean ≈ 0.3846, A_std ≈ 0.0045
- W = 100: A_mean ≈ 0.2811, A_std ≈ 0.0039

Over the range W = 10–100, A_mean decreases monotonically with W_coh, 
consistent with a diffusive-like suppression of single-thread inertial noise.

> Rough log–log fit over these four points gives an effective β ≈ 0.31. This is in the expected diffusive range, though a more careful β-fit (using the IV_c pipeline and broader W_coh range) will be needed for publication-quality numbers.

**Interpretation / comments:**

> Single-thread soft-rudder behaviour in bcqm_bundles looks reasonable: larger W_coh → smaller A(W_coh). The precise exponent β is not yet tuned, but the trend is qualitatively aligned with the IV_c diffusive picture.


---

### 5.2 Flip statistics and κ_eff (N = 1)

- W = 10: P0 ≈ 0.799, P1 ≈ 0.201, κ_eff ≈ 1.381
- W = 20: P0 ≈ 0.900, P1 ≈ 0.100, κ_eff ≈ 2.198
- W = 50: P0 ≈ 0.960, P1 ≈ 0.040, κ_eff ≈ 3.181
- W = 100: P0 ≈ 0.980, P1 ≈ 0.020, κ_eff ≈ 3.890

**Interpretation / comments:**

> As W_coh increases, the slip probability q(W) = 2/W decreases, so the process spends more time in 'no-flip' steps. This appears as increasing P0 and κ_eff with W_coh, as expected from the telegraph-process intuition.


---

### 5.3 Alignment and lifetime (N = 1)

- W = 10: mean_Sv = 1.000, std_Sv = 0.000, mean_lifetime = 10000 steps, frac_survived = 1.0
- W = 20: mean_Sv = 1.000, std_Sv = 0.000, mean_lifetime = 20000 steps, frac_survived = 1.0
- W = 50: mean_Sv = 1.000, std_Sv = 0.000, mean_lifetime = 50000 steps, frac_survived = 1.0
- W = 100: mean_Sv = 1.000, std_Sv = 0.000, mean_lifetime = 100000 steps, frac_survived = 1.0

**Interpretation / comments:**

> For N = 1, the alignment indicator Sv is identically 1 and the evaporation criterion never triggers, so lifetimes are equal to the total run length and frac_survived = 1. This confirms that the lifetime machinery behaves sensibly in the trivial single-thread case.


---

## 6. Plots / figures generated (if any)

- For this run, no figures were saved; inspection was done via `summary.json`. Future IV_d figures will use similar runs but with more W_coh values and, for bundles, more N values.


---

## 7. Issues, anomalies, or TODOs

- [ ] Optionally increase W_coh grid and/or adjust the amplitude-fit band
      to get a cleaner estimate of β for N = 1.

- [ ] Once A2 (independent bundles) is run, compare A(W_coh, N=1) here directly with the N=1 slice of A2 as a cross-check.


---

## 8. Conclusions from this run

> Run A1 confirms that the N = 1 soft-rudder implementation in bcqm_bundles produces sensible single-thread inertial-noise behaviour: A(W_coh) decreases with W_coh, κ_eff increases with W_coh as slips become rarer, and the lifetime and alignment diagnostics behave trivially but correctly. This provides the single-thread baseline needed before exploring bundles (N > 1) in Runs A2 and B1.
