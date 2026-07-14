# Final Report — Proteomics Differential Expression

| Field | Details |
|---|---|
| Research Project | Proteomics Differential Expression |
| Study Scope | Synthetic differential protein abundance testing under multiple-testing correction, replicate/noise design, heteroscedasticity, and missingness |
| Methodological Approach | Hypothesis-driven statistical simulation and workflow stress testing |
| Generated | 2026-07-10 |
| Last Updated | 2026-07-10 |
| Report Status | FINAL |
| Primary Sources | [background/01_initial_question.md](background/01_initial_question.md); [ANALYSIS_01.md](analysis/ANALYSIS_01.md); [ANALYSIS_02.md](analysis/ANALYSIS_02.md); [ANALYSIS_03.md](analysis/ANALYSIS_03.md) |

---

## 1. Executive Summary

This project evaluated how standard differential-abundance testing behaves in quantitative proteomics when the ground truth is known. The workflow used synthetic protein abundance matrices with planted true differentially abundant proteins, then tested Welch's t-test with Benjamini-Hochberg correction under clean Gaussian noise, replicate/noise parameter sweeps, heteroscedastic noise, and MNAR missingness.

The central positive result is that Benjamini-Hochberg correction effectively controls false discoveries under clean synthetic assumptions. The key boundary finding is that controlled FDR can come with severe loss of recall, especially under low replicate counts, standard noise, heteroscedastic abundance-dependent variance, and constant-value missing-data imputation.

The most actionable conclusion is methodological: discovery-oriented quantitative proteomics designs require adequate replication, low measurement noise, and careful missingness handling. Flat local-minimum imputation can destroy power; replicate-presence filtering preserved FDR while retaining more recall under the tested conditions.

---

## 2. Project Question and Study Scope

### Central Question

Under what experimental designs and data artifacts can differential protein abundance testing recover true changes while controlling false discovery rate?

### Study Scope

This report covers the completed synthetic validation phase: baseline multiple-testing correction, replicate/noise parameter sweeps, heteroscedastic noise, MNAR missingness, and imputation/filtering comparisons.

### Model, Data, or Experimental Context

The simulations use 2,000 proteins with 100 planted true differentially abundant proteins. The statistical workflow applies per-protein Welch's t-tests followed by Benjamini-Hochberg correction. Later iterations introduce replicate count variation, noise variation, abundance-dependent heteroscedasticity, logistic limit-of-detection missingness, MinDet imputation, and replicate-presence filtering.

### What This Study Does Not Resolve

The current evidence is simulation-based. It does not yet validate on real mass-spectrometry benchmark datasets, peptide-level aggregation pipelines, batch effects, normalization choices, protein inference ambiguity, or advanced imputation algorithms.

---

## 3. Research Audit Trail

| Iteration | Hypothesis | Script or Method | Log or Evidence | Analysis | Status |
|---|---|---|---|---|---|
| 01 | [H1_bh_correction_baseline.md](proteomics_de/proteomics_de/hypotheses/H1_bh_correction_baseline.md) | [script_01_bh_correction.py](proteomics_de/proteomics_de/experiments/01_synthetic/script_01_bh_correction.py) | [script_01_bh_correction_20260630_110058.log](proteomics_de/proteomics_de/results/logs/script_01_bh_correction_20260630_110058.log) | [ANALYSIS_01.md](proteomics_de/proteomics_de/analysis/ANALYSIS_01.md) | Partially supported |
| 02 | [H2_parameter_sweep.md](proteomics_de/proteomics_de/hypotheses/H2_parameter_sweep.md) | [script_02_parameter_sweep.py](proteomics_de/proteomics_de/experiments/01_synthetic/script_02_parameter_sweep.py) | [script_02_parameter_sweep_20260630_111010.log](proteomics_de/proteomics_de/results/logs/script_02_parameter_sweep_20260630_111010.log) | [ANALYSIS_02.md](proteomics_de/proteomics_de/analysis/ANALYSIS_02.md) | Supported with statistical caveats |
| 03 | [H3_missingness_heteroscedasticity.md](proteomics_de/proteomics_de/hypotheses/H3_missingness_heteroscedasticity.md) | [script_03_missingness_heteroscedasticity.py](proteomics_de/proteomics_de/experiments/01_synthetic/script_03_missingness_heteroscedasticity.py) | [script_03_missingness_heteroscedasticity_20260630_111724.log](proteomics_de/proteomics_de/results/logs/script_03_missingness_heteroscedasticity_20260630_111724.log) | [ANALYSIS_03.md](proteomics_de/proteomics_de/analysis/ANALYSIS_03.md) | Partially supported |

---

## 4. Final Results Matrix

