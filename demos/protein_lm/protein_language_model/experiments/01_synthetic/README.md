# Synthetic Data Experiments

Some questions (not all) might be amenable to experimentation with synthetic
data. This is convenient, especially at the start of the process, because it
makes the scripts self-contained and the data can be synthesized with different
noise levels, and with different types of structures.

## Purpose

- Fast iteration without dependencies
- Test if code works before committing to real data
- Very rapid turnaround time

## Scripts in This Folder

| Script | Hypothesis Tested | Result | Date |
|--------|-------------------|--------|------|
| `script_01_validate_generator.py` | HYPOTHESIS_01 (H_01A, H_01B): generator plants the `G-x-G-x-x-G` motif exactly and masking plumbing is correct | PASS — all checks; baseline to beat = 0.1076 | 2026-06-29 |
| `script_02_train_nano_mlm.py` | HYPOTHESIS_02 (H_02A/B/C): nano-MLM beats baseline & reconstructs motif | PARTIAL — motif acc=1.000, bg=0.048, loss↓ (H_02B/C PASS); overall acc 0.1072 ties baseline (H_02A inconclusive — motif residue = baseline's guess) | 2026-06-29 |
| `script_03_discriminating_motif.py` | HYPOTHESIS_03 (H_03A/B/C/D): multi-residue motif `GKTYRG` + dual baselines | PASS — all checks; model acc 0.160 vs global baseline 0.084, motif=1.000, reaches per-column ceiling 0.164 | 2026-06-29 |
| `script_04_conservation_sweep.py` | HYPOTHESIS_04 (H_04A/B/C): motif accuracy tracks conservation level p∈{1.0,0.9,0.7,0.5,0.25} | PASS — motif acc tracks Bayes-optimal p+(1-p)/20 (max dev 0.049), monotone, bg at chance | 2026-06-29 |
| `script_05_two_family_embeddings.py` | HYPOTHESIS_05 (H_05A/B/C/D): mean-pooled embeddings separate two families differing by motif position | PARTIAL — trained AUC=0.9998 & both-family motif=1.000 (H_05A/D PASS); composition control at chance (0.486 ✓) but untrained control also separates (0.978) → position is free to the architecture, so the test can't isolate *learning* (H_05C FAIL); silhouette wrong metric (H_05B FAIL). Fix → iteration 06 covariation design | 2026-06-29 |
| `script_06_covariation_families.py` | HYPOTHESIS_06 (H_06A/B/C): families differ ONLY by a single pairwise coupling i↔j (equal marginals) | PARTIAL — both controls now at chance (untrained 0.486, comp 0.476) so the iter-05 confound is fixed (H_06B PASS); but trained model also at chance (0.485) and never learned the coupling (j-acc 0.055) — a single pair barely affects the MLM loss (H_06A/C FAIL). Fix → iteration 07 many bijection-coupled pairs | 2026-06-29 |
| `script_07_bijection_coupling.py` | HYPOTHESIS_07 (H_07A/B/C): K=10 bijection-coupled pairs (uniform marginals) | PARTIAL — controls clean at chance (untrained 0.520, comp 0.510 → H_07B PASS); trained model now ABOVE controls (AUC 0.604, FamA coupled-col acc 0.183 vs chance 0.054) so signal is loss-relevant, but arbitrary 20-symbol permutation too hard at nano budget (H_07A/C FAIL). Fix → iteration 08 identity-copy rule | 2026-06-29 |
| `script_08_identity_coupling.py` | HYPOTHESIS_08 (H_08A/B/C): K=10 identity-copy pairs `seq[b]=seq[a]` (uniform marginals, 40 epochs) | **PASS — ALL CHECKS.** Trained AUC=1.000, both controls at chance (untrained 0.516, comp 0.511), copy rule learned perfectly (FamA coupled-col acc 1.000 vs FamB 0.049). Airtight + learnable → closes the synthetic-rung embedding claim | 2026-06-29 |

## Naming Convention

`script_XX_brief_description.py`

## Output Convention

1. Output to console for immediate feedback
2. Output to log file via `TeeLogger`: `../../results/logs/script_XX_description_TIMESTAMP.log`
3. Reference hypothesis file in script docstring (audit trail)
