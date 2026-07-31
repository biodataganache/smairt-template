from __future__ import annotations

import os
import pty
import select
import subprocess
import sys
import time
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
    assert result.stdout.strip() == "smairt 0.1.0"


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
            "--no-git",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Slug must start with a lowercase letter" in result.stderr
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
        "scaffold_version": "0.1.0",
        "project": {
            "name": "Protein Study",
            "slug": "protein_study",
            "description": "A reproducible protein study.",
            "domain": "Computational biology",
        },
        "people": {"researcher": {"name": "Ada Researcher"}},
        "assistant": "opencode",
        "starting_phase": "synthetic",
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


def test_downloaded_project_omits_synthetic_phase_directories(tmp_path: Path) -> None:
    destination = tmp_path / "downloaded"

    result = create_project(destination, phase="downloaded")

    assert result.returncode == 0, result.stderr
    assert paths(destination) >= {
        "data/downloaded",
        "data/real",
        "experiments/02_downloaded",
        "experiments/03_real_data",
    }
    assert "data/synthetic" not in paths(destination)
    assert "experiments/01_synthetic" not in paths(destination)


def test_real_project_omits_earlier_phase_directories(tmp_path: Path) -> None:
    destination = tmp_path / "real"

    result = create_project(destination, phase="real")

    assert result.returncode == 0, result.stderr
    assert paths(destination) >= {"data/real", "experiments/03_real_data"}
    assert "data/synthetic" not in paths(destination)
    assert "data/downloaded" not in paths(destination)
    assert "experiments/01_synthetic" not in paths(destination)
    assert "experiments/02_downloaded" not in paths(destination)


def test_paper_and_hpc_are_independent_additive_capabilities(tmp_path: Path) -> None:
    paper_only = tmp_path / "paper"
    hpc_only = tmp_path / "hpc"

    paper_result = create_project(paper_only, paper=True)
    hpc_result = create_project(hpc_only, hpc=True)

    assert paper_result.returncode == 0, paper_result.stderr
    assert "paper/analysis" in paths(paper_only)
    assert "hpc" not in paths(paper_only)
    assert hpc_result.returncode == 0, hpc_result.stderr
    assert "hpc" in paths(hpc_only)
    assert "hpc/slurm_job.sh" in paths(hpc_only)
    assert "paper" not in paths(hpc_only)
    assert "{{" not in (hpc_only / "hpc" / "slurm_job.sh").read_text()


def test_generated_project_keeps_managed_bookkeeping_local(tmp_path: Path) -> None:
    destination = tmp_path / "managed"

    result = create_project(destination)

    assert result.returncode == 0, result.stderr
    manifest = yaml.safe_load((destination / ".smairt" / "managed-files.yaml").read_text())
    assert manifest["version"] == 1
    assert "README.md" in manifest["files"]
    assert "smairt.yaml" not in manifest["files"]
    assert ".smairt/" in (destination / ".gitignore").read_text()


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


def test_optional_email_is_omitted_and_scaffold_uses_log_first_guidance(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "no-email"

    result = create_project(destination)

    assert result.returncode == 0, result.stderr
    metadata = yaml.safe_load((destination / "smairt.yaml").read_text())
    assert "email" not in metadata["people"]["researcher"]
    assert not list(destination.rglob("*browser*"))
    assert not list(destination.rglob("*session_log*"))
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
    ]
    command.append("--git" if initialize_git else "--no-git")
    if paper:
        command.append("--paper")
    if hpc:
        command.append("--hpc")
    environment = None if path is None else {"PATH": path}
    return subprocess.run(
        command, check=False, capture_output=True, text=True, env=environment
    )


def paths(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*")}


def test_interactive_wizard_creates_a_project_from_a_real_input_stream(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "guided-project"

    result = run_interactive_new(
        "\n".join(
            [
                str(destination),
                "Guided Protein Study",
                "guided_protein_study",
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
    assert "Step 1 of 15" in result.stdout
    assert "Step 15 of 15" in result.stdout
    assert "Final review" in result.stdout
    assert "Created SMAIRT project at" in result.stdout
    assert "Creating your SMAIRT project" not in result.stdout
    metadata = yaml.safe_load((destination / "smairt.yaml").read_text())
    assert metadata["project"] == {
        "name": "Guided Protein Study",
        "slug": "guided_protein_study",
        "description": "A project created through the guided setup.",
        "domain": "Computational biology",
    }
    assert metadata["assistant"] == "opencode"
    assert metadata["starting_phase"] == "synthetic"
    assert metadata["license"] == "MIT"
    assert metadata["git_requested"] is False
    assert metadata["capabilities"] == {
        "paper": {"state": "enabled"},
        "hpc": {"state": "enabled"},
    }


def test_interactive_wizard_keeps_answers_when_going_back_and_edits_review_answers(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "edited-project"

    result = run_interactive_new(
        "\n".join(
            [
                str(destination),
                "Original Name",
                "original_name",
                ":back",
                "Original Name",
                "original_name",
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
                "2",
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
    assert metadata["project"]["slug"] == "original_name"
    assert metadata["project"]["description"] == "A retained description."


def test_interactive_wizard_validates_destination_before_final_review(tmp_path: Path) -> None:
    destination = tmp_path / "occupied"
    destination.mkdir()
    preserved = destination / "notes.txt"
    preserved.write_text("keep this")

    result = run_interactive_new(f"{destination}\n:cancel\n")

    assert result.returncode == 1
    assert "Destination is not empty" in result.stdout
    assert preserved.read_text() == "keep this"
    assert not (destination / "smairt.yaml").exists()


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
    return "\n".join(
        [
            str(destination),
            "Test Project",
            "test_project",
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
    ) + "\n"


def run_interactive_new(input_text: str) -> subprocess.CompletedProcess[str]:
    command = [str(installed_smairt()), "new"]
    master, slave = pty.openpty()
    process = subprocess.Popen(
        command,
        stdin=slave,
        stdout=slave,
        stderr=slave,
        text=False,
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
        if not sent and b"Destination" in output:
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
