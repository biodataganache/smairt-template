# Collaborative SMAIRT Practices

## Work in Evidence Slices

A complete research change normally includes a hypothesis, experiment script, execution log,
analysis, and any figure or result summary needed for the decision. Commit those related
files together when practical.

## Branches

Use short-lived branches for independent experiments or contributors. Merge only after the
evidence and interpretation are readable. Pull current shared findings before beginning a
new dependent experiment.

## Reduce Conflicts

- Create separate hypothesis and analysis files instead of editing one large record.
- Coordinate script numbering or use descriptive contributor/track suffixes.
- Treat `prompts/KNOWN_PATTERNS.md`, `analysis/BREADCRUMB_TRAIL.md`, and contribution records
  as append-oriented living documents.
- Discuss edits that change shared background assumptions or data provenance.

## Required Handoff Evidence

1. Hypothesis with author/date and predeclared criteria.
2. Script or method linked to its inputs.
3. Complete tracked execution log, unless sensitivity or size requires an explicit exception.
4. Analysis stating the evidence-based decision and boundaries.
5. Contribution record for important human choices, critiques, or pivots.

New collaborators and assistants should reconstruct the project from `smairt.yaml`, project
context, hypotheses, scripts, logs, and analyses. A conversation transcript is not the
scientific record.
