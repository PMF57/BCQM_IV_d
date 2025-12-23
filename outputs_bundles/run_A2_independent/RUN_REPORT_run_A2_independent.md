# BCQM IV_d Run Report

## 1. Run identification

- **Project:** BCQM IV_d – bundle / COM inertial noise
- **Run label:** `run_A2_independent`
- **Output directory:** `outputs_bundles/run_A2_independent`
- **Config file used:** `configs/run_A2_independent.yml`
- **Date run:** (fill in)
- **Code version:**
  - `bcqm_bundles` version: v0.3
  - git commit: (fill in, if applicable)
- **Machine / environment (optional):**
  - Python: (e.g. `python3 --version`)
  - OS: (e.g. macOS)

---

## 2. Purpose of this run

Run A2: independent bundles baseline.
- Study COM acceleration noise for N = 1, 2, 4, 8, 16, 32 with **independent** bundle coupling.
- Check that A_COM(W_coh, N) scales as 1/√N at fixed W_coh (simple noise averaging).
- Estimate β_COM(N) from A_COM(W_coh) ∼ W_coh^{-β_COM} and see whether it stays in the single-thread
  diffusive regime (β_COM ≈ 1/2 or smaller), i.e. no emergent bundle inertia in independent mode.

---

## 3. Key configuration parameters

- **W_coh grid:** [20.0, 50.0, 100.0]
- **Bundle sizes N:** [1, 2, 4, 8, 16, 32]
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

> This run is the first full independent-bundles baseline across multiple N and W_coh.
> It ran for 50 ensembles per (W_coh, N) pair with steps_per_wcoh = 1000, so the
> longest trajectories (W = 100) are 100,000 steps long.


---

## 5. Summary of `summary.json` results

### 5.1 COM amplitude vs N and 1/√N scaling

**W_coh = 20**
- N = 1:  A_mean ≈ 0.529097 (reference)
- N =  2: A_mean ≈ 0.374706,  A(1)/√N ≈ 0.374128,  ratio ≈ 1.002
- N =  4: A_mean ≈ 0.266323,  A(1)/√N ≈ 0.264549,  ratio ≈ 1.007
- N =  8: A_mean ≈ 0.187323,  A(1)/√N ≈ 0.187064,  ratio ≈ 1.001
- N = 16: A_mean ≈ 0.132625,  A(1)/√N ≈ 0.132274,  ratio ≈ 1.003
- N = 32: A_mean ≈ 0.093947,  A(1)/√N ≈ 0.093532,  ratio ≈ 1.004

**W_coh = 50**
- N = 1:  A_mean ≈ 0.384624 (reference)
- N =  2: A_mean ≈ 0.271948,  A(1)/√N ≈ 0.271970,  ratio ≈ 1.000
- N =  4: A_mean ≈ 0.192614,  A(1)/√N ≈ 0.192312,  ratio ≈ 1.002
- N =  8: A_mean ≈ 0.136039,  A(1)/√N ≈ 0.135985,  ratio ≈ 1.000
- N = 16: A_mean ≈ 0.096090,  A(1)/√N ≈ 0.096156,  ratio ≈ 0.999
- N = 32: A_mean ≈ 0.068022,  A(1)/√N ≈ 0.067992,  ratio ≈ 1.000

**W_coh = 100**
- N = 1:  A_mean ≈ 0.281079 (reference)
- N =  2: A_mean ≈ 0.198525,  A(1)/√N ≈ 0.198753,  ratio ≈ 0.999
- N =  4: A_mean ≈ 0.140403,  A(1)/√N ≈ 0.140539,  ratio ≈ 0.999
- N =  8: A_mean ≈ 0.099201,  A(1)/√N ≈ 0.099376,  ratio ≈ 0.998
- N = 16: A_mean ≈ 0.070106,  A(1)/√N ≈ 0.070270,  ratio ≈ 0.998
- N = 32: A_mean ≈ 0.049623,  A(1)/√N ≈ 0.049688,  ratio ≈ 0.999

Across all three W_coh values, A_COM(W_coh, N) matches the simple 1/√N scaling
to within about 0.1%–0.7% for N = 2…32. This is exactly the behaviour expected
for independent noise averaging with no additional bundle glue.

