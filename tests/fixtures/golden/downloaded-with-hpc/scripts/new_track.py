#!/usr/bin/env python3
"""Start a research track: a plan and a hypothesis.

A track is a direction of inquiry spanning as many iterations as it takes. This helper
creates the two records a track needs before any work starts.

Both records are filled in from the templates that ship with the project,
`hypotheses/HYPOTHESIS_TEMPLATE.md` and `plans/PLAN_TEMPLATE.md`, rather than from copies
kept inside this file. A researcher who edits a template to suit their field then gets
their own version, and the template a reader is told to follow cannot silently disagree
with what the helper produces.

It deliberately does not create the first script. The criteria have to be written and
committed before an experiment exists: committing them first is what keeps the test a test
rather than a rationalization, and a helper that produced an empty-criteria hypothesis and
a script in the same instant would leave nothing to show any ordering at all. Run
`new_iteration.py` once the criteria are recorded.

Nothing is overwritten. If a file is already there, this refuses rather than replacing it.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

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

    rigor = _rigor_settings(root)
    hypothesis = _hypothesis(
        _template(parser, root / "hypotheses" / "HYPOTHESIS_TEMPLATE.md"),
        hypothesis_id=hypothesis_id,
        number=hypothesis_number,
        question=arguments.question,
        phase=arguments.phase,
    ) + _rigor_block(rigor)
    plan = _plan(
        _template(parser, root / "plans" / "PLAN_TEMPLATE.md"),
        hypothesis_id=hypothesis_id,
        question=arguments.question,
    )
    if any(rigor.values()):
        plan += "\n## Project rigor declarations\n\nSee `analysis/RIGOR.md` for the standing commitments that apply to this track.\n"

    hypothesis_path.parent.mkdir(parents=True, exist_ok=True)
    hypothesis_path.write_text(hypothesis)
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(plan)

    print(f"Created {hypothesis_path.relative_to(root)}")
    print(f"Created {plan_path.relative_to(root)}")

    print()
    print("Next: write the prediction and both criteria in the hypothesis file, and commit")
    print("them before creating the first iteration. Committing the criteria first is what")
    print("keeps the test a test, so this helper deliberately stops here:")
    print(
        f"  python3 scripts/new_iteration.py baseline {arguments.phase} --hypothesis {hypothesis_id}"
    )


def _template(parser: argparse.ArgumentParser, path: Path) -> str:
    """Return a shipped template, reporting its absence rather than inventing a substitute.

    Falling back to a built-in copy would be worse than stopping: the researcher would get
    a file that quietly differs from the template the guidance tells them to follow.
    `smairt regenerate` restores a missing template.
    """
    try:
        return path.read_text()
    except OSError:
        parser.error(
            f"missing template {path.name}; restore it with `smairt regenerate` before "
            "starting a track"
        )
        raise  # `parser.error` exits, and this keeps the return type honest.


def _next_hypothesis_number(root: Path) -> int:
    """Return the next hypothesis number, so identifiers stay unique and ordered."""
    numbers = [
        int(match.group(1))
        for path in (root / "hypotheses").glob("HYPOTHESIS_*.md")
        if (match := re.match(r"HYPOTHESIS_(\d+)\.md$", path.name))
    ]
    return max(numbers, default=0) + 1


def _hypothesis(
    template: str, *, hypothesis_id: str, number: int, question: str, phase: str
) -> str:
    """Return the hypothesis template with what this helper actually knows filled in.

    Only the identity of the hypothesis is filled: its number, the question it came from,
    and the phase. Every prediction and criterion is left as a prompt, because those are
    the researcher's to write and are the whole point of stopping before the script.
    """
    filled = template.replace(
        "# Hypothesis [XX] - [Brief Title]", f"# {hypothesis_id} - {question}"
    )
    filled = filled.replace(
        "PENDING | SUPPORTED | REFUTED | PARTIALLY SUPPORTED | INCONCLUSIVE", "PENDING"
    )
    filled = filled.replace("- **Phase**: synthetic | downloaded | real", f"- **Phase**: {phase}")
    return filled.replace("HYPOTHESIS_XX", f"HYPOTHESIS_{number:02d}")


def _rigor_settings(root: Path) -> dict[str, bool]:
    """Read optional booleans directly so generated projects need only PyYAML."""
    try:
        contract = yaml.safe_load((root / "smairt.yaml").read_text())
    except (OSError, yaml.YAMLError):
        return {}
    rigor = contract.get("rigor", {}) if isinstance(contract, dict) else {}
    if not isinstance(rigor, dict):
        return {}
    return {key: value for key, value in rigor.items() if isinstance(value, bool)}


def _rigor_block(rigor: dict[str, bool]) -> str:
    """Return track-level declarations requested for newly created files.

    Per-probe status is iteration structure, so it appears only when `new_iteration.py`
    knows that the artifact is a panel rather than as an inapplicable hypothesis field.
    """
    fields: list[tuple[str, str]] = []
    if rigor.get("declare_multiplicity_policy"):
        fields.append(
            ("Multiplicity declaration", "[How repeated tests or probes will be interpreted]")
        )
    if rigor.get("separate_discovery_validation"):
        fields.append(
            (
                "Discovery or validation role",
                "[Discovery | Validation, and which data are held out]",
            )
        )
    if rigor.get("declare_unit_of_inference"):
        fields.append(("Unit of inference", "[What independent unit supports the claim]"))
    if not fields:
        return ""
    lines = ["", "## Project rigor declarations", "", "Standing policy: `analysis/RIGOR.md`.", ""]
    lines.extend(f"- **{name}**: {prompt}" for name, prompt in fields)
    return "\n".join(lines) + "\n"


def _plan(template: str, *, hypothesis_id: str, question: str) -> str:
    """Return the plan template with the track's question and hypothesis filled in."""
    filled = template.replace("# Plan: [Brief Title]", f"# Plan: {question}")
    filled = filled.replace("DRAFT | ACTIVE | COMPLETED | ABANDONED", "DRAFT")
    return filled.replace(
        "[The hypothesis this track sets out to settle, as `hypotheses/HYPOTHESIS_XX.md`.]",
        f"`hypotheses/{hypothesis_id}.md`",
    )


if __name__ == "__main__":
    main()
