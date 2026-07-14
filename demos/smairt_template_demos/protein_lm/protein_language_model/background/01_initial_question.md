# 01_initial_question.md

## Brief Background

A **protein language model (PLM)** treats an amino-acid sequence like a sentence:
each residue is a "token" drawn from a 20-letter alphabet, and the model learns
the statistical rules of how residues co-occur. Large PLMs (ESM-2, ProtT5) are
trained on hundreds of millions of sequences and capture structure and function,
but the *core idea* is small: a model that, shown a sequence with some residues
hidden ("masked"), predicts the missing residues better than chance. If a protein
family has a **conserved motif** (a short pattern that is almost always present,
like the phosphate-binding loop `G-x-G-x-x-G`), a working PLM should learn to fill
that motif back in with high confidence.

This SMAIRT project builds a **nano** PLM on a **synthetic corpus with a planted
grammar**: you generate protein-like sequences where you control the conserved
motif and the family-specific residue biases, so you know the ground truth. You
then train a tiny masked-language model and check that it **recovers the signal
you planted** (predicts masked residues above a frequency baseline, and nails the
conserved motif positions). It is CPU-only and runs in minutes; the only heavier
dependency than the other demos is `torch` (CPU build).

## Question

Can a **nano masked-language model** trained on synthetic protein-like sequences
learn the **planted grammar** of those sequences, predicting masked residues
above a frequency baseline and reconstructing a conserved motif far above chance?

## Hypothesis

A tiny transformer (1-2 layers, small embedding dimension, a few hundred thousand
parameters) trained with masked-residue prediction will (a) reach masked-token
accuracy **clearly above the unigram-frequency baseline**, and (b) predict the
**conserved-motif positions with near-perfect accuracy** while predicting
positions in variable regions only near the background rate. Learned per-sequence
embeddings will **separate two planted families** that differ in their motif or
residue composition.

## Evidence / metrics

- **Masked-token accuracy:** fraction of masked residues predicted correctly on a
  held-out set, compared against the unigram-frequency baseline (predict the most
  common residue). The model must beat the baseline by a clear margin.
- **Motif reconstruction:** accuracy on masked positions that fall inside the
  planted conserved motif should approach 1.0, well above accuracy on variable
  positions.
- **Family separation (Rung 2):** with two planted families, per-sequence
  embeddings (mean-pooled) should cluster by family (e.g. silhouette score, or
  a simple logistic-regression classifier AUC on the embeddings).
- **Learning curve / loss:** masked cross-entropy loss should drop steadily and
  the train/val gap should stay reasonable (no wild overfitting on the nano set).

## Domain Context

### Key terms
- **Token / vocabulary:** the 20 standard amino acids (plus special tokens like
  `[MASK]` and `[PAD]`). A char-level tokenizer maps each letter to an integer.
- **Masked language modeling (MLM):** hide a fraction of residues (e.g. 15%) and
  train the model to predict them from the surrounding context. This is how
  BERT and ESM-2 are trained.
- **Conserved motif:** a short residue pattern that is functionally important and
  therefore almost invariant across a family (e.g. the `G-x-G-x-x-G` Walker-A /
  P-loop, where `x` is any residue). The planted "grammar" the model should learn.
- **Embedding:** the model's internal vector representation of a residue or a
  whole sequence. Similar sequences land near each other in embedding space.
- **Unigram-frequency baseline:** the trivial predictor that always guesses the
  most frequent residue. Any real learning must beat it.
- **Synthetic data with known truth:** you generate sequences from a grammar you
  define (background residue distribution + planted motif at known positions), so
  you can check exactly what the model should have learned.

### How the synthetic corpus is built
1. Choose a sequence length (e.g. 40-60 residues) and a background amino-acid
   distribution (uniform, or biased like real proteins).
2. Plant a conserved motif at a fixed (or jittered) position, e.g. insert
   `G-x-G-x-x-G` where `x` is sampled from the background.
3. Sample many sequences; this is your training corpus with a known grammar.

### Fidelity ladder (SMAIRT data progression)
1. **Synthetic / planted (start here):** one family with a single conserved motif.
   Train the nano MLM and confirm it beats the frequency baseline and reconstructs
   the motif positions far above chance.
2. **Synthetic, harder:** two families with different motifs (or different residue
   biases). Show masked prediction still works, and that mean-pooled embeddings
   **separate the two families**. Probe how accuracy degrades with less training
   data, shorter training, or a noisier (less conserved) motif.
3. **Real (optional, later):** download a small set of real sequences from one
   family (e.g. a few dozen kinases or a Pfam family from UniProt/InterPro) and,
   instead of training from scratch, use a **tiny pretrained ESM-2 model**
   (`esm2_t6_8M`, ~8M params, CPU-runnable) to embed them and show the family
   clusters. Truth is now real biology, so discuss what the embeddings capture.

### Caveats
- A nano model on synthetic data proves the **mechanism**, not biological insight:
  the grammar is one you planted, so success means "the training loop works and
  the model can learn a known signal," not "this rivals ESM-2."
- Masked-token accuracy depends heavily on how conserved the planted motif is. A
  perfectly invariant motif is trivially learnable; the interesting science is how
  accuracy tracks the conservation level you set.
- Tiny models overfit small corpora. Use a held-out validation split and a fixed
  seed, and report the train/val gap honestly.
- The optional real rung uses a pretrained model for **embeddings only** (no
  fine-tuning); separating families there shows transfer, not that you trained a
  competitive PLM.

## Known design values (for validation)

| Item | Value |
|------|-------|
| Vocabulary | 20 amino acids + `[MASK]`, `[PAD]` (and optionally `[CLS]`) |
| Sequence length | your choice (e.g. 40-60 residues) |
| Mask fraction | ~15% of positions per sequence |
| Conserved motif | a known short pattern (e.g. `G-x-G-x-x-G`) at known positions |
| Model size | tiny: 1-2 layers, embed dim ~64, a few hundred K params |
| Baseline to beat | unigram-frequency (most-common-residue) masked accuracy |
| Motif-position accuracy target | near 1.0 (vs. background rate on variable positions) |
| Optional pretrained model | ESM-2 `esm2_t6_8M` (~8M params, CPU) for Rung 3 |
| random seed | fixed (reproducibility) |
