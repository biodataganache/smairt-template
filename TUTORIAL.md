# SMAIRT Complete Tutorial

A comprehensive walkthrough of the SMAIRT framework using a real example: building a simple classifier and testing it across synthetic, benchmark, and real data.

> **Looking for a domain-specific example?** Browse the [SMAIRT Demo Collection](demos/README.md) for guided research tracks across physics, biology, epidemiology, and more.

---

## Table of Contents

1. [Overview](#overview)
2. [Setting Up Your Project](#setting-up-your-project)
3. [Phase 1: Synthetic Data](#phase-1-synthetic-data)
4. [Phase 2: Downloaded Benchmark Data](#phase-2-downloaded-benchmark-data)
5. [Phase 3: Real Data](#phase-3-real-data)
6. [Compiling Results](#compiling-results)
7. [Writing Up Findings](#writing-up-findings)

---

## Overview

In this tutorial, we'll work through a complete SMAIRT research cycle investigating the question:

> **"How well does a simple decision boundary approach separate two classes under varying noise conditions?"**

We'll follow the scientific method:
- **Background**: What we know about classification
- **Hypothesis**: Our testable prediction
- **Methods**: Code to test the hypothesis
- **Results + Interpretation**: What we found and what it means

SMAIRT uses the **10 Steps** (see `docs/12_STEPS.md`) to keep you rigorous while moving fast with AI assistance. The key innovation is the **audit trail**: every experiment links a hypothesis file → a numbered script → a log file → an analysis document.

---

## Setting Up Your Project

### Install and Generate

```bash
pip install cookiecutter
cookiecutter gh:yourusername/smairt-cookiecutter
```

Enter these values when prompted:
- **project_name**: Classification Noise Study
- **project_slug**: classification_noise_study
- **author_name**: Your Name
- **initial_research_question**: How does noise affect simple classification boundaries?
- **domain**: machine_learning
- **ai_tool**: claude (or your preferred AI)
- **starting_phase**: synthetic (start from the beginning)

### Project Structure

```
classification_noise_study/
├── docs/                    # SMAIRT reference (10 Steps, philosophy)
├── prompts/                 # AI context files and session logs
│   ├── AI_CONTEXT.md        # Instructions for your AI assistant
│   ├── CODE_CONVENTIONS.md  # How scripts should be structured
│   ├── KNOWN_PATTERNS.md    # Reusable patterns & known errors
│   └── SESSION_START.md     # Priming prompts for new sessions
├── plans/                   # Research plans before execution
├── background/              # Literature and prior knowledge
├── hypotheses/              # Formal hypothesis files
├── experiments/
│   ├── 01_synthetic/
│   ├── 02_downloaded/
│   └── 03_real_data/
├── analysis/                # Interpretation of results
├── results/
│   ├── logs/                # Script output (auto-generated)
│   └── figures/             # Plots and visualizations
├── data/
│   ├── synthetic/
│   ├── downloaded/
│   └── real/
└── scripts/
    ├── shared/              # Reusable utilities (TeeLogger, etc.)
    └── compile_for_ai.py    # Context compiler for browser-paste
```

### Prime Your AI

**IDE-Native (Zoo Code, Cursor, Windsurf):** Your AI can read the project files directly. Start a session with a prompt from `prompts/SESSION_START.md`:

```
Please read prompts/AI_CONTEXT.md, prompts/CODE_CONVENTIONS.md, and prompts/KNOWN_PATTERNS.md.

I'm starting a new SMAIRT project called "Classification Noise Study".
My research question: How does noise affect simple classification boundaries?

I'd like to begin with a baseline experiment on synthetic data.
```

**Browser-Paste (ChatGPT, Claude web):** Run `python scripts/compile_for_ai.py` and paste the output into your chat.

---

## Phase 1: Synthetic Data

Synthetic data lets us iterate quickly without external dependencies. We control all parameters, making it easy to isolate variables.

### Iteration 1: Establish Baseline

**Step 1 — Write the hypothesis** in `hypotheses/HYPOTHESIS_01.md`:

```markdown
# Hypothesis 01: Baseline Linear Classification

## Statement
A linear decision boundary can achieve >90% accuracy on linearly separable synthetic data with no noise.

## Rationale
With perfectly separable classes in 2D, a linear classifier should perform nearly perfectly. This establishes our baseline.

## Success Criteria
- Accuracy > 90% on test set
- Decision boundary visually separates the classes

## Status: Testing
## Date: [today]
```

**Step 2 — Ask your AI to create the script**:

```
Please create script_01_baseline_no_noise.py in experiments/01_synthetic/ that:

1. Generates 2D synthetic data with two linearly separable classes (200 points each)
2. Fits a simple linear classifier (logistic regression or similar)
3. Reports accuracy, plots the decision boundary
4. Saves the plot to results/figures/
5. Uses TeeLogger to capture output to results/logs/

Hypothesis: HYPOTHESIS_01.md — linear boundary achieves >90% accuracy on clean data.
```

The AI will generate a script following `CODE_CONVENTIONS.md`, using `TeeLogger` for the audit trail.

**Step 3 — Run the script**:

```bash
cd classification_noise_study
python experiments/01_synthetic/script_01_baseline_no_noise.py
```

Output is automatically captured to `results/logs/script_01_baseline_no_noise_YYYYMMDD_HHMMSS.log`.

**Step 4 — Write the analysis** in `analysis/ANALYSIS_01.md`:

```markdown
# Analysis 01: Baseline No Noise

## Hypothesis
HYPOTHESIS_01.md — Linear boundary achieves >90% on clean data.

## Result
Linear classifier accuracy: 0.98. **Hypothesis SUPPORTED.**

## Interpretation
Clean separation as expected. This establishes our baseline for noise experiments.

## Next Steps
Test with increasing noise levels to find where accuracy degrades.
```

**Step 5 — Track intellectual contribution** in `prompts/intellectual_contribution.md`:

```markdown
## Iteration 01 - Baseline

### What AI Suggested
- Use logistic regression for linear boundary
- Standard train/test split

### What I Contributed
- Decided to start with 2D for visualization
- Chose 200 samples per class as reasonable starting point
- Identified that we need noise testing next
```

> **Note:** If your AI tool has Active Innovation Detection enabled, it will proactively ask you when it notices novel contributions — you don't have to remember to log them yourself.

### Iteration 2: Add Noise

**Write hypothesis** in `hypotheses/HYPOTHESIS_02.md`:

```markdown
# Hypothesis 02: Noise Sensitivity

## Statement
Accuracy will degrade gracefully as Gaussian noise increases, dropping below 90% around noise_std=0.5.

## Rationale
Based on class separation distance in H01, moderate noise should overlap the decision boundary.

## Builds On
HYPOTHESIS_01 (baseline established at 98% accuracy)

## Status: Testing
```

**Create the next script**:

```
Please create script_02_noise_sweep.py that:

1. Uses the same data generation as script_01
2. Adds Gaussian noise with std values: [0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
3. For each noise level, trains classifier and reports accuracy
4. Plots accuracy vs noise level
5. Identifies the threshold where accuracy drops below 90%

Hypothesis: HYPOTHESIS_02.md — Accuracy drops below 90% around noise_std=0.5
```

**Run and analyze**:

```bash
python experiments/01_synthetic/script_02_noise_sweep.py
```

Then write `analysis/ANALYSIS_02.md` with your interpretation. The AI can read the log file directly to help you interpret results.

### Iteration 3: Explore Boundaries

Based on results, you might find the threshold is different than expected. This is where YOUR insight matters:

```markdown
# analysis/ANALYSIS_03.md

## My Contribution - Iteration 03

Results showed accuracy dropped below 90% at noise_std=0.3, not 0.5.

I noticed the classes were closer together than I assumed.
AI suggested increasing class separation, but I realized we should
instead test whether a non-linear boundary helps at the CURRENT separation.

This is a different question than AI suggested — testing boundary
complexity rather than data properties.
```

Add this insight to `prompts/KNOWN_PATTERNS.md` if it becomes a recurring lesson:

```markdown
### 1.X Class Separation vs. Boundary Complexity
**Context**: When accuracy is lower than expected
**Lesson**: Check whether the issue is data overlap or boundary flexibility before adjusting data
```

---

## Phase 2: Downloaded Benchmark Data

Now we validate our findings on real-world benchmark datasets that others have used.

### Transition to Benchmarks

**Document the transition** in a brief plan in `plans/` or update `background/`:

```markdown
# Summary of Synthetic Phase

- Linear boundaries achieve 98% on clean data
- Accuracy degrades to <90% at noise_std=0.3
- Non-linear boundaries provide ~5% improvement at high noise

## Questions for Benchmark Phase

1. Do these patterns hold on real datasets?
2. What noise levels exist in common benchmarks?
3. Are there datasets where linear boundaries fail unexpectedly?
```

### Iteration 4: Download and Characterize Data

```
Please create script_01_download_benchmarks.py in experiments/02_downloaded/ that:

1. Downloads these sklearn datasets: Iris, Wine, Breast Cancer
2. For each dataset:
   - Reports basic statistics (samples, features, classes)
   - Estimates "noise level" via class overlap
   - Tests linear classifier accuracy
3. Saves data to data/downloaded/
4. Creates a summary comparing to our synthetic findings

Hypothesis: HYPOTHESIS_03.md — Linear accuracy >90% on clean datasets,
lower on datasets with more class overlap.
```

### Iteration 5: Validate Noise Findings

```
Please create script_02_benchmark_noise_analysis.py that:

1. Loads the downloaded benchmark datasets
2. For each dataset:
   - Adds artificial noise at levels [0, 0.1, 0.2, 0.3, 0.5]
   - Measures accuracy degradation
   - Compares degradation curve to synthetic results
3. Tests whether our synthetic threshold (0.3) predicts benchmark behavior

Hypothesis: HYPOTHESIS_04.md — Datasets with inherent noise equivalent to
std=0.3 will show similar accuracy to our synthetic experiments.
```

### Document Cross-Validation

Write `analysis/ANALYSIS_05.md`:

```markdown
# Analysis 05: Benchmark Validation Summary

## Findings
- Iris: Linear accuracy 97%, matches synthetic clean data
- Wine: Linear accuracy 91%, some natural class overlap
- Breast Cancer: Linear accuracy 95%, clean separation

## Comparison to Synthetic
Our synthetic noise threshold (0.3) correctly predicted:
- Iris would have high accuracy (low inherent noise)
- Wine would be borderline (moderate inherent noise)

## Limitations Discovered
- 2D synthetic data doesn't capture high-dimensional effects
- Real datasets have non-Gaussian noise patterns

## Known Patterns Update
Added to KNOWN_PATTERNS.md: "High-dimensional data may have lower effective
noise thresholds than 2D synthetics suggest."
```

---

## Phase 3: Real Data

Now apply your validated approach to your actual research data.

### Prepare Real Data

Place your data in `data/real/` and document it:

```markdown
# data/real/README.md

## Dataset: [Your Dataset Name]

**Source**: [Where it came from]
**Samples**: [Number]
**Features**: [Number and description]
**Classes**: [What you're classifying]

**Known characteristics**:
- Expected noise level based on collection method
- Any preprocessing applied
```

### Iteration 6: Apply to Real Data

```
Please create script_01_real_data_baseline.py in experiments/03_real_data/ that:

1. Loads my real dataset from data/real/
2. Applies the same linear classifier we validated
3. Reports accuracy and compares to benchmark expectations
4. Identifies whether results match our noise-accuracy model

Based on synthetic and benchmark phases, I expect:
- If data is clean: >95% accuracy
- If data has moderate noise: 85-95% accuracy
- If data has high noise: <85% accuracy
```

### Iteration 7: Apply Insights

Based on your real data results, apply what you learned:

```
Results show 82% accuracy on real data, suggesting high noise.

From our synthetic experiments, we found non-linear boundaries
improved accuracy by ~5% at high noise levels.

Please create script_02_nonlinear_comparison.py that:
1. Tests non-linear classifiers (SVM with RBF, Random Forest)
2. Compares to linear baseline
3. Determines if the ~5% improvement holds on real data
```

---

## Compiling Results

### Generate AI Context

When starting a new session or switching AI tools:

```bash
python scripts/compile_for_ai.py
```

This creates a summary of:
- All scripts and their log outputs
- Hypotheses tested and results
- Current state of the research

For **IDE-native** tools, the AI can read these files directly. For **browser-paste**, copy the compiled output into your new session.

### Review the Audit Trail

Your project now contains a complete audit trail:

```
hypotheses/
├── HYPOTHESIS_01.md    # Baseline prediction
├── HYPOTHESIS_02.md    # Noise sensitivity
├── HYPOTHESIS_03.md    # Benchmark behavior
└── HYPOTHESIS_04.md    # Cross-validation

experiments/
├── 01_synthetic/
│   ├── script_01_baseline_no_noise.py
│   ├── script_02_noise_sweep.py
│   └── script_03_nonlinear_test.py
├── 02_downloaded/
│   ├── script_01_download_benchmarks.py
│   └── script_02_benchmark_noise_analysis.py
└── 03_real_data/
    ├── script_01_real_data_baseline.py
    └── script_02_nonlinear_comparison.py

results/logs/
├── script_01_baseline_no_noise_20250115_143022.log
├── script_02_noise_sweep_20250115_152311.log
└── ...  (one log per script run)

analysis/
├── ANALYSIS_01.md      # Baseline interpretation
├── ANALYSIS_02.md      # Noise sweep findings
├── ANALYSIS_03.md      # Boundary complexity insight
├── ANALYSIS_04.md      # Benchmark characterization
└── ANALYSIS_05.md      # Cross-validation summary
```

Each hypothesis links to a script, each script produces a log, each log gets an analysis. No output pasting needed — the AI reads logs directly.

---

## Writing Up Findings

### Export for Paper

Use the `paper_draft/` directory to compile findings:

**methods_schematic.md**:
```markdown
## Methods

1. Established baseline on synthetic data (N=400, 2 classes)
2. Characterized noise-accuracy relationship
3. Validated on 3 benchmark datasets
4. Applied to real dataset (N=[your N])
```

**results_narrative.md**:
```markdown
## Results

### Synthetic Phase
Linear classification achieved 98% accuracy on clean synthetic data.
Accuracy degraded below 90% at noise std=0.3.

### Benchmark Validation
The noise threshold correctly predicted accuracy on Iris (97%),
Wine (91%), and Breast Cancer (95%) datasets.

### Real Data Application
Real data showed 82% linear accuracy, consistent with high noise.
Non-linear methods improved accuracy to 87%, matching synthetic predictions.
```

### Track Final Contributions

In `prompts/intellectual_contribution.md`:

```markdown
## Project Summary - Intellectual Contributions

### Key Insights I Provided
1. Identified noise threshold as the key variable to characterize
2. Recognized that benchmark validation should precede real data
3. Connected synthetic findings to real data interpretation
4. Chose boundary complexity over data adjustment (Iteration 3)

### Where AI Helped
1. Generated boilerplate code quickly
2. Suggested standard datasets for validation
3. Implemented visualization consistently

### Novel Contribution
The systematic characterization of noise thresholds across synthetic,
benchmark, and real data provides a framework for predicting classifier
performance on new datasets.
```

---

## Summary

You've now completed a full SMAIRT cycle:

1. ✅ **Synthetic**: Fast iteration, established baseline and thresholds
2. ✅ **Benchmark**: Validated findings on known datasets
3. ✅ **Real Data**: Applied validated approach to actual research
4. ✅ **Documentation**: Complete audit trail for reproducibility

### Key Practices (The 10 Steps)

1. **Track intellectual contributions** — document YOUR insights vs AI's
2. **Write hypotheses before experiments** — forces clarity
3. **Follow the data progression** — synthetic → downloaded → real
4. **Number scripts sequentially** — clear timeline
5. **Maintain the audit trail** — hypothesis → script → log → analysis
6. **Name log files to match scripts** — handled by TeeLogger
7. **Use compile_for_ai.py** for cross-tool context transfer
8. **Use priming prompts** from SESSION_START.md; maintain KNOWN_PATTERNS.md
9. **Follow 4-part structure** — Background, Hypothesis, Methods, Results
10. **Use future directions to seed next iteration** — keep momentum

### What's Different from Legacy SMAIRT

| Old Pattern | New Pattern |
|-------------|-------------|
| Paste output into script comments | TeeLogger writes to `results/logs/` automatically |
| AI can't read your files | IDE-native AI reads logs, hypotheses, analysis directly |
| Manual session logging required | AI tracks context via project files |
| 12 Steps | Streamlined to 10 Steps |
| No error tracking | `KNOWN_PATTERNS.md` prevents repeated mistakes |
| No shared code | `scripts/shared/` for reusable utilities |

### Next Steps

- Explore `scripts/README.md` for additional helper scripts
- Read `docs/SMAIRT_PHILOSOPHY.md` for deeper framework understanding
- Check `docs/BEST_PRACTICE_SINGLE.md` or `BEST_PRACTICE_COLLABORATIVE.md` for workflow tips
- Review `docs/12_STEPS.md` for the complete 10 Steps reference
