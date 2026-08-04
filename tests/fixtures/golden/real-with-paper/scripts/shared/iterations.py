"""Locate, number, and record iterations.

An iteration is one attempt at moving the work forward: one script, the log it
produced, and the interpretation of that log. Iterations are numbered across the whole
project in the order the work happened, so the numbering reads as a timeline rather
than a filing scheme.

Shared by the `new_track.py`, `new_iteration.py`, and `select_result.py` helpers so all
three agree on where things live and how they are numbered.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

PHASES = {
    "synthetic": "01_synthetic",
    "downloaded": "02_downloaded",
    "real": "03_real_data",
}
"""Phase names a researcher types, and the directory each one means."""

ITERATION_LOG_HEADER = """# Iteration Log

One row per iteration, in the order the work happened. Rows are appended and never
rewritten: a row that turned out to be wrong is corrected by a later row saying so,
because the sequence of attempts is itself evidence.

`Kind` is `single` when the iteration tests one change, or `panel (N)` when it probes N
candidate directions at once. `Outcome` is prose rather than a keyword, because a panel
that improves three of eight candidates cannot be described by a single verdict.

Fill in `Outcome` once the run has been interpreted. Full results belong in the matching
`analysis/ANALYSIS_NN.md`; this table is the index into them.

| Iteration | Date | Script | Hypotheses | Kind | Changed from | Outcome |
|---|---|---|---|---|---|---|
"""


def project_root() -> Path:
    """Return the project root, derived from this file's location."""
    return Path(__file__).resolve().parents[2]


def slugify(text: str) -> str:
    """Return a filename-safe form of researcher-supplied text."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def next_iteration_number(root: Path) -> int:
    """Return the next iteration number, counting scripts across every phase.

    Numbering is project-wide rather than per phase so that the numbers order the work
    in time. A researcher who moves from synthetic to real data continues counting.
    """
    return max(existing_iterations(root), default=0) + 1


def existing_iterations(root: Path) -> list[int]:
    """Return every iteration number that already has a script."""
    return [
        int(match.group(1))
        for script in (root / "experiments").glob("*/script_*.py")
        if (match := re.match(r"script_(\d+)", script.name))
    ]


def find_iteration_script(root: Path, number: int) -> Path | None:
    """Return the script for an iteration, or None when that iteration has none."""
    matches = sorted((root / "experiments").glob(f"*/script_{number:02d}_*.py"))
    return matches[0] if matches else None


def append_iteration_row(
    root: Path,
    *,
    number: int,
    script_name: str,
    hypotheses: str,
    kind: str,
    changed_from: str,
) -> Path:
    """Append one row to the iteration log, creating the log when it is absent.

    Appending rather than printing a row for someone to paste is deliberate: the paste
    is the step that gets skipped, and a log with gaps cannot be trusted as a record.
    Existing rows are never read back or modified.
    """
    log_path = root / "analysis" / "ITERATION_LOG.md"
    if not log_path.exists():
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(ITERATION_LOG_HEADER)
    row = (
        f"| {number:02d} | {date.today().isoformat()} | `{script_name}` | "
        f"{hypotheses} | {kind} | {changed_from} | [Record after interpreting] |\n"
    )
    with log_path.open("a") as log:
        log.write(row)
    return log_path