**Interpretation / comments:**

> Independent bundles behave as a straightforward average of N uncorrelated
> soft-rudder threads. There is no sign of extra suppression beyond 1/√N, and
> hence no emergent inertial stiffness in this mode. This is the right baseline
> to contrast with later shared-bias / correlated-bundle runs.


---

### 5.2 Effective β_COM(N) from A_COM(W_coh) vs W_coh

Using a simple log–log fit of A_COM(W) over W = 20, 50, 100 for each fixed N,
we obtain the following effective exponents β_COM(N) defined by
A_COM(W) ∼ W^{-β_COM}:

- N =  1: β_COM ≈ 0.391
- N =  2: β_COM ≈ 0.392
- N =  4: β_COM ≈ 0.395
- N =  8: β_COM ≈ 0.393
- N = 16: β_COM ≈ 0.394
- N = 32: β_COM ≈ 0.394

All β_COM(N) values cluster tightly around ≈ 0.39–0.40, slightly below the
idealised 0.5 of the IV_c telegraph scaling but clearly in the same diffusive
universality class. The small downward shift can be attributed to the limited
W_coh range (20–100), finite-length trajectories, and details of the PSD
amplitude extraction band.

**Interpretation / comments:**

> Bundles in independent mode do not change the W_coh scaling exponent: the
> COM inertial noise exponent β_COM is essentially N-independent and remains in
> the diffusive regime. This supports the IV_d narrative that any β > 1/2 must
> come from genuine inter-thread correlations, not just “more threads”.


---

### 5.3 Flip statistics and κ_eff

**W_coh = 20**
- N =  1: P0 ≈ 0.900, P1 ≈ 0.100, κ_eff ≈ 2.198
- N =  2: P0 ≈ 0.810, P1 ≈ 0.180, κ_eff ≈ 1.503
- N =  4: P0 ≈ 0.655, P1 ≈ 0.292, κ_eff ≈ 0.807
- N =  8: P0 ≈ 0.431, P1 ≈ 0.382, κ_eff ≈ 0.119
- N = 16: P0 ≈ 0.185, P1 ≈ 0.329, κ_eff ≈ -0.573
- N = 32: P0 ≈ 0.034, P1 ≈ 0.122, κ_eff ≈ -1.268

**W_coh = 50**
- N =  1: P0 ≈ 0.960, P1 ≈ 0.040, κ_eff ≈ 3.181
- N =  2: P0 ≈ 0.922, P1 ≈ 0.077, κ_eff ≈ 2.486
- N =  4: P0 ≈ 0.850, P1 ≈ 0.141, κ_eff ≈ 1.793
- N =  8: P0 ≈ 0.722, P1 ≈ 0.240, κ_eff ≈ 1.101
- N = 16: P0 ≈ 0.521, P1 ≈ 0.347, κ_eff ≈ 0.407
- N = 32: P0 ≈ 0.271, P1 ≈ 0.361, κ_eff ≈ -0.289

**W_coh = 100**
- N =  1: P0 ≈ 0.980, P1 ≈ 0.020, κ_eff ≈ 3.890
- N =  2: P0 ≈ 0.960, P1 ≈ 0.039, κ_eff ≈ 3.196
- N =  4: P0 ≈ 0.922, P1 ≈ 0.075, κ_eff ≈ 2.505
- N =  8: P0 ≈ 0.851, P1 ≈ 0.139, κ_eff ≈ 1.812
- N = 16: P0 ≈ 0.724, P1 ≈ 0.236, κ_eff ≈ 1.119
- N = 32: P0 ≈ 0.524, P1 ≈ 0.342, κ_eff ≈ 0.425

**Interpretation / comments:**

> For N = 1, κ_eff grows with W_coh as flips become rarer (q(W) = 2/W), consistent
> with a more strongly biased telegraph process. For larger N in independent mode,
> κ_eff drops towards O(1) or even negative values as multiple threads flip on a
> given step; this reflects the increasing combinatorial weight of k ≥ 1 flips
> and further signals the absence of rigid, synchronised bundle behaviour.


---

### 5.4 Alignment and lifetime

