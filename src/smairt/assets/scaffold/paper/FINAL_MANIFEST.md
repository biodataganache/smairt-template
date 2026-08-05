# Final Manifest

**Project**: {{ project.name }}
**Author**: {{ researcher.name }}
**Created**: [DATE]
**Last Updated**: [DATE]

Every claim in the paper maps here to the evidence behind it. This is the file that
answers "where did this number come from" without anyone reconstructing it from memory.

---

## Summary

| Paper Element | Claim | Iteration | Status |
|---|---|---|---|
| Figure 1 | [What it is evidence for] | [NN] | Pending |
| Figure 2 | [What it is evidence for] | [NN] | Pending |
| Table 1 | [What it is evidence for] | [NN] | Pending |

Status: `Pending`, `Draft`, `Final`.

---

## How to Use This File

1. **While the work is ongoing**: add an entry when a result becomes a claim you intend
   to publish
2. **While writing**: use it to find the source of every number in the manuscript
3. **For reproducibility**: each entry names the script and log needed to repeat the run

## Updating This File

Use the selection helper when you decide an iteration is reportable:

```bash
python3 scripts/select_result.py 7 --claim "The wider layer exceeds the target" --paper
```

For a panel, include `--probes` naming the arms that support the claim. The helper appends
one detailed entry with the exact log path and never edits an existing claim. It may write
the entry because invoking it is your explicit selection decision; it never chooses what to
report.

Use `python3 scripts/generate_manifest.py` when you need an inventory of evidence that
exists but has not been selected. That helper only prints or creates an inventory; it never
rewrites this file.

---

## Detailed Entries

### [Paper Element Name]

- **Claim**: [The specific statement this element supports]
- **Iteration**: [NN]
- **Script**: `experiments/[phase]/script_NN_description.py`
- **Evidence**: `results/logs/script_NN_description_<timestamp>.log`
- **Interpretation**: `analysis/ANALYSIS_NN.md`
- **Figure or table file**: [path, if applicable]
- **Recorded**: YYYY-MM-DD
- **Notes**: [Caveats, or the boundary where the result stops holding]

The log is what makes the claim checkable, so name the exact one rather than the
directory. If the element came from a panel iteration, name which probes support the
claim; a panel where three of eight candidates worked must not be reported as though the
panel succeeded.

---

*This file is yours to maintain. `scripts/generate_manifest.py` can inventory the
evidence it finds, but nothing overwrites your claims.*
