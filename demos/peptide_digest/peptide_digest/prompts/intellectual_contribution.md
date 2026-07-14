# Intellectual Contribution Log

Track where YOU made the critical steps vs. where AI generated ideas.

---

## Why This Matters
What you bring to the process is an important thing to track. This is where
the AI moves from being a prompt-driven engine for generating stuff to
a scientific tool that enables exploration of gaps and what will and won't work
for a specific scientific question.
---

## How to Use This File

For each iteration, document:
1. What AI suggested
2. What YOU suggested
3. Where YOU made critical insights—especially at dead ends or turning points
4. Key decisions you made that shaped the direction of the project

---

## Iteration 1 - 2026-06-29

**Phase:** Synthetic

**Hypothesis being tested:**
Implementing the canonical trypsin rule—cleaving after Lysine (K) or Arginine (R), but not when followed immediately by Proline (P)—will perfectly reconstruct expected peptide lists for hand-curated test sequences.

**AI suggested:**
- Formulate a clean summary of the research question and proposed test cases.
- Structure a multi-step todo list to coordinate tasks.
- Create a test suite incorporating basic tryptic cleavage, terminal boundaries, and proline blocks.

**I suggested:**
- Set up a clean, structured Python project using the SMAIRT template pattern.
- Prime the session with sequential instructions, validating on hand-checked cases before jumping to mass/length filters.
- Approved the initial hypothesis file (`HYPOTHESIS_01.md`) and overall project execution steps.

**Critical insight (mine):**
- Recognized that validating *in-silico* digestion rules exactly on tiny, deterministic sequences is a mandatory foundation before introducing missed cleavages, physical mass parameters, or complex noise.

**Decision I made:**
- Decided to start with a simplified pure-Python standard-library digester first to confirm boundary conditions and proline exceptions.

**Where I pushed past a dead end:**
- None encountered in Iteration 1; tests passed on the first run.

---

## Iteration 2 - 2026-06-29

**Phase:** Synthetic

**Hypothesis being tested:**
Allowing a maximum of $N$ missed cleavages will systematically expand the pool of candidate peptides by combining up to $N+1$ adjacent, fully-cleaved peptides. This will increase the total peptide yield and the average peptide length in a predictable, mathematically bounded manner.

**AI suggested:**
- Model missed cleavages as combinations of consecutive segments generated at $N=0$.
- Formulate mathematical bounding proofs to self-validate combinations.
- Write Case A, B, and C hand-curated test scenarios to verify code boundaries.

**I suggested:**
- Approved the $N=0$ segments combining logic over recursive approaches, as combining adjacent arrays is simpler, robust, and less error-prone.
- Approved test metrics analyzing the yield sum of subsegments and trend monotonically on a longer model protein.
- Logged this second hypothesis (`HYPOTHESIS_02.md`) to finalize the iteration plan.

**Critical insight (mine):**
- Realized that missed cleavage calculations are mathematically bounded by segment counts $M$, meaning letting $N \geq M$ should saturate yield and prevent duplicate recombinations.

**Decision I made:**
- Decided to compare sorted list arrays in our assertions to stay completely order-independent in case different combinatorics loops are evaluated.

**Where I pushed past a dead end:**
- None encountered; the combinatorics logic behaved perfectly on the first execution.

---

## Iteration 3 - 2026-06-29

**Phase:** Synthetic (validated on real BSA protein sequence)

**Hypothesis being tested:**
Calculating peptide monoisotopic masses and filtering against physical mass spectrometry constraints (mass 500–5000 Da, length 6–40 residues) will filter out very short and very long peptides. The observable fraction of peptides will be maximized at standard experimental missed cleavage levels ($N=1, 2$) on real target proteins like Bovine Serum Albumin (BSA).

**AI suggested:**
- Implement standard monoisotopic masses of standard IUPAC residues.
- Set up a filter function taking standard length (6–40 residues) and mass (500–5000 Da) boundaries.
- Run validation calculations on tiny peptides `MK` and `WVTFISLLR`.

**I suggested:**
- Noticed a calculation discrepancy on `WVTFISLLR` where AI calculated 1114 Da, but standard monoisotopic summation equals 1133 Da (due to an off-by-one addition of fluorine/mass differences or simple arithmetic mistake on standard masses). Corrected the hand-calculated expectation to 1133.65969 Da to restore strict mathematical compliance.
- Approved testing on real mature Bovine Serum Albumin (BSA) containing 583 residues to show real physical filtration yields.
- Logged this third hypothesis (`HYPOTHESIS_03.md`) to guide iteration targets.

**Critical insight (mine):**
- Caught that fully-cleaved trypsin segmentations drop almost half ($41\%$) of total peptides due to short tryptic segments. Thus, allowing missed cleavages isn't just an "imperfection tolerance"—it is physically necessary to rescue peptide signals into standard instrument scanning ranges.

**Decision I made:**
- Decided to use standard mature BSA (minus its signal peptide) as the validation target, yielding exactly 78 raw peptides at $N=0$.

**Where I pushed past a dead end:**
- Corrected the initial hand-calculated mass verification of `WVTFISLLR` to 1133.65969 Da, allowing the assertion test suite to compile and pass with $100\%$ accuracy.

---

## AI-Detected Contributions

_The AI will append entries here when you confirm a novel contribution during a session._

<!-- Example entry (AI will follow this format):
### [DATE] — [Short Title]
**Insight:** "[User's words or paraphrase]"
**Why it matters:** [Brief explanation of impact on project direction]
**Context:** During [what you were working on]
-->

---

## Summary Table

| Iteration | Date | Key Human Contribution | Impact on Project |
|-----------|------|------------------------|-------------------|
| 1 | 2026-06-29 | Demanded initial focus on deterministic sequence testing before complex noise or mass calculations. | Ensured solid, bug-free boundary handling and proline exception rules as a validated foundation. |
| 2 | 2026-06-29 | Specified that missed-cleavage segments should saturate at maximum segment counts and approved order-insensitive assertions. | Confirmed robust combinatorics math and complete, reproducible code for standard database searches. |
| 3 | 2026-06-29 | Corrected monoisotopic mass arithmetic calculations and validated physically observable constraints on Bovine Serum Albumin (BSA). | Discovered that missed cleavages physically rescue unobservable segments, maximizing absolute yields. |

---

## Types of Contributions to Track

### Conceptual Contributions
- Novel questions or framings
- Connections between disparate ideas
- Recognizing patterns AI missed

### Methodological Contributions
- Suggesting approaches AI didn't think of
- Deciding which path to pursue at branch points
- Identifying when to pivot

### Interpretive Contributions
- Seeing implications AI missed
- Recognizing when results seem inconsistent or unexpected
- Connecting results to broader context

### Critical Judgment
- Knowing when an approach isn't working
- Recognizing limitations of AI suggestions
- Deciding what is sufficient vs. what needs more work

---

## Reflection Questions

Ask yourself at the end of each iteration:

1. Where did I provide direction that AI wouldn't have come up with?
2. Did I recognize a dead end before AI did?
3. What connections did I make between domains or ideas?
4. Where did I exercise judgment about what to pursue?
5. What would have happened if I had simply accepted AI suggestions without critical evaluation?

---

## Remember

AI excels at regression toward the mean. It may not be giving you anything really
novel in the way of new gaps or innovation. However, it can move you quickly
to the frontier of what's known. Identifying genuine gaps and making
really innovative connections requires human insight. That's what you're tracking here.
