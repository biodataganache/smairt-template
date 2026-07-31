from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

REPOSITORY_ROOT = Path(__file__).parents[1]


def test_legacy_cookiecutter_generates_canonical_project(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    canonical_destination = tmp_path / "canonical"
    canonical_result = subprocess.run(
        [
            str(Path(sys.executable).with_name("smairt")),
            "new",
            str(canonical_destination),
            "--name",
            "Legacy Project",
            "--slug",
            "legacy_project",
            "--description",
            "Generated through compatibility.",
            "--researcher",
            "Ada Researcher",
            "--domain",
            "Computational biology",
            "--phase",
            "downloaded",
            "--assistant",
            "opencode",
            "--paper",
            "--hpc",
            "--no-git",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    result = subprocess.run(
        [
            "cookiecutter",
            str(REPOSITORY_ROOT),
            "--no-input",
            "--output-dir",
            str(output_dir),
            "project_name=Legacy Project",
            "project_slug=legacy_project",
            "author_name=Ada Researcher",
            "description=Generated through compatibility.",
            "domain=Computational biology",
            "starting_phase=downloaded",
            "assistant=opencode",
            "paper=yes",
            "hpc=yes",
        ],
        check=False,
        capture_output=True,
        text=True,
        env={"PATH": str(Path(sys.executable).parent)},
    )

    assert canonical_result.returncode == 0, canonical_result.stderr
    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    destination = output_dir / "legacy_project"
    assert "Legacy Cookiecutter compatibility path" in result.stdout
    assert not (destination / "LEGACY_COOKIECUTTER.md").exists()
    assert (destination / "smairt.yaml").is_file()
    assert (destination / "paper" / "analysis").is_dir()
    assert (destination / "hpc" / "slurm_job.sh").is_file()
    assert not (destination / "data" / "synthetic").exists()
    assert not (destination / "experiments" / "01_synthetic").exists()
    metadata = yaml.safe_load((destination / "smairt.yaml").read_text())
    assert metadata["project"]["slug"] == "legacy_project"
    assert metadata["capabilities"] == {
        "paper": {"state": "enabled"},
        "hpc": {"state": "enabled"},
    }
    assert file_contents(canonical_destination) == file_contents(destination)


def file_contents(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }
