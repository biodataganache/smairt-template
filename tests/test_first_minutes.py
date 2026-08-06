"""The first commands a researcher runs must work, and the record must stay joinable.

Every finding here was reachable within minutes of creating a project: a documented command
that does not exist on macOS, a project that fails its own check on creation, a listing that
buries the one row that matters under forty that do not, and a typo that silently breaks the
chain the whole workflow exists to build.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).parents[1]
SCAFFOLD = REPOSITORY_ROOT / "src" / "smairt" / "assets" / "scaffold"
GUIDANCE_SUFFIXES = {".md", ".py", ".sh", ".yaml"}

# `python ` as a command, but not inside `python3` and not in prose like "the Python version".
BARE_PYTHON = re.compile(r'(?<![\w3])python (?=[\w"$/-])')


def installed_smairt() -> Path:
    return Path(sys.executable).with_name("smairt")


def helper_python() -> Path:
    """Return an interpreter that has the scaffold helpers' dependencies available.

    The generated helpers import PyYAML, which a bare system `python3` may not have. Tests
    exercise them with the interpreter running the installed tool, which is what a researcher
    who installed via `uv tool install` or `pipx` actually has.
    """
    return Path(sys.executable)


def run(*arguments: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(installed_smairt()), *arguments],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def run_helper(project: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(helper_python()), *arguments],
        cwd=project,
        check=False,
        capture_output=True,
        text=True,
    )


def create_project(destination: Path, **overrides: str) -> subprocess.CompletedProcess[str]:
    values = {
        "--name": "Study",
        "--slug": "study_project",
        "--description": "A project for first-minutes checks.",
        "--researcher": "Ada Researcher",
        "--domain": "Computational biology",
    }
    values.update(overrides)
    arguments = [item for pair in values.items() for item in pair]
    return run("new", str(destination), *arguments, "--accept-license", "--no-git")


def test_no_generated_guidance_tells_a_researcher_to_run_bare_python() -> None:
    """`python` does not exist on a stock macOS; only `python3` does.

    This is the first command a researcher types after creating a project, so getting it
    wrong means the tool fails at the point of first contact. The shipped helpers already
    carry `#!/usr/bin/env python3` shebangs, so the guidance was contradicting its own files.
    """
    offenders: list[str] = []
    for path in sorted(SCAFFOLD.rglob("*")):
        if path.is_file() and path.suffix in GUIDANCE_SUFFIXES:
            for number, line in enumerate(path.read_text().splitlines(), start=1):
                if BARE_PYTHON.search(line):
                    offenders.append(f"{path.relative_to(SCAFFOLD)}:{number}: {line.strip()}")
    assert not offenders, "generated guidance names `python` instead of `python3`:\n" + "\n".join(
        offenders
    )


def test_the_dashboard_next_action_also_names_python3() -> None:
    """The tool's own suggested commands have to be runnable too."""
    from smairt.project import next_workflow_action  # noqa: PLC0415

    source = Path(next_workflow_action.__code__.co_filename).read_text()
    suggestions = [
        line for line in source.splitlines() if "scripts/" in line and "python" in line.lower()
    ]
    assert suggestions
    for line in suggestions:
        assert not BARE_PYTHON.search(line), line


@pytest.mark.parametrize("marker", ["{{ 7*7 }}", "{% if x %}", "}}"])
def test_template_markers_in_metadata_are_refused_at_entry(tmp_path: Path, marker: str) -> None:
    """A project created cleanly must not fail its own check.

    `Study {{ n }}` used to be accepted, and then `smairt check` reported five unresolved
    template tokens in files the researcher never touched.
    """
    result = create_project(tmp_path / "templated", **{"--name": f"Study {marker}"})

    assert result.returncode == 2, result.stdout
    assert "cannot contain" in result.stderr
    assert "Remove the braces" in result.stderr
    assert not (tmp_path / "templated").exists()


def test_each_metadata_field_is_screened_and_named_correctly(tmp_path: Path) -> None:
    """A rejection must point at the field the researcher actually typed."""
    cases = {
        "--name": "project name",
        "--description": "project description",
        "--domain": "research domain",
        "--researcher": "researcher name",
        "--question": "research question",
    }
    for option, label in cases.items():
        result = create_project(tmp_path / f"case{option}", **{option: "text {{ x }} here"})
        assert result.returncode == 2, f"{option}: {result.stdout}"
        assert label in result.stderr, f"{option} reported as: {result.stderr}"


