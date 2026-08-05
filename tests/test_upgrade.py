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

import subprocess
import sys
from pathlib import Path

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
    """Record an older scaffold version, as a project from an earlier release would."""
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

    assert result.returncode == 1
    assert "Not a SMAIRT project" in result.stderr
