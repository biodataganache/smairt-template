# Project State — {{ cookiecutter.project_name }}

> **Layer 1 of 3: working memory.** Keep this file SHORT and CURRENT — overwrite it,
> don't append. It answers one question: *where are we right now?* It is re-read at
> the start of every session and after every compaction/restart.
>
> Long-term knowledge does NOT live here — established findings go in `FINDINGS.md`
> (layer 2), and the full record lives in `analysis/`, `results/logs/`,
> `hypotheses/` (layer 3, never deleted).

_Last updated: [DATE] · iteration [XX] · phase [synthetic / downloaded / real]_

## Research Question

{{ cookiecutter.initial_research_question }}

## Current Hypothesis

<!-- The one hypothesis under test right now. Link: hypotheses/HYPOTHESIS_XX.md -->
-

## Last Result

<!-- One or two lines. What did the most recent experiment show? Link the log. -->
- Script:
- Log: `results/logs/`
- Outcome:

## Next Step

<!-- The single next action. Keep it to one concrete thing. -->
-

## Open Threads / Parked Ideas

<!-- Short bullets. Things to come back to, not yet active. -->
-

## Active Constraints

<!-- Anything that must hold for current work (data, compute, deadlines). -->
-

---

### How to keep this file healthy

- **Overwrite, don't grow.** If a section is getting long, you're putting history
  here that belongs in `analysis/` or `FINDINGS.md`.
- **Before a new experiment:** read `FINDINGS.md` and search recent `analysis/`
  files so you don't repeat past work or violate an established requirement.
- **When a result becomes a durable fact:** promote it to `FINDINGS.md` (see
  `prompts/COMPACTION.md`), then trim it down to a one-line "Last Result" here.