def test_ordinary_metadata_is_still_accepted_and_checks_clean(tmp_path: Path) -> None:
    """Screening braces must not reject the punctuation researchers actually use."""
    destination = tmp_path / "punctuated"
    result = create_project(
        destination,
        **{
            "--name": "Study: phase 1 (baseline) — 50% subset",
            "--description": "Tests f(x) = y, where x ∈ [0, 1] & y > 0.",
            "--domain": "Computational biology",
        },
    )

    assert result.returncode == 0, result.stderr
    assert run("check", str(destination)).returncode == 0


def test_an_iteration_cannot_name_a_hypothesis_that_does_not_exist(tmp_path: Path) -> None:
    """A typo used to write a row pointing at nothing, and the project still read as clean."""
    destination = tmp_path / "typo_project"
    assert create_project(destination).returncode == 0
    assert (
        run_helper(destination, "scripts/new_track.py", "The baseline exceeds chance", "synthetic")
    ).returncode == 0

    refused = run_helper(
        destination,
        "scripts/new_iteration.py",
        "attempt",
        "synthetic",
        "--hypothesis",
        "HYPOTHESIS_99",
    )

    assert refused.returncode != 0
    assert "no hypothesis file at hypotheses/HYPOTHESIS_99.md" in refused.stderr
    assert "HYPOTHESIS_01" in refused.stderr
    assert not list((destination / "experiments").glob("*/script_*.py"))
    assert "HYPOTHESIS_99" not in (destination / "analysis" / "ITERATION_LOG.md").read_text()


def test_a_valid_hypothesis_reference_is_still_accepted(tmp_path: Path) -> None:
    destination = tmp_path / "valid_project"
    assert create_project(destination).returncode == 0
    assert (
        run_helper(destination, "scripts/new_track.py", "The baseline exceeds chance", "synthetic")
    ).returncode == 0

    created = run_helper(
        destination,
        "scripts/new_iteration.py",
        "baseline",
        "synthetic",
        "--hypothesis",
        "HYPOTHESIS_01",
    )

    assert created.returncode == 0, created.stderr
    assert run("check", str(destination)).returncode == 0


def test_check_reports_a_reference_broken_after_the_fact(tmp_path: Path) -> None:
    """Refusing at creation cannot help a row that is already there, or a renamed file."""
    destination = tmp_path / "broken_link_project"
    assert create_project(destination).returncode == 0
    assert (
        run_helper(destination, "scripts/new_track.py", "The baseline exceeds chance", "synthetic")
    ).returncode == 0
    assert (
        run_helper(
            destination,
            "scripts/new_iteration.py",
            "baseline",
            "synthetic",
            "--hypothesis",
            "HYPOTHESIS_01",
        )
    ).returncode == 0
    assert run("check", str(destination)).returncode == 0

    hypotheses = destination / "hypotheses"
    (hypotheses / "HYPOTHESIS_01.md").rename(hypotheses / "HYPOTHESIS_07.md")

    checked = run("check", str(destination))

    assert checked.returncode == 1
    assert "dangling-hypothesis-reference" in checked.stdout
    assert "HYPOTHESIS_01" in checked.stdout


def test_regenerate_leads_with_what_needs_doing(tmp_path: Path) -> None:
    """The listing used to print every managed asset, so the one missing row was invisible."""
    destination = tmp_path / "regenerate_project"
    assert create_project(destination).returncode == 0
    (destination / "docs" / "README.md").unlink()

    listed = run("regenerate", str(destination))

    assert listed.returncode == 0, listed.stderr
    assert "Missing, so regenerating would restore them:" in listed.stdout
    assert "- docs/README.md" in listed.stdout
    assert "are already current" in listed.stdout
    assert "Use --all to list them" in listed.stdout
    # The point of the change: the actionable row is not buried.
    assert len(listed.stdout.splitlines()) < 10

    everything = run("regenerate", str(destination), "--all")
    assert everything.returncode == 0
    assert len(everything.stdout.splitlines()) > 40
    assert "prompts/AI_CONTEXT.md" in everything.stdout


def test_regenerate_names_files_it_would_refuse(tmp_path: Path) -> None:
    destination = tmp_path / "modified_project"
    assert create_project(destination).returncode == 0
    (destination / "docs" / "12_STEPS.md").write_text("My own version of the loop.\n")

    listed = run("regenerate", str(destination))

    assert listed.returncode == 0, listed.stderr
    assert "Differ from the installed version, so not eligible:" in listed.stdout
    assert "- docs/12_STEPS.md" in listed.stdout


