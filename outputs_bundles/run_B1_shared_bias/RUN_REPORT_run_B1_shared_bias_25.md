# RUN_REPORT: run_B1_shared_bias_25

**Date:** 22 Dec 2025  
**Model name:** `run_B1_shared_bias`  
**Output directory:** `outputs_bundles/run_B1_shared_bias`  

## 1. Purpose of this run

First glued-bundle scan for the soft-rudder kernel:

- Bundles evolve under the same single-thread soft-rudder law as in IV_c, **but with shared-bias coupling** between threads.
- Coupling mode: `shared_bias`, with moderate strength λ = 0.25.
- Goal:
  - Compare COM inertial-noise amplitude A(W_coh, N) and persistence length L_persist(W_coh, N) against the A2 independent baseline.
  - Check whether modest glue produces any enhancement in COM persistence beyond the independent value, or mainly modifies amplitudes and lifetimes.

This is the **B1 “weak glue” run** in the IV_d B-series.

## 2. Configuration summary

From `metadata.json`:

- **Coherence horizon grid:** W_coh ∈ [20.0, 50.0, 100.0]
- **Bundle sizes:** N ∈ [1, 2, 4, 8, 16, 32]
- **Ensemble:** n_ensembles = 50, steps_per_wcoh = 1000
- **Kernel:**
  - type = `soft_rudder_bundle`
  - step_size = 1.0
  - slip_law: form = `power_law`, α = 1.0, k_prefactor = 2.0
- **Bundle coupling:** mode = `shared_bias`, λ = 0.25 (shared-bias coupling).
- **Phase dynamics:** enabled = False (disabled here; pure kinematics).
- **Analysis settings:**  
  - PSD: window = `hann`, segment_length = 512, overlap = 0.5
  - amplitude fit: freq ∈ [0.01, 0.1]
  - β fit: log10 W_coh ∈ [1.0, 2.5]
  - lifetime: f_min = 0.6, evap_window = 20

Random seed: 23456

## 3. Key scalar results (per W_coh and N)

Aggregate statistics from `summary.json`:

| W_coh |  N  | A_mean | A_std | L_persist_mean (hops) | L_persist_mean / W_coh | mean_lifetime (steps) | frac_survived |
|-------|-----|--------|-------|------------------------|------------------------|-----------------------|---------------|
|    20 |   1 | 0.529934 | 0.006610 | 10.046 | 0.502 | 20000.00 | 1.000 |
|    20 |   2 | 0.368881 | 0.004791 | 6.924 | 0.346 | 518.88 | 0.000 |
|    20 |   4 | 0.262438 | 0.003249 | 5.617 | 0.281 | 37.74 | 0.000 |
|    20 |   8 | 0.186530 | 0.002564 | 4.919 | 0.246 | 26.50 | 0.000 |
|    20 |  16 | 0.132011 | 0.001585 | 4.656 | 0.233 | 23.68 | 0.000 |
|    20 |  32 | 0.093736 | 0.001117 | 4.582 | 0.229 | 19.00 | 0.000 |
|    50 |   1 | 0.384815 | 0.004371 | 24.979 | 0.500 | 50000.00 | 1.000 |
|    50 |   2 | 0.255950 | 0.003281 | 16.911 | 0.338 | 119.50 | 0.000 |
|    50 |   4 | 0.184433 | 0.001762 | 12.988 | 0.260 | 28.36 | 0.000 |
|    50 |   8 | 0.132371 | 0.001104 | 10.442 | 0.209 | 27.32 | 0.000 |
|    50 |  16 | 0.094211 | 0.000578 | 8.850 | 0.177 | 20.54 | 0.000 |
|    50 |  32 | 0.067247 | 0.000515 | 7.959 | 0.159 | 19.00 | 0.000 |
|   100 |   1 | 0.280683 | 0.003488 | 49.995 | 0.500 | 100000.00 | 1.000 |
|   100 |   2 | 0.184948 | 0.002019 | 33.422 | 0.334 | 67.12 | 0.000 |
|   100 |   4 | 0.133019 | 0.001062 | 25.336 | 0.253 | 23.18 | 0.000 |
|   100 |   8 | 0.095806 | 0.000574 | 19.704 | 0.197 | 25.06 | 0.000 |
|   100 |  16 | 0.068483 | 0.000466 | 15.672 | 0.157 | 21.84 | 0.000 |
|   100 |  32 | 0.048795 | 0.000277 | 13.104 | 0.131 | 19.00 | 0.000 |


Notes:

- **Amplitude A(W_coh, N):**
  - For N = 1, A_mean(W_coh) is slightly smaller than in the A1 regression but shows the same monotone decrease with W_coh, consistent with diffusive single-thread dynamics.
  - For N > 1, A_mean decreases with N roughly as expected from averaging, but the precise N-dependence and comparison to A2 should be checked in the amplitude-scaling fit.

- **Persistence length L_persist_mean(W_coh, N):**
  - N = 1: L_persist_mean ≈ 0.5 W_coh, as in the A1 regression.
  - N > 1: L_persist_mean grows with W_coh but the ratio L_persist_mean / W_coh remains below 0.5 and typically decreases with N. At this modest glue strength (λ = 0.25), there is **no dramatic enhancement** of COM persistence beyond the independent baseline; if anything, the behaviour is close to independent threads with slight correlations.

- **Lifetimes and evaporation:**
  - N = 1 bundles do not evaporate within the run budget (mean_lifetime = steps_per_wcoh × W_coh, frac_survived = 1.0).
  - For N > 1, mean lifetimes are of order 20–500 steps (depending on W_coh and N), with frac_survived = 0.0. This is qualitatively similar to the A2 independent case: modest glue at λ = 0.25 does not prevent evaporation for larger bundles.

## 4. Interpretation

1. **Weak glue does not radically change persistence.**  
   At λ = 0.25, the shared-bias coupling is too weak to generate a large persistence-length enhancement. L_persist_mean / W_coh remains at or below the single-thread baseline (~0.5) for all N. This confirms that any strong increase in COM stiffness must come from stronger glue or more structured/hierarchical mechanisms, not from weak shared bias.

2. **Consistency with independent baseline.**  
   Comparing qualitatively with A2:
   - Amplitudes A(W_coh, N) for B1 are in the same ballpark as the independent run, with no drastic deviations.
   - Persistence lengths show the same qualitative trend: adding more threads without strong glue does not create long-lived straight COM segments.

3. **Role of B1 in the B-series.**  
   This run establishes that:
   - Weak shared-bias coupling behaves nearly like independence for the purposes of persistence and lifetimes.
   - Any significant change in L_persist_mean / W_coh or β_COM in later runs (B2 with λ = 0.5, B3 with λ = 0.75) can be attributed to increased glue strength rather than artefacts of the implementation.

## 5. Follow-up / actions

- Use this run as the **B1 weak-glue anchor** in the IV_d narrative and appendices.
- When analysing B2 and B3:
  - Compare L_persist_mean / W_coh vs B1 to highlight the effect of increasing λ.
  - Track how mean_lifetime and κ_eff evolve with λ and N.
- Store this RUN_REPORT alongside:
  - `configs/run_B1_shared_bias_25.yml`
  - `outputs_bundles/run_B1_shared_bias/summary.json`
  - and the corresponding timeseries files.

