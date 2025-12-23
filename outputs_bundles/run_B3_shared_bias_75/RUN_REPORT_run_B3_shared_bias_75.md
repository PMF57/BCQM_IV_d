# RUN_REPORT: run_B3_shared_bias_75

**Date:** 22 Dec 2025  
**Model name:** `run_B3_shared_bias_75`  
**Output directory:** `outputs_bundles/run_B3_shared_bias_75`  

## 1. Purpose of this run

Strong-glue bundle scan for the soft-rudder kernel:

- Bundles evolve under the same single-thread soft-rudder law as in IV_c, but with **strong shared-bias coupling** between threads.
- Coupling mode: `shared_bias`, with λ = 0.75 (significantly stronger than in B1).
- Goals:
  - Test whether strong glue can substantially **enhance COM persistence length** beyond the independent baseline.
  - Measure how the COM inertial-noise amplitude A(W_coh, N) and persistence length L_persist(W_coh, N) behave across W_coh and N.
  - Identify any small-N regimes (e.g. N = 2) where bundles become effectively rigid over a coherence horizon.

This is the **B3 “strong glue” run** in the IV_d B-series.

## 2. Configuration summary

From `metadata.json`:

- **Coherence horizon grid:** W_coh ∈ [20.0, 50.0, 100.0]
- **Bundle sizes:** N ∈ [1, 2, 4, 8, 16, 32]
- **Ensemble:** n_ensembles = 50, steps_per_wcoh = 1000
- **Kernel:**
  - type = `soft_rudder_bundle`
  - step_size = 1.0
  - slip_law: form = `power_law`, α = 1.0, k_prefactor = 2.0
- **Bundle coupling:** mode = `shared_bias`, λ = 0.75 (strong shared-bias coupling).
- **Phase dynamics:** enabled = False (disabled here; pure kinematics).
- **Analysis settings:**  
  - PSD: window = `hann`, segment_length = 512, overlap = 0.5
  - amplitude fit: freq ∈ [0.01, 0.1]
  - β fit: log10 W_coh ∈ [1.0, 2.5]
  - lifetime: f_min = 0.6, evap_window = 20

Random seed: 23458

## 3. Key scalar results (per W_coh and N)

Aggregate statistics from `summary.json`:

| W_coh |  N  | A_mean | A_std | L_persist_mean (hops) | L_persist_mean / W_coh | mean_lifetime (steps) | frac_survived |
|-------|-----|--------|-------|------------------------|------------------------|-----------------------|---------------|
|    20 |   1 | 0.531982 | 0.006349 | 9.995 | 0.500 | 20000.00 | 1.000 |
|    20 |   2 | 0.276053 | 0.005353 | 20.326 | 1.016 | 1316.46 | 0.000 |
|    20 |   4 | 0.231973 | 0.003583 | 9.750 | 0.488 | 43.26 | 0.000 |
|    20 |   8 | 0.177522 | 0.001894 | 6.338 | 0.317 | 33.82 | 0.000 |
|    20 |  16 | 0.129158 | 0.001569 | 5.316 | 0.266 | 19.90 | 0.000 |
|    20 |  32 | 0.092594 | 0.001046 | 4.963 | 0.248 | 19.06 | 0.000 |
|    50 |   1 | 0.384378 | 0.003948 | 25.035 | 0.501 | 50000.00 | 1.000 |
|    50 |   2 | 0.177767 | 0.003005 | 50.492 | 1.010 | 298.56 | 0.000 |
|    50 |   4 | 0.153030 | 0.001673 | 22.650 | 0.453 | 31.46 | 0.000 |
|    50 |   8 | 0.120429 | 0.000977 | 13.680 | 0.274 | 29.36 | 0.000 |
|    50 |  16 | 0.089490 | 0.000720 | 10.250 | 0.205 | 20.62 | 0.000 |
|    50 |  32 | 0.064871 | 0.000464 | 8.684 | 0.174 | 19.00 | 0.000 |
|   100 |   1 | 0.280179 | 0.003638 | 50.055 | 0.501 | 100000.00 | 1.000 |
|   100 |   2 | 0.126328 | 0.001827 | 100.310 | 1.003 | 176.16 | 0.000 |
|   100 |   4 | 0.108965 | 0.001228 | 44.434 | 0.444 | 32.32 | 0.000 |
|   100 |   8 | 0.086169 | 0.000618 | 25.750 | 0.258 | 22.60 | 0.000 |
|   100 |  16 | 0.064325 | 0.000401 | 18.354 | 0.184 | 20.28 | 0.000 |
|   100 |  32 | 0.046789 | 0.000264 | 14.308 | 0.143 | 19.00 | 0.000 |


Notes (qualitative patterns):

- **Amplitude A(W_coh, N):**
  - For N = 1, A_mean(W_coh) behaves much like in A1/B1: monotonically decreasing with W_coh, consistent with the diffusive single-thread soft-rudder law.
  - For N > 1, A_mean decreases with N at fixed W_coh (roughly compatible with 1/√N-style suppression), and decreases with W_coh at fixed N. There is no sign of a dramatic amplitude anomaly from strong glue.

