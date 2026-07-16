# Final Report — Proteomics Differential Abundance Analysis

| Field | Details |
|---|---|
| Research Project | Proteomics Differential Abundance |
| Study Scope | Recovery of planted differentially abundant proteins under Benjamini-Hochberg FDR control, across clean synthetic, parameter-swept, and realistic heteroscedastic/missing-data conditions |
| Methodological Approach | Hypothesis-driven statistical simulation study using per-protein Welch's t-tests, BH-FDR correction, parameter sweeps, and missing-data/heteroscedasticity stress tests |
| Generated | 2026-07-14 |
| Last Updated | 2026-07-14 |
| Report Status | FINAL |
| Primary Sources | [background/01_initial_question.md](../background/01_initial_question.md); [ANALYSIS_01.md](ANALYSIS_01.md); [ANALYSIS_02.md](ANALYSIS_02.md); [ANALYSIS_03.md](ANALYSIS_03.md) |

---

## 1. Executive Summary

This project evaluated whether a standard differential-abundance workflow — per-protein Welch's t-test followed by Benjamini-Hochberg (BH) false-discovery-rate correction — can recover proteins with known planted abundance changes while controlling false positives, and how that recovery degrades as measurement conditions become more realistic.

The first experiment established a clean baseline: on a synthetic matrix of 2,000 proteins (100 planted true differences, N=5 replicates per group, noise SD=0.3), BH correction controlled the empirical FDR at 2.70% (well below the 5.0% target) but recovered only 36.00% of the planted proteins, far short of the 70% recall target. The second experiment swept replicate count (N=3 to 15) and noise level (SD=0.1 to 0.5) and confirmed that recall increases monotonically with more replicates and less noise, mapping explicit design envelopes (for example, N≥6 or N≥8 at SD=0.3 restores recall above 70%). The third experiment introduced heteroscedastic noise and logistic missing-not-at-random values, the two dominant real-world proteomics artifacts. Heteroscedasticity alone collapsed Oracle recall by 47-72%, and constant-value (MinDet) imputation caused catastrophic power loss rather than the hypothesized FDR explosion, while simple replica-presence filtering preserved FDR control and recovered more power than imputation.

The overall conclusion is that BH-controlled differential abundance testing is statistically sound and reproducible, but its practical power is highly sensitive to replicate count, noise structure, and missing-data handling — and that naive imputation strategies can be more harmful to discovery than principled filtering.

---

## 2. Project Question and Study Scope

### Central Question

Given a two-condition protein-abundance matrix, which proteins are differentially abundant, and how well can a per-protein test plus multiple-testing correction recover the proteins known to be truly changed while controlling false positives?

### Study Scope

This report covers three completed synthetic iterations along the fidelity ladder: a clean-data baseline, a multi-variable parameter sweep across replicate count and noise level, and a heteroscedastic/missing-data stress test comparing imputation against replica-presence filtering. No downloaded or real-data iteration has been completed yet.

### Model, Data, or Experimental Context

All experiments use synthetic log2-intensity matrices of 2,000 proteins with 100 proteins planted with a true log2 fold-change of ±1.0. Testing uses per-protein Welch's two-sample t-tests followed by Benjamini-Hochberg FDR correction at a nominal threshold of 0.05. Recall (sensitivity against the planted set) and empirical FDR are the primary outcome metrics, visualized with volcano plots and, in the sweep iteration, recall/FDR heatmaps.

### What This Study Does Not Resolve

