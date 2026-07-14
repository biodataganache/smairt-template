# Intellectual Contribution Log

Track where YOU made the critical steps vs. where AI generated ideas.

---

## Why This Matters
What you bring to the process is an important thing to track. This is where
the AI moves from being a prompt-driven engine for generating stuff to
a scientific tool that enables exploration of gaps and what will and won't work
for a specific scientific question.

---

## The 01-09 Scientific Arc: Key Contributions

| Iteration | Phase | Key Human Contribution | Impact on Project | Type of Contribution |
|-----------|-------|------------------------|-------------------|----------------------|
| **01** | Synthetic | Insisted on a **validation-first** approach before training any model. Changed the AI's naive individual confidence check to a **Chi-Square Goodness-of-Fit test**. | Caught potential data generator flaws early and established a clean, statistically validated synthetic corpus. | Methodological / Critical Judgment |
| **02 & 03** | Synthetic | Identified that **overall accuracy** was a noise-diluted metric and the glycine motif was **non-discriminating** against the unigram baseline. Re-designed the motif to `GKTYRG` and stratified evaluation metrics. | Pushed past a false failure. The model was shown to learn the grammar perfectly (1.000 motif accuracy vs 0.084 baseline) once evaluated correctly. | Interpretive / Conceptual |
| **05** | Synthetic | Recognized that the perfect family separation (AUC=0.9998) was a **confound** because the **untrained model** also separated them (AUC=0.978) due to positional embeddings. | Prevented a false "PASS" claim. Exposed that the architecture, not learning, was separating families by position. | Critical Judgment |
| **06** | Synthetic | Redesigned the family differentiator to be a **pairwise covariation** (coupled columns), neutralizing position/composition shortcuts. Diagnosed why a single pair failed to train (sparse loss signal). | Successfully forced controls to chance, isolating learning. Proved MLM needs a loss-relevant signal to train. | Conceptual / Methodological |
| **07 & 08** | Synthetic | Recognized that the arbitrary permutation $\pi$ was too complex for a nano-budget, representing **partial learning** (AUC=0.604). Simplified the mapping to **identity copy** and increased epochs to 40. | Closed the Rung 2 embedding claim with a flawless PASS (Trained AUC=1.000, both controls = ~0.51, Copy Accuracy=1.000). | Critical Judgment / Methodological |
| **09** | Real | Orchestrated the transition to Rung 3: live UniProt Swiss-Prot API fetches (Globin vs Cytochrome c), loading a frozen pretrained **ESM-2** model on CPU, and introducing **shuffled-label** and **length-only** controls. | Demonstrated real biological transfer (AUC=1.000, silhouette=0.392, controls at chance), completing the full SMAIRT fidelity ladder. | Conceptual / Interpretive |

---

## Detailed Iteration Logs

### Iteration 1 - 2026-06-29
**Phase:** Synthetic

**Hypothesis being tested:** HYPOTHESIS_01 (Generator correctness & baseline)

**AI suggested:**
- Jump straight into building the PyTorch training loop and train a model on the synthetic sequence data.
- Check background frequencies by checking if they fall within standard deviation bands per element.

**I suggested:**
- **No training yet.** We must validate the data generator first.
- Use a **Chi-Square Goodness-of-Fit test** ($\alpha=0.001$, $df=19$) to evaluate column-wise uniform background distributions instead of a multi-comparison-flawed $\sigma$-band check.

**Critical insight (mine):**
- Checking 47 background columns using individual $3\sigma$ bounds creates a multiple-comparisons problem where false rejections are guaranteed (family-wise error rate). A Chi-Square test is mathematically correct.

**Decision I made:**
- Establish the baseline unigram accuracy (0.1076) and statistical criteria *before* PyTorch or torch tensors are introduced.

---

### Iteration 2 & 3 - 2026-06-29
**Phase:** Synthetic

**Hypothesis being tested:** HYPOTHESIS_02 & HYPOTHESIS_03 (Motif reconstruction & discriminating baseline)

**AI suggested:**
- When Overall Accuracy (0.1072) tied the unigram baseline (0.1076), the AI suggested adding layers, increasing the learning rate, or trying a larger model to solve "underfitting."

**I suggested:**
- Stratify the metrics: separate motif-column accuracy from background-column accuracy.
- Plant a multi-residue motif (`GKTYRG`) instead of an all-glycine motif.

**Critical insight (mine):**
- The model hadn't failed; the **metric** was flawed. Because 47 out of 50 columns are unlearnable background noise, their average dilutes the 3 motif columns. Furthermore, because the motif was glycine and glycine was the background's most common residue, the baseline's default guess coincided with the motif, masking the model's learning.

**Decision I made:**
- Redesigned the motif to `GKTYRG` so that the baseline could match at most 1/20 of the motif columns. Added a per-column-optimal baseline.

---

### Iteration 5 - 2026-06-29
**Phase:** Synthetic

**Hypothesis being tested:** HYPOTHESIS_05 (Two-family embedding separation by position)

**AI suggested:**
- Separate families by motif position (cols 22-27 vs cols 10-15). When the linear probe achieved AUC=0.9998, the AI declared a successful demonstration of learned family separation.

**I suggested:**
- Let's check the **untrained, random-init model control**.

**Critical insight (mine):**
- The untrained model also separated families perfectly (AUC=0.9785). The separation wasn't *learned*—the model's fixed position embeddings encode motif position "for free" before any weights are updated.

**Decision I made:**
- Rejected the PASS. Logged a new anti-pattern (§2.3: "Discriminator a control already solves") and ordered a redesign where position is held constant across families.

