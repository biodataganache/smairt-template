# Iteration Review Prompt

{% if cookiecutter.project_mode == 'paper_driven' %}
## Context

You are reviewing an iteration of an analysis for a paper-driven SMAIRT project.

## Your Task

Review the current iteration and help decide whether to:
- **ACCEPT** - Results meet targets, ready for paper
- **REVISE** - Promising but needs parameter tuning
- **ABANDON** - Fundamental issue, try different approach

## Information to Provide

Please share:
1. **Analysis name and iteration number**
2. **The script that was run** (or key code sections)
3. **The results/metrics obtained**
4. **Any figures generated**
5. **Your observations**

## Review Checklist

### Results Quality
- [ ] Metrics are reasonable for the domain
- [ ] Results are consistent across runs (reproducible)
- [ ] No obvious errors or anomalies
- [ ] Results align with hypotheses (or provide interesting counter-evidence)

### Code Quality
- [ ] Code is readable and documented
- [ ] Parameters are configurable (in config file)
- [ ] Random seed is set for reproducibility
- [ ] Output paths are correct

### Documentation
- [ ] NOTES.md is updated for this iteration
- [ ] Key findings are documented
- [ ] Any issues or surprises are noted

## Decision Framework

### ACCEPT if:
- Metrics meet or exceed targets
- Results are stable and reproducible
- Findings are interpretable and meaningful
- Ready to include in paper

### REVISE if:
- Results are promising but not optimal
- Specific parameters could be tuned
- Minor issues that can be addressed
- Clear path to improvement

### ABANDON if:
- Fundamental flaw in approach
- Results are not meaningful
- Better alternative approach exists
- Time better spent elsewhere

## Next Steps

Based on the decision:
- **ACCEPT**: Update ITERATION_LOG.md, copy to `final/`, update FINAL_MANIFEST.md
- **REVISE**: Create new iteration, document changes to try
- **ABANDON**: Document learnings, propose alternative approach
{% else %}
This prompt is for paper-driven mode only.
{% endif %}