def test_generated_guidance_does_not_claim_new_track_creates_an_iteration() -> None:
    """`new_track.py` deliberately stops before the first script.

    Committing the criteria before a script exists is what keeps the test a test, so the
    helper stops and says so. Guidance that promises a first iteration teaches a researcher
    to expect a script that was never written, and to skip the commit the workflow depends on.
    """
    offenders: list[str] = []
    for path in sorted(SCAFFOLD.rglob("*.md")):
        for number, line in enumerate(path.read_text().splitlines(), start=1):
            lowered = line.lower()
            if "new_track" not in lowered:
                continue
            # Only a claim about what new_track itself produces counts. A line that names
            # both helpers is describing the pair, not promising a script.
            if "new_iteration" in lowered:
                continue
            if "does not" in lowered or "not create" in lowered:
                continue
            if "iteration" in lowered or "first script" in lowered:
                offenders.append(f"{path.relative_to(SCAFFOLD)}:{number}: {line.strip()}")
    assert not offenders, (
        "generated guidance says new_track.py creates an iteration or script:\n"
        + "\n".join(offenders)
    )


def test_open_reports_where_the_project_stands(tmp_path: Path) -> None:
    """The generated README promises this, so the command has to deliver it.

    `smairt open` printed only the path it had just been given. The state it claimed to
    report already existed behind `next_workflow_action`, so the guidance was describing a
    capability the project had but the command did not reach for.
    """
    destination = tmp_path / "opened_project"
    assert create_project(destination).returncode == 0

    opened = run("open", str(destination))

    assert opened.returncode == 0, opened.stderr
    assert str(destination) in opened.stdout
    # Freshly created, so the honest next step is recording the question.
    assert "No research question recorded yet" in opened.stdout
    assert "smairt settings --question" in opened.stdout


def test_open_reports_the_next_step_as_the_project_advances(tmp_path: Path) -> None:
    """The reported state has to follow the record, not a fixed script."""
    destination = tmp_path / "advancing_project"
    assert create_project(destination, **{"--question": "Does X predict Y?"}).returncode == 0

    opened = run("open", str(destination))

    assert opened.returncode == 0, opened.stderr
    assert "No hypothesis yet" in opened.stdout
    assert "new_track.py" in opened.stdout


def test_paper_capability_is_reached_by_the_command_the_skills_document(tmp_path: Path) -> None:
    """`smairt new --paper` has to mean Paper, or it must not be documented.

    With no destination the flag was accepted and then dropped: creation entered the wizard,
    which supplies its own options. A researcher following the skill got a project with no
    Paper workspace and no indication that the flag had been ignored.
    """
    destination = tmp_path / "paper_project"

    created = run(
        "new",
        str(destination),
        "--name",
        "Paper Study",
        "--slug",
        "paper_study",
        "--description",
        "A project that needs Paper.",
        "--researcher",
        "Ada Researcher",
        "--domain",
        "Computational biology",
        "--paper",
        "--accept-license",
        "--no-git",
    )

    assert created.returncode == 0, created.stderr
    assert (destination / "paper").is_dir()


def test_no_shipped_guidance_documents_a_flag_that_creation_would_ignore() -> None:
    """A flag that only works with a destination must not be shown without one.

    The skills told a researcher to run `smairt new --paper`. Read literally that enters the
    wizard and the flag is discarded, so the instruction produced a project missing exactly
    the capability the skill exists to set up.
    """
    documents = sorted((REPOSITORY_ROOT / "skills").rglob("*.md"))
    assert documents
    offenders: list[str] = []
    for path in documents:
        for number, line in enumerate(path.read_text().splitlines(), start=1):
            if "smairt new" not in line:
                continue
            if "--paper" in line or "--hpc" in line:
                offenders.append(f"{path.relative_to(REPOSITORY_ROOT)}:{number}: {line.strip()}")
    assert not offenders, (
        "skills document a capability flag on `smairt new` without a destination, "
        "which wizard mode ignores:\n" + "\n".join(offenders)
    )


def test_creation_refuses_a_capability_flag_it_would_silently_ignore(tmp_path: Path) -> None:
    """Wizard mode asks about capabilities, so a flag it cannot honour must not be accepted.

    Accepting and discarding it is the worst of the three options: the researcher gets no
    Paper workspace and no reason to suspect one is missing. Refusing names the conflict
    while nothing has been written.
    """
    refused = subprocess.run(
        [str(installed_smairt()), "new", "--paper"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        input="",
    )

    assert refused.returncode == 2, refused.stdout
    assert "--paper" in refused.stderr
    assert "asks which capabilities" in refused.stderr
    assert not list(tmp_path.iterdir())
