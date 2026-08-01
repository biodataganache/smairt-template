# SMAIRT Paper Overlay Reference

## Evidence Mapping

For each publication element, record:

| Field | Meaning |
| --- | --- |
| Paper element | Outline section, claim, figure, table, or reviewer concern |
| Question/hypothesis | Scientific motivation and prediction |
| Phase experiment | Exact script, data, and configuration used |
| Raw evidence | Matching files under `results/logs/` and `results/figures/` |
| Analysis/decision | Interpretation and accept, revise, or reject decision |
| Study report | Consolidated scientific conclusion and limitations |

Store publication-focused mapping and planning under `paper/`; do not relocate
or duplicate the authoritative experimental audit trail there.

## Reviewer Revisions

1. Record each concern and the affected paper element.
2. Classify it as writing-only, reanalysis, or new experiment.
3. For reanalysis or new experiments, update the hypothesis if needed and run
   the work in the appropriate phase directory.
4. Preserve the raw log, write an analysis/decision, and update the study report.
5. Link the evidence and response from the paper overlay.

## Final Check

- Every scientific claim maps to recorded evidence.
- Every selected figure or table has reproducible provenance.
- Negative and superseded results remain in the audit trail.
- Exploratory and publication-focused analyses remain distinguishable.
- The manuscript does not overstate the study report's conclusions.