| Result Area | Best or Representative Case | Main Quantitative Outcome | Interpretation |
|---|---:|---:|---|
| Baseline BH correction | N=5 per group, sigma=0.3 | FDR 2.70%; recall 36.00% | FDR controlled, but power was much lower than expected. |
| Replicate/noise design sweep | N=6, sigma=0.3; N=5, sigma=0.2 | Recall 87.00% and 95.00%, respectively | Adequate replication or reduced noise can recover high power under clean assumptions. |
| Heteroscedasticity and missingness | Config B, replicate filter | Recall 45.00%; FDR 4.26% | Filtering preserved FDR and retained more power than MinDet imputation under MNAR missingness. |

---

## 5. Iteration-Level Findings

### Iteration 01 — Benjamini-Hochberg Baseline

The baseline study showed that uncorrected p-values produced a catastrophic empirical FDR of 47.31%, while BH correction reduced FDR to 2.70%. However, recall dropped to 36.00%, refuting the expected 70% recovery threshold under N=5, sigma=0.3, and two-fold effect size.

### Iteration 02 — Replicate and Noise Parameter Sweep

The parameter sweep mapped the feasibility envelope for high recall. At standard noise sigma=0.3, N>=6 was needed for recall above 70%. If N=5 was fixed, noise had to drop to sigma<=0.2 for high recall. Very low sample sizes such as N=3 were effectively powerless under realistic noise.

### Iteration 03 — Missingness and Heteroscedasticity

Introducing abundance-dependent noise caused severe power loss even before missingness. MinDet imputation did not primarily explode FDR; instead, it destroyed power by compressing group differences and corrupting variance behavior. Replicate-presence filtering gave the best balance of controlled FDR and retained recall under the tested missingness assumptions.

---

## 6. Key Scientific Conclusions

1. BH correction controls false discoveries under clean assumptions but can severely reduce sensitivity.
2. Replicate count and measurement noise jointly determine whether true differential abundance can be recovered.
3. Heteroscedasticity invalidates overly optimistic homoscedastic power expectations.
4. Constant local-minimum imputation can suppress true differences and should not be treated as a neutral preprocessing step.
5. Replicate-presence filtering is a defensible baseline missingness strategy under the simulated MNAR conditions.

---

## 7. Reproducibility Manifest

| Artifact | Purpose |
|---|---|
| [script_01_bh_correction.py](proteomics_de/proteomics_de/experiments/01_synthetic/script_01_bh_correction.py) | Baseline Welch t-test plus BH correction. |
| [script_02_parameter_sweep.py](proteomics_de/proteomics_de/experiments/01_synthetic/script_02_parameter_sweep.py) | Replicate/noise feasibility mapping. |
| [script_03_missingness_heteroscedasticity.py](proteomics_de/proteomics_de/experiments/01_synthetic/script_03_missingness_heteroscedasticity.py) | Heteroscedasticity, MNAR missingness, imputation, and filtering comparison. |
| [script_01_bh_correction_volcano.png](proteomics_de/proteomics_de/results/figures/script_01_bh_correction_volcano.png) | Baseline volcano plot. |
| [script_02_parameter_sweep_recall_heatmap.png](proteomics_de/proteomics_de/results/figures/script_02_parameter_sweep_recall_heatmap.png) | Recall design landscape. |
| [script_02_parameter_sweep_fdr_heatmap.png](proteomics_de/proteomics_de/results/figures/script_02_parameter_sweep_fdr_heatmap.png) | FDR design landscape. |
| [script_03_missingness_heteroscedasticity_comparison.csv](proteomics_de/proteomics_de/results/script_03_missingness_heteroscedasticity_comparison.csv) | Comparative results matrix. |

---

## 8. Limitations and Caveats

1. All results are synthetic and require benchmark validation.
2. The simulations simplify normalization, batch effects, peptide aggregation, and protein inference.
3. Empirical FDR varies stochastically in single-seed simulations.
4. Only a small set of missingness and imputation strategies was tested.

---

## 9. Recommended Next Steps

1. Validate the design rules on a published spike-in proteomics dataset.
2. Evaluate non-constant imputation strategies such as KNN, random forest, or model-based imputation.
3. Add normalization and batch-effect simulations.
4. Repeat key sweeps across multiple seeds and summarize uncertainty.

---

## 10. Final Assessment

### Primary Findings

- Multiple-testing correction controls FDR but can sharply reduce recall.
- High-power proteomics designs require sufficient replication or reduced noise.
- Heteroscedasticity and missingness are major determinants of real discovery power.

### Research Significance

The study provides practical design boundaries for quantitative proteomics experiments and identifies missing-data handling as a central determinant of reliable differential abundance discovery.

### Methodological Assessment

The research progression moved from a clean baseline to a design sweep and then to harder synthetic artifacts. This sequence separated statistical power limits from missingness-processing artifacts and produced actionable guidance for future benchmark validation.
