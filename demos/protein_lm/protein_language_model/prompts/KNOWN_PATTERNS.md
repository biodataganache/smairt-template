# Known Patterns & Common Errors

## Purpose

This file is a **living reference** that records:
1. **Reusable code patterns** — Copy-pasteable implementations that work reliably
2. **Recurring errors** — Mistakes that have been made, their impact, and how to fix/prevent them
3. **Standards** — Canonical ways to perform common operations
4. **Pre-flight checklist** — Verification steps before submitting any new analysis

**Give this file to your AI at the start of every session** alongside `AI_CONTEXT.md` and `CODE_CONVENTIONS.md`. This prevents repeating solved problems and ensures consistency across iterations.

---

## How to Use This File

1. **At session start**: Feed this to your AI so it doesn't repeat past mistakes
2. **Before writing code**: Check standards and patterns for the operation you're implementing
3. **Before submitting analysis**: Run through the pre-flight checklist
4. **After each iteration**: If you encountered an error or wrote reusable code, add it here
5. **When switching contexts**: API keys, paths, environment quirks go here

---

## 1. Reusable Code Patterns

Organized by operation type. Each pattern should be copy-pasteable.

### 1.1 Data Loading

```python
# Pattern: [Brief description, e.g., "Load dataset from API with file-based fallback"]
# Used in: [script_XX_name.py]
# Notes: [Why this works / what to watch out for]

# [Paste working code here]
```

### 1.2 Data Processing & Filtering

```python
# Pattern: [Brief description, e.g., "Canonical pair ordering, filtering, deduplication"]
# Used in: [script_XX_name.py]
# Notes: [Order of operations matters — filter before dedup]

# [Paste working code here]
```

### 1.3 API Calls & External Services

```python
# Pattern: [Brief description, e.g., "API call with retry logic"]
# Endpoint: [URL or service]
# Auth: [How authentication is handled]
# Rate limits: [If applicable]
# Fallback: [What to do if API is unavailable]

# [Paste working code here]
```

### 1.4 Metrics & Evaluation

```python
# Pattern: [Brief description, e.g., "Precision@K calculation", "AUROC/AUPRC", "F1-score"]
# Used in: [script_XX_name.py]
# Notes: [Edge cases, expected ranges, validation checks]

# [Paste working code here]
```

### 1.5 Tool/CLI Invocation

```python
# Pattern: [Brief description, e.g., "Invoke external tool with standard parameters"]
# Tool: [Name and version]
# Required inputs: [What files/args it needs]
# Expected outputs: [What it produces]

# [Paste working code here]
```

### 1.6 Output / Logging

```python
# Pattern: [Brief description]
# Used in: [script_XX_name.py]

# [Paste working code here]
```

### 1.7 Visualization

```python
# Pattern: [Brief description]
# Output format: [png/pdf/svg]
# Used in: [script_XX_name.py]

# [Paste working code here]
```

### 1.8 Results Reporting

```python
# Pattern: [Brief description, e.g., "Save results with full metadata"]
# Used in: [script_XX_name.py]
# Notes: [Always include these fields in output]

# [Paste working code here]
```

### 1.9 File Organization

```python
# Pattern: [Brief description, e.g., "Standard path resolution and output directory setup"]
# Used in: [All scripts]

# [Paste working code here]
```

### 1.10 Seed Setting & Reproducibility

```python
# Pattern: [Brief description]
# Used in: [All scripts]

# [Paste working code here]
```

---

## 2. Recurring Errors & Anti-Patterns

Each entry documents a mistake that was made, its impact, and how to prevent it.

### Error Template

```
### 2.X [Brief Error Title]

**What happened**: [Describe the mistake]

**Impact**: [Quantify the damage — e.g., "Precision degraded 4.7×", "Results were unreproducible"]

**Fix**: [What solved it]

**Prevention**: [How to avoid in future scripts — check that goes in pre-flight]

**Learned from**: [Iteration/script where this was discovered]
```

### 2.1 Per-element sigma-band check across many estimates (multiple comparisons)

**What happened**: script_01's generator validation tested all 47×20 = 940
per-column residue frequencies against an individual binomial 3-sigma band. Two
background columns tripped it (dev 0.0150 vs tol 0.0146) and the run reported
"CHECKS FAILED" even though the generator was correct.

**Impact**: A correct, validated synthetic generator was flagged as broken; ~2.5
of 940 estimates are expected to exceed 3 sigma by chance alone.

**Fix**:
```python
# Test each COLUMN's full distribution with one chi-square GOF test vs uniform,
# then count rejections and compare to the expected false-positive rate.
chi2 = np.sum((counts - expected_count) ** 2 / expected_count)  # df = 19
# reject if chi2 > 43.820 (alpha=0.001); expect ~0 rejections over 47 columns
```

