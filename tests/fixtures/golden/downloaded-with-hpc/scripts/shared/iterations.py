"""Locate, number, create, and record iterations.

An iteration is one attempt at moving the work forward: one script, the log it
produced, and the interpretation of that log. Iterations are numbered across the whole
project in the order the work happened, so the numbering reads as a timeline rather
than a filing scheme.

Every numbered script under `experiments/` is an iteration and appears in
`analysis/ITERATION_LOG.md`. This module is the only place that assigns a number or
writes such a script, because two independent numbering authorities cannot stay
consistent: each would hand out a number the other had already used. Utilities that are
not attempts at the research question belong in `scripts/utilities/` and never take an
iteration number.

Shared by the `new_track.py`, `new_iteration.py`, and `select_result.py` helpers so all
of them agree on where things live and how they are numbered.
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

OUTCOME_PLACEHOLDER = "[Record after interpreting]"
"""What `new_iteration.py` writes into a new row's `Outcome` cell.

This exact text is how `record_outcome.py` recognises a cell it may fill: a helper may
replace a placeholder it wrote itself, and may never touch text a researcher wrote. Once
the cell holds the researcher's own prose, the helper appends to the history and stops.
"""

OUTCOME_HISTORY_HEADING = "## Outcome history"
"""The heading separating the scannable state table from the append-only history."""

ITERATION_LOG_HEADER = f"""# Iteration Log

Two records in one file, because a reader needs two different things from them.

## Current state

One row per iteration, in the order the work happened. This is the scannable view: what
has been attempted on this project, and what came of each attempt. `new_iteration.py`
appends a row when it creates an iteration.

`Kind` is `single` when the iteration tests one change, or `panel (N)` when it probes N
candidate directions at once. `Outcome` is prose rather than a keyword, because a panel
that improves three of eight candidates cannot be described by a single verdict, and
`SUPPORTED` would discard the finding.

`record_outcome.py` fills `{OUTCOME_PLACEHOLDER}` the first time an outcome is recorded.
After that the cell holds your words, so a revised understanding is yours to write; the
helper appends to the history below and leaves the row alone. `smairt check` reports a row
that no longer agrees with the latest history entry.

| Iteration | Date | Script | Hypotheses | Kind | Changed from | Outcome |
|---|---|---|---|---|---|---|

{OUTCOME_HISTORY_HEADING}

Appended, never edited. Every recording and every revision adds a line here, so a
conclusion that changed still shows what it changed from. The sequence of attempts, and of
readings of those attempts, is itself evidence.

| Date | Iteration | Outcome recorded |
|---|---|---|
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


def recorded_iterations(root: Path) -> list[int]:
    """Return every iteration number that appears in the iteration log.

    A script alone is not an iteration; being recorded is what makes it one. Reading the
    record rather than the filesystem is what lets a caller refuse to treat an
    unrecorded script as reportable evidence.
    """
    return sorted(iteration_records(root))


def iteration_records(root: Path) -> dict[int, dict[str, str]]:
    """Return the current-state rows keyed by iteration number.

    The log already records structural facts callers need, especially whether an
    iteration was a single point or a panel. Reading those facts here keeps helpers from
    asking a researcher to repeat them on the command line and from silently treating a
    panel as a single successful result.
    """
    log_path = root / "analysis" / "ITERATION_LOG.md"
    if not log_path.exists():
        return {}
    records: dict[int, dict[str, str]] = {}
    for line in log_path.read_text().splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 7 or not cells[0].isdigit():
            continue
        records[int(cells[0])] = {
            "date": cells[1],
            "script": cells[2].strip("`"),
            "hypotheses": cells[3],
            "kind": cells[4],
            "changed_from": cells[5],
            "outcome": cells[6],
        }
    return records


def find_iteration_script(root: Path, number: int) -> Path | None:
    """Return the script for an iteration, or None when that iteration has none."""
    matches = sorted((root / "experiments").glob(f"*/script_{number:02d}_*.py"))
    return matches[0] if matches else None


def iteration_script_path(root: Path, phase: str, script_name: str) -> Path:
    """Return where an iteration's script belongs, without creating anything."""
    return root / "experiments" / PHASES[phase] / f"{script_name}.py"


def write_new_script(path: Path, body: str) -> None:
    """Write a script that does not exist yet, refusing to replace one that does.

    The refusal matters more than it first appears. Overwriting destroys an attempt whose
    log and analysis still reference it, leaving a record that points at code which no
    longer exists.
    """
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing script: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)


