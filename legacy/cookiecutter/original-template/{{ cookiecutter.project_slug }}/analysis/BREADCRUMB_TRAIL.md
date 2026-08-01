# Breadcrumb Trail

{% if cookiecutter.project_mode == 'paper_driven' %}
## Project: {{ cookiecutter.project_name }}

This file maintains a running log of all analyses performed, creating a breadcrumb trail for reproducibility and AI context.

---

## Log Format

Each entry should include:
- Date
- Analysis performed
- Key findings
- Next steps

---

## Analysis Log

### [DATE] - Project Setup

**What was done**:
- Created project structure
- Added initial data to `data/`
- Created analysis plan

**Key findings**:
- [Initial observations about data]

**Next steps**:
- Begin with analysis in `01_*/`

---

### [DATE] - [Analysis Name]

**What was done**:
- [Description of analysis]
- Iteration: [iter_XX]
- Script: [path to script]

**Key findings**:
- [Finding 1]
- [Finding 2]

**Metrics**:
- [Metric 1]: [Value]
- [Metric 2]: [Value]

**Decision**: [ACCEPT/REVISE/ABANDON]

**Next steps**:
- [What to do next]

---

## Quick Reference

| Date | Analysis | Iteration | Decision | Notes |
|------|----------|-----------|----------|-------|
| YYYY-MM-DD | [Name] | iter_01 | REVISE | [Brief note] |

---

## Tips for Maintaining This Log

1. Update after each significant analysis run
2. Include enough detail for AI to understand context
3. Link to specific files/iterations
4. Note any unexpected findings
5. Document dead ends (they're valuable too!)
{% else %}
This file is only used in paper-driven mode.

For standard SMAIRT mode, the breadcrumb trail is maintained through:
- TeeLogger auto-captures all script output to `results/logs/`
- `hypotheses/` tracks each hypothesis and its outcome
- `analysis/ANALYSIS_TEMPLATE.md` documents interpretation per iteration
- `prompts/KNOWN_PATTERNS.md` accumulates reusable patterns and error solutions
- `prompts/intellectual_contribution.md` records your contributions
{% endif %}
