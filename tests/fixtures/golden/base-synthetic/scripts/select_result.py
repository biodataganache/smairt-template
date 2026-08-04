#!/usr/bin/env python3
"""Record which iteration you would report, and the evidence behind it.

Creates `analysis/SELECTED_NN.md`: the claim, the iteration that supports it, and every
file a reader would need to check it.

This copies nothing and deletes nothing. Evidence stays in `results/logs/` where it was
produced, and this record points at it. A duplicate can drift from the original; a
pointer cannot.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.shared.iterations import (  # noqa: E402
    existing_iterations,
    find_iteration_script,
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
    arguments = parser.parse_args()

    root = project_root()
    number = arguments.iteration
    script = find_iteration_script(root, number)
    if script is None:
        available = ", ".join(f"{value:02d}" for value in sorted(existing_iterations(root)))
        parser.error(
            f"no script found for iteration {number:02d}"
            + (f"; iterations present: {available}" if available else "")
        )

    target = root / "analysis" / f"SELECTED_{number:02d}.md"
    if target.exists():
        parser.error(f"refusing to overwrite existing record: {target}")

    logs = sorted((root / "results" / "logs").glob(f"{script.stem}_*.log"))
    if not logs:
        parser.error(
            f"no log found for {script.stem}; run the iteration before selecting its result"
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        _record(
            number=number,
            claim=arguments.claim,
            script=script.relative_to(root),
            logs=[log.relative_to(root) for log in logs],
            probes=arguments.probes,
        )
    )
    print(f"Created {target.relative_to(root)}")
    print(f"Evidence: {len(logs)} log(s), left where they were produced")
    if arguments.probes is None:
        print("If this was a panel iteration, rerun with --probes naming the supporting probes")
    print("With the Paper capability, add a matching entry to FINAL_MANIFEST.md by hand")


def _record(
    *,
    number: int,
    claim: str,
    script: Path,
    logs: list[Path],
    probes: str | None,
) -> str:
    log_lines = "\n".join(f"- `{log.as_posix()}`" for log in logs)
    scope = _panel_scope(probes) if probes is not None else _single_point_scope()

    return f"""# Selected Result: Iteration {number:02d}

**Claim**: {claim}

**Recorded**: {date.today().isoformat()}

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


def _panel_scope(probes: str) -> str:
    """Return the section that keeps a panel's failed probes visible.

    A panel reported as its best arm is a panel reported dishonestly, and the probes
    that did not work are usually the more transferable finding.
    """
    named = [probe.strip() for probe in probes.split(",") if probe.strip()]
    supporting = "\n".join(f"- `{probe}`" for probe in named)
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
