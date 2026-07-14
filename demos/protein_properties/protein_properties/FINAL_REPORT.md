# Final Report — Protein Properties

| Field | Details |
|---|---|
| Research Project | Protein Properties |
| Study Scope | Protein molecular weight, isoelectric point, hydropathy calculation, and membrane-vs-soluble classification |
| Methodological Approach | Hypothesis-driven computational protein feature validation and benchmark classification |
| Generated | 2026-07-10 |
| Last Updated | 2026-07-10 |
| Report Status | FINAL |
| Primary Sources | [background/01_initial_question.md](background/01_initial_question.md); [ANALYSIS_01.md](analysis/ANALYSIS_01.md); [ANALYSIS_02.md](analysis/ANALYSIS_02.md); [ANALYSIS_03.md](analysis/ANALYSIS_03.md) |

---

## 1. Executive Summary

This project evaluated whether simple sequence-derived protein properties can support reliable classification of membrane-like and soluble-like proteins. The study first validated molecular weight, isoelectric point, and GRAVY calculators against hand-computed and reference proteins, then tested classification on synthetic composition-biased protein pools, and finally benchmarked the approach on reviewed human UniProt proteins.

The main positive result is that sequence hydropathy is a powerful classifier when the membrane signal is distributed across the whole sequence. GRAVY achieved 100% accuracy and AUROC 1.0000 on synthetic membrane-like versus soluble-like pools. The main boundary finding is that whole-sequence GRAVY fails on real proteins when localized transmembrane helices are diluted by large soluble domains. A 19-residue sliding-window GRAVY feature restored real-data accuracy to 83.33%, showing that localized hydropathy is the appropriate feature family for real membrane classification.

---

## 2. Project Question and Study Scope

### Central Question

Can basic protein sequence properties distinguish membrane-like proteins from soluble-like proteins, and where do whole-sequence features break down?

### Study Scope

This report covers calculator validation, synthetic classification, and downloaded benchmark classification on reviewed human UniProt proteins.

### Model, Data, or Experimental Context

The project calculates molecular weight, pI, and GRAVY directly from amino-acid sequence. Classification experiments compare whole-sequence features with localized 19-residue window hydropathy.

### What This Study Does Not Resolve

The study does not model three-dimensional structure, signal peptides, beta-barrels, lipid anchors, post-translational modifications, or full annotation-scale benchmarking.

---

## 3. Research Audit Trail

| Iteration | Hypothesis | Script or Method | Log or Evidence | Analysis | Status |
|---|---|---|---|---|---|
| 01 | [HYPOTHESIS_01.md](protein_properties/protein_properties/hypotheses/HYPOTHESIS_01.md) | [script_01_validate_calculators.py](protein_properties/protein_properties/experiments/01_synthetic/script_01_validate_calculators.py) | [script_01_validate_calculators_20260630_090732.log](protein_properties/protein_properties/results/logs/script_01_validate_calculators_20260630_090732.log) | [ANALYSIS_01.md](protein_properties/protein_properties/analysis/ANALYSIS_01.md) | Supported |
| 02 | [HYPOTHESIS_02.md](protein_properties/protein_properties/hypotheses/HYPOTHESIS_02.md) | [script_02_synthetic_classification.py](protein_properties/protein_properties/experiments/01_synthetic/script_02_synthetic_classification.py) | [script_02_synthetic_classification_20260630_090904.log](protein_properties/protein_properties/results/logs/script_02_synthetic_classification_20260630_090904.log) | [ANALYSIS_02.md](protein_properties/protein_properties/analysis/ANALYSIS_02.md) | Supported |
| 03 | [HYPOTHESIS_03.md](protein_properties/protein_properties/hypotheses/HYPOTHESIS_03.md) | [script_04_benchmark_classification.py](protein_properties/protein_properties/experiments/02_downloaded/script_04_benchmark_classification.py) | [script_04_benchmark_classification_20260630_091724.log](protein_properties/protein_properties/results/logs/script_04_benchmark_classification_20260630_091724.log) | [ANALYSIS_03.md](protein_properties/protein_properties/analysis/ANALYSIS_03.md) | Partially supported |

---

## 4. Final Results Matrix