**Prevention**: Never apply a per-element sigma band across many estimates without
a multiple-comparisons correction. Use one test per logical unit (column), or
correct alpha (Bonferroni/FDR).

**Learned from**: iter_01 / script_01_validate_generator.py (see ANALYSIS_01.md)

---

### 2.2 Non-discriminating baseline + noise-diluted average

**What happened**: script_02 trained a nano-MLM on an all-glycine motif. The model
learned it perfectly (motif cols = 1.000, background = chance) but overall masked
accuracy (0.1072) tied the unigram baseline (0.1076), so the run looked like a
failure (H_02A FAIL).

**Impact**: A Bayes-optimal model appeared to fail. Cause: (a) the planted motif
residue equaled the baseline's single guess (glycine), and (b) 47/50 positions are
unlearnable noise that dominates the average, hiding the model's real success.

**Fix**:
```python
# 1. Use a MULTI-RESIDUE motif of distinct residues (not the global mode), e.g.
MOTIF = "GKTYRG"  # baseline can match at most one motif column
# 2. Report per-column accuracy AND a per-column-optimal baseline (the ceiling),
#    not just a global-unigram baseline and overall average.
```
After the fix (script_03): model 0.1600 vs global baseline 0.0840, motif=1.000,
per-column ceiling 0.1640 — all checks PASS.

**Prevention**: Design baselines that are *discriminating* on the positions of
interest; never let the planted signal coincide with the baseline's guess; always
report per-position/per-stratum metrics when most positions carry no signal.

**Learned from**: iter_02-03 / script_02, script_03 (see ANALYSIS_02.md, ANALYSIS_03.md)

---

### 2.3 Discriminator a control already solves (no learning required)

**What happened**: script_05 tested whether trained embeddings separate two
families. The families differed only by motif POSITION (cols 22–27 vs 10–15).
The trained model separated them (AUC 0.9998) — but so did an UNTRAINED random-init
model (AUC 0.978), because position embeddings are added before the encoder, so
positional differences are encoded at initialization. The composition control was
correctly at chance (0.486), but the untrained control was not, so the experiment
could not attribute separation to *learning*.

**Impact**: A "PASS" on the headline metric (AUC) would have falsely claimed the
model *learned* to distinguish families, when the architecture does it for free.

**Fix**:
```python
# Make the family difference invisible to BOTH composition AND position:
# use a PAIRWISE COVARIATION rule at FIXED columns, identical marginals.
#   Family A: residues at cols i,j are coupled (j determined by i)
#   Family B: residues at cols i,j are independent
# Only attention over content can capture the dependency -> untrained control
# should drop to chance, isolating learning.
```

**Prevention**: For any "the model learned X" claim, include an **untrained
random-init control** and require it to be at chance. If a control already solves
the task, the discriminator is too easy — redesign it so only learning can succeed.
Also: prefer AUC (or in-subspace silhouette) over raw high-dim Euclidean silhouette,
which understates one-direction separation.

**Learned from**: iter_05 / script_05 (see ANALYSIS_05.md)

---

### 2.4 Signal too sparse to affect the training objective (null is about learnability, not truth)

**What happened**: script_06 planted a single pairwise coupling (`seq[j]=seq[i]`)
that distinguished two families. The design was clean — both the untrained and
composition controls were at chance (the iteration-05 confound was fixed) — but the
TRAINED nano-MLM also stayed at chance (AUC 0.485) and never learned the coupling
(conditional j-accuracy = 0.055 = chance for both families).

**Impact**: A perfectly valid, confound-free experiment returned a null, which
could be misread as "attention can't learn dependencies." The real cause: one
coupled pair among 50 columns barely lowers the masked-LM loss (it only helps when
j is masked AND i is visible, on 1/50 columns), so there is no gradient signal.

**Fix**:
```python
# Make learning the rule materially reduce the loss while keeping marginals uniform:
# use MANY coupled pairs via a fixed alphabet bijection, e.g. K=10 disjoint pairs
#   Family A: seq[b] = PERM[seq[a]] for each pair (a,b)  # each column still uniform
#   Family B: all columns independent uniform
# Now ~K/50 of masked tokens are predictable only by learning the rule -> trainable.
```

**Prevention**: When testing whether a model *learns* a planted structure, size the
signal so that capturing it yields a **non-trivial loss reduction**; a true-but-rare
dependency the objective can ignore will produce a null that is about learnability
under the loss, not about the structure's existence. Always include the mechanistic
probe (here: conditional accuracy at the coupled position) to tell "didn't learn"
from "couldn't matter".