---

### Iteration 6 - 2026-06-29
**Phase:** Synthetic

**Hypothesis being tested:** HYPOTHESIS_06 (Two-family separation by single covariation)

**AI suggested:**
- Link the families by a single pairwise coupling (`seq[j] = seq[i]`) at fixed columns in Family A, and independent in Family B.

**I suggested:**
- Run a conditional mechanistic accuracy check at column $j$ while column $i$ is visible to see if the model has actually learned the association.

**Critical insight (mine):**
- When AUC and copy accuracy both stayed at chance (0.055), I realized that a *single* coupled pair in a 50-residue sequence is too sparse to affect the masked-LM cross-entropy loss (it only helps on $\approx 1\%$ of masked tokens). The model has no optimization incentive to learn it.

**Decision I made:**
- Keep the joint-distribution design (controls successfully dropped to chance!), but increase the density of the coupling to make it loss-relevant.

---

### Iteration 7 & 8 - 2026-06-29
**Phase:** Synthetic

**Hypothesis being tested:** HYPOTHESIS_07 & HYPOTHESIS_08 (Many-pair coupling & identity copy)

**AI suggested:**
- Couple K=10 pairs using a complex 20-symbol alphabet permutation $\pi$.
- When AUC reached 0.604, the AI treated this as a model failure.

**I suggested:**
- This is **partial learning**, not a failure! The design is correct (controls are at 0.51).
- Simplify the mapping to an **identity copy** (`seq[b] = seq[a]`), which a single copy-attention head can route, and bump training to 40 epochs.

**Critical insight (mine):**
- Routing 10 independent pairs and learning a full 20x20 permutation mapping simultaneously is too hard a credit-assignment task for a 2-layer model under CPU-minute epoch budgets. Trivializing the mapping to identity copy retains uniform marginals (airtight controls) while making routing learnable.

**Decision I made:**
- Executed Iteration 08 with K=10 identity copies. Achieved a perfect PASS: trained AUC=1.000, controls=0.51, conditional copy accuracy=1.000.

---

### Iteration 9 - 2026-06-29
**Phase:** Real Data

**Hypothesis being tested:** HYPOTHESIS_09 (Pretrained ESM-2 family separation)

**AI suggested:**
- Put a synthetic mock dataset into `data/real/` or use standard composition vectors on dummy sequences to simulate real data.

**I suggested:**
- No, let's go all the way. Install `fair-esm` and write a live fetcher for the **UniProt Swiss-Prot REST API**.
- Use highly distinct Pfam families: **Globin (PF00042)** and **Cytochrome c (PF00034)** to ensure a biologically sound test.
- Introduce **shuffled-label** and **length-only** controls to validate the transfer representation.

**Critical insight (mine):**
- To show real biological transfer, we must use a frozen pretrained model (no fine-tuning) on real reviewed biological sequences, while proving with controls that the separation is not a sequence-length or label-leakage artifact.

**Decision I made:**
- Fetched 60 reviewed sequences from UniProt. Embedded using `esm2_t6_8M_UR50D`. Achieved held-out AUC=1.000, silhouette=0.3918, while shuffled-label (0.4375) and length-only (0.2208) stayed at chance. This successfully closed Rung 3 of the fidelity ladder.

---

## AI-Detected Contributions

### 2026-06-29 — The Noise-Dilution Discovery
**Insight:** "Overall accuracy hides local learning in variable-background datasets. We must evaluate motif positions separately."
**Why it matters:** Rescued the project from a false-negative underfitting diagnosis. Guided the creation of stratified evaluation metrics now used across the codebase.
**Context:** During Iteration 02 overall accuracy evaluation.

### 2026-06-29 — Position Embeddings Confound
**Insight:** "If an untrained random-init model separates families as well as a trained one, your representation difference is structural/architectural, not learned."
**Why it matters:** Established the "untrained model" as an indispensable control for PLM family-separation claims, leading to the covariation and identity-copy designs.
**Context:** During Iteration 05 embedding evaluation.

### 2026-06-29 — Learnability vs. Loss Sparsity
**Insight:** "A model won't learn a real data dependency if that dependency does not materially reduce the training loss."
**Why it matters:** Explained why the mathematically clean single-covariance coupling failed to train, introducing the dense K-pair bijection and identity-copy layouts.
**Context:** During Iteration 06 covariation evaluation.

---

## Summary Table

| Iteration | Date | Key Human Contribution | Impact on Project |
|-----------|------|------------------------|-------------------|
| **01** | 2026-06-29 | Validation-first; Chi-Square background checks. | Prevented downstream modeling errors on dirty synthetic data. |
| **02 & 03** | 2026-06-29 | Strata-based evaluation metrics; `GKTYRG` discriminating motif. | Showed the model was successfully learning the motif despite poor overall accuracy. |
| **05** | 2026-06-29 | Untrained-model control verification. | Caught position-embedding confound; forced a rigorous joint-distribution redesign. |
| **06** | 2026-06-29 | Pairwise covariation family difference. | Eliminated positional shortcuts; identified MLM loss-relevance bottlenecks. |
| **07 & 08** | 2026-06-29 | Identified partial learning; simplified permutation to identity copy. | Completed Rung 2 with a perfect, airtight learned family-separation PASS. |
| **09** | 2026-06-29 | Live UniProt REST fetcher; Frozen ESM-2 representation; shuffled & length controls. | Completed Rung 3, demonstrating true PLM transfer on real biological sequences. |