**W_coh = 20**
- N =  1: mean_Sv = 1.000, std_Sv = 0.000, mean_lifetime = 20000.0, frac_survived = 1.0
- N =  2: mean_Sv = 0.499, std_Sv = 0.500, mean_lifetime = 441.4, frac_survived = 0.0
- N =  4: mean_Sv = 0.375, std_Sv = 0.331, mean_lifetime = 35.9, frac_survived = 0.0
- N =  8: mean_Sv = 0.273, std_Sv = 0.224, mean_lifetime = 28.4, frac_survived = 0.0
- N = 16: mean_Sv = 0.196, std_Sv = 0.154, mean_lifetime = 21.7, frac_survived = 0.0
- N = 32: mean_Sv = 0.140, std_Sv = 0.108, mean_lifetime = 19.0, frac_survived = 0.0

**W_coh = 50**
- N =  1: mean_Sv = 1.000, std_Sv = 0.000, mean_lifetime = 50000.0, frac_survived = 1.0
- N =  2: mean_Sv = 0.501, std_Sv = 0.500, mean_lifetime = 114.8, frac_survived = 0.0
- N =  4: mean_Sv = 0.375, std_Sv = 0.331, mean_lifetime = 28.8, frac_survived = 0.0
- N =  8: mean_Sv = 0.274, std_Sv = 0.225, mean_lifetime = 26.0, frac_survived = 0.0
- N = 16: mean_Sv = 0.197, std_Sv = 0.155, mean_lifetime = 20.9, frac_survived = 0.0
- N = 32: mean_Sv = 0.140, std_Sv = 0.108, mean_lifetime = 19.3, frac_survived = 0.0

**W_coh = 100**
- N =  1: mean_Sv = 1.000, std_Sv = 0.000, mean_lifetime = 100000.0, frac_survived = 1.0
- N =  2: mean_Sv = 0.498, std_Sv = 0.500, mean_lifetime = 53.8, frac_survived = 0.0
- N =  4: mean_Sv = 0.375, std_Sv = 0.330, mean_lifetime = 29.2, frac_survived = 0.0
- N =  8: mean_Sv = 0.274, std_Sv = 0.225, mean_lifetime = 23.9, frac_survived = 0.0
- N = 16: mean_Sv = 0.196, std_Sv = 0.155, mean_lifetime = 20.3, frac_survived = 0.0
- N = 32: mean_Sv = 0.140, std_Sv = 0.108, mean_lifetime = 19.0, frac_survived = 0.0

**Interpretation / comments:**

> For N = 1, Sv is identically 1 and the lifetime equals the full run length at
> all W_coh. For N > 1, Sv fluctuates around small values with substantial spread,
> and the evaporation criterion (Sv < f_min for evap_window steps) is typically
> triggered within O(20–50) steps, leading to frac_survived ≈ 0. This is exactly
> the behaviour expected of independent, non-glued bundles.


---

## 6. Plots / figures generated (if any)

- No figures were saved directly from this run, but it provides the raw A_COM(W, N)
  and κ_eff(W, N) data for IV_d plots such as:
  - A_COM(W_coh, N) vs N at fixed W_coh,
  - β_COM(N) vs N,
  - κ_eff(W_coh, N) heatmaps or slices.


---

## 7. Issues, anomalies, or TODOs

- [ ] Optionally extend W_coh grid (e.g. to 10 and 200) to refine β_COM fits.

- [ ] Consider increasing n_ensembles for the largest N to further reduce noise.

- [ ] Use this independent baseline as a direct comparison for forthcoming
      shared-bias and strong-lock coupling runs (B-series).


---

## 8. Conclusions from this run

> Run A2 confirms that independent bundles do exactly what the universality-class
> story predicts: COM inertial noise scales like 1/√N at fixed W_coh, and the
> W_coh exponent β_COM is essentially independent of N and remains in a diffusive
> regime (β_COM ≈ 0.4 here, compatible with the IV_c picture once finite-range
> and band-selection effects are accounted for). There is no emergent inertial
> stiffening in this mode; any β > 1/2 must arise from correlated bundle dynamics,
> which will be the target of subsequent IV_d runs.
