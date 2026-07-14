# Real Data Experiments

The final phase: testing on your actual target data.


## Purpose

- Validate whether approaches that worked on synthetic and benchmark data transfer
- Test the actual hypothesis with actual target data
- Internal checks become possible


## Scripts in This Folder

| Script | Data Used | Hypothesis Tested | Result | Date |
|--------|-----------|-------------------|--------|------|
| `fetch_uniprot_families.py` | UniProt REST (Swiss-Prot) | data acquisition for HYPOTHESIS_09 | OK — 30 globin (PF00042) + 30 cytochrome c (PF00034) → `data/downloaded/rung3_two_families.fasta` | 2026-06-29 |
| `script_09_esm2_family_separation.py` | `rung3_two_families.fasta` | HYPOTHESIS_09 (H_09A/B/C): frozen ESM-2 `esm2_t6_8M` embeddings separate two real families | **PASS — ALL CHECKS.** probe AUC=1.000, silhouette=0.392; shuffled-label 0.438 & length-only 0.221 (controls behave). Transfer from a real PLM, no fine-tuning | 2026-06-29 |

## Naming Convention

`script_XX_brief_description.py`

## Output Convention

1. Output to console for immediate feedback
2. Output to log file via `TeeLogger`: `../../results/logs/script_XX_description_TIMESTAMP.log`
3. Reference hypothesis file in script docstring (audit trail)
