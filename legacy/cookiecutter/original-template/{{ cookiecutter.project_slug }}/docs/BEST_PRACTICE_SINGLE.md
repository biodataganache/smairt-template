# SMAIRT Git Best Practices

## Single-User Use Case

### File Creation Timeline

**At Project Start:**
1. `background/01_initial_question.md` - Define your research question
2. `hypotheses/H1_*.md` - Record your first hypothesis (using `HYPOTHESIS_TEMPLATE.md`)
3. `prompts/KNOWN_PATTERNS.md` - Begin documenting patterns as they emerge
4. `prompts/intellectual_contribution.md` - Start tracking your contributions

**At Each Iteration:**
1. Create script: `experiments/[phase]/script_XX_description.py` (uses TeeLogger)
2. Run script — output auto-captured to `results/logs/`
3. Update `hypotheses/` with results (supported/not supported)
4. Document interpretation in `analysis/ANALYSIS_TEMPLATE.md` (copy for each iteration)
5. Update `prompts/KNOWN_PATTERNS.md` with any patterns or errors discovered
6. Update `prompts/intellectual_contribution.md` with YOUR critical insights

{% if cookiecutter.starting_phase != 'real' %}
**At Phase Transitions:**
1. Create `background/iteration_XX_background.md` summarizing what was learned
2. Archive or tag the phase completion
{% endif %}

### Git Workflow

```
# Commit cadence: Once per completed iteration

# Pattern for commit messages:
git commit -m "Iteration XX: [hypothesis tested] - [result: supported/refuted]"

# Example commits:
git commit -m "Iteration 01: Test linear separability on synthetic data - supported"
git commit -m "Iteration 02: Add noise robustness test - partial support, breaks >20% noise"
git commit -m "Iteration 03: Validate on Iris benchmark - supported"
```

**Tagging Strategy:**
```bash
# Tag phase completions
git tag -a "phase-synthetic-complete" -m "Synthetic phase complete. Key findings: [summary]"
git tag -a "phase-downloaded-complete" -m "Benchmark validation complete"
git tag -a "v1.0-initial-findings" -m "First complete cycle through all phases"
```

**Branch Strategy (optional for single user):**
- Keep it simple: work on `main`
- Use branches only for exploratory tangents you might abandon
```bash
git checkout -b explore/alternative-algorithm
# If it works, merge back; if not, leave as documentation of what didn't work
```

### Recommended Commit Points

| Event | Commit? | Message Pattern |
|-------|---------|-----------------|
| New hypothesis formulated | ✓ | "Hypothesis XX: [brief statement]" |
| Script created and run | ✓ | "Iteration XX: [script name] - [result]" |
| Dead end reached | ✓ | "Dead end: [approach] - [why it failed]" |
| Phase transition | ✓ + Tag | "Complete [phase] phase" |
| Major insight | ✓ | "Insight: [discovery]" |
| Session log updated | Bundle with iteration | — |