| Result Area | Best or Representative Case | Main Quantitative Outcome | Interpretation |
|---|---:|---:|---|
| Calculator validation | Human ubiquitin and short peptides | MW error 0.0004%; pI error <0.001; GRAVY exact | Feature calculations are mathematically reliable under the chosen formulas. |
| Synthetic classification | GRAVY-only logistic regression | 100% test accuracy; AUROC 1.0000 | Whole-sequence hydropathy perfectly separates composition-biased pools. |
| Real benchmark classification | 19-residue max-window GRAVY | Accuracy improves from 41.67% whole-sequence to 83.33% window-based | Local hydropathy resolves transmembrane signal dilution in real proteins. |

---

## 5. Iteration-Level Findings

### Iteration 01 — Property Calculator Validation

The calculators for molecular weight, GRAVY, and pI matched reference expectations for short peptides and human ubiquitin. This established a rigorous feature-extraction foundation.

### Iteration 02 — Synthetic Membrane vs. Soluble Classification

GRAVY separated synthetic membrane-like and soluble-like pools perfectly, while pI and molecular weight behaved close to random. This supported hydropathy as the correct discriminating feature under whole-sequence compositional shifts.

### Iteration 03 — Real-World Comparative Classification

Whole-sequence GRAVY collapsed to 41.67% accuracy on real reviewed human proteins because localized transmembrane segments were diluted by soluble domains. A maximum 19-residue window GRAVY feature restored accuracy to 83.33%, but false positives from packed soluble hydrophobic cores prevented reaching the 90% target.

---

## 6. Key Scientific Conclusions

1. The implemented sequence property calculators are accurate for standard amino-acid sequences.
2. Average hydropathy is highly discriminative when membrane signal is sequence-wide.
3. Whole-sequence hydropathy is not sufficient for real proteins with localized membrane segments.
4. Sliding-window hydropathy substantially improves biological relevance but can confuse soluble hydrophobic cores with transmembrane helices.

---

## 7. Reproducibility Manifest

| Artifact | Purpose |
|---|---|
| [script_01_validate_calculators.py](protein_properties/protein_properties/experiments/01_synthetic/script_01_validate_calculators.py) | Validates MW, pI, and GRAVY calculators. |
| [script_02_synthetic_classification.py](protein_properties/protein_properties/experiments/01_synthetic/script_02_synthetic_classification.py) | Tests synthetic membrane-vs-soluble classification. |
| [script_04_benchmark_classification.py](protein_properties/protein_properties/experiments/02_downloaded/script_04_benchmark_classification.py) | Tests real reviewed UniProt classification. |
| [gravy_distributions.png](protein_properties/protein_properties/results/figures/gravy_distributions.png) | Synthetic hydropathy separation plot. |
| [uniprot_distribution_comparison.png](protein_properties/protein_properties/results/figures/uniprot_distribution_comparison.png) | Whole-sequence vs window GRAVY comparison. |

---

## 8. Limitations and Caveats

1. pI calculations depend on the selected pKa scale.
2. Whole-sequence features can hide localized structural signals.
3. The real benchmark contains only 12 proteins and should be expanded.
4. Sequence-only hydropathy does not distinguish all hydrophobic cores from true membrane spans.

---

## 9. Recommended Next Steps

1. Expand to a larger reviewed UniProt benchmark.
2. Add dual-threshold rules combining localized hydropathy with charge or flanking polarity.
3. Evaluate beta-barrel and lipid-anchored proteins separately.
4. Compare against established transmembrane prediction tools.

---

## 10. Final Assessment

### Primary Findings

- Feature calculators are validated against reference values.
- GRAVY is a perfect classifier under synthetic whole-sequence hydropathy shifts.
- Real protein classification requires localized hydropathy features.

### Research Significance

The project establishes both the utility and the boundary of simple biophysical sequence features. It shows that feature engineering must match the biological scale of the signal: whole-sequence averages work for global composition shifts, while transmembrane classification requires local-window detection.

### Methodological Assessment

The research progression successfully moved from exact feature validation to synthetic separation and then to real-data failure analysis. The real-data partial failure strengthened the study by revealing the soluble-domain dilution effect and motivating a biologically more appropriate windowed feature.
