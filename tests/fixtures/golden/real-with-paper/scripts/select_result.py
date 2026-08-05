#!/usr/bin/env python3
"""Record which iteration you would report, and the evidence behind it.

Creates `analysis/SELECTED_NN.md`: the claim, the iteration that supports it, and every
file a reader would need to check it. With `--paper`, the same command appends a detailed
entry to `FINAL_MANIFEST.md` when the Paper capability is present.

This copies nothing and deletes nothing. Evidence stays in `results/logs/` where it was
produced, and both records point at the exact log. A duplicate can drift from the original;
a pointer cannot.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.shared.iterations import (  # noqa: E402
    find_iteration_script,
    iteration_records,
    project_root,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("iteration", type=int, help="Iteration number being selected.")
    parser.add_argument("--claim", required=True, help="The statement this result supports.")
    parser.add_argument(
        "--probes",
        help=(
            "For a panel iteration, the probes supporting the claim, comma separated. "
            "Required so a panel is never reported as though all of it succeeded."
        ),
    )
    parser.add_argument(
        "--paper",
        action="store_true",
        help="Also append the selected claim and exact log to FINAL_MANIFEST.md.",
    )
    arguments = parser.parse_args()

    root = project_root()
    number = arguments.iteration
    records = iteration_records(root)
    if number not in records:
        available = ", ".join(f"{value:02d}" for value in sorted(records))
        detail = f"recorded iterations: {available}" if available else "no iterations are recorded"
        parser.error(
            f"iteration {number:02d} is not recorded in analysis/ITERATION_LOG.md, so it is "
            f"not a reportable attempt; {detail}"
        )

    kind = records[number]["kind"]
    probes = _named_probes(arguments.probes)
    if kind.startswith("panel") and not probes:
        parser.error(
            f"iteration {number:02d} is recorded as {kind}; --probes is required to name "
            "which probes support the claim, so the panel is not reported as though all "
            "of it succeeded"
        )
    if kind == "single" and probes:
        parser.error(
            f"iteration {number:02d} is recorded as single, so --probes would describe "
            "evidence the iteration did not produce"
        )

    script = find_iteration_script(root, number)
    if script is None:
        parser.error(
            f"iteration {number:02d} is recorded but its script is missing; the record "
            "points at code that is not there"
        )

    target = root / "analysis" / f"SELECTED_{number:02d}.md"
    if target.exists():
        parser.error(f"refusing to overwrite existing record: {target}")

    logs = sorted((root / "results" / "logs").glob(f"{script.stem}_*.log"))
    if not logs:
        parser.error(
            f"no log found for {script.stem}; run the iteration before selecting its result"
        )

    manifest = root / "FINAL_MANIFEST.md"
    if arguments.paper and not manifest.exists():
        parser.error(
            "--paper requires the Paper capability and FINAL_MANIFEST.md; enable it with "
            "`smairt paper enable` before selecting this result"
        )

    relative_script = script.relative_to(root)
    relative_logs = [log.relative_to(root) for log in logs]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        _record(
            number=number,
            claim=arguments.claim,
            script=relative_script,
            logs=relative_logs,
            kind=kind,
            probes=probes,
        )
    )
    if arguments.paper:
        _append_manifest_entry(
            manifest,
            number=number,
            claim=arguments.claim,
            script=relative_script,
            logs=relative_logs,
            kind=kind,
            probes=probes,
        )

    print(f"Created {target.relative_to(root)}")
    print(f"Evidence: {len(logs)} log(s), left where they were produced")
    if arguments.paper:
        print("Appended the Paper manifest entry with the exact log path(s)")
    elif manifest.exists():
        print("Use --paper to append the same claim and exact log to FINAL_MANIFEST.md")


def _named_probes(value: str | None) -> list[str]:
    """Return non-empty probe names from a comma-separated option."""
    if value is None:
        return []
    return [probe.strip() for probe in value.split(",") if probe.strip()]


def _record(
    *,
    number: int,
    claim: str,
    script: Path,
    logs: list[Path],
    kind: str,
    probes: list[str],
) -> str:
    log_lines = "\n".join(f"- `{log.as_posix()}`" for log in logs)
    scope = _panel_scope(probes) if kind.startswith("panel") else _single_point_scope()

    return f"""# Selected Result: Iteration {number:02d}

**Claim**: {claim}

**Recorded**: {date.today().isoformat()}

**Iteration kind**: {kind}

---

## Why this iteration

[Why this attempt is the one worth reporting. Compare it to the other attempts at the
same question rather than describing it alone.]

## Evidence

- **Script**: `{script.as_posix()}`
- **Logs**:

{log_lines}

- **Interpretation**: `analysis/ANALYSIS_{number:02d}.md`
- **Hypothesis**: [The hypothesis file and its status]
- **Figures**: [Paths, if any]

Every number in the claim should be findable in one of the logs above. If a number came
from somewhere else, name that source too.

{scope}
## Limitations

[Where this result stops holding. Conditions not tested, populations not covered,
assumptions relied on.]

## Notes

[Anything a reader checking this claim would want to know.]
"""


def _append_manifest_entry(
    manifest: Path,
    *,
    number: int,
    claim: str,
    script: Path,
    logs: list[Path],
    kind: str,
    probes: list[str],
) -> None:
    """Append one selected claim without editing any existing manifest wording.

    Selection is the researcher's explicit decision that a result is reportable, so the
    helper may record that decision. It appends rather than finding and replacing a
    placeholder: existing paper claims are researcher prose and are never helper-owned.
    """
    evidence = "\n".join(f"- **Evidence**: `{log.as_posix()}`" for log in logs)
    probe_line = (
        f"- **Supporting probes**: {', '.join(f'`{probe}`' for probe in probes)}\n"
        if kind.startswith("panel")
        else ""
    )
    entry = f"""

### Selected Result: Iteration {number:02d}

- **Claim**: {claim}
- **Iteration**: {number:02d}
- **Kind**: {kind}
- **Script**: `{script.as_posix()}`
{evidence}
- **Interpretation**: `analysis/ANALYSIS_{number:02d}.md`
{probe_line}- **Recorded**: {date.today().isoformat()}
- **Notes**: [Caveats, or the boundary where the result stops holding]
"""
    with manifest.open("a") as handle:
        handle.write(entry)


def _panel_scope(probes: list[str]) -> str:
    """Return the section that keeps a panel's failed probes visible.

    A panel reported as its best arm is a panel reported dishonestly, and the probes
    that did not work are usually the more transferable finding.
    """
    supporting = "\n".join(f"- `{probe}`" for probe in probes)
    return f"""## Supporting probes

This was a panel iteration. These probes support the claim:

{supporting}

Record what the remaining probes showed, including the ones that changed nothing and the
ones that made things worse:

- [Probes with no effect, and what that suggests]
- [Probes that regressed, and what that suggests]
- [Any pattern across the panel as a whole]
"""


def _single_point_scope() -> str:
    """Return the section that keeps a single-point claim inside its boundary."""
    return """## Scope of the claim

State what this result does *not* establish. A single-point iteration tests one change
under one set of conditions, and that boundary is part of the finding.
"""


if __name__ == "__main__":
    main()
