from __future__ import annotations

from pathlib import Path

import pytest

from smairt.generator import generate_project
from smairt.models import (
    Assistant,
    License,
    ProjectIdentity,
    ProjectOptions,
    Researcher,
    StartingPhase,
)
from smairt.project import (
    capability_plan,
    load_contract,
    set_capabilities,
)


def build_project(root: Path, *, paper: bool = False, hpc: bool = False) -> Path:
    destination = root / "study"
    generate_project(
        destination,
        ProjectOptions(
            project=ProjectIdentity(
                name="Study",
                slug="study",
                description="A study.",
                domain="Computational biology",
            ),
            researcher=Researcher(name="Researcher"),
            assistant=Assistant.OPENCODE,
            starting_phase=StartingPhase.SYNTHETIC,
            license=License.MIT,
            initialize_git=False,
            paper=paper,
            hpc=hpc,
        ),
    )
    return destination


def test_a_plan_that_changes_nothing_says_so_and_writes_nothing(tmp_path: Path) -> None:
    root = build_project(tmp_path)
    plan = capability_plan(root, [])
    assert plan.changes == ()
    assert plan.creates == ()
    assert plan.is_empty is True


def test_enabling_a_capability_names_the_files_it_would_create(tmp_path: Path) -> None:
    root = build_project(tmp_path)
    plan = capability_plan(root, ["paper"])
    assert [change.name for change in plan.changes] == ["paper"]
    assert plan.changes[0].enabling is True
    assert plan.creates
    assert all(not (root / relative).exists() for relative in plan.creates)


def test_a_preview_names_exactly_the_files_the_operation_writes(tmp_path: Path) -> None:
    """A preview derived from anything but the real operation would eventually lie."""
    root = build_project(tmp_path)
    before = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    predicted = set(capability_plan(root, ["paper", "hpc"]).creates)

    set_capabilities(root, ["paper", "hpc"])

    after = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    created = after - before
    assert created - {"smairt.yaml"} == predicted


def test_disabling_a_capability_promises_no_deletions(tmp_path: Path) -> None:
    root = build_project(tmp_path, paper=True)
    plan = capability_plan(root, [])
    assert [change.name for change in plan.changes] == ["paper"]
    assert plan.changes[0].enabling is False
    assert plan.creates == ()


def test_deactivation_changes_contract_state_without_removing_files(tmp_path: Path) -> None:
    root = build_project(tmp_path, paper=True)
    retained = sorted(path for path in root.rglob("*") if path.is_file())

    set_capabilities(root, [])

    assert load_contract(root).capabilities["paper"].state.value == "inactive"
    assert sorted(path for path in root.rglob("*") if path.is_file()) == retained


def test_reenabling_a_capability_preserves_researcher_edits(tmp_path: Path) -> None:
    root = build_project(tmp_path, paper=True)
    edited = next(path for path in (root / "paper").rglob("*.md") if path.is_file())
    edited.write_text("My own words.\n")
    set_capabilities(root, [])

    plan = capability_plan(root, ["paper"])
    assert edited.relative_to(root).as_posix() not in plan.creates

    set_capabilities(root, ["paper"])
    assert edited.read_text() == "My own words.\n"


def test_applying_a_plan_reports_what_it_did_for_every_capability(tmp_path: Path) -> None:
    root = build_project(tmp_path)
    messages = set_capabilities(root, ["hpc"])
    assert any("HPC" in message for message in messages)
    contract = load_contract(root)
    assert contract.capabilities["hpc"].state.value == "enabled"
    assert contract.capabilities["paper"].state.value == "never_enabled"


def test_an_unknown_capability_is_refused_before_anything_is_written(tmp_path: Path) -> None:
    root = build_project(tmp_path)
    with pytest.raises(Exception):
        capability_plan(root, ["telepathy"])
