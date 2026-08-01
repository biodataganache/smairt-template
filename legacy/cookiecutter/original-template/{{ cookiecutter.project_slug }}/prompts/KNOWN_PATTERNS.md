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

### 2.1 [Example: Self-referencing entries in evaluation data]

**What happened**: [e.g., Evaluation set included self-pairs (A-A) which inflated scores]

**Impact**: [e.g., Precision degraded 4.7×]

**Fix**:
```python
# [Corrected code]
```

**Prevention**: [e.g., Always filter where item_A != item_B before evaluation]

**Learned from**: [iter_XX / script_XX]

---

### 2.2 [Example: Lenient parsing of input files]

**What happened**: [e.g., Used >= 2 columns instead of == 2, allowing malformed rows]

**Impact**: [e.g., Silently included garbage data in analysis]

**Fix**:
```python
# [Corrected code]
```

**Prevention**: [e.g., Validate exact column count on load]

**Learned from**: [iter_XX / script_XX]

---

### 2.3 [Example: Evaluation set mismatch]

**What happened**: [e.g., Used wrong dataset's evaluation criteria for scoring]

**Impact**: [e.g., All metrics were meaningless]

**Fix**: [e.g., Parameterize dataset/domain in config, validate against data]

**Prevention**: [e.g., Pre-flight check #3 — verify evaluation set matches data domain]

**Learned from**: [iter_XX / script_XX]

---

### 2.4 [Example: dtype not specified for ID columns]

**What happened**: [e.g., IDs loaded as int instead of string, causing join failures]

**Impact**: [e.g., Silent data loss — 30% of pairs dropped]

**Fix**:
```python
# [Corrected code with dtype='str']
```

**Prevention**: [e.g., Always specify dtype for ID columns]

**Learned from**: [iter_XX / script_XX]

---

### 2.5 [Example: Not deduplicating pairs]

**What happened**: [e.g., (A,B) and (B,A) both present, inflating pair count]

**Impact**: [e.g., Metrics computed on inflated N, overestimating significance]

**Fix**:
```python
# [Canonical ordering + dedup code]
```

**Prevention**: [e.g., Always apply canonical_order() then drop_duplicates()]

**Learned from**: [iter_XX / script_XX]

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

{% if cookiecutter.project_mode == 'paper_driven' %}
### 5.5 HPC-Specific Patterns

- **Cluster**: [Name]
- **Module loads**: [Required modules]
- **Job submission**: [Working sbatch patterns]
- **Data paths**: [Scratch vs. project vs. home]

```bash
# Pattern: [Brief description of working HPC submission]
# [Paste working command/script here]
```
{% endif %}

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
| [YYYY-MM-DD] | [What was added] | [Pattern/Error/Standard] | [iter_XX / script_XX] |