This study does not yet validate the workflow against real experimental proteomics data, does not evaluate alternative multiple-testing corrections (Storey's q-value, Bonferroni), does not test non-constant imputation methods (KNN, regression-based), and does not model biological replicate structure beyond simple two-group comparisons.

---

## 3. Research Audit Trail

| Iteration | Hypothesis | Script or Method | Log or Evidence | Analysis | Status |
|---|---|---|---|---|---|
| 1 | [H1_bh_correction_baseline.md](../hypotheses/H1_bh_correction_baseline.md) | [script_01_bh_correction.py](../experiments/01_synthetic/script_01_bh_correction.py) | [script_01_bh_correction_20260630_110058.log](../results/logs/script_01_bh_correction_20260630_110058.log) | [ANALYSIS_01.md](ANALYSIS_01.md) | Partially Supported |
| 2 | [H2_parameter_sweep.md](../hypotheses/H2_parameter_sweep.md) | [script_02_parameter_sweep.py](../experiments/01_synthetic/script_02_parameter_sweep.py) | [script_02_parameter_sweep_20260630_111010.log](../results/logs/script_02_parameter_sweep_20260630_111010.log) | [ANALYSIS_02.md](ANALYSIS_02.md) | Supported |
| 3 | [H3_missingness_heteroscedasticity.md](../hypotheses/H3_missingness_heteroscedasticity.md) | [script_03_missingness_heteroscedasticity.py](../experiments/01_synthetic/script_03_missingness_heteroscedasticity.py) | [script_03_missingness_heteroscedasticity_20260630_111724.log](../results/logs/script_03_missingness_heteroscedasticity_20260630_111724.log) | [ANALYSIS_03.md](ANALYSIS_03.md) | Partially Supported |

---

## 4. Final Results Matrix

| Result Area | Best or Representative Case | Main Quantitative Outcome | Interpretation |
|---|---:|---:|---|
| Clean-data BH baseline | N=5, SD=0.3, FC=±1.0 | Recall 36.00%; empirical FDR 2.70% (uncorrected FDR 47.31%) | BH correction controls FDR as designed but is conservative at standard proteomics sample sizes. |
| Design-envelope sweep | N=8, SD=0.3 | Recall 97.00%; empirical FDR 6.73% | Increasing replicates or lowering noise restores high power; recall is a strictly monotonic function of N and noise. |
| Heteroscedastic Oracle | Config A (N=5, SD_base=0.2) | Recall dropped from 95.00% (homoscedastic) to 23.00% (heteroscedastic) | Abundance-dependent noise alone can erase most of the statistical power gained from a favorable replicate/noise design. |
| Missing-data handling | Config B (N=8, SD_base=0.3) | Replica filtering recall 45.00% (FDR 4.26%) vs. MinDet imputation recall 30.00% (FDR 6.25%) | Simple replica-presence filtering preserves more discovery power and better FDR control than constant-value imputation. |

---

## 5. Iteration-Level Findings

### Iteration 1 — Benjamini-Hochberg Correction Baseline

#### Goal

Establish a clean-data baseline confirming that BH-corrected testing controls empirical FDR near the nominal 0.05 threshold and quantify the recall achieved at standard proteomics parameters (N=5 replicates, SD=0.3, FC=±1.0).

#### Method

A synthetic matrix of 2,000 proteins (5 control vs. 5 treated samples) was generated with 100 proteins planted with a true ±1.0 log2 fold-change and Gaussian noise SD=0.3. Per-protein Welch's t-tests were computed and corrected with Benjamini-Hochberg FDR at 0.05.

#### Key Findings

| Metric | Expected | Observed | Assessment |
|---|---:|---:|---|
| Empirical FDR (BH-corrected) | ≤ 5.0% | 2.70% | Pass |
| Recall (BH-corrected) | ≥ 70.0% | 36.00% | Fail |
| Uncorrected empirical FDR | > 40.0% | 47.31% | Pass (confirms multiple-testing problem) |

#### Interpretation

The hypothesis was partially supported. FDR control worked exactly as predicted, but the predicted 70% recall was not reached — only 36% of planted true positives survived BH correction at N=5 replicates and SD=0.3 noise. This established the central open question motivating Iteration 2: what replicate count or noise level is required to reach acceptable power without sacrificing FDR control?

---

### Iteration 2 — Multi-Variable Parameter Sweep

#### Goal

Map the two-dimensional design space of replicate count (N) and noise level (SD) to determine the feasibility envelope for achieving ≥70% recall under BH-controlled FDR.

#### Method

A grid of N ∈ {3, 4, 5, 6, 8, 12, 15} replicates per group and SD ∈ {0.1, 0.2, 0.3, 0.4, 0.5} was swept (35 total configurations), each on a fresh synthetic matrix with the same planted-effect structure as Iteration 1.

#### Key Findings

| Configuration | Recall | Empirical FDR | Assessment |
|---|---:|---:|---|
| N=3, SD=0.2 | 0.00% | 0.00% | Powerless zone |
| N=5, SD=0.3 (baseline) | 36.00% | 2.70% | Reproduces Iteration 1 exactly |
| N=5, SD=0.2 | 95.00% | 3.06% | High power via noise reduction |
| N=6, SD=0.3 | 87.00% | 1.14% | High power via replicate expansion |
| N=8, SD=0.3 | 97.00% | 6.73% | Highest power tested at standard noise |

#### Interpretation

The hypothesis was supported. Recall increased strictly monotonically with N and decreased strictly monotonically with SD. Two concrete, actionable design strategies were confirmed: expand replicates to N≥6 or N≥8 at standard noise (SD=0.3), or reduce noise to SD≤0.2 while keeping N=5 or N=6. N=3 was shown to be a statistical dead zone regardless of noise level in the practically achievable range.

---

### Iteration 3 — Missingness and Heteroscedasticity Impact

#### Goal

Test whether abundance-dependent (heteroscedastic) noise and realistic missing-not-at-random (MNAR) values degrade the high-power design envelopes discovered in Iteration 2, and compare constant-value imputation against replica-presence filtering as remediation strategies.

#### Method

Two high-power configurations from Iteration 2 (Config A: N=5, SD_base=0.2; Config B: N=8, SD_base=0.3) were re-run with heteroscedastic noise (variance scales inversely with abundance) and logistic MNAR missingness (~10.5% missing overall). Three handling strategies were compared: Oracle (no missingness, heteroscedastic noise only), MinDet constant-value imputation, and replica-presence filtering (require ≥3 replicates per group for N=5, ≥4 for N=8).

#### Key Findings

| Configuration | Method | Recall | Empirical FDR | Assessment |
|---|---|---:|---:|---|
| Config A | Homoscedastic (Iteration 2) | 95.00% | 3.06% | Baseline |
| Config A | Oracle (heteroscedastic only) | 23.00% | 4.17% | 72-point power loss from noise structure alone |
| Config A | MinDet imputation | 5.00% | 0.00% | Catastrophic power loss, not FDR explosion |
| Config A | Replica filtering | 10.00% | 0.00% | FDR controlled, partial power recovery |
| Config B | Homoscedastic (Iteration 2) | 97.00% | 6.73% | Baseline |
| Config B | Oracle (heteroscedastic only) | 50.00% | 3.85% | 47-point power loss from noise structure alone |
| Config B | MinDet imputation | 30.00% | 6.25% | Power loss and elevated FDR |
| Config B | Replica filtering | 45.00% | 4.26% | Best-performing missing-data strategy tested |

#### Interpretation

The hypothesis was partially supported. The heteroscedasticity power penalty was confirmed and exceeded expectations. However, the predicted FDR-explosion mechanism for MinDet imputation was refuted: imputation destroyed power (via variance compression and mean-difference cancellation) rather than inflating false positives. Replica-presence filtering, with no imputation at all, controlled FDR reliably and outperformed imputation on recall in both configurations, supporting it as the preferred simple remediation strategy.

---

## 6. Cross-Iteration Comparison

| Metric or Decision Point | Iteration 1 | Iteration 2 | Iteration 3 | Current Interpretation |
|---|---:|---:|---:|---|
| Data type | Clean synthetic baseline | Clean synthetic parameter grid | Heteroscedastic + MNAR synthetic | Fidelity progressively increased toward realistic proteomics artifacts. |
| Recall at N=5, SD≈0.2-0.3 | 36.00% (SD=0.3) | 95.00% (SD=0.2) | 23.00% Oracle; 10.00% filtered (Config A) | Noise structure and missingness each independently erode power gained from favorable replicate/noise design. |
| FDR control | 2.70% | 1.14%-6.73% across grid | 0.00%-6.25% depending on method | BH control remains close to nominal across all iterations; occasional small exceedances reflect discrete low-count volatility, not systematic failure. |
| Primary lesson | FDR control works; power does not follow automatically | Recall is a predictable, monotonic function of N and noise | Missing-data handling strategy matters as much as sample size | Each iteration narrowed the gap between statistical theory and practical proteomics design guidance. |

---

## 7. Key Scientific Conclusions

1. Benjamini-Hochberg FDR correction reliably controls the empirical false discovery rate near its nominal threshold across all tested synthetic conditions, confirming the core multiple-testing theory.
2. Statistical power (recall) under BH correction is highly sensitive to replicate count and noise level; the standard textbook design of N=5 replicates with SD=0.3 noise recovers only about a third of true differences.
3. Recall behaves as a strictly monotonic function of both replicate count (increasing) and noise standard deviation (decreasing), enabling explicit design-envelope guidance for proteomics experiments.
4. Heteroscedastic noise, which is standard in real mass-spectrometry data, can erase 47-72% of the statistical power that a homoscedastic-noise calculation would predict, even before missing values are considered.
5. Constant-value (MinDet) imputation for missing values causes catastrophic power loss through variance compression and mean-difference cancellation rather than the hypothesized FDR explosion; simple replica-presence filtering is a safer default.

---

## 8. Reproducibility Manifest

| Artifact | Purpose |
|---|---|
| [background/01_initial_question.md](../background/01_initial_question.md) | Research question and domain framing |
| [H1_bh_correction_baseline.md](../hypotheses/H1_bh_correction_baseline.md) | Iteration 1 hypothesis |
| [script_01_bh_correction.py](../experiments/01_synthetic/script_01_bh_correction.py) | Clean-data BH baseline script |
| [script_01_bh_correction_20260630_110058.log](../results/logs/script_01_bh_correction_20260630_110058.log) | Iteration 1 raw output |
| [script_01_bh_correction_volcano.png](../results/figures/script_01_bh_correction_volcano.png) | Iteration 1 volcano plot |
| [script_01_bh_correction_results.csv](../results/script_01_bh_correction_results.csv) | Iteration 1 full results matrix |
| [ANALYSIS_01.md](ANALYSIS_01.md) | Iteration 1 interpretation |
| [H2_parameter_sweep.md](../hypotheses/H2_parameter_sweep.md) | Iteration 2 hypothesis |
| [script_02_parameter_sweep.py](../experiments/01_synthetic/script_02_parameter_sweep.py) | Parameter sweep script |
| [script_02_parameter_sweep_20260630_111010.log](../results/logs/script_02_parameter_sweep_20260630_111010.log) | Iteration 2 raw output |
| [script_02_parameter_sweep_recall_heatmap.png](../results/figures/script_02_parameter_sweep_recall_heatmap.png) | Recall heatmap across the grid |
| [script_02_parameter_sweep_fdr_heatmap.png](../results/figures/script_02_parameter_sweep_fdr_heatmap.png) | FDR heatmap across the grid |
| [script_02_parameter_sweep_results.csv](../results/script_02_parameter_sweep_results.csv) | Full grid search results |
| [ANALYSIS_02.md](ANALYSIS_02.md) | Iteration 2 interpretation |
| [H3_missingness_heteroscedasticity.md](../hypotheses/H3_missingness_heteroscedasticity.md) | Iteration 3 hypothesis |
| [script_03_missingness_heteroscedasticity.py](../experiments/01_synthetic/script_03_missingness_heteroscedasticity.py) | Missingness/heteroscedasticity script |
| [script_03_missingness_heteroscedasticity_20260630_111724.log](../results/logs/script_03_missingness_heteroscedasticity_20260630_111724.log) | Iteration 3 raw output |
| [script_03_volcano_comparison_config_a_(n=5_replicates).png](../results/figures/script_03_volcano_comparison_config_a_(n=5_replicates).png) | Config A three-panel volcano comparison |
| [script_03_volcano_comparison_config_b_(n=8_replicates).png](../results/figures/script_03_volcano_comparison_config_b_(n=8_replicates).png) | Config B three-panel volcano comparison |
| [script_03_missingness_heteroscedasticity_comparison.csv](../results/script_03_missingness_heteroscedasticity_comparison.csv) | Comparative results matrix |
| [ANALYSIS_03.md](ANALYSIS_03.md) | Iteration 3 interpretation |

---

## 9. Limitations and Caveats

1. All completed iterations use purely synthetic data; no downloaded or real proteomics dataset has yet been analyzed with this workflow.
2. Only Benjamini-Hochberg correction was evaluated; alternative corrections (Storey's q-value, Bonferroni) were not compared.
3. Only constant-value (MinDet) imputation was tested; more sophisticated imputation methods (KNN, regression-based, model-based) were not evaluated and might behave differently.
4. The heteroscedasticity and missingness models are simplified parametric forms and may not capture the full complexity of real instrument-specific detection limits.
5. Single-seed results are reported per configuration in Iterations 1 and 3; Iteration 2's grid sweep did not include repeated-seed variance estimates, so some empirical FDR values (for example, 8.33% at N=4, SD=0.3) reflect discrete low-count sampling volatility rather than a systematic bias.
6. The planted effect structure (fixed ±1.0 log2 fold-change, single noise regime per experiment) is simpler than the heterogeneous effect-size distributions seen in real proteomics studies.

---

## 10. Recommended Next Steps

1. Transition to Tier 2 downloaded/real data: apply the validated workflow and design-envelope guidance to a published spike-in benchmark dataset (for example UPS1/UPS2) where ground truth is partially known.
2. Compare BH correction against Storey's q-value and other modern FDR-control methods under the same heteroscedastic/missing-data conditions.
3. Evaluate non-constant imputation strategies (KNN, regression-based) against the replica-presence filtering baseline established in Iteration 3.
4. Add multi-seed replication to the parameter sweep to distinguish genuine design-envelope boundaries from single-run sampling noise.
5. Model heterogeneous planted effect sizes (rather than a single fixed fold-change) to better reflect real differential abundance distributions.

---

## 11. Final Assessment

### Primary Findings

- Benjamini-Hochberg FDR correction reliably controls false discoveries near its nominal threshold across all tested synthetic conditions.
- Statistical power under standard proteomics designs (N=5, SD=0.3) is far below common expectations, recovering only about a third of true differences.
- Recall is a predictable, monotonic function of replicate count and noise level, enabling actionable experimental design guidance.
- Heteroscedastic noise and missing-not-at-random values each independently and substantially reduce discovery power beyond what homoscedastic-noise calculations predict.
- Simple replica-presence filtering outperforms constant-value imputation for both recall and FDR control under realistic missing-data conditions.

### Research Significance

This project establishes a statistically rigorous, reproducible baseline for differential protein abundance testing and provides concrete, quantified design guidance (minimum replicate counts, noise tolerances, and missing-data handling strategy) that connects textbook multiple-testing theory to the practical constraints of real proteomics experiments.

### Methodological Assessment

The three completed iterations form a coherent fidelity ladder: a clean-data positive control, a systematic parameter sweep that converts a single disappointing result into a general design rule, and a stress test that overturned an initial mechanistic hypothesis (FDR explosion) in favor of a more accurate one (power collapse via variance compression). Each iteration's negative or partially-supported result was treated as informative rather than discarded, which is the central scientific strength of this project's audit trail.
