# Final Manifest

**Project**: {{ project.name }}
**Author**: {{ researcher.name }}
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

The helper only prints or creates an inventory; it never rewrites this file. Edit it
by hand as claims settle, since deciding what counts as final evidence is yours.

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

*This file is yours to maintain. `scripts/generate_manifest.py` can inventory the
evidence it finds, but nothing overwrites your claims.*
