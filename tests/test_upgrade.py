"""An out-of-date project has a route forward rather than a dead end.

ADR 0001 ties a project to its recorded scaffold version and requires an explicit upgrade
flow before package-owned assets may be rewritten. Until that flow existed, the refusal was
the whole behavior: a project created by an earlier release could not change its settings,
its capabilities, or its structure, and the documented answer was to generate a new project.
A researcher months into a study cannot do that.

These tests cover the flow and, more importantly, its safety boundary: an upgrade rewrites
tool-owned guidance and never touches researcher work or an edited starter.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from smairt import __version__

OLDER_VERSION = "0.2.0"


def installed_smairt() -> Path:
    return Path(sys.executable).with_name("smairt")


def run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(installed_smairt()), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def create_project(destination: Path) -> None:
    created = run(
        "new",
        str(destination),
        "--name",
        "Ongoing Study",
        "--slug",
        "ongoing_study",
        "--description",
        "A study already under way when SMAIRT was updated.",
        "--researcher",
        "Ada Researcher",
        "--domain",
        "Computational biology",
        "--accept-license",
        "--no-git",
    )
    assert created.returncode == 0, created.stderr


def age_project(destination: Path) -> None:
    """Record an older scaffold version, as a project from an earlier release would.

    This edits only the recorded version, so the project's files are current. That is enough to
    exercise the refusal, routing, and containment behavior, and deliberately not enough to
    stand in for a real inter-release upgrade: file contents, ownership, and the set of declared
    assets all move between versions. A genuine 0.3.0 project built with a real 0.3.0 install
    was carried through a track, two iterations, a run, and an interpretation, then upgraded
    with this build; the result is recorded in docs/scaffold-transition.md. Reproducing that
    here would mean shipping and building a second release inside the test suite.
    """
    contract = destination / "smairt.yaml"
    contract.write_text(
        contract.read_text().replace(
            f"scaffold_version: {__version__}", f"scaffold_version: {OLDER_VERSION}"
        )
    )
    assert f"scaffold_version: {OLDER_VERSION}" in contract.read_text()


def test_every_blocked_operation_names_the_upgrade_command(tmp_path: Path) -> None:
    """A refusal must state the route forward, not only that the door is closed."""
    destination = tmp_path / "aged_project"
    create_project(destination)
    age_project(destination)

    blocked = (
        run("settings", str(destination), "--phase", "real"),
        run("paper", "enable", str(destination)),
        run("hpc", "enable", str(destination)),
        run("regenerate", str(destination)),
        run("repair", str(destination)),
        run("regenerate", str(destination), "--select", "docs/12_STEPS.md", "--confirm"),
    )

    for result in blocked:
        assert result.returncode == 1, result.stdout
        assert "smairt upgrade" in result.stderr, result.stderr

    checked = run("check", str(destination))
    assert checked.returncode == 1
    assert "smairt upgrade" in checked.stdout


def test_repair_does_not_report_success_when_every_repair_is_blocked(tmp_path: Path) -> None:
    """`repair` used to print "No safe repairs are available" and exit 0 while blocked.

    Reporting nothing to do, successfully, is the most misleading answer available: it tells
    a researcher the project is fine.
    """
    destination = tmp_path / "aged_for_repair"
    create_project(destination)
    (destination / "results" / "logs" / "README.md").unlink()
    (destination / "results" / "logs").rmdir()
    age_project(destination)

    repaired = run("repair", str(destination))

    assert repaired.returncode == 1
    assert "No safe repairs are available" not in repaired.stdout
    assert "smairt upgrade" in repaired.stderr


def test_regenerate_does_not_offer_assets_it_would_refuse(tmp_path: Path) -> None:
    """The listing used to present every managed asset as eligible, then refuse on confirm."""
    destination = tmp_path / "aged_for_regenerate"
    create_project(destination)
    age_project(destination)

    listed = run("regenerate", str(destination))

    assert listed.returncode == 1
    assert "eligible for regeneration" not in listed.stdout
    assert "smairt upgrade" in listed.stderr


def test_the_preview_writes_nothing_and_describes_the_real_operation(tmp_path: Path) -> None:
    destination = tmp_path / "previewed_project"
    create_project(destination)
    guidance = destination / "docs" / "12_STEPS.md"
    guidance.write_text("Researcher-adjusted tool guidance.\n")
    missing = destination / "results" / "logs" / "README.md"
    missing.unlink()
    age_project(destination)

    preview = run("upgrade", str(destination))

    assert preview.returncode == 0, preview.stderr
    assert f"scaffold {OLDER_VERSION} to {__version__}" in preview.stdout
    assert "docs/12_STEPS.md" in preview.stdout
    assert "results/logs/README.md" in preview.stdout
    assert "No changes made" in preview.stdout
    # Nothing the preview described may have happened yet.
    assert guidance.read_text() == "Researcher-adjusted tool guidance.\n"
    assert not missing.exists()
    contract = yaml.safe_load((destination / "smairt.yaml").read_text())
    assert contract["scaffold_version"] == OLDER_VERSION


def test_an_upgrade_preserves_researcher_work_and_edited_starters(tmp_path: Path) -> None:
    """The safety boundary. An upgrade may rewrite tool guidance and nothing else.

    Researcher work is excluded from the managed-asset set entirely, and an editable starter
    is meant to be edited, so a difference there is the researcher's work rather than drift.
    """
    destination = tmp_path / "upgraded_project"
    create_project(destination)
    researcher_work = {
        destination / "hypotheses" / "HYPOTHESIS_01.md": "Six months of thinking.\n",
        destination / "analysis" / "BREADCRUMB_TRAIL.md": "My own decision record.\n",
        destination / "prompts" / "KNOWN_PATTERNS.md": "Patterns I found myself.\n",
    }
    edited_starter = destination / "hypotheses" / "HYPOTHESIS_TEMPLATE.md"
    edited_starter.write_text("My own template shape.\n")
    for path, content in researcher_work.items():
        path.write_text(content)
    age_project(destination)

    upgraded = run("upgrade", str(destination), "--confirm")

    assert upgraded.returncode == 0, upgraded.stderr
    assert f"upgraded to scaffold {__version__}" in upgraded.stdout
    for path, content in researcher_work.items():
        assert path.read_text() == content, f"{path.name} was modified by the upgrade"
    assert edited_starter.read_text() == "My own template shape.\n"
    contract = yaml.safe_load((destination / "smairt.yaml").read_text())
    assert contract["scaffold_version"] == __version__


def test_an_upgrade_preserves_a_populated_scientific_record(tmp_path: Path) -> None:
    """The case that matters: a study already under way, not a fresh project.

    A real release changes tool guidance and helper scripts, which is exactly when a
    researcher has most to lose. Every artifact the workflow produced must survive byte for
    byte, because the audit trail is the product.
    """
    destination = tmp_path / "study_under_way"
    create_project(destination)
    track = subprocess.run(
        [sys.executable, "scripts/new_track.py", "The baseline exceeds chance", "synthetic"],
        cwd=destination,
        check=False,
        capture_output=True,
        text=True,
    )
    assert track.returncode == 0, track.stderr
    iteration = subprocess.run(
        [
            sys.executable,
            "scripts/new_iteration.py",
            "baseline",
            "synthetic",
            "--hypothesis",
            "HYPOTHESIS_01",
        ],
        cwd=destination,
        check=False,
        capture_output=True,
        text=True,
    )
    assert iteration.returncode == 0, iteration.stderr
    ran = subprocess.run(
        [sys.executable, "experiments/01_synthetic/script_01_baseline.py"],
        cwd=destination,
        check=False,
        capture_output=True,
        text=True,
    )
    assert ran.returncode == 0, ran.stderr

    record = {
        path: path.read_bytes()
        for path in sorted(destination.rglob("*"))
        if path.is_file()
        and (
            path.match("hypotheses/HYPOTHESIS_0*.md")
            or path.match("experiments/*/script_*.py")
            or path.match("results/logs/*.log")
            or path.match("analysis/ITERATION_LOG.md")
            or path.match("plans/PLAN_*.md")
        )
    }
    assert record, "the workflow produced no artifacts to protect"
    age_project(destination)

    upgraded = run("upgrade", str(destination), "--confirm")

    assert upgraded.returncode == 0, upgraded.stderr
    for path, content in record.items():
        assert path.read_bytes() == content, f"{path.name} changed during the upgrade"
    assert run("check", str(destination), "--json").returncode == 0


def test_an_upgraded_project_passes_check_and_accepts_blocked_operations(tmp_path: Path) -> None:
    """The upgrade has to actually restore the operations the mismatch blocked."""
    destination = tmp_path / "unblocked_project"
    create_project(destination)
    age_project(destination)

    assert run("upgrade", str(destination), "--confirm").returncode == 0

    checked = run("check", str(destination), "--json")
    assert checked.returncode == 0, checked.stdout
    assert run("settings", str(destination), "--phase", "real").returncode == 0
    assert run("paper", "enable", str(destination)).returncode == 0


def test_upgrading_a_current_project_is_a_clear_no_op(tmp_path: Path) -> None:
    destination = tmp_path / "current_project"
    create_project(destination)

    for arguments in (("upgrade", str(destination)), ("upgrade", str(destination), "--confirm")):
        result = run(*arguments)
        assert result.returncode == 0, result.stderr
        assert "already on the installed" in result.stdout


def test_upgrade_reports_a_missing_project_rather_than_failing_obscurely(tmp_path: Path) -> None:
    result = run("upgrade", str(tmp_path))

    # Exit 2 rather than 1: there is no project to operate on, which is a different outcome
    # from an operation that ran against a real project and failed.
    assert result.returncode == 2
    assert "Not a SMAIRT project" in result.stderr


def researcher_work_files() -> list[str]:
    """Return every file the blueprint declares as researcher-owned.

    Read from the blueprint rather than listed here, so an asset reclassified as
    researcher-work is protected by these tests the moment it is declared.
    """
    blueprint = yaml.safe_load(
        (
            Path(__file__).parents[1] / "src" / "smairt" / "assets" / "scaffold-blueprint.yaml"
        ).read_text()
    )
    return [
        asset["path"]
        for asset in blueprint["assets"]
        if asset["kind"] == "file" and asset["ownership"] == "researcher-work"
    ]


def test_an_upgrade_never_recreates_researcher_work_the_preview_did_not_mention(
    tmp_path: Path,
) -> None:
    """A deleted researcher record must stay deleted, and the preview must be complete.

    The upgrade used to finish with a general materialize pass that created every missing
    active asset, including the blueprint's researcher-work records. A researcher who had
    deliberately removed `analysis/BREADCRUMB_TRAIL.md` silently got a fresh package template
    back from an operation whose preview never named the file. A preview that omits a write is
    not a preview.
    """
    destination = tmp_path / "deleted_records_project"
    create_project(destination)
    removed = []
    for relative in researcher_work_files():
        path = destination / relative
        if path.is_file():
            path.unlink()
            removed.append(relative)
    assert removed, "no researcher-work files were present to delete"
    age_project(destination)

    preview = run("upgrade", str(destination))
    assert preview.returncode == 0, preview.stderr
    for relative in removed:
        assert relative not in preview.stdout, f"preview mentions researcher work: {relative}"

    upgraded = run("upgrade", str(destination), "--confirm")

    assert upgraded.returncode == 0, upgraded.stderr
    for relative in removed:
        assert not (destination / relative).exists(), f"upgrade recreated {relative}"


def test_an_upgrade_will_not_write_through_a_symlinked_file(tmp_path: Path) -> None:
    """A managed path pointing outside the project must never be written.

    Blueprint paths are validated as lexically safe, which says nothing about the filesystem.
    Pointing `docs/12_STEPS.md` at an unrelated file and upgrading used to overwrite that file
    with scaffold guidance, destroying data outside the project entirely.
    """
    destination = tmp_path / "symlinked_project"
    create_project(destination)
    outside = tmp_path / "unrelated_notes.txt"
    outside.write_text("data that has nothing to do with SMAIRT\n")
    guidance = destination / "docs" / "12_STEPS.md"
    guidance.unlink()
    guidance.symlink_to(outside)
    age_project(destination)

    preview = run("upgrade", str(destination))
    assert preview.returncode == 0, preview.stderr
    assert "Resolves outside the project" in preview.stdout
    assert "docs/12_STEPS.md" in preview.stdout

    upgraded = run("upgrade", str(destination), "--confirm")

    assert upgraded.returncode == 0, upgraded.stderr
    assert outside.read_text() == "data that has nothing to do with SMAIRT\n"


def test_an_upgrade_will_not_create_a_file_outside_through_a_dangling_symlink(
    tmp_path: Path,
) -> None:
    """A missing managed file must not be created somewhere else via a broken link."""
    destination = tmp_path / "dangling_project"
    create_project(destination)
    outside = tmp_path / "should_not_be_created.txt"
    guidance = destination / "docs" / "12_STEPS.md"
    guidance.unlink()
    guidance.symlink_to(outside)
    age_project(destination)

    upgraded = run("upgrade", str(destination), "--confirm")

    assert upgraded.returncode == 0, upgraded.stderr
    assert not outside.exists(), "upgrade created a file outside the project"


def test_an_upgrade_will_not_write_through_a_symlinked_parent_directory(tmp_path: Path) -> None:
    """Containment has to hold for parent directories, not only for the file itself."""
    destination = tmp_path / "symlinked_parent_project"
    create_project(destination)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (elsewhere / "12_STEPS.md").write_text("not SMAIRT's to rewrite\n")
    shutil.rmtree(destination / "docs")
    (destination / "docs").symlink_to(elsewhere, target_is_directory=True)
    age_project(destination)

    upgraded = run("upgrade", str(destination), "--confirm")

    assert upgraded.returncode == 0, upgraded.stderr
    assert (elsewhere / "12_STEPS.md").read_text() == "not SMAIRT's to rewrite\n"


def test_a_failed_write_leaves_the_previous_file_intact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each asset is replaced atomically, so an interruption cannot truncate a file.

    Writing directly would empty the file first and then fill it, so a full disk or a killed
    process left a truncated guidance file behind. The content goes to a neighbour and is moved
    into place, which either succeeds completely or not at all.
    """
    from smairt import project as project_module  # noqa: PLC0415

    target = tmp_path / "guidance.md"
    target.write_text("original content\n")

    def fail(*args: object, **kwargs: object) -> None:
        raise OSError("no space left on device")

    monkeypatch.setattr("smairt.project.os.replace", fail)

    with pytest.raises(OSError):
        project_module._replace_atomically(target, "replacement content\n")

    assert target.read_text() == "original content\n"
    # The neighbour is cleaned up even when the move fails, so a retry is not blocked by it.
    assert not list(tmp_path.glob(".guidance.md.smairt-tmp"))
