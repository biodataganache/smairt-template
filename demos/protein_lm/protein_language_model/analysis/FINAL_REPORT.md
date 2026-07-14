# Final Report — Protein Language Model

| Field | Details |
|---|---|
| Research Project | Protein Language Model |
| Study Scope | Synthetic protein grammar recovery, learned embedding separability, and frozen ESM-2 real protein family separation |
| Methodological Approach | Hypothesis-driven protein language model validation from controlled synthetic rules to real sequence embeddings |
| Generated | 2026-07-10 |
| Last Updated | 2026-07-10 |
| Report Status | FINAL |
| Primary Sources | [background/01_initial_question.md](../background/01_initial_question.md); [ANALYSIS_01.md](ANALYSIS_01.md); [ANALYSIS_04.md](ANALYSIS_04.md); [ANALYSIS_08.md](ANALYSIS_08.md); [ANALYSIS_09.md](ANALYSIS_09.md) |

---

## 1. Executive Summary

This project tested whether protein language models can learn planted sequence grammar and whether learned embeddings separate protein families for the right reasons. The research progressed through a fidelity ladder: validating a synthetic sequence generator, training nano masked language models on planted motifs, refining controls for family-separating embeddings, and finally applying a frozen pretrained ESM-2 model to real UniProt protein families.

The strongest synthetic result is that a nano-MLM recovered planted motif conservation nearly at the Bayes-optimal ceiling and, after multiple controlled redesigns, produced embeddings that perfectly separated two synthetic families by a learned identity-copy rule rather than composition or position shortcuts. The strongest real-data result is that frozen ESM-2 embeddings separated globins from cytochrome c proteins with held-out AUC 1.0000, while shuffled-label and length-only controls stayed at chance or worse.

The final conclusion is that masked-residue learning can encode family-relevant sequence structure in embeddings, but careful controls are essential to distinguish true learned grammar from trivial composition, position, or length artifacts.

---

## 2. Project Question and Study Scope

### Central Question

Can masked protein language models learn sequence grammar and produce embeddings that separate protein families based on meaningful learned structure rather than shortcuts?

### Study Scope

This report covers the synthetic generator and motif-learning rung, the synthetic embedding-separation rung, and the real pretrained ESM-2 family-separation rung.

### Model, Data, or Experimental Context

Synthetic experiments use 50-residue sequences with planted motifs, conservation sweeps, and two-family grammar rules. Later experiments use a frozen ESM-2 model as a feature extractor for reviewed UniProt globin and cytochrome c sequences.

### What This Study Does Not Resolve

The study does not train a competitive large protein language model, does not exhaustively benchmark family separation across many close homolog families, and does not fully disentangle every possible real-data biological confound.

---

## 3. Research Audit Trail

| Iteration | Hypothesis | Script or Method | Log or Evidence | Analysis | Status |
|---|---|---|---|---|---|
| 01 | [HYPOTHESIS_01.md](../hypotheses/HYPOTHESIS_01.md) | [script_01_validate_generator.py](../experiments/01_synthetic/script_01_validate_generator.py) | [script_01_validate_generator_20260629_094052.log](../results/logs/script_01_validate_generator_20260629_094052.log) | [ANALYSIS_01.md](ANALYSIS_01.md) | Supported |
| 04 | [HYPOTHESIS_04.md](../hypotheses/HYPOTHESIS_04.md) | [script_04_conservation_sweep.py](../experiments/01_synthetic/script_04_conservation_sweep.py) | [script_04_conservation_sweep_20260629_100305.log](../results/logs/script_04_conservation_sweep_20260629_100305.log) | [ANALYSIS_04.md](ANALYSIS_04.md) | Supported |
| 08 | [HYPOTHESIS_08.md](../hypotheses/HYPOTHESIS_08.md) | [script_08_identity_coupling.py](../experiments/01_synthetic/script_08_identity_coupling.py) | [script_08_identity_coupling_20260629_104619.log](../results/logs/script_08_identity_coupling_20260629_104619.log) | [ANALYSIS_08.md](ANALYSIS_08.md) | Supported |
| 09 | [HYPOTHESIS_09.md](../hypotheses/HYPOTHESIS_09.md) | [script_09_esm2_family_separation.py](../experiments/03_real_data/script_09_esm2_family_separation.py) | [script_09_esm2_family_separation_20260629_113657.log](../results/logs/script_09_esm2_family_separation_20260629_113657.log) | [ANALYSIS_09.md](ANALYSIS_09.md) | Supported |

---

## 4. Final Results Matrix