**Learned from**: iter_06 / script_06 (see ANALYSIS_06.md)

---

### 2.5 Planted rule too complex for the model budget (partial learning)

**What happened**: script_07 made the family-distinguishing signal loss-relevant
(K=10 coupled column pairs, fixing iter 06's sparsity), but the rule was an
ARBITRARY 20-symbol permutation routed across 10 RANDOM column pairs. The nano
model (2 layers, 64-dim, 30 epochs) only partially learned it: coupled-column
accuracy 0.183 (>3× chance) and AUC 0.604 — clearly above the at-chance controls,
but far below the ≥0.90 target.

**Impact**: A real effect (model ≫ controls) looked like a FAIL because the target
assumed the rule was fully learnable at this budget. Risk: mistaking a
capacity/complexity limit for a design flaw.

**Fix**:
```python
# Keep the airtight uniform-marginal design but make the MAPPING trivial to learn:
#   Family A: seq[b] = seq[a]   # identity copy -> one copy-attention head suffices
#   (still uniform marginals -> both controls stay at chance)
# Optionally bump epochs/heads slightly. Reserve hard rules (permutations) for
# larger models.
```

**Prevention**: Separate the two knobs of a learnability test: (1) does the signal
affect the loss (sparsity), and (2) is the mapping within model capacity
(complexity). Start with the easiest mapping (identity copy) to confirm the
mechanism, then increase difficulty. Always read "model ≫ controls but < target" as
*partial learning*, not failure.

**Learned from**: iter_07 / script_07 (see ANALYSIS_07.md)

---

### 2.6 [Example: Inconsistent column names across files]

**What happened**: [e.g., Some files use "item_a/item_b", others "source/target"]

**Impact**: [e.g., Merge failures, silent empty results]

**Fix**: [e.g., Standardize on load with rename mapping]

**Prevention**: [e.g., Standards section 3.1 defines canonical column names]

**Learned from**: [iter_XX / script_XX]

---

### 2.7 [Example: Missing metadata in results]

**What happened**: [e.g., Results saved without recording which benchmark/parameters were used]

**Impact**: [e.g., Cannot reproduce or compare results across iterations]

**Fix**: [e.g., Always save config + metadata alongside results]

**Prevention**: [e.g., Use standard results reporting pattern (Section 1.8)]

**Learned from**: [iter_XX / script_XX]

---

### 2.8 [Example: Hardcoded paths instead of constants]

**What happened**: [e.g., Paths were hardcoded, broke when directory structure changed]

**Impact**: [e.g., Scripts failed silently or read wrong data]

**Fix**: [e.g., Define all paths as constants relative to project root]

**Prevention**: [e.g., Use file organization pattern (Section 1.9)]

**Learned from**: [iter_XX / script_XX]

---

## 3. Standards

Canonical ways to perform common operations. These are the "right way" to do things in this project.

### 3.1 Data Loading Standards

| Aspect | Standard | Rationale |
|--------|----------|-----------|
| [e.g., Column names] | [e.g., Always "source", "target", "weight"] | [Consistency across scripts] |
| [e.g., ID dtype] | [e.g., Always load as str] | [Prevent silent join failures] |
| [e.g., Validation] | [e.g., Assert expected columns exist] | [Fail fast on bad data] |
| [e.g., Missing values] | [e.g., Drop rows with NaN in ID columns] | [Prevent downstream errors] |

### 3.2 Evaluation Set Construction Standards

| Aspect | Standard | Rationale |
|--------|----------|-----------|
| [e.g., Pair ordering] | [e.g., Alphabetical canonical order] | [Prevent duplicates] |
| [e.g., Self-references] | [e.g., Always remove] | [Prevents inflated metrics] |
| [e.g., Deduplication] | [e.g., Always after canonical ordering] | [Exact pair count] |
| [e.g., Domain check] | [e.g., Validate evaluation set matches data] | [Prevent mismatch errors] |

### 3.3 Tool/Analysis Invocation Standards

| Aspect | Standard | Rationale |
|--------|----------|-----------|
| [e.g., Seed] | [e.g., Always 1024] | [Reproducibility] |
| [e.g., Parameters] | [e.g., Load from config.yaml] | [Traceability] |
| [e.g., Output location] | [e.g., results/ in current iteration dir] | [Organization] |

### 3.4 Results Reporting Standards

| Aspect | Standard | Rationale |
|--------|----------|-----------|
| [e.g., Metadata] | [e.g., Always save config hash + timestamp] | [Reproducibility] |
| [e.g., Metrics format] | [e.g., JSON with nested structure] | [Machine-readable] |
| [e.g., Figure format] | [e.g., PDF + PNG, 300 DPI] | [Publication quality] |
| [e.g., Comparison baseline] | [e.g., Always include random baseline] | [Context for metrics] |

### 3.5 File Organization Standards

| Aspect | Standard | Rationale |
|--------|----------|-----------|
| [e.g., Path constants] | [e.g., Defined at top of script relative to project root] | [Portability] |
| [e.g., Output naming] | [e.g., {method}_{dataset}_{metric}.{ext}] | [Findability] |
| [e.g., Intermediate files] | [e.g., results/intermediate/ — gitignored] | [Clean repo] |

---

## 4. Pre-Flight Checklist

**Run through this checklist before submitting any new analysis.** Each item addresses a recurring error from Section 2.

- [ ] **1. Data integrity** — Loaded data has expected shape, dtypes, and no unexpected NaN/null values
- [ ] **2. ID consistency** — ID columns loaded as correct dtype (typically str); no silent type coercion
- [ ] **3. Evaluation set validity** — Evaluation set matches the data being analyzed (correct domain/version/split)
- [ ] **4. Self-references removed** — No self-pairs (A-A) in evaluation or analysis sets
- [ ] **5. Canonical ordering applied** — Pairs are in canonical order (e.g., alphabetical) before deduplication
- [ ] **6. Deduplication done** — No duplicate pairs after canonical ordering
- [ ] **7. Column names consistent** — Using standard column names per Section 3.1
- [ ] **8. Paths use constants** — No hardcoded absolute paths; all paths relative to defined constants
- [ ] **9. Metadata captured** — Results include benchmark name, parameters, seed, timestamp, iteration
- [ ] **10. Reproducibility verified** — Running twice with same seed produces identical output

---

## 5. Environment & Configuration

### 5.1 Python Environment

- **Python version**: [e.g., 3.11.4]
- **Virtual environment**: [path or name]
- **Key packages**: [list with versions]

### 5.2 Paths & Directories

```python
# Project root resolution that works from any script location
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

### 5.3 API Keys & Credentials

- **Service**: [Name]
- **How to load**: [env var, config file, etc.]
- **Gotchas**: [Rate limits, auth expiry, etc.]

### 5.4 Platform-Specific Notes

- **OS**: [macOS / Linux / Windows]
- **Known issues**: [e.g., path separators, line endings]



---

## 6. Consistency Rules

Record rules that must be followed for cross-script consistency:

| Rule | Reason | Example |
|------|--------|---------|
| [e.g., Always use seed=1024] | [Reproducibility] | `np.random.seed(1024)` |
| [e.g., Figures at 300 DPI] | [Publication quality] | `plt.savefig(..., dpi=300)` |
| [e.g., Log timestamps in ISO format] | [Parseable logs] | `datetime.now().isoformat()` |
| [e.g., Canonical pair order before any comparison] | [Prevent duplicates] | `sorted([a, b])` |

---

## 7. Session-Specific Quick Reference

Update this section at the start of each session with the most critical current patterns:

**Current working data loading**:
```python
# [Paste current best approach]
```

**Current working output format**:
```python
# [Paste current best approach]
```

**Current active workarounds**:
- [ ] [Workaround 1 - will be fixed when X]
- [ ] [Workaround 2 - will be fixed when Y]

---

## Version History

Track when each lesson was learned and from which iteration:

| Date | Addition | Category | Learned From |
|------|----------|----------|--------------|
| 2026-06-29 | Per-element sigma-band check across many estimates (multiple comparisons) | Error/Anti-pattern | iter_01 / script_01 |
| 2026-06-29 | Non-discriminating baseline + noise-diluted average | Error/Anti-pattern | iter_02-03 / script_02, script_03 |
| 2026-06-29 | Consistency: seed=1024, figures at 300 DPI, TeeLogger→results/logs/ | Standard | iter_01-03 |
| 2026-06-29 | Discriminator a control already solves (need untrained-model control at chance) | Error/Anti-pattern | iter_05 / script_05 |
| 2026-06-29 | Signal too sparse to affect the training objective (null about learnability, not truth) | Error/Anti-pattern | iter_06 / script_06 |
| 2026-06-29 | Planted rule too complex for model budget (partial learning, not failure) | Error/Anti-pattern | iter_07 / script_07 |
| 2026-06-29 | Embedding-separation needs both an untrained-model AND a shuffled-label control to claim real learned signal | Standard | iter_08-09 / script_08, script_09 |
| 2026-06-29 | Rung 3 stack: fair-esm 2.0.0 + esm2_t6_8M_UR50D (CPU, frozen, embeddings only); UniProt REST for data | Environment | iter_09 / script_09 |
