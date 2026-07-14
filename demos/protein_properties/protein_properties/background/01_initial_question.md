# 01_initial_question.md

## Brief Background

Every protein's behavior is shaped by simple, computable properties of its amino-
acid sequence: its **molecular weight (MW)**, its **isoelectric point (pI**, the
pH at which it carries no net charge), and its average **hydrophobicity** (often
summarized as **GRAVY**, the grand average of hydropathy). These properties
predict practical things, for example whether a protein is likely to sit in a
membrane (hydrophobic) or dissolve in water (hydrophilic), and how it will behave
in techniques like isoelectric focusing.

This SMAIRT project computes these properties from sequence and **validates them
against known answers**: short sequences where MW can be summed by hand, and
reference proteins with published MW/pI values. Once the calculators are trusted,
it uses them as features to ask a biological question: **can a simple
hydrophobicity-based rule separate membrane proteins from soluble ones?**

It is CPU-only, pure Python (numpy/pandas/scikit-learn/matplotlib), and needs no
external data to get started.

## Question

From an amino-acid sequence alone, can we compute MW, pI, and GRAVY accurately
(validated against references), and can a **hydrophobicity threshold or simple
classifier separate membrane proteins from soluble proteins**?

## Hypothesis

Per-residue calculations of MW, pI, and GRAVY will match reference values for
known proteins within a small tolerance. Membrane proteins, which are enriched in
hydrophobic residues, will have **systematically higher GRAVY** than soluble
proteins, so a simple threshold on GRAVY (or a one-feature classifier) will
separate the two classes well above chance, while pI alone will not.

## Evidence / metrics

- **Validation accuracy:** computed MW (and pI) for reference proteins match
  published values within tolerance (e.g. MW within ~0.1%).
- **Separation metric:** classification accuracy / AUC for membrane vs. soluble
  using GRAVY (and how much MW or pI add).
- **Distribution check:** GRAVY histograms for the two classes should be visibly
  shifted if the hypothesis holds.
- **Feature importance:** which property best separates the classes.

## Domain Context

### The properties
- **Molecular weight (MW):** sum of residue (monoisotopic or average) masses +
  one water for the terminal groups. Exactly checkable on short sequences.
- **Isoelectric point (pI):** the pH where net charge = 0. Computed by solving
  the charge-vs-pH curve using standard pKa values for ionizable groups (N-/C-
  termini and D, E, C, Y, H, K, R).
- **GRAVY:** the average of a per-residue hydropathy scale (the Kyte-Doolittle
  scale is standard). Positive = hydrophobic, negative = hydrophilic.

### Why membrane vs. soluble
- Membrane-spanning regions are rich in hydrophobic residues (e.g. L, I, V, F),
  so transmembrane proteins tend to have higher GRAVY than cytosolic, water-
  soluble proteins. This is the planted signal the classifier should pick up.

### Fidelity ladder (SMAIRT data progression)
1. **Synthetic / hand-checked:** compute MW and GRAVY for tiny sequences you can
   verify by hand; check pI on a couple of reference proteins. (Start here.)
2. **Synthetic, harder:** generate two pools of sequences, one biased toward
   hydrophobic residues ("membrane-like") and one toward charged/polar residues
   ("soluble-like"), then show GRAVY separates them and a one-feature classifier
   recovers the planted labels.
3. **Real (optional, later):** download a small labeled set from UniProt (a
   handful of known transmembrane vs. soluble proteins) and test whether the
   GRAVY rule still separates them. Truth is now real biology, not planted, so
   discuss misclassifications honestly.

### Caveats
- GRAVY is a coarse, whole-sequence average; real membrane prediction uses
  per-window hydropathy and topology models. A single threshold will misclassify
  edge cases (e.g. lipid-anchored or partially buried proteins). Naming these
  limits next to the result is part of the SMAIRT method.

## Known reference values (for validation)

| Item | Value |
|------|-------|
| Water (for MW terminal groups) | ~18.02 Da (average) / 18.0106 (monoisotopic) |
| Hydropathy scale | Kyte-Doolittle (standard) |
| Ionizable groups for pI | N-term, C-term, D, E, C, Y, H, K, R |
| GRAVY sign | positive = hydrophobic, negative = hydrophilic |
| Validation target | MW within ~0.1% of a reference tool (e.g. ExPASy ProtParam) |
| random seed | fixed (reproducibility) |
