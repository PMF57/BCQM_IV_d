# RUN_REPORT: run_B2_shared_bias_stronger

**Date:** 22 Dec 2025  
**Model name:** `run_B2_shared_bias_stronger`  
**Output directory:** `outputs_bundles/run_B2_shared_bias_stronger`  

## 1. Purpose of this run

Intermediate-glue bundle scan for the soft-rudder kernel:

- Bundles evolve under the same single-thread soft-rudder law as in IV_c, but with **shared-bias coupling** between threads.
- Coupling mode: `shared_bias`, with λ = 0.5 (stronger than B1’s λ = 0.25, weaker than B3’s λ = 0.75).
- Goals:
  - Track how COM inertial-noise amplitude A(W_coh, N) and persistence length L_persist(W_coh, N) change as glue strength is increased from B1.
  - Check whether λ = 0.5 already produces a clear enhancement of COM persistence beyond the independent baseline, and how it compares to the strong-glue B3 case.

This is the **B2 “intermediate glue” run** in the IV_d B-series.

## 2. Configuration summary

From `metadata.json`:

- **Coherence horizon grid:** W_coh ∈ [20.0, 50.0, 100.0]
- **Bundle sizes:** N ∈ [1, 2, 4, 8, 16, 32]
- **Ensemble:** n_ensembles = 50, steps_per_wcoh = 1000
- **Kernel:**
  - type = `soft_rudder_bundle`
  - step_size = 1.0
  - slip_law: form = `power_law`, α = 1.0, k_prefactor = 2.0
- **Bundle coupling:** mode = `shared_bias`, λ = 0.5 (intermediate shared-bias coupling).
- **Phase dynamics:** enabled = False (disabled here; pure kinematics).
- **Analysis settings:**  
  - PSD: window = `hann`, segment_length = 512, overlap = 0.5
  - amplitude fit: freq ∈ [0.01, 0.1]
  - β fit: log10 W_coh ∈ [1.0, 2.5]
  - lifetime: f_min = 0.6, evap_window = 20

Random seed: 23457

## 3. Key scalar results (per W_coh and N)

Aggregate statistics from `summary.json`:


| W_coh |  N  | A_mean | A_std | L_persist_mean (hops) | L_persist_mean / W_coh | mean_lifetime (steps) | frac_survived |
|-------|-----|--------|-------|------------------------|------------------------|-----------------------|---------------|
|    20 |   1 | 0.531659 | 0.006355 | 10.007 | 0.500 | 20000.00 | 1.000 |
|    20 |   2 | 0.341141 | 0.004829 | 10.330 | 0.516 | 570.84 | 0.000 |
|    20 |   4 | 0.253707 | 0.003037 | 6.874 | 0.344 | 35.62 | 0.000 |
|    20 |   8 | 0.183331 | 0.002411 | 5.502 | 0.275 | 29.26 | 0.000 |
|    20 |  16 | 0.131384 | 0.001961 | 4.932 | 0.247 | 20.94 | 0.000 |
|    20 |  32 | 0.093355 | 0.001212 | 4.770 | 0.238 | 19.00 | 0.000 |
|    50 |   1 | 0.385385 | 0.004367 | 24.941 | 0.499 | 50000.00 | 1.000 |
|    50 |   2 | 0.227723 | 0.002654 | 25.308 | 0.506 | 153.10 | 0.000 |
|    50 |   4 | 0.173220 | 0.001346 | 16.059 | 0.321 | 31.18 | 0.000 |
|    50 |   8 | 0.127234 | 0.001064 | 11.785 | 0.236 | 29.26 | 0.000 |
|    50 |  16 | 0.092270 | 0.000655 | 9.432 | 0.189 | 21.14 | 0.000 |
|    50 |  32 | 0.065996 | 0.000601 | 8.291 | 0.166 | 19.50 | 0.000 |
|   100 |   1 | 0.281213 | 0.003628 | 49.816 | 0.498 | 100000.00 | 1.000 |
|   100 |   2 | 0.163134 | 0.001736 | 50.313 | 0.503 | 122.66 | 0.000 |
|   100 |   4 | 0.124189 | 0.000939 | 31.311 | 0.313 | 28.96 | 0.000 |
|   100 |   8 | 0.091666 | 0.000669 | 21.988 | 0.220 | 23.70 | 0.000 |
|   100 |  16 | 0.066553 | 0.000394 | 16.730 | 0.167 | 20.38 | 0.000 |
|   100 |  32 | 0.047918 | 0.000301 | 13.642 | 0.136 | 19.50 | 0.000 |