def iteration_log_path(root: Path) -> Path:
    """Return the iteration log's location, creating the file when it is absent."""
    log_path = root / "analysis" / "ITERATION_LOG.md"
    if not log_path.exists():
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(ITERATION_LOG_HEADER)
    return log_path


def append_iteration_row(
    root: Path,
    *,
    number: int,
    script_name: str,
    hypotheses: str,
    kind: str,
    changed_from: str,
) -> Path:
    """Add one row to the state table, creating the log when it is absent.

    Writing the row here rather than printing one for someone to paste is deliberate: the
    paste is the step that gets skipped, and a log with gaps cannot be trusted as a
    record.

    The row goes at the end of the state table, which sits above the outcome history, so
    this inserts rather than appending to the file. No existing line is read back or
    changed.
    """
    log_path = iteration_log_path(root)
    row = (
        f"| {number:02d} | {date.today().isoformat()} | `{script_name}` | "
        f"{hypotheses} | {kind} | {changed_from} | {OUTCOME_PLACEHOLDER} |\n"
    )
    lines = log_path.read_text().splitlines(keepends=True)
    log_path.write_text("".join(_with_state_row(lines, row)))
    return log_path


def _with_state_row(lines: list[str], row: str) -> list[str]:
    """Return the log's lines with a new state row placed at the end of that table."""
    for index, line in enumerate(lines):
        if line.startswith(OUTCOME_HISTORY_HEADING):
            end = index
            while end > 0 and not lines[end - 1].strip():
                end -= 1
            return [*lines[:end], row, *lines[end:]]
    return [*lines, row]


def append_outcome_history(root: Path, *, number: int, outcome: str) -> Path:
    """Append one line to the outcome history, which is never edited.

    A recording and a later revision both add a line, so a conclusion that changed still
    shows what it changed from. That is the property a single editable cell cannot hold,
    and it is why the log carries two records rather than one.
    """
    log_path = iteration_log_path(root)
    line = f"| {date.today().isoformat()} | {number:02d} | {outcome} |\n"
    with log_path.open("a") as log:
        log.write(line)
    return log_path


def fill_outcome_placeholder(root: Path, *, number: int, outcome: str) -> bool:
    """Fill an iteration's outcome cell if it still holds the placeholder we wrote.

    Returns whether the cell was filled. A helper may replace its own placeholder, and may
    never overwrite a researcher's prose: once the cell holds their words, a revised
    understanding is theirs to write, and this reports False so the caller can say so.
    """
    log_path = iteration_log_path(root)
    lines = log_path.read_text().splitlines(keepends=True)
    prefix = f"| {number:02d} |"
    for index, line in enumerate(lines):
        if line.startswith(prefix) and OUTCOME_PLACEHOLDER in line:
            lines[index] = line.replace(OUTCOME_PLACEHOLDER, outcome)
            log_path.write_text("".join(lines))
            return True
    return False


def record_run_status(root: Path, number: int, status: str, log_path: Path) -> None:
    """Append a run status and exact log path without editing the iteration's state row.

    Runs are events, so a rerun must not erase the status of the run before it. A separate
    append-only history also means a crash is recorded even when no interpretation will
    ever be written for it. The current-state row remains researcher-facing scientific
    prose rather than a mixture of execution and interpretation state.
    """
    history = root / "analysis" / "RUN_HISTORY.md"
    if not history.exists():
        history.parent.mkdir(parents=True, exist_ok=True)
        history.write_text(
            "# Run History\n\n"
            "Appended by generated iteration scripts. Each line identifies one execution, "
            "its exact log, and whether it completed. Earlier lines are never edited.\n\n"
            "| Date | Iteration | Status | Log |\n"
            "|---|---|---|---|\n"
        )
    relative = log_path.relative_to(root).as_posix()
    with history.open("a") as handle:
        handle.write(f"| {date.today().isoformat()} | {number:02d} | {status} | `{relative}` |\n")


def state_row_outcome(root: Path, number: int) -> str | None:
    """Return an iteration's recorded outcome from the state table, if it has a row."""
    log_path = root / "analysis" / "ITERATION_LOG.md"
    if not log_path.exists():
        return None
    prefix = f"| {number:02d} |"
    for line in log_path.read_text().splitlines():
        if line.startswith(prefix):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            return cells[-1] if cells else None
    return None
