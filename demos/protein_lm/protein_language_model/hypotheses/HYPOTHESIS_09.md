# Hypothesis 09 — Pretrained ESM-2 embeddings separate two REAL protein families

## Status: PENDING

## Background

The synthetic ladder is complete:

- **Rung 1** (iters 01–04): generator validated; the nano-MLM beats the unigram
  baseline, reconstructs a conserved motif, and tracks the Bayes-optimal
  conservation curve.
- **Rung 2** (iters 05–08): a single nano-MLM learns multi-position structure and,
  in iteration 08 ([`ANALYSIS_08.md`](../analysis/ANALYSIS_08.md)), its mean-pooled
  embeddings **separate two planted families by a learned rule** (trained AUC 1.000;
  composition and untrained controls at chance) — the embedding claim demonstrated
  in its strongest, confound-free form.

The remaining rung in the background document
([`01_initial_question.md`](../background/01_initial_question.md), "Fidelity ladder"
#3) is **real biology**: instead of training from scratch, use a **tiny pretrained
ESM-2** (`esm2_t6_8M_UR50D`, ~8M params, CPU-runnable) for **embeddings only** (no
fine-tuning) and show that two real protein families cluster. Truth is now real
sequences, so we discuss what the embeddings capture.

## Hypothesis Statement

**Prediction**: Mean-pooled per-residue embeddings from a frozen pretrained ESM-2
(`esm2_t6_8M`) will **separate two distinct real protein families** fetched live
from UniProt. A linear probe on the embeddings will classify family near perfectly
(AUC ≥ 0.95) and the families will form visibly distinct clusters (silhouette
clearly positive), whereas a **shuffled-label control** sits at chance.

**Rationale**: ESM-2 was pretrained by masked-residue modeling on ~50M UniRef50
sequences — the same objective our nano-MLM used, at scale. It should encode
family-distinguishing sequence/structure signal in its residue embeddings, so
mean-pooling yields family-separable per-sequence vectors **without any
fine-tuning**. This shows *transfer* from a real PLM, not that we trained a
competitive model.

**Success criteria**: see sub-hypotheses.

## Experimental Design

- **Data fetch script**: `experiments/03_real_data/fetch_uniprot_families.py`
  - Two families via the UniProt REST API (`rest.uniprot.org`), reviewed
    (Swiss-Prot) only, length 50–400, ~30 sequences each, written as FASTA to
    `data/downloaded/`. Fixed deterministic queries (logged) for reproducibility.
  - **Family 1**: Globins (Pfam **PF00042**) — e.g. hemoglobin/myoglobin.
  - **Family 2**: Cytochrome c (Pfam **PF00034**).
  - These are small, well-characterized, and structurally distinct → a fair,
    interpretable real-world test.
- **Embedding/eval script**: `experiments/03_real_data/script_09_esm2_family_separation.py`
  - Load `esm2_t6_8M_UR50D` via `fair-esm` (CPU); embed each sequence as the mean
    over per-residue representations from the final layer (layer 6), excluding
    BOS/EOS/pad.
  - Metrics: logistic-regression probe AUC (held-out split), silhouette score, 2D
    PCA visualization, colored by family.
- **Controls**:
  1. **Shuffled-label control**: same embeddings, family labels permuted → AUC ≈ 0.5
     (guards against a probe that "cheats" on split leakage / class imbalance).
  2. **Sequence-length control**: report whether a length-only classifier separates
     the families, so we can state separation is not merely a length artifact.

## Sub-Hypotheses

### H_09A: ESM-2 embeddings separate the families
- **Success criteria**: logistic-regression probe AUC on held-out embeddings ≥ 0.95.

### H_09B: Families cluster
- **Success criteria**: silhouette score of embeddings (family labels) ≥ 0.20.

### H_09C: Controls behave
- **Success criteria**: shuffled-label AUC ≤ 0.65; and separation is not explained
  by sequence length alone (length-only AUC reported; embedding AUC clearly higher,
  or length-only ≤ 0.75).

## Dependencies

- torch (CPU 2.12.1), numpy, matplotlib, **fair-esm 2.0.0** (installed), internet
  (UniProt REST + one-time ESM-2 weight download, cached under torch hub).
- Builds on the embedding methodology from
  [`script_08_identity_coupling.py`](../experiments/01_synthetic/script_08_identity_coupling.py)
  (mean-pool → linear-probe AUC → PCA), now applied to a frozen real PLM.

## Design Parameters

| Parameter | Value |
|-----------|-------|
| Seed | 1024 |
| Pretrained model | ESM-2 `esm2_t6_8M_UR50D` (~8M params, 6 layers, CPU) |
| Embedding | mean over final-layer per-residue reps (exclude BOS/EOS/pad) |
| Family 1 | Globin, Pfam PF00042 (~30 reviewed seqs) |
| Family 2 | Cytochrome c, Pfam PF00034 (~30 reviewed seqs) |
| Sequence length filter | 50–400 residues |
| Probe | logistic regression (held-out split) |
| Metrics | AUC, silhouette, 2D PCA |
| Controls | shuffled-label AUC; length-only AUC |

## Results

*(Filled in after experiment runs — see [`analysis/ANALYSIS_09.md`](../analysis/ANALYSIS_09.md))*

## Notes

- **No fine-tuning**: ESM-2 is used purely as a fixed feature extractor; success
  shows transfer, not that we trained a competitive PLM (per the background
  document's caveat).
- If UniProt is transiently unavailable, the fetch script caches FASTA to
  `data/downloaded/` so the embedding step is reproducible offline thereafter.
- Real families differ in length/composition as well as deep structure; the
  length-only control keeps the interpretation honest about *what* separates them.