| Result Area | Best or Representative Case | Main Quantitative Outcome | Interpretation |
|---|---:|---:|---|
| Generator validation | Planted P-loop motif | Glycine invariant columns 1.000; masking 0.1496; reproducible seed | The synthetic ground truth is trustworthy. |
| Motif conservation sweep | p from 0.25 to 1.0 | Model accuracy tracks Bayes-optimal ceiling within max deviation 0.049 | Nano-MLM learns exactly the planted signal strength. |
| Synthetic embedding separation | Identity-copy family rule | Trained AUC 1.0000; untrained 0.5157; composition 0.5108 | Embedding separation is caused by learned grammar, not shortcuts. |
| Real family separation | Globin vs cytochrome c with frozen ESM-2 | AUC 1.0000; silhouette 0.3918; shuffled-label AUC 0.4375 | Real pretrained embeddings separate biologically distinct families. |

---

## 5. Iteration-Level Findings

### Rung 1 — Generator and Motif Learning

The generator correctly planted motif structure and avoided background artifacts after replacing flawed per-element sigma checks with column-level chi-square tests. Subsequent training showed motif recovery tracked planted conservation levels near the theoretical Bayes-optimal ceiling.

### Rung 2 — Learned Embedding Separation

Iterations 05-08 refined the embedding claim by eliminating confounds. Earlier attempts showed that motif position could be a free shortcut, sparse dependencies were too weak, and arbitrary permutation rules were too hard for the nano model. Iteration 08 solved the design: two families had identical marginals and composition, and only differed by a learnable identity-copy rule. The trained model achieved AUC 1.0000 while controls stayed near chance.

### Rung 3 — Real Protein Family Embeddings

Frozen ESM-2 embeddings separated reviewed UniProt globins from cytochrome c proteins with AUC 1.0000. Shuffled-label and length-only controls ruled out label leakage and simple sequence-length shortcuts.

---

## 6. Key Scientific Conclusions

1. Synthetic protein grammar must be validated before model training; otherwise metric artifacts can masquerade as biology.
2. Nano masked language models can recover planted motif conservation near the theoretical limit.
3. Learned embeddings can separate families by learned multi-position grammar when composition and position shortcuts are controlled.
4. Frozen pretrained ESM-2 embeddings contain sufficient real family signal to separate globins from cytochromes with a linear probe.
5. Controls are essential; without them, embedding separation can reflect shortcuts rather than learned biology.

---

## 7. Reproducibility Manifest

| Artifact | Purpose |
|---|---|
| [script_01_validate_generator.py](../experiments/01_synthetic/script_01_validate_generator.py) | Validates planted synthetic motif data. |
| [script_04_conservation_sweep.py](../experiments/01_synthetic/script_04_conservation_sweep.py) | Tests motif recovery versus planted conservation. |
| [script_08_identity_coupling.py](../experiments/01_synthetic/script_08_identity_coupling.py) | Tests learned-rule embedding separation. |
| [script_09_esm2_family_separation.py](../experiments/03_real_data/script_09_esm2_family_separation.py) | Tests real family separation with frozen ESM-2. |
| [script_08_auc_vs_controls.png](../results/figures/script_08_auc_vs_controls.png) | Synthetic trained-vs-control embedding result. |
| [script_09_auc_vs_controls.png](../results/figures/script_09_auc_vs_controls.png) | Real ESM-2 embedding controls. |

---

## 8. Limitations and Caveats

1. Synthetic identity-copy grammar is intentionally simplified.
2. Many results are single-seed and should be repeated for publication-grade uncertainty.
3. Real family testing used a small and relatively easy pair of protein families.
4. ESM-2 was used as a frozen feature extractor; this does not evaluate fine-tuning or competitive model training.

---

## 9. Recommended Next Steps

1. Test harder, closely related protein families.
2. Add k-fold and multi-seed validation.
3. Run layerwise probes to locate where family signal emerges in ESM-2.
4. Extend real-data controls to composition, length, taxonomy, and family-size matching.

---

## 10. Final Assessment

### Primary Findings

- Nano-MLMs can learn planted motif grammar in proportion to the available signal.
- Learned embeddings can separate synthetic families by learned rules when shortcuts are controlled.
- Frozen ESM-2 embeddings separate two real protein families with strong control behavior.

### Research Significance

The project establishes a coherent bridge from controlled synthetic grammar learning to real pretrained protein embeddings. It demonstrates both the promise of protein language model representations and the necessity of careful confound controls.

### Methodological Assessment

The research process is strong because failed or confounded intermediate designs were used to refine the hypothesis. The final synthetic and real experiments distinguish learned structure from simpler artifacts more convincingly than a single positive embedding result would have.
