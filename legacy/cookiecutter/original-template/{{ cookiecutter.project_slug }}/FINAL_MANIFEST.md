# Final Manifest

{% if cookiecutter.project_mode == 'paper_driven' %}
**Project**: {{ cookiecutter.project_name }}
**Author**: {{ cookiecutter.author_name }}
**Created**: [DATE]
**Last Updated**: [DATE]

This file maps all final results to their source analyses and iterations.
It serves as the definitive record of which iteration produced each paper element.

---

## Summary

| Paper Element | Analysis | Iteration | Status |
|---------------|----------|-----------|--------|
| Figure 1 | [analysis path] | iter_XX | ⏳ Pending |
| Figure 2 | [analysis path] | iter_XX | ⏳ Pending |
| Table 1 | [analysis path] | iter_XX | ⏳ Pending |

---

## How to Use This File

1. **During analysis**: Update this file when you finalize an iteration
2. **For paper writing**: Reference this file to find the source of each result
3. **For reproducibility**: This file documents the exact path to reproduce any result

## Updating This File

Use the helper script:
```bash
python scripts/generate_manifest.py
```

Or update manually when finalizing an iteration:
```bash
python scripts/finalize_iteration.py --analysis 01_section/01_analysis --iteration 02
```

---

## Detailed Entries

### [Paper Element Name]

- **Source**: `analysis/[section]/[analysis]/final/`
- **Iteration**: iter_XX
- **Script**: `run_analysis_XX.py`
- **Config**: `config_XX.yaml`
- **Finalized**: YYYY-MM-DD
- **Notes**: [Any relevant notes]

---

*This file is automatically updated by `scripts/finalize_iteration.py` and `scripts/generate_manifest.py`*
{% else %}
This file is only used in paper-driven mode.

For standard SMAIRT mode, results are tracked through the audit trail:
- `hypotheses/` - Hypothesis documentation (H1_*.md, H2_*.md, ...)
- `results/logs/` - Auto-captured output logs (via TeeLogger)
- `results/figures/` - Generated figures
- `prompts/intellectual_contribution.md` - Your contributions
{% endif %}
