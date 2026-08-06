#!/usr/bin/env python3
"""Record what an iteration turned out to show.

An iteration is not finished when its script runs; it is finished when someone has read
the log and written down what it means. This records that reading in
`analysis/ITERATION_LOG.md`, so the log answers "what came of iteration 04" without
opening every analysis file.

It refuses until `analysis/ANALYSIS_NN.md` exists. An outcome recorded before the run has
been interpreted is a guess, and the ordering the workflow claims — interpret, then
record — is worth enforcing. This helper has no opinion about *what* the outcome says.

Two things happen, and the difference matters:

- A line is appended to the outcome history, always. Nothing there is ever edited, so a
  revised conclusion still shows what it revised.
- The state table's outcome cell is filled, but only while it still holds the placeholder
  `new_iteration.py` wrote. Once it holds your prose, it is yours to change.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.shared.iterations import (  # noqa: E402
    append_outcome_history,
    fill_outcome_placeholder,
    project_root,
    recorded_iterations,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("iteration", type=int, help="Iteration the outcome belongs to.")
    parser.add_argument(
        "--outcome",
        required=True,
        help=(
            "What the run showed, in prose. A panel needs every probe's result, because "
            "'3 of 8 above criterion, 1 regression' is the finding and a single verdict "
            "would discard it."
        ),
    )
    arguments = parser.parse_args()

    root = project_root()
    number = arguments.iteration

    recorded = sorted(recorded_iterations(root))
    if number not in recorded:
        available = ", ".join(f"{value:02d}" for value in recorded)
        detail = f"recorded iterations: {available}" if available else "no iterations are recorded"
        parser.error(
            f"iteration {number:02d} is not recorded in analysis/ITERATION_LOG.md; {detail}"
        )

    analysis = root / "analysis" / f"ANALYSIS_{number:02d}.md"
    if not analysis.exists():
        parser.error(
            f"no interpretation found at {analysis.relative_to(root)}; interpret the run "
            "before recording what it showed"
        )

    log_path = append_outcome_history(root, number=number, outcome=arguments.outcome)
    filled = fill_outcome_placeholder(root, number=number, outcome=arguments.outcome)

    print(f"Recorded the outcome of iteration {number:02d} in {log_path.relative_to(root)}")
    if filled:
        print("Filled the row's outcome cell, which still held its placeholder.")
        return
    print(
        "The row already holds your own wording, so it was left untouched. Update it "
        "yourself if this supersedes what it says; the history above keeps both."
    )


if __name__ == "__main__":
    main()
