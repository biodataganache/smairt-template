# 01_initial_question.md

## Brief Background

In bottom-up (shotgun) proteomics, proteins are not measured directly. They are
first **cut into peptides** by a protease (almost always **trypsin**), and the
mass spectrometer measures those peptides. To know which protein a measurement
came from, you must predict, for any protein sequence, **what peptides trypsin
would produce**. This in-silico digestion is the foundation of every database
search and is simple enough to compute exactly.

This SMAIRT project builds a tryptic-digestion calculator and **validates it
against known answers**: short sequences where you can list the expected
peptides by hand, and reference peptide masses you can check against published
values. Because the rules are deterministic, "correct" is unambiguous, which
makes it an ideal first project for learning the SMAIRT loop.

It is CPU-only and pure Python (standard library), and needs no external data.

## Question

For a given protein sequence, what set of peptides does trypsin produce, and
which of those peptides fall in the **mass and length window a mass
spectrometer can actually observe**?

## Hypothesis

Implementing the canonical trypsin rule (cleave after K or R, but **not before
P**) will reproduce the expected peptides for hand-checkable test sequences
exactly. Allowing a small number of **missed cleavages** will increase peptide
count and average length in a predictable way, and filtering to an
MS-observable window (e.g. mass 500-5000 Da, length 6-40 residues) will retain
the peptides typically used for identification.

## Evidence / metrics

- **Exact-match validation:** for hand-curated test sequences, the predicted
  peptide list matches the expected list exactly (the unit-test of the digest).
- **Cleavage-rule check:** no peptide ends in K/R immediately followed by P
  (the "not before P" exception is honored).
- **Mass accuracy:** computed monoisotopic peptide masses match reference values
  to within a small tolerance (validates the mass table).
- **Missed-cleavage effect:** peptide count and length distribution shift as
  expected when 0 -> 1 -> 2 missed cleavages are allowed.
- **Observable fraction:** fraction of peptides inside the MS mass/length window.

## Domain Context

### The trypsin rule
- Trypsin cleaves the peptide bond **C-terminal to lysine (K) and arginine (R)**.
- **Exception:** it does *not* cleave when the next residue is **proline (P)**
  (i.e. no cut at K-P or R-P).
- A "fully tryptic" peptide therefore starts after a K/R (or at the protein N-
  terminus) and ends at a K/R (or the protein C-terminus).

### Missed cleavages
- Digestion is imperfect: trypsin sometimes skips a site. Allowing N "missed
  cleavages" means a peptide may contain up to N internal K/R sites. Search
  engines typically allow 1-2.

### Peptide mass
- **Monoisotopic mass** = sum of residue masses + one water (H2O) for the
  terminal groups. Use a standard residue-mass table (monoisotopic).
- Mass spectrometers observe a limited range; very small or very large peptides
  are not useful for identification.

### Fidelity ladder (SMAIRT data progression)
1. **Synthetic / hand-checked:** tiny sequences (e.g. `AKPR`, `MKWVTFISLLR`)
   where you can verify the peptide list and the "not before P" rule by hand.
   (Start here.)
2. **Synthetic, harder:** a realistic-length random or template protein; add
   missed cleavages and the MS-observable mass/length filter; check the
   distributions behave sensibly.
3. **Real (optional, later):** paste a real protein sequence (e.g. human serum
   albumin or BSA from a FASTA) and compare your peptide list / masses against a
   public digestion tool (e.g. ExPASy PeptideMass) as an external check.

### Caveats
- This models the *rules* of digestion, not real-world reality: it ignores
  semi-tryptic peptides, post-translational modifications (which shift mass),
  charge states, and detectability biases. Naming these limits next to the
  result is part of the SMAIRT method.

## Known reference values (for validation)

| Item | Value |
|------|-------|
| Trypsin cleaves after | K, R |
| Trypsin exception | not before P |
| Water (monoisotopic) | 18.0106 Da |
| Typical MS mass window | ~500-5000 Da |
| Typical MS length window | ~6-40 residues |
| Common missed-cleavage allowance | 0, 1, or 2 |
