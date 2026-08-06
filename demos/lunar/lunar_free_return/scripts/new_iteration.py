#!/usr/bin/env python3
"""Create the next iteration and record it in the iteration log.

An iteration is one attempt: one script, its log, its interpretation. This helper
creates the script, optionally seeded from a previous iteration, and appends a row to
`analysis/ITERATION_LOG.md`.

Two shapes are supported. A single point tests one change. A panel probes several
candidate directions at once and reports a result for every probe.

Nothing is overwritten and no existing line is modified.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.shared.iterations import (  # noqa: E402
    PHASES,
    append_iteration_row,
    find_iteration_script,
    iteration_script_path,
    next_iteration_number,
    project_root,
    slugify,
    write_new_script,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("description", help="Short description used in the filename.")
    parser.add_argument("phase", choices=PHASES, help="Data phase this iteration runs in.")
    parser.add_argument(
        "--hypothesis",
        required=True,
        help=(
            "Hypothesis this iteration tests, for example HYPOTHESIS_01. Required, because "
            "naming what an attempt should settle before writing it is the convention."
        ),
    )
    parser.add_argument(
        "--probes",
        type=int,
        help="Number of probes, which makes this a panel iteration instead of a single point.",
    )
    parser.add_argument(
        "--from-iteration",
        type=int,
        help="Seed the script from this earlier iteration instead of the blank template.",
    )
    arguments = parser.parse_args()

    if arguments.probes is not None and arguments.probes < 2:
        parser.error("a panel needs at least 2 probes; omit --probes for a single point")

    root = project_root()
    description = slugify(arguments.description)
    if not description:
        parser.error("description must contain a letter or number")

    _require_existing_hypothesis(root, arguments.hypothesis, parser)

    number = next_iteration_number(root)
    script_name = f"script_{number:02d}_{description}"
    target = iteration_script_path(root, arguments.phase, script_name)

    seed = _seed_script(root, arguments.from_iteration, parser)
    rigor = _rigor_settings(root)
    declaration = _rigor_block(rigor, panel=arguments.probes is not None)
    body = (
        _seeded_body(
            seed,
            script_name=script_name,
            hypothesis=arguments.hypothesis,
            number=number,
            from_iteration=arguments.from_iteration,
            probes=arguments.probes,
            rigor_block=declaration,
        )
        if seed is not None
        else _template(
            script_name,
            arguments.hypothesis,
            number,
            arguments.probes,
            rigor_block=declaration,
        )
    )
    try:
        write_new_script(target, body)
    except FileExistsError as error:
        parser.error(str(error))

    kind = "single" if arguments.probes is None else f"panel ({arguments.probes})"
    log_path = append_iteration_row(
        root,
        number=number,
        script_name=script_name,
        hypotheses=arguments.hypothesis,
        kind=kind,
        changed_from=(
            "—" if arguments.from_iteration is None else f"{arguments.from_iteration:02d}"
        ),
    )

    print(f"Created {target.relative_to(root)}")
    print(f"Recorded iteration {number:02d} in {log_path.relative_to(root)}")
    if seed is not None:
        print(f"Seeded from {seed.relative_to(root)}; state what changed in the docstring")
    if arguments.probes is not None:
        print(f"Panel of {arguments.probes} probes; report a result for every probe")


def _require_existing_hypothesis(
    root: Path, hypothesis: str, parser: argparse.ArgumentParser
) -> None:
    """Refuse an iteration that names a hypothesis file the project does not contain.

    The number is what ties hypothesis, script, log, and analysis into one chain, so a typo
    here silently breaks a link: the row is written, the reference points at nothing, and
    `smairt check` reported the project as clean. Refusing costs one comparison and keeps the
    record joinable.

    This checks that the file exists, and nothing about what it says. Whether a hypothesis is
    any good is the researcher's judgment, not the tool's.
    """
    directory = root / "hypotheses"
    candidate = directory / f"{hypothesis}.md"
    if candidate.is_file():
        return
    available = sorted(path.stem for path in directory.glob("HYPOTHESIS_[0-9]*.md"))
    listed = ", ".join(available) if available else "none yet"
    parser.error(
        f"no hypothesis file at hypotheses/{hypothesis}.md; existing hypotheses: {listed}. "
        "Create one with new_track.py, or correct the --hypothesis value."
    )


def _seed_script(
    root: Path, from_iteration: int | None, parser: argparse.ArgumentParser
) -> Path | None:
    """Return the script to copy forward, or None when starting from the template."""
    if from_iteration is None:
        return None
    found: Path | None = find_iteration_script(root, from_iteration)
    if found is None:
        parser.error(f"no script found for iteration {from_iteration:02d}")
    return found


def _seeded_body(
    seed: Path,
    *,
    script_name: str,
    hypothesis: str,
    number: int,
    from_iteration: int | None,
    probes: int | None,
    rigor_block: str,
) -> str:
    """Return the earlier script re-headed for this iteration.

    Copying the previous attempt forward is what makes two iterations comparable: the
    difference between them is the thing under test, so it has to be stated rather than
    reconstructed from a diff.

    The copy's own identity must be replaced, not just annotated. A seeded script that
    kept the earlier `SCRIPT_NAME` would write its evidence into the earlier iteration's
    log name, so two attempts would claim one log and the newer would overwrite the
    older.
    """
    body = _without_leading_docstring(seed.read_text())
    body, replaced = re.subn(
        r'^SCRIPT_NAME = ".*?"$',
        f'SCRIPT_NAME = "{script_name}"',
        body,
        count=1,
        flags=re.MULTILINE,
    )
    header = f'''#!/usr/bin/env python3
"""Iteration {number:02d}: {script_name}