- **Persistence length L_persist_mean(W_coh, N):**
  - **N = 1:** L_persist_mean ≈ 0.5 W_coh (ratios ≈ 0.5 across the grid), reproducing the IV_c/A1 baseline even in the presence of shared bias (which is effectively irrelevant for a single thread).
  - **N = 2:** L_persist_mean ≈ W_coh for all W_coh:
    - W = 20:  L_persist_mean ≈ 20.3  (≈ 1.02 W)
    - W = 50:  L_persist_mean ≈ 50.5  (≈ 1.01 W)
    - W = 100: L_persist_mean ≈ 100.3 (≈ 1.00 W)
    This is the key strong-glue effect: a tightly glued 2-thread bundle has a COM direction that typically persists for **about one full coherence horizon** before flipping.
  - **N ≥ 4:** L_persist_mean grows with W_coh but more slowly, and the ratio L_persist_mean / W_coh **decreases with N**:
    - For N = 4, ratios are ≈ 0.49, 0.45, 0.44 at W = 20, 50, 100.
    - For N = 8, ratios are ≈ 0.32, 0.27, 0.26.
    - For N = 16, ratios are ≈ 0.27, 0.21, 0.18.
    - For N = 32, ratios are ≈ 0.25, 0.17, 0.14.
    Strong glue thus creates an **optimal small-N regime** (N = 2) where bundles are very stiff over W_coh, but larger bundles do not become more rigid; instead, their persistence per W_coh drops.

- **Lifetimes and evaporation:**
  - **N = 1:** mean_lifetime = steps_per_wcoh × W_coh (20000, 50000, 100000) and frac_survived = 1.0: single threads never evaporate within the run window.
  - **N = 2:** mean_lifetime ranges from ~1300 (W = 20) down to ~300 (W = 50) and ~176 (W = 100), with frac_survived = 0.0. Bundles live long enough to maintain long COM persistence but eventually evaporate.
  - **N ≥ 4:** mean_lifetime is O(20–45) steps almost independent of W_coh, with frac_survived = 0.0: large bundles are fragile despite the strong shared bias.

## 4. Interpretation

1. **Evidence for a small-N “rigidity window”.**  
   The B3 run provides clear quantitative evidence that:
   - Single threads (N = 1) remain in the IV_c diffusive regime with L_persist_mean ≈ 0.5 W_coh.
   - Strongly glued **two-thread bundles (N = 2)** achieve L_persist_mean ≈ W_coh across the grid, i.e. their COM direction typically persists over an entire coherence window before flipping.
   - Larger bundles (N ≥ 4) do *not* become stiffer; instead, their L_persist_mean / W_coh decreases with N and their lifetimes remain short.

   This supports the idea that there is an **optimal small-N regime** in which simple shared-bias glue can generate effectively inertial behaviour over W_coh, while uncontrolled large bundles do not.

2. **Scale separation without changing universality class.**  
   Even with strong glue, all bundles remain in the **diffusive universality class** at long times (as indicated by the underlying IV_c logic and A(W_coh) scaling). What changes is the **persistence length**:
   - For N = 2, L_persist_mean ≈ W_coh ≫ 1 yields COM trajectories that look effectively straight over each coherence window, even though the primitive process is still a soft-rudder random walk.
   - This matches the “scale-separation” story: emergent rigidity as L_persist ≫ 1 and, ideally, L_persist ≳ W_coh.

3. **Glue alone is not enough for large bundles.**  
   The fact that N ≥ 4 bundles do not gain additional persistence (and may even become more fragile) indicates:
   - Simple shared-bias coupling is *not* sufficient to stabilise large bundles.
   - Any move towards realistic “massive” composites will require more structured glue and/or hierarchical bundling (triplet cores, dimers/trimers of cores, etc.), rather than indiscriminately gluing many primitive threads together.

4. **Role of B3 in the B-series.**  
   B3 is the most informative of the current B-series:
   - It demonstrates that strong glue can push a small bundle (N = 2) into a regime where L_persist_mean ≈ W_coh.
   - It simultaneously shows the limits of this mechanism for large N, motivating the move to hierarchical bundles and more nuanced glue in BCQM~V.

## 5. Follow-up / actions

- Use this run as the **B3 strong-glue case** in IV_d, with emphasis on:
  - the N = 2 L_persist_mean ≈ W_coh result,
  - the decline of L_persist_mean / W_coh with N beyond 2,
  - and the short lifetimes of large bundles.
- In the IV_d paper:
  - Highlight B3 as the main quantitative support for the “small bundles as effective inertial carriers” narrative.
  - Clearly distinguish between “rigidity over W_coh” (via L_persist) and “universality class” (still diffusive).
- Store this RUN_REPORT alongside:
  - `configs/run_B3_shared_bias_75.yml`
  - `outputs_bundles/run_B3_shared_bias_75/summary.json`
  - and the corresponding timeseries files.