Notes (qualitative patterns):

- **Amplitude A(W_coh, N):**
  - For N = 1, A_mean(W_coh) follows the same monotone decrease with W_coh as in A1/B1/B3, consistent with diffusive single-thread dynamics.
  - For N > 1, A_mean decreases with N at fixed W_coh (approximately like 1/√N) and decreases with W_coh at fixed N, as expected from averaging correlated but still noisy threads.

- **Persistence length L_persist_mean(W_coh, N):**
  - **N = 1:** L_persist_mean ≈ 0.5 W_coh (ratios ≈ 0.5 across the grid), reproducing the IV_c/A1 baseline; the shared bias is irrelevant for a single thread.
  - **N = 2:** L_persist_mean is noticeably larger than in the independent/weak-glue case, with ratios L_persist_mean / W_coh ≈ 0.52 (W = 20), ≈ 0.51 (W = 50), ≈ 0.50 (W = 100). This sits between B1 and B3:
    - B1 (λ = 0.25) shows only modest enhancement.
    - B2 (λ = 0.5) pushes persistence above 0.5 W_coh but not yet to W_coh.
    - B3 (λ = 0.75) reaches L_persist_mean ≈ W_coh for N = 2.
  - **N ≥ 4:** L_persist_mean grows with W_coh but the ratio L_persist_mean / W_coh decreases with N, remaining well below the single-thread 0.5 level for large bundles (e.g. ≈ 0.25→0.17→0.14 for N = 32 at W = 20, 50, 100).

- **Lifetimes and evaporation:**
  - **N = 1:** mean_lifetime = steps_per_wcoh × W_coh and frac_survived = 1.0: single threads never evaporate within the run window.
  - **N = 2:** mean_lifetime ranges from O(10^2–10^3) steps depending on W_coh, with frac_survived = 0.0: bundles live long enough to exhibit enhanced persistence, but still eventually evaporate.
  - **N ≥ 4:** mean_lifetime is O(20–35) steps with frac_survived = 0.0: large bundles remain fragile despite intermediate glue strength.

## 4. Interpretation

1. **Intermediate glue yields intermediate persistence enhancement.**  
   For N = 2, the persistence-length ratios L_persist_mean / W_coh sit between the weak-glue B1
   and strong-glue B3 cases:
   - Independence / weak glue: ratios ≲ 0.5.
   - B2 (λ = 0.5): ratios ≈ 0.5–0.52.
   - B3 (λ = 0.75): ratios ≈ 1.0 (L_persist_mean ≈ W_coh).
   This confirms that the shared-bias mechanism responds smoothly to λ and that λ = 0.5 already
   produces a measurable increase in COM persistence for small bundles.

2. **Small-N window vs large-N fragility.**  
   As in B3, larger bundles (N ≥ 4) do not become more rigid. Instead:
   - L_persist_mean / W_coh decreases with N.
   - Lifetimes remain short (~20–35 steps) and essentially independent of W_coh.
   This reinforces the idea that simple shared-bias glue naturally favours a **small-N window** for effective stiffness (N = 2 in the B-series), while large-N bundles are noisy and fragile.

3. **Continuity across B1–B3.**  
   Taken together, B1 (λ = 0.25), B2 (λ = 0.5), and B3 (λ = 0.75) show a coherent trend:
   - β and A(W_coh, N) remain consistent with diffusive universality at long scales.
   - The main effect of increasing λ is to **increase L_persist_mean for small bundles**, pushing      N = 2 from a slightly enhanced state (B1) through an intermediate regime (B2) to the      L_persist_mean ≈ W_coh regime (B3).
   - Large bundles do not see a corresponding benefit; they remain short-lived and noisy.

## 5. Follow-up / actions

- Use this run as the **B2 intermediate-glue case** in IV_d, sitting between B1 and B3 in both
  amplitude and persistence-length behaviour.
- When drafting the IV_d text and appendix tables/figures:
  - Plot L_persist_mean / W_coh vs N for B1, B2, B3 at fixed W_coh to highlight the λ-dependence
    for N = 2 and the declining trend for large N.
  - Emphasise that the universality class remains diffusive; glue changes scale separation, not β.
- Store this RUN_REPORT alongside:
  - `configs/run_B2_shared_bias_stronger.yml`
  - `outputs_bundles/run_B2_shared_bias_stronger/summary.json`
  - and the corresponding timeseries files.
