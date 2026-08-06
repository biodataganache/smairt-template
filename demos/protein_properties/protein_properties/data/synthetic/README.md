# Synthetic data

Generated in-project, not obtained from an external source.

| Filename | Rows | Contents | SHA-256 |
|---|---|---|---|
| `synthetic_protein_dataset.csv` | 1000 | sequence, length, label, class_name, molecular_weight, gravy, pi | `71489bcf848b54cee2ef4f1b4f05537203c538f1e5dd4c182c56e8a42e40e42a` |

## How to regenerate

```bash
python3 experiments/01_synthetic/script_02_synthetic_classification.py
```

Deterministic given the seed, so a regenerated file matches the checksum above.

| Parameter | Value | Where |
|---|---|---|
| Random seed | 1024 | `script_02_synthetic_classification.py:43` |
| Sequences | 1000 | generated in `script_02_synthetic_classification.py` |
| Train/test split seed | 1024, stratified | `script_02_synthetic_classification.py:178` |

## Why this is an easy case on purpose

Sequences are drawn from residue distributions chosen to make transmembrane and soluble classes
separable by average hydropathy. Iteration 02 reaches AUROC 1.0000 on GRAVY alone, while pI and
molecular weight stay at chance — which is the point. It establishes that the calculators work and
that the signal is where the biology says it should be, before iteration 03 shows the same approach
degrading on real human proteins where transmembrane helices are diluted by long soluble regions.

An AUROC of 1.0 here is a property of the generator, not evidence about real proteins.
