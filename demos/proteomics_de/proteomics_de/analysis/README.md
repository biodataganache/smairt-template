# Analysis

Interpretation of results and documentation of the research journey.

### The 4-Part Structure

The template records **4 pieces of information in separate files**:

1. **Background** - The question that went into prompting it, what has been done on that area, what's known about that question from the literature, and a summary of the previous results that have come up to this point
2. **Hypothesis** - Could be in a separate file or at the end of the background
3. **Methods** - The actual code and data required to test the hypothesis
4. **Results + Interpretation** - The output logs (auto-captured by TeeLogger) plus analysis through the lens of the hypothesis

The **next steps** from your analysis feed right back into the background for the next iteration.

## Files

- `ANALYSIS_TEMPLATE.md` - Template for documenting each iteration's results, interpretation, and next steps
- `BREADCRUMB_TRAIL.md` - Running log of all analyses performed (paper-driven mode)
- `ANALYSIS_PLAN.md` - Paper structure mapping and iteration planning (paper-driven mode)
- `REPOSITORY_PLAN.md` - Repository organization plan (paper-driven mode)

## The Audit Trail

The modern SMAIRT audit trail connects:

```
hypotheses/H1_*.md → experiments/script_XX_*.py → results/logs/script_XX_*.log → analysis/ANALYSIS_TEMPLATE.md
```

- **Hypotheses** are documented in `hypotheses/` using `HYPOTHESIS_TEMPLATE.md`
- **Scripts** test hypotheses; TeeLogger auto-captures output to `results/logs/`
- **Analysis** interprets log results through the lens of the hypothesis

## What Goes Here

1. Did results support the hypothesis?
2. What limitations were identified?
3. What secondary observations were made?
4. What are the logical next steps?

Next steps (#4) will often be used to seed the next round of experimentation. Document any reusable patterns or recurring errors in `prompts/KNOWN_PATTERNS.md`.