Hypothesis: {hypothesis}
Kind: {"single point" if probes is None else f"panel of {probes} probes"}
Seeded from iteration {from_iteration:02d}.

Changed from iteration {from_iteration:02d}: [state exactly what varies, and why]
{rigor_block}"""
'''
    if not replaced:
        header += (
            f'\n# This script did not declare SCRIPT_NAME. Set it to "{script_name}" so the\n'
            "# log records this iteration rather than the one it was seeded from.\n"
        )
    return header + body


def _without_leading_docstring(text: str) -> str:
    """Return the script with its shebang and module docstring removed."""
    remainder = re.sub(r"\A#![^\n]*\n", "", text)
    return re.sub(r'\A\s*""".*?"""\n', "", remainder, count=1, flags=re.DOTALL)


def _rigor_settings(root: Path) -> dict[str, bool]:
    """Return optional declaration switches from the generated project's contract."""
    try:
        contract = yaml.safe_load((root / "smairt.yaml").read_text())
    except (OSError, yaml.YAMLError):
        return {}
    rigor = contract.get("rigor", {}) if isinstance(contract, dict) else {}
    if not isinstance(rigor, dict):
        return {}
    return {key: value for key, value in rigor.items() if isinstance(value, bool)}


def _rigor_block(rigor: dict[str, bool], *, panel: bool) -> str:
    """Create docstring fields only for declarations enabled at creation time."""
    fields: list[tuple[str, str]] = []
    if rigor.get("declare_multiplicity_policy"):
        fields.append(("Multiplicity declaration", "[Apply the policy in analysis/RIGOR.md]"))
    if rigor.get("separate_discovery_validation"):
        fields.append(
            ("Discovery or validation role", "[Discovery | Validation; identify held-out data]")
        )
    if rigor.get("declare_unit_of_inference"):
        fields.append(("Unit of inference", "[Name the independent unit supporting this claim]"))
    if panel and rigor.get("track_per_probe_status"):
        fields.append(
            ("Per-probe hypothesis status", "[Pre-specify each probe; record each status later]")
        )
    if not fields:
        return ""
    lines = ["", "Project rigor declarations (standing policy: analysis/RIGOR.md):"]
    lines.extend(f"- {name}: {prompt}" for name, prompt in fields)
    return "\n".join(lines) + "\n"


def _template(
    script_name: str,
    hypothesis: str,
    number: int,
    probes: int | None,
    *,
    rigor_block: str,
) -> str:
    if probes is None:
        experiment = """            print("TODO: implement the experiment")"""
    else:
        experiment = f"""            probes = {{
                f"probe_{{index:02d}}": "TODO: describe this variation"
                for index in range(1, {probes} + 1)
            }}
            # Report every probe, including the ones that change nothing or make things
            # worse. A panel reported as its best arm is a panel reported dishonestly.
            for label, variation in probes.items():
                print(f"{{label}}: {{variation}}")
                print(f"{{label}} result: TODO")"""

    return f'''#!/usr/bin/env python3
"""Iteration {number:02d}: {script_name}

Hypothesis: {hypothesis}
Kind: {"single point" if probes is None else f"panel of {probes} probes"}
{rigor_block}"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, record_run_status, setup_logging, write_provenance

SCRIPT_NAME = "{script_name}"
ITERATION_NUMBER = {number}


def main() -> None:
    log_path = setup_logging(SCRIPT_NAME, PROJECT_ROOT / "results" / "logs")
    logger = TeeLogger(log_path)
    try:
        with logger:
            write_provenance(project_root=PROJECT_ROOT, config={{}})
            print("Hypothesis: {hypothesis}")
{experiment}
            print(f"Log: {{log_path.relative_to(PROJECT_ROOT)}}")
    finally:
        # This runs after TeeLogger has classified the run, even when the experiment
        # raised. A record failure is reported but never masks the experiment's exception.
        try:
            record_run_status(PROJECT_ROOT, ITERATION_NUMBER, logger.status, log_path)
        except OSError as error:
            print(f"Warning: could not append run history: {{error}}", file=sys.stderr)


if __name__ == "__main__":
    main()
'''


if __name__ == "__main__":
    main()
