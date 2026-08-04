#!/usr/bin/env python3
"""Start a research track: a plan and a hypothesis.

A track is a direction of inquiry spanning as many iterations as it takes. This helper
creates the two records a track needs before any work starts.

It deliberately does not create the first script. The criteria have to be written and
committed before an experiment exists, because that commit order is the only evidence
that the criterion preceded the result. A helper that produced an empty-criteria
hypothesis and a script in the same instant would destroy the thing it was meant to
protect. Run `new_iteration.py` once the criteria are recorded.

Nothing is overwritten. If a file is already there, this refuses rather than replacing it.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.shared.iterations import PHASES, project_root, slugify  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", help="What this track sets out to settle.")
    parser.add_argument("phase", choices=PHASES, help="Data phase the first iteration runs in.")
    arguments = parser.parse_args()

    root = project_root()
    name = slugify(arguments.question)
    if not name:
        parser.error("question must contain a letter or number")
    short_name = "_".join(name.split("_")[:5])

    hypothesis_number = _next_hypothesis_number(root)
    hypothesis_id = f"HYPOTHESIS_{hypothesis_number:02d}"
    hypothesis_path = root / "hypotheses" / f"{hypothesis_id}.md"
    plan_path = root / "plans" / f"PLAN_{short_name.upper()}.md"

    for path in (hypothesis_path, plan_path):
        if path.exists():
            parser.error(f"refusing to overwrite existing file: {path}")

    hypothesis_path.parent.mkdir(parents=True, exist_ok=True)
    hypothesis_path.write_text(_hypothesis(hypothesis_id, arguments.question, arguments.phase))
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(_plan(arguments.question, hypothesis_id))

    print(f"Created {hypothesis_path.relative_to(root)}")
    print(f"Created {plan_path.relative_to(root)}")

    print()
    print("Next: write the prediction and both criteria in the hypothesis file, and commit")
    print("them before creating the first iteration. That commit order is what shows the")
    print("criterion preceded the result, so this helper deliberately stops here:")
    print(
        f"  python scripts/new_iteration.py baseline {arguments.phase} --hypothesis {hypothesis_id}"
    )


def _next_hypothesis_number(root: Path) -> int:
    """Return the next hypothesis number, so identifiers stay unique and ordered."""
    numbers = [
        int(match.group(1))
        for path in (root / "hypotheses").glob("HYPOTHESIS_*.md")
        if (match := re.match(r"HYPOTHESIS_(\d+)\.md$", path.name))
    ]
    return max(numbers, default=0) + 1


def _hypothesis(hypothesis_id: str, question: str, phase: str) -> str:
    return f"""# Hypothesis {hypothesis_id} - {question}

## Status

PENDING

## Background

[What question or prior result motivates this? Link the background, analysis, or
iteration that led here.]

## Hypothesis Statement

**Prediction**: [State a specific, testable prediction.]

**Rationale**: [Why the available evidence makes this prediction plausible.]

**Alternative explanations**: [Other mechanisms that could produce the same observation.]

**Success criteria**: [What result would support this. Write this before running anything.]

**Rejection criteria**: [What result would refute or materially weaken this.]

Both criteria belong here before the experiment script exists. A criterion written after
the data is a rationalization.

## Experimental Design

- **Phase**: {phase}
- **Data**: [Inputs and their provenance record]
- **Controls**: [Baselines, negative controls, or comparison methods]
- **Key metrics**: [Measurements and uncertainty estimates]
- **Randomness**: [Seeds, repetitions, or sampling plan]

## Sub-Hypotheses

Use these when a panel iteration probes several directions at once, one entry per probe.

### {hypothesis_id}A: [First sub-prediction]

- **Prediction**: [Specific outcome]
- **Success criteria**: [Measurable threshold]

## Iterations

| Iteration | What it tested | Outcome |
|---|---|---|

## Results

Complete after interpreting. Link the log, figures, and `analysis/ANALYSIS_NN.md` rather
than copying output here.

## Notes

[Caveats, or decisions made before execution.]
"""


def _plan(question: str, hypothesis_id: str) -> str:
    return f"""# Plan: {question}

## Status

DRAFT

## Question

{question}

## Hypotheses

- `{hypothesis_id}` - [Short form of the prediction]

## Approach

[How this track answers the question. Name what would make you abandon it.]

## Success criteria

[How you will know the track answered its question, as distinct from the criteria for
any single hypothesis.]

## Dependencies

- [ ] Data: [What must be available]
- [ ] Code: [What must exist first]
- [ ] Results: [Prior iterations that must complete]

## Planned iterations

| # | Kind | What it tests | Depends on |
|---|---|---|---|
| 1 | single | [Baseline] | — |

`single` tests one change. `panel (N)` probes N candidate directions at once.

## Expected outputs

- Interpretations: `analysis/ANALYSIS_NN.md`
- Figures: [Which figures, and the claim each supports]

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| [Risk] | High/Medium/Low | [How to handle it] |

## Notes

[Related work, links, or context.]
"""


if __name__ == "__main__":
    main()
