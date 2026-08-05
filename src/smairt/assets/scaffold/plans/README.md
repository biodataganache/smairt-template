# Plans

Planning documents for this SMAIRT project.

## Purpose

Plans are created **before** embarking on multi-step work. They serve as:
- A contract between you and the AI about what will be built
- A reference to prevent scope creep during implementation
- A record of architectural decisions and their rationale

## When to Create a Plan

Create a plan document when:
- Starting a new research track
- Designing a complex multi-script experiment
- Proposing an architecture change
- Coordinating work across team members
- Pivoting to a new approach after a dead end

## Plan Template

`PLAN_TEMPLATE.md` in this directory is the template. `scripts/new_track.py` fills it in
when it starts a track, so a plan you write by hand and a plan the helper creates have the
same shape. Edit the template to suit your field and both follow.

```bash
python3 scripts/new_track.py "The wider layer exceeds the baseline" synthetic
```

## Naming Convention

```
PLAN_[BRIEF_DESCRIPTION].md
```

Examples:
- `PLAN_RAY_TUNE_STRATEGY.md`
- `PLAN_MULTIMODAL_INTEGRATION.md`
- `PLAN_FITNESS_EMBEDDING_DYNAMICS.md`

A track is named by what it investigates, not by a letter. Track identity lives in
`analysis/ANALYSIS_PLAN.md` and in the hypothesis a plan points at, never in a prefix on a
filename — a letter in front of a number would make the iteration numbering unreadable.
