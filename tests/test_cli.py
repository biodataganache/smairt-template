from __future__ import annotations

import fcntl
import json
import os
import pty
import re
import select
import struct
import subprocess
import sys
import termios
import time
from datetime import datetime
from pathlib import Path

import yaml


def installed_smairt() -> Path:
    return Path(sys.executable).with_name("smairt")


def test_installed_command_reports_its_version() -> None:
    result = subprocess.run(
        [str(installed_smairt()), "--version"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "smairt 0.2.0"


def test_invalid_slug_exits_cleanly_without_creating_a_project(tmp_path: Path) -> None:
    destination = tmp_path / "invalid-slug"

    result = subprocess.run(
        [
            str(installed_smairt()),
            "new",
            str(destination),
            "--name",
            "Invalid Slug",
            "--slug",
            "Invalid-Slug",
            "--description",
            "Must not be created.",
            "--researcher",
            "Test Researcher",
            "--domain",
            "Not sure yet",
            "--accept-license",
            "--no-git",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Slug must start with a lowercase letter" in result.stderr
    assert not destination.exists()


def test_noninteractive_creation_requires_explicit_license_acceptance(tmp_path: Path) -> None:
    destination = tmp_path / "unaccepted-license"

    result = subprocess.run(
        [
            str(installed_smairt()),
            "new",
            str(destination),
            "--name",
            "License Test",
            "--slug",
            "license_test",
            "--description",
            "Must not be created without acceptance.",
            "--researcher",
            "Test Researcher",
            "--domain",
            "Not sure yet",
            "--no-git",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "--accept-license" in result.stderr
    assert not destination.exists()


def test_installed_command_creates_a_project_with_a_versioned_contract(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "protein-study"

    result = subprocess.run(
        [
            str(installed_smairt()),
            "new",
            str(destination),
            "--name",
            "Protein Study",
            "--slug",
            "protein_study",
            "--description",
            "A reproducible protein study.",
            "--researcher",
            "Ada Researcher",
            "--domain",
            "Computational biology",
            "--phase",
            "synthetic",
            "--assistant",
            "opencode",
            "--license",
            "MIT",
            "--accept-license",
            "--no-git",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == f"Created SMAIRT project at {destination}\n"
    metadata = yaml.safe_load((destination / "smairt.yaml").read_text())
    assert metadata == {
        "schema_version": 1,
        "scaffold_version": "0.2.0",
        "project": {
            "name": "Protein Study",
            "slug": "protein_study",
            "description": "A reproducible protein study.",
            "domain": "Computational biology",
        },
        "people": {"researcher": {"name": "Ada Researcher"}},
        "assistant": "opencode",
        "starting_phase": "synthetic",
        "current_phase": "synthetic",
        "license_year": datetime.now().year,
        "license": "MIT",
        "git_requested": False,
        "git_initialized": False,
        "capabilities": {
            "paper": {"state": "never_enabled"},
            "hpc": {"state": "never_enabled"},
        },
    }


def test_synthetic_project_contains_all_phase_directories(tmp_path: Path) -> None:
    destination = tmp_path / "synthetic"

    result = create_project(destination, phase="synthetic")

    assert result.returncode == 0, result.stderr
    assert paths(destination) >= {
        "data/synthetic",
        "data/downloaded",
        "data/real",
        "experiments/01_synthetic",
        "experiments/02_downloaded",
        "experiments/03_real_data",
    }


def test_downloaded_project_contains_all_phase_directories(tmp_path: Path) -> None:
    destination = tmp_path / "downloaded"

    result = create_project(destination, phase="downloaded")

    assert result.returncode == 0, result.stderr
    assert paths(destination) >= {
        "data/synthetic",
        "data/downloaded",
        "data/real",
        "experiments/01_synthetic",
        "experiments/02_downloaded",
        "experiments/03_real_data",
    }
    metadata = yaml.safe_load((destination / "smairt.yaml").read_text())
    assert metadata["starting_phase"] == "downloaded"
    assert metadata["current_phase"] == "downloaded"


def test_real_project_contains_all_phase_directories(tmp_path: Path) -> None:
    destination = tmp_path / "real"

    result = create_project(destination, phase="real")

    assert result.returncode == 0, result.stderr
    assert paths(destination) >= {
        "data/synthetic",
        "data/downloaded",
        "data/real",
        "experiments/01_synthetic",
        "experiments/02_downloaded",
        "experiments/03_real_data",
    }
    metadata = yaml.safe_load((destination / "smairt.yaml").read_text())
    assert metadata["starting_phase"] == "real"
    assert metadata["current_phase"] == "real"


def test_generated_project_restores_the_scientific_workflow_surface(tmp_path: Path) -> None:
    destination = tmp_path / "restored"

    result = create_project(destination)

    assert result.returncode == 0, result.stderr
    assert paths(destination) >= {
        "analysis/ANALYSIS_PLAN.md",
        "analysis/BREADCRUMB_TRAIL.md",
        "analysis/REPOSITORY_PLAN.md",
        "analysis/XX_figures/README.md",
        "docs/BEST_PRACTICE_COLLABORATIVE.md",
        "hypotheses/README.md",
        "prompts/00_priming_prompts.md",
        "prompts/README.md",
        "prompts/SESSION_START.md",
        "prompts/session_log.md",
        "scripts/generate_manifest.py",
        "scripts/monitor_template.py",
        "scripts/shared/README.md",
    }
    gitignore = (destination / ".gitignore").read_text()
    assert "data/**" in gitignore
    assert "!data/**/README.md" in gitignore
    assert "results/logs/*.log" not in gitignore
    assert len((destination / "hypotheses/HYPOTHESIS_TEMPLATE.md").read_text().splitlines()) > 30
    assert len((destination / "analysis/ANALYSIS_TEMPLATE.md").read_text().splitlines()) > 30
    assert len((destination / "analysis/STUDY_REPORT_TEMPLATE.md").read_text().splitlines()) > 60


def test_paper_and_hpc_are_independent_additive_capabilities(tmp_path: Path) -> None:
    paper_only = tmp_path / "paper"
    hpc_only = tmp_path / "hpc"

    paper_result = create_project(paper_only, paper=True)
    hpc_result = create_project(hpc_only, hpc=True)

    assert paper_result.returncode == 0, paper_result.stderr
    assert "paper/analysis" in paths(paper_only)
    assert paths(paper_only) >= {
        "FINAL_MANIFEST.md",
        "paper/drafts/README.md",
        "paper/reviewer_feedback/README.md",
        "prompts/InitialPrompt_paper_driven.md",
        "prompts/figure_generation_prompt.md",
        "prompts/iteration_review_prompt.md",
    }
    assert "hpc" not in paths(paper_only)
    assert hpc_result.returncode == 0, hpc_result.stderr
    assert "hpc" in paths(hpc_only)
    assert "hpc/slurm_job.sh" in paths(hpc_only)
    assert paths(hpc_only) >= {
        "hpc/config.yaml",
        "hpc/logs/README.md",
        "hpc/templates/slurm_basic.sh",
    }
    assert "paper" not in paths(hpc_only)
    assert "{{" not in (hpc_only / "hpc" / "slurm_job.sh").read_text()


def test_hpc_guidance_is_a_phase_independent_editable_template(tmp_path: Path) -> None:
    for phase in ("synthetic", "downloaded", "real"):
        destination = tmp_path / phase

        result = create_project(destination, phase=phase, hpc=True)

        assert result.returncode == 0, result.stderr
        script = (destination / "hpc" / "slurm_job.sh").read_text()
        assert "experiments/03_real_data/run.py" not in script
        assert "Usage: sbatch hpc/slurm_job.sh <experiment-command> [arguments...]" in script
        assert "results/logs" in script


def test_generated_script_captures_stdout_stderr_warnings_and_tracebacks(tmp_path: Path) -> None:
    destination = tmp_path / "logging"
    assert create_project(destination).returncode == 0
    created = subprocess.run(
        [
            sys.executable,
            "scripts/new_script.py",
            "synthetic",
            "capture failure",
            "--hypothesis",
            "Logging captures a complete execution record.",
        ],
        cwd=destination,
        check=False,
        capture_output=True,
        text=True,
    )
    script = destination / "experiments" / "01_synthetic" / "script_01_capture_failure.py"
    contents = script.read_text().replace(
        'print("TODO: implement the experiment")',
        'print("standard output")\n        print("standard error", file=sys.stderr)\n'
        '        import warnings\n        warnings.warn("warning output")\n'
        '        raise RuntimeError("failure output")',
    )
    script.write_text(contents)

    ran = subprocess.run(
        [sys.executable, str(script)],
        cwd=destination,
        check=False,
        capture_output=True,
        text=True,
    )
    logs = list((destination / "results" / "logs").glob("script_01_capture_failure_*.log"))

    assert created.returncode == 0, created.stderr
    assert ran.returncode != 0
    assert len(logs) == 1
    log = logs[0].read_text()
    assert "standard output" in log
    assert "standard error" in log
    assert "standard output" in ran.stdout
    assert "standard error" in ran.stderr
    assert "standard error" not in ran.stdout
    assert "warning output" in log
    assert "Traceback (most recent call last)" in log
    assert "RuntimeError: failure output" in log


def test_managed_assets_are_derived_from_the_package_after_clone(tmp_path: Path) -> None:
    destination = tmp_path / "managed"

    result = create_project(destination, initialize_git=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=SMAIRT Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "-m",
            "initial",
        ],
        cwd=destination,
        check=True,
        capture_output=True,
        text=True,
    )
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "clone", "--quiet", str(destination), str(clone)],
        check=True,
        capture_output=True,
        text=True,
    )
    checked = subprocess.run(
        [str(installed_smairt()), "check", str(clone), "--json"],
        check=False,
        capture_output=True,
        text=True,
    )
    inspected = subprocess.run(
        [str(installed_smairt()), "inspect", str(clone)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert not (destination / ".smairt" / "managed-files.yaml").exists()
    assert ".smairt/" in (destination / ".gitignore").read_text()
    assert checked.returncode == 0, checked.stdout
    assert json.loads(checked.stdout) == {"issues": [], "ok": True, "repairs": []}
    assert inspected.returncode == 0, inspected.stderr
    assert "README.md: unchanged" in inspected.stdout


def test_existing_destination_is_never_overwritten_or_partially_exposed(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "occupied"
    destination.mkdir()
    preserved = destination / "research.txt"
    preserved.write_text("do not overwrite")

    result = create_project(destination)

    assert result.returncode == 1
    assert result.stderr == f"Error: Destination is not empty: {destination}\n"
    assert preserved.read_text() == "do not overwrite"
    assert "smairt.yaml" not in paths(destination)
    assert not list(tmp_path.glob(".occupied.smairt-*"))


def test_dangling_symlink_destination_is_never_replaced(tmp_path: Path) -> None:
    destination = tmp_path / "dangling"
    destination.symlink_to(tmp_path / "missing-target", target_is_directory=True)

    result = create_project(destination)

    assert result.returncode == 1
    assert "Destination is not empty" in result.stderr
    assert destination.is_symlink()


def test_optional_email_is_omitted_and_scaffold_uses_log_first_guidance(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "no-email"

    result = create_project(destination)

    assert result.returncode == 0, result.stderr
    metadata = yaml.safe_load((destination / "smairt.yaml").read_text())
    assert "email" not in metadata["people"]["researcher"]
    assert not list(destination.rglob("*browser*"))
    assert (
        "not a pasted conversation transcript"
        in (destination / "prompts" / "session_log.md").read_text()
    )
    assert "results/logs/" in (destination / "prompts" / "AI_CONTEXT.md").read_text()


def test_git_initialization_stages_files_without_a_commit(tmp_path: Path) -> None:
    destination = tmp_path / "git-project"

    result = create_project(destination, initialize_git=True)
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=destination,
        check=False,
        capture_output=True,
        text=True,
    )
    commits = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=destination,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "Git repository initialized and files staged." in result.stdout
    assert "A  README.md" in status.stdout
    assert "A  smairt.yaml" in status.stdout
    assert commits.returncode != 0
    metadata = yaml.safe_load((destination / "smairt.yaml").read_text())
    assert metadata["git_requested"] is True
    assert metadata["git_initialized"] is True


def test_git_unavailability_does_not_prevent_generation(tmp_path: Path) -> None:
    destination = tmp_path / "without-git"

    result = create_project(destination, initialize_git=True, path="")

    assert result.returncode == 0, result.stderr
    assert "Git was requested but is unavailable" in result.stdout
    assert (destination / "smairt.yaml").is_file()
    metadata = yaml.safe_load((destination / "smairt.yaml").read_text())
    assert metadata["git_requested"] is True
    assert metadata["git_initialized"] is False


def create_project(
    destination: Path,
    *,
    phase: str = "synthetic",
    paper: bool = False,
    hpc: bool = False,
    assistant: str = "opencode",
    initialize_git: bool = False,
    path: str | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [
        str(installed_smairt()),
        "new",
        str(destination),
        "--name",
        "Test Project",
        "--slug",
        "test_project",
        "--description",
        "A test project.",
        "--researcher",
        "Test Researcher",
        "--domain",
        "Not sure yet",
        "--phase",
        phase,
        "--assistant",
        assistant,
    ]
    command.append("--git" if initialize_git else "--no-git")
    command.append("--accept-license")
    if paper:
        command.append("--paper")
    if hpc:
        command.append("--hpc")
    environment = {
        **os.environ,
        "XDG_DATA_HOME": str(destination.parent / ".smairt-test-data"),
    }
    if path is not None:
        environment["PATH"] = path
    return subprocess.run(command, check=False, capture_output=True, text=True, env=environment)


def paths(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*")}


def test_project_management_commands_are_safe_and_idempotent(tmp_path: Path) -> None:
    destination = tmp_path / "managed-project"

    created = create_project(destination)
    enabled = subprocess.run(
        [str(installed_smairt()), "paper", "enable", str(destination)],
        check=False,
        capture_output=True,
        text=True,
    )
    paper_readme = destination / "paper" / "README.md"
    paper_readme.write_text("researcher-owned paper guidance\n")
    disabled = subprocess.run(
        [str(installed_smairt()), "paper", "disable", str(destination)],
        check=False,
        capture_output=True,
        text=True,
    )
    reenabled = subprocess.run(
        [str(installed_smairt()), "paper", "enable", str(destination)],
        check=False,
        capture_output=True,
        text=True,
    )
    enabled_again = subprocess.run(
        [str(installed_smairt()), "paper", "enable", str(destination)],
        check=False,
        capture_output=True,
        text=True,
    )
    checked = subprocess.run(
        [str(installed_smairt()), "check", str(destination), "--json"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert created.returncode == 0, created.stderr
    assert enabled.returncode == 0, enabled.stderr
    assert "Paper support enabled" in enabled.stdout
    assert disabled.returncode == 0, disabled.stderr
    assert "Paper support deactivated" in disabled.stdout
    assert reenabled.returncode == 0, reenabled.stderr
    assert "Paper support enabled" in reenabled.stdout
    assert enabled_again.returncode == 0, enabled_again.stderr
    assert "already enabled" in enabled_again.stdout
    assert paper_readme.read_text() == "researcher-owned paper guidance\n"
    assert checked.returncode == 1, checked.stdout
    assert json.loads(checked.stdout) == {
        "issues": [
            {
                "code": "modified-managed-file",
                "message": "Managed file was modified and will be preserved: paper/README.md",
                "path": "paper/README.md",
            }
        ],
        "ok": False,
        "repairs": [],
    }


def test_researcher_work_and_editable_starters_are_not_modified_file_failures(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "ownership"
    assert create_project(destination, paper=True).returncode == 0
    (destination / "analysis" / "BREADCRUMB_TRAIL.md").write_text("research decisions\n")
    (destination / "analysis" / "ANALYSIS_PLAN.md").write_text("research plan\n")
    (destination / "FINAL_MANIFEST.md").write_text("claim evidence\n")
    (destination / ".gitignore").write_text("custom ignores\n")

    checked = subprocess.run(
        [str(installed_smairt()), "check", str(destination), "--json"],
        check=False,
        capture_output=True,
        text=True,
    )
    inspected = subprocess.run(
        [str(installed_smairt()), "inspect", str(destination)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert checked.returncode == 0, checked.stdout
    assert json.loads(checked.stdout) == {"issues": [], "ok": True, "repairs": []}
    assert "analysis/ANALYSIS_PLAN.md: modified" in inspected.stdout
    assert "analysis/BREADCRUMB_TRAIL.md" not in inspected.stdout
    assert "FINAL_MANIFEST.md" not in inspected.stdout


def test_settings_license_check_and_repair_are_guarded(tmp_path: Path) -> None:
    destination = tmp_path / "configured-project"
    assert create_project(destination).returncode == 0

    settings = subprocess.run(
        [
            str(installed_smairt()),
            "settings",
            str(destination),
            "--name",
            "Renamed Project",
            "--phase",
            "real",
            "--collaborator-role",
            "analyst",
            "--collaborator-name",
            "Grace Analyst",
            "--experience",
            "advanced",
            "--no-motion",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    preview = subprocess.run(
        [str(installed_smairt()), "settings", str(destination), "--license", "Apache-2.0"],
        check=False,
        capture_output=True,
        text=True,
    )
    confirmed = subprocess.run(
        [
            str(installed_smairt()),
            "settings",
            str(destination),
            "--license",
            "Apache-2.0",
            "--confirm-license",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    (destination / "LICENSE").write_text("custom legal terms\n")
    refused = subprocess.run(
        [
            str(installed_smairt()),
            "settings",
            str(destination),
            "--license",
            "MIT",
            "--confirm-license",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    missing_directory = destination / "plans"
    (missing_directory / "README.md").unlink()
    missing_directory.rmdir()
    check_before = subprocess.run(
        [str(installed_smairt()), "check", str(destination), "--json"],
        check=False,
        capture_output=True,
        text=True,
    )
    preview_repair = subprocess.run(
        [
            str(installed_smairt()),
            "repair",
            str(destination),
            "--select",
            "create-directory:plans",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert preview_repair.returncode == 0
    assert not missing_directory.exists()
    assert "No changes made" in preview_repair.stdout
    applied_repair = subprocess.run(
        [
            str(installed_smairt()),
            "repair",
            str(destination),
            "--select",
            "create-directory:plans",
            "--confirm",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    metadata = yaml.safe_load((destination / "smairt.yaml").read_text())
    preferences = yaml.safe_load((destination / ".smairt" / "preferences.yaml").read_text())
    assert settings.returncode == 0, settings.stderr
    assert metadata["project"]["name"] == "Renamed Project"
    assert metadata["project"]["slug"] == "test_project"
    assert metadata["starting_phase"] == "synthetic"
    assert metadata["current_phase"] == "real"
    assert metadata["people"]["analyst"] == {"name": "Grace Analyst"}
    assert preferences == {"experience": "advanced", "motion": False}
    assert preview.returncode == 0
    assert "Preview:" in preview.stdout
    assert "No license change made" in preview.stdout
    assert confirmed.returncode == 0, confirmed.stderr
    assert "License changed to Apache-2.0." in confirmed.stdout
    assert refused.returncode == 1
    assert "will not replace custom legal text" in refused.stderr
    assert check_before.returncode == 1
    assert "create-directory:plans" in json.loads(check_before.stdout)["repairs"]
    assert applied_repair.returncode == 0
    assert missing_directory.is_dir()


def test_license_change_updates_managed_asset_and_renaming_researcher_is_not_a_legal_edit(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "license-project"
    assert create_project(destination).returncode == 0

    renamed = subprocess.run(
        [
            str(installed_smairt()),
            "settings",
            str(destination),
            "--researcher",
            "Renamed Researcher",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    changed = subprocess.run(
        [
            str(installed_smairt()),
            "settings",
            str(destination),
            "--license",
            "Apache-2.0",
            "--confirm-license",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    license_path = destination / "LICENSE"
    license_path.unlink()
    regenerated = subprocess.run(
        [
            str(installed_smairt()),
            "regenerate",
            str(destination),
            "--select",
            "LICENSE",
            "--confirm",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert renamed.returncode == 0, renamed.stderr
    assert changed.returncode == 0, changed.stderr
    assert regenerated.returncode == 0, regenerated.stderr
    assert "Apache License" in license_path.read_text()
    assert "Renamed Researcher" in license_path.read_text()
    checked = subprocess.run(
        [str(installed_smairt()), "check", str(destination), "--json"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert checked.returncode == 0, checked.stdout


def test_open_tracks_recents_and_home_cleans_stale_paths(tmp_path: Path) -> None:
    data_home = tmp_path / "local-data"
    destination = tmp_path / "opened-project"
    assert create_project(destination).returncode == 0
    environment = {**os.environ, "XDG_DATA_HOME": str(data_home), "TERM": "dumb", "CI": "1"}
    opened = subprocess.run(
        [str(installed_smairt()), "open", str(destination)],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )
    recents_path = data_home / "smairt" / "recent-projects.json"
    stale_entries = [
        {"path": str(tmp_path / "missing"), "opened_at": "2026-01-01T00:00:00+00:00"},
        *json.loads(recents_path.read_text()),
    ]
    recents_path.write_text(json.dumps(stale_entries))
    home = subprocess.run(
        [str(installed_smairt())],
        input="2\n\n5\n",
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert opened.returncode == 0, opened.stderr
    assert opened.stdout == f"Opened SMAIRT project: {destination}\n"
    assert "SMAIRT Home" in home.stdout
    recents = json.loads(recents_path.read_text())
    assert recents == [{"path": str(destination), "opened_at": recents[0]["opened_at"]}]


def test_assistant_aliases_and_dashboard_are_available_from_installed_command(
    tmp_path: Path,
) -> None:
    expected_aliases = {
        "claude-code": "CLAUDE.md",
        "opencode": "AGENTS.md",
        "codex": "AGENTS.md",
        "pi": "AGENTS.md",
        "cursor": ".cursor/rules/smairt.mdc",
    }
    for assistant, alias in expected_aliases.items():
        destination = tmp_path / assistant
        created = create_project(destination, assistant=assistant)

        assert created.returncode == 0, created.stderr
        assert (destination / alias).read_text() == (
            "# SMAIRT AI Context\n\nRead `prompts/AI_CONTEXT.md` before working in this project.\n"
        )

    dashboard_project = tmp_path / "dashboard"
    assert create_project(dashboard_project).returncode == 0
    dashboard = subprocess.run(
        [str(installed_smairt())],
        input="settings\nname\nDashboard Project\nback\nexit\n",
        check=False,
        capture_output=True,
        text=True,
        cwd=dashboard_project,
        env={**os.environ, "TERM": "dumb", "CI": "1"},
    )

    assert dashboard.returncode == 0, dashboard.stderr
    assert "SMAIRT Standard Mode: Test Project" in dashboard.stdout
    assert "Project Check" in dashboard.stdout
    assert (
        yaml.safe_load((dashboard_project / "smairt.yaml").read_text())["project"]["name"]
        == "Dashboard Project"
    )


def test_dashboard_capability_changes_are_previewed_before_anything_is_written(
    tmp_path: Path,
) -> None:
    """A researcher sees the real file list and can refuse it without side effects."""
    destination = tmp_path / "capability-dashboard"
    assert create_project(destination).returncode == 0

    refused = run_dashboard(destination, "capabilities\npaper\nno\nexit\n")
    still_inactive = yaml.safe_load((destination / "smairt.yaml").read_text())

    assert refused.returncode == 0, refused.stderr
    assert "Pending capability changes" in refused.stdout
    assert "Enable Paper Support" in refused.stdout
    assert "+ paper/outline.md" in refused.stdout
    assert "No changes made." in refused.stdout
    assert still_inactive["capabilities"]["paper"] == {"state": "never_enabled"}
    assert not (destination / "paper").exists()

    applied = run_dashboard(destination, "capabilities\npaper\nyes\nexit\n")
    metadata = yaml.safe_load((destination / "smairt.yaml").read_text())

    assert applied.returncode == 0, applied.stderr
    assert metadata["capabilities"]["paper"] == {"state": "enabled"}
    assert (destination / "paper" / "outline.md").is_file()


def test_dashboard_capability_selection_refuses_a_contradictory_request(
    tmp_path: Path,
) -> None:
    """None and a capability cannot both be requested, so the answer is refused."""
    destination = tmp_path / "contradictory-capabilities"
    assert create_project(destination).returncode == 0

    dashboard = run_dashboard(destination, "capabilities\nnone,paper\nexit\n")

    assert dashboard.returncode == 0, dashboard.stderr
    assert "cannot be combined with one" in dashboard.stdout
    assert "Pending capability changes" not in dashboard.stdout
    assert yaml.safe_load((destination / "smairt.yaml").read_text())["capabilities"]["paper"] == {
        "state": "never_enabled"
    }
    assert not (destination / "paper").exists()


def test_standard_dashboard_previews_and_confirms_safe_repairs(tmp_path: Path) -> None:
    destination = tmp_path / "repair-dashboard"
    assert create_project(destination).returncode == 0
    plans = destination / "plans"
    (plans / "README.md").unlink()
    plans.rmdir()

    dashboard = run_dashboard(destination, "check\ncreate-directory:plans\nyes\nexit\n")

    assert dashboard.returncode == 0, dashboard.stderr
    assert "Safe repairs available:" in dashboard.stdout
    assert "Preview: create-directory:plans" in dashboard.stdout
    assert "Selected safe repairs applied." in dashboard.stdout
    assert plans.is_dir()


def test_recents_are_capped_and_hpc_deactivation_preserves_modified_templates(
    tmp_path: Path,
) -> None:
    data_home = tmp_path / "local-data"
    environment = {**os.environ, "XDG_DATA_HOME": str(data_home)}
    destinations: list[Path] = []
    for number in range(11):
        destination = tmp_path / f"project-{number}"
        assert create_project(destination).returncode == 0
        opened = subprocess.run(
            [str(installed_smairt()), "open", str(destination)],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )
        assert opened.returncode == 0, opened.stderr
        destinations.append(destination)
    hpc_project = destinations[-1]
    enabled = subprocess.run(
        [str(installed_smairt()), "hpc", "enable", str(hpc_project)],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )
    template = hpc_project / "hpc" / "slurm_job.sh"
    template.write_text("#!/usr/bin/env bash\n# researcher template\n")
    disabled = subprocess.run(
        [str(installed_smairt()), "hpc", "disable", str(hpc_project)],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )
    reenabled = subprocess.run(
        [str(installed_smairt()), "hpc", "enable", str(hpc_project)],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    recents = json.loads((data_home / "smairt" / "recent-projects.json").read_text())
    metadata = yaml.safe_load((hpc_project / "smairt.yaml").read_text())
    assert len(recents) == 10
    assert str(destinations[0]) not in [entry["path"] for entry in recents]
    assert enabled.returncode == 0, enabled.stderr
    assert disabled.returncode == 0, disabled.stderr
    assert reenabled.returncode == 0, reenabled.stderr
    assert template.read_text() == "#!/usr/bin/env bash\n# researcher template\n"
    assert metadata["capabilities"]["hpc"] == {"state": "enabled"}


def test_deactivated_capabilities_do_not_offer_guidance_until_safely_reenabled(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "inactive-capabilities"
    assert create_project(destination, paper=True, hpc=True).returncode == 0
    paper_readme = destination / "paper" / "README.md"
    hpc_readme = destination / "hpc" / "README.md"
    paper_outline = destination / "paper" / "outline.md"
    hpc_template = destination / "hpc" / "slurm_job.sh"
    paper_readme.write_text("researcher paper notes\n")
    hpc_readme.write_text("researcher cluster notes\n")

    disabled_paper = subprocess.run(
        [str(installed_smairt()), "paper", "disable", str(destination)],
        check=False,
        capture_output=True,
        text=True,
    )
    disabled_hpc = subprocess.run(
        [str(installed_smairt()), "hpc", "disable", str(destination)],
        check=False,
        capture_output=True,
        text=True,
    )
    inactive_check = subprocess.run(
        [str(installed_smairt()), "check", str(destination), "--json"],
        check=False,
        capture_output=True,
        text=True,
    )
    paper_outline.unlink()
    hpc_template.unlink()
    reenabled_paper = subprocess.run(
        [str(installed_smairt()), "paper", "enable", str(destination)],
        check=False,
        capture_output=True,
        text=True,
    )
    reenabled_hpc = subprocess.run(
        [str(installed_smairt()), "hpc", "enable", str(destination)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert disabled_paper.returncode == 0, disabled_paper.stderr
    assert disabled_hpc.returncode == 0, disabled_hpc.stderr
    assert inactive_check.returncode == 0, inactive_check.stdout
    assert json.loads(inactive_check.stdout) == {"issues": [], "ok": True, "repairs": []}
    assert reenabled_paper.returncode == 0, reenabled_paper.stderr
    assert reenabled_hpc.returncode == 0, reenabled_hpc.stderr
    assert paper_readme.read_text() == "researcher paper notes\n"
    assert hpc_readme.read_text() == "researcher cluster notes\n"
    assert paper_outline.read_text().startswith("# Paper Outline\n")
    assert "Usage: sbatch hpc/slurm_job.sh" in hpc_template.read_text()


def test_enabled_capability_repairs_missing_starters_outside_capability_directories(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "paper-repair"
    assert create_project(destination, paper=True).returncode == 0
    prompt = destination / "prompts" / "figure_generation_prompt.md"
    prompt.unlink()

    checked = subprocess.run(
        [str(installed_smairt()), "check", str(destination), "--json"],
        check=False,
        capture_output=True,
        text=True,
    )
    payload = json.loads(checked.stdout)

    assert checked.returncode == 1
    assert "restore-capability:paper" in payload["repairs"]

    repaired = subprocess.run(
        [
            str(installed_smairt()),
            "repair",
            str(destination),
            "--select",
            "restore-capability:paper",
            "--confirm",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert repaired.returncode == 0, repaired.stderr
    assert prompt.is_file()


def test_advanced_controls_are_local_safe_and_visible_from_installed_command(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "advanced-project"
    assert create_project(destination).returncode == 0

    configured = subprocess.run(
        [
            str(installed_smairt()),
            "settings",
            str(destination),
            "--experience",
            "advanced",
            "--prompt-convention",
            "plan-first",
            "--code-convention",
            "typed-python",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    inspection = subprocess.run(
        [str(installed_smairt()), "inspect", str(destination), "--hashes"],
        check=False,
        capture_output=True,
        text=True,
    )
    configured_prompt = (destination / "prompts" / "AI_CONTEXT.md").read_text()
    configured_code = (destination / "prompts" / "CODE_CONVENTIONS.md").read_text()
    (destination / "prompts" / "AI_CONTEXT.md").write_text("researcher-owned prompt\n")
    verbose_check = subprocess.run(
        [str(installed_smairt()), "check", str(destination), "--verbose"],
        check=False,
        capture_output=True,
        text=True,
    )
    refused_regeneration = subprocess.run(
        [
            str(installed_smairt()),
            "regenerate",
            str(destination),
            "--select",
            "prompts/AI_CONTEXT.md",
            "--confirm",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert (
        subprocess.run(
            [str(installed_smairt()), "paper", "enable", str(destination)],
            check=False,
            capture_output=True,
            text=True,
        ).returncode
        == 0
    )
    (destination / "paper" / "outline.md").unlink()
    preview = subprocess.run(
        [
            str(installed_smairt()),
            "regenerate",
            str(destination),
            "--select",
            "paper/outline.md",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    restored = subprocess.run(
        [
            str(installed_smairt()),
            "regenerate",
            str(destination),
            "--select",
            "paper/outline.md",
            "--confirm",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    dashboard = subprocess.run(
        [str(installed_smairt())],
        input="advanced\nback\nexit\n",
        check=False,
        capture_output=True,
        text=True,
        cwd=destination,
        env={**os.environ, "TERM": "dumb", "CI": "1"},
    )

    metadata = yaml.safe_load((destination / "smairt.yaml").read_text())
    assert configured.returncode == 0, configured.stderr
    assert metadata["conventions"] == {
        "prompt": "plan-first",
        "code": "typed-python",
    }
    assert "Project prompt convention: create a plan before complex work." in configured_prompt
    assert "Project code convention: use type annotations" in configured_code
    assert "Full project contract:" in inspection.stdout
    assert "Managed files:" in inspection.stdout
    assert "expected SHA-256" in inspection.stdout
    assert "Python:" in inspection.stdout
    assert "Git:" in inspection.stdout
    assert "Selected assistant (opencode):" in inspection.stdout
    assert verbose_check.returncode == 1
    assert "Artifact: prompts/AI_CONTEXT.md" in verbose_check.stdout
    assert "Detected local tools:" in verbose_check.stdout
    assert refused_regeneration.returncode == 1
    assert "researcher-owned prompt" in (destination / "prompts" / "AI_CONTEXT.md").read_text()
    assert preview.returncode == 0, preview.stderr
    assert "No changes made" in preview.stdout
    assert restored.returncode == 0, restored.stderr
    assert (destination / "paper" / "outline.md").read_text().startswith("# Paper Outline\n")
    assert dashboard.returncode == 0, dashboard.stderr
    assert "SMAIRT Advanced Mode: Test Project" in dashboard.stdout
    assert "Launch assistant or open folder [assistant]" in dashboard.stdout
    assert "Project Settings [settings]" in dashboard.stdout
    assert "Optional capabilities: Paper [capabilities]" in dashboard.stdout
    assert "Project Check [check]" in dashboard.stdout
    assert "Advanced ▸ [advanced]" in dashboard.stdout
    assert "Inspect project contract [inspect]" in dashboard.stdout
    assert "Regenerate managed assets [regenerate]" in dashboard.stdout
    assert "Detected local tools [tools]" in dashboard.stdout


def test_advanced_mode_preference_is_local_to_each_project_checkout(tmp_path: Path) -> None:
    advanced_project = tmp_path / "advanced"
    standard_project = tmp_path / "standard"
    assert create_project(advanced_project).returncode == 0
    assert create_project(standard_project).returncode == 0

    configured = subprocess.run(
        [
            str(installed_smairt()),
            "settings",
            str(advanced_project),
            "--experience",
            "advanced",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    advanced_dashboard = subprocess.run(
        [str(installed_smairt())],
        input="exit\n",
        check=False,
        capture_output=True,
        text=True,
        cwd=advanced_project,
        env={**os.environ, "TERM": "dumb", "CI": "1"},
    )
    standard_dashboard = subprocess.run(
        [str(installed_smairt())],
        input="exit\n",
        check=False,
        capture_output=True,
        text=True,
        cwd=standard_project,
        env={**os.environ, "TERM": "dumb", "CI": "1"},
    )

    assert configured.returncode == 0, configured.stderr
    assert yaml.safe_load((advanced_project / ".smairt" / "preferences.yaml").read_text()) == {
        "experience": "advanced"
    }
    assert not (standard_project / ".smairt" / "preferences.yaml").exists()
    assert "SMAIRT Advanced Mode: Test Project" in advanced_dashboard.stdout
    assert "SMAIRT Standard Mode: Test Project" in standard_dashboard.stdout
    assert "Advanced ▸ [advanced]" in advanced_dashboard.stdout
    assert "Advanced ▸" not in standard_dashboard.stdout
    assert "Advanced mode adds contract inspection" in standard_dashboard.stdout


def test_interactive_wizard_creates_a_project_from_a_real_input_stream(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "guided-project"

    result = run_interactive_new(
        "\n".join(
            [
                "Guided Protein Study",
                "2",
                str(destination.parent),
                destination.name,
                "A project created through the guided setup.",
                "1",
                ":skip",
                "Ada Researcher",
                ":skip",
                "paper,hpc",
                "",
                "3",
                "",
                "yes",
                "no",
                "create",
            ]
        )
        + "\n"
    )

    assert result.returncode == 0, result.stderr
    assert "Step 1 of 14" in result.stdout
    assert "Step 14 of 14" in result.stdout
    assert "Final review" in result.stdout
    assert "Created SMAIRT project at" in result.stdout
    assert "Creating your SMAIRT project" not in result.stdout
    assert "Folder: guided-project" in result.stdout
    assert "Identifier: guided_project" in result.stdout
    metadata = yaml.safe_load((destination / "smairt.yaml").read_text())
    assert metadata["project"] == {
        "name": "Guided Protein Study",
        "slug": "guided_project",
        "description": "A project created through the guided setup.",
        "domain": "Computational biology",
    }
    assert metadata["assistant"] == "opencode"
    assert metadata["starting_phase"] == "synthetic"
    assert metadata["current_phase"] == "synthetic"
    assert metadata["license"] == "MIT"
    assert metadata["git_requested"] is False
    assert metadata["capabilities"] == {
        "paper": {"state": "enabled"},
        "hpc": {"state": "enabled"},
    }


def test_interactive_wizard_creates_a_new_child_under_a_selected_parent(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "parent-based-study"

    result = run_interactive_new(
        "\n".join(
            [
                "Parent Based Study",
                "2",
                str(tmp_path),
                destination.name,
                "A project created under a selected parent.",
                "5",
                ":skip",
                "Ada Researcher",
                ":skip",
                "",
                "",
                "3",
                "",
                "yes",
                "no",
                "create",
            ]
        )
        + "\n"
    )

    assert result.returncode == 0, result.stderr
    assert "Will create:" in result.stdout
    assert (destination / "smairt.yaml").is_file()


def test_interactive_wizard_creates_a_new_child_in_the_current_workspace(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "workspace-study"

    result = run_interactive_new(
        "\n".join(
            [
                "Workspace Study",
                "",
                "",
                "A project created in the current workspace.",
                "5",
                ":skip",
                "Ada Researcher",
                ":skip",
                "",
                "",
                "3",
                "",
                "yes",
                "no",
                "create",
            ]
        )
        + "\n",
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    assert (destination / "smairt.yaml").is_file()


def test_interactive_wizard_keeps_answers_when_going_back_and_edits_review_answers(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "edited-project"

    result = run_interactive_new(
        "\n".join(
            [
                "Original Name",
                ":back",
                "Original Name",
                "2",
                str(destination.parent),
                destination.name,
                "A retained description.",
                "5",
                ":skip",
                "Grace Researcher",
                ":skip",
                "",
                "",
                "3",
                "",
                "yes",
                "no",
                "name",
                "Edited Name",
                "create",
            ]
        )
        + "\n"
    )

    assert result.returncode == 0, result.stderr
    assert "Back: your earlier answers are kept." in result.stdout
    metadata = yaml.safe_load((destination / "smairt.yaml").read_text())
    assert metadata["project"]["name"] == "Edited Name"
    assert metadata["project"]["slug"] == "edited_project"
    assert metadata["project"]["description"] == "A retained description."


def test_interactive_wizard_reconfirms_a_license_changed_during_final_review(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "reviewed-license-project"

    result = run_interactive_new(
        wizard_answers(
            destination,
            review_action="license\n3\ncreate\nyes",
        )
    )

    assert result.returncode == 0, result.stderr
    assert "Apache-2.0 controls how others may use this project" in result.stdout
    assert yaml.safe_load((destination / "smairt.yaml").read_text())["license"] == "Apache-2.0"


def test_saved_motion_preference_controls_a_project_dashboard_tty(tmp_path: Path) -> None:
    enabled_project = tmp_path / "motion-enabled"
    disabled_project = tmp_path / "motion-disabled"
    assert create_project(enabled_project).returncode == 0
    assert create_project(disabled_project).returncode == 0
    configured = subprocess.run(
        [str(installed_smairt()), "settings", str(disabled_project), "--no-motion"],
        check=False,
        capture_output=True,
        text=True,
    )

    enabled_dashboard = run_interactive_dashboard(enabled_project, "\x1b")
    disabled_dashboard = run_interactive_dashboard(disabled_project, "exit\n")

    assert configured.returncode == 0, configured.stderr
    assert enabled_dashboard.returncode == 0, enabled_dashboard.stderr
    assert disabled_dashboard.returncode == 0, disabled_dashboard.stderr
    assert "\x1b[1;36mSMAIRT Standard Mode: Test Project" in enabled_dashboard.stdout
    assert "\x1b[1;36mSMAIRT Standard Mode: Test Project" not in disabled_dashboard.stdout
    enabled_screen = visible_text(enabled_dashboard.stdout)
    disabled_screen = visible_text(disabled_dashboard.stdout)
    assert "Up/Down or j/k move" in enabled_screen
    assert "(*) Launch assistant or open folder" in enabled_screen
    assert "Up/Down or j/k move" not in disabled_screen
    assert "1. Launch assistant or open folder [assistant]" in disabled_screen


def test_home_offers_a_scrollable_menu_in_a_capable_terminal(tmp_path: Path) -> None:
    data_home = tmp_path / "home-data"
    empty_workspace = tmp_path / "no-project-here"
    empty_workspace.mkdir()

    home = run_interactive_dashboard(
        empty_workspace,
        "\x1b",
        environment={"XDG_DATA_HOME": str(data_home)},
    )

    assert home.returncode == 0, home.stdout
    screen = visible_text(home.stdout)
    assert "SMAIRT Home" in screen
    assert "(*) Create New Project" in screen
    assert "( ) Recent Projects" in screen
    assert "Up/Down or j/k move" in screen


def test_visual_settings_menu_is_reachable_and_returns_to_the_dashboard(tmp_path: Path) -> None:
    destination = tmp_path / "visual-settings"
    assert create_project(destination).returncode == 0

    dashboard = run_interactive_dashboard(destination, "\x1b[B\r\x1b\x03")

    assert dashboard.returncode == 0, dashboard.stdout
    screen = visible_text(dashboard.stdout)
    assert "( ) Project Settings" in screen
    assert "Local experience and motion" in screen
    assert yaml.safe_load((destination / "smairt.yaml").read_text())["project"]["name"] == (
        "Test Project"
    )


def test_interactive_wizard_validates_destination_before_final_review(tmp_path: Path) -> None:
    destination = tmp_path / "occupied"
    destination.mkdir()
    preserved = destination / "notes.txt"
    preserved.write_text("keep this")

    result = run_interactive_new(
        f"Occupied Study\n2\n{destination.parent}\n{destination.name}\n:cancel\n"
    )

    assert result.returncode == 1
    assert "Destination is not empty" in result.stdout
    assert preserved.read_text() == "keep this"
    assert not (destination / "smairt.yaml").exists()


def test_interactive_wizard_treats_a_symlinked_directory_as_the_parent(
    tmp_path: Path,
) -> None:
    real_parent = tmp_path / "real-parent"
    real_parent.mkdir()
    parent_link = tmp_path / "documents"
    parent_link.symlink_to(real_parent, target_is_directory=True)
    destination = real_parent / "symlink-study"

    result = run_interactive_new(wizard_answers(parent_link / destination.name))

    assert result.returncode == 0, result.stderr
    assert (destination / "smairt.yaml").is_file()


def test_interactive_wizard_rejects_a_missing_selected_parent(tmp_path: Path) -> None:
    missing_parent = tmp_path / "missing"

    result = run_interactive_new(f"Missing Parent Study\n2\n{missing_parent}\nstudy\n:cancel\n")

    assert result.returncode == 1
    assert "Destination parent does not exist" in result.stdout
    assert not missing_parent.exists()


def test_interactive_wizard_cancellation_at_review_writes_no_project(tmp_path: Path) -> None:
    destination = tmp_path / "cancelled-project"

    result = run_interactive_new(wizard_answers(destination, review_action="cancel"))

    assert result.returncode == 1
    assert "Project creation cancelled. No files were written." in result.stdout
    assert not destination.exists()


def test_interactive_wizard_reports_generation_failure_without_exposing_a_project(
    tmp_path: Path,
) -> None:
    destination = tmp_path / ("a" * 248)

    result = run_interactive_new(wizard_answers(destination))

    assert result.returncode == 1
    assert "Could not create the project:" in result.stdout
    assert not destination.exists()


def wizard_answers(destination: Path, *, review_action: str = "create") -> str:
    """Return one full pass through the wizard, addressed by tokens where it offers them.

    The location step confirms the folder and derives the identifier from it, so
    there is no separate identifier answer to supply.
    """
    return (
        "\n".join(
            [
                "Test Project",
                "2",
                str(destination.parent),
                destination.name,
                "A test project.",
                "5",
                ":skip",
                "Test Researcher",
                ":skip",
                "",
                "",
                "3",
                "",
                "yes",
                "no",
                review_action,
            ]
        )
        + "\n"
    )


def run_interactive_new(
    input_text: str, *, cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    command = [str(installed_smairt()), "new"]
    master, slave = pty.openpty()
    process = subprocess.Popen(
        command,
        stdin=slave,
        stdout=slave,
        stderr=slave,
        text=False,
        cwd=cwd,
        env={**os.environ, "TERM": "dumb", "CI": "1"},
    )
    os.close(slave)
    output = bytearray()
    sent = False
    deadline = time.monotonic() + 10
    while process.poll() is None and time.monotonic() < deadline:
        readable, _, _ = select.select([master], [], [], 0.1)
        if readable:
            try:
                output.extend(os.read(master, 4096))
            except OSError:
                break
        if not sent and b"Project name" in output:
            os.write(master, input_text.encode())
            sent = True
    if process.poll() is None:
        process.kill()
        raise AssertionError(f"interactive command timed out: {output.decode()}")
    while True:
        try:
            chunk = os.read(master, 4096)
        except OSError:
            break
        if not chunk:
            break
        output.extend(chunk)
    os.close(master)
    return subprocess.CompletedProcess(command, process.wait(), output.decode(), "")


def run_dashboard(root: Path, input_text: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(installed_smairt())],
        input=input_text,
        check=False,
        capture_output=True,
        text=True,
        cwd=root,
        env={**os.environ, "TERM": "dumb", "CI": "1"},
    )


def visible_text(output: str) -> str:
    """Return the words a researcher reads, without terminal control sequences.

    A framed screen positions the cursor while drawing, so a label is not
    necessarily contiguous bytes in the stream. Assertions belong on the visible
    text rather than on the escape sequences that happen to produce it.
    """
    without_escapes = re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]|\x1b[()][B0]|\x1b[=>]", "", output)
    return re.sub(r"[ \t]+", " ", without_escapes)


def run_interactive_dashboard(
    root: Path,
    input_text: str,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [str(installed_smairt())]
    environment = {**os.environ, "TERM": "xterm-256color", **(environment or {})}
    environment.pop("CI", None)
    environment.pop("PYTEST_CURRENT_TEST", None)
    master, slave = pty.openpty()
    fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 50, 200, 0, 0))
    process = subprocess.Popen(
        command,
        stdin=slave,
        stdout=slave,
        stderr=slave,
        text=False,
        cwd=root,
        env=environment,
    )
    os.close(slave)
    output = bytearray()
    sent = False
    deadline = time.monotonic() + 10
    while process.poll() is None and time.monotonic() < deadline:
        readable, _, _ = select.select([master], [], [], 0.1)
        if readable:
            try:
                output.extend(os.read(master, 4096))
            except OSError:
                break
        if not sent and b"Choose an action" in output:
            os.write(master, input_text.encode())
            sent = True
    if process.poll() is None:
        process.kill()
        raise AssertionError(f"interactive command timed out: {output.decode()}")
    while True:
        try:
            chunk = os.read(master, 4096)
        except OSError:
            break
        if not chunk:
            break
        output.extend(chunk)
    os.close(master)
    return subprocess.CompletedProcess(command, process.wait(), output.decode(), "")
