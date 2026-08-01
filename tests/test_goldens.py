from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import yaml

from smairt import __version__

ROOT = Path(__file__).parents[1]
GOLDEN_ROOT = ROOT / "tests" / "fixtures" / "golden"
CASES = {
    "base-synthetic": [
        "--name",
        "Golden Synthetic Study",
        "--slug",
        "golden_synthetic_study",
        "--description",
        "A normalized synthetic-phase golden project.",
        "--researcher",
        "Ada Synthetic",
        "--domain",
        "Computational biology",
        "--phase",
        "synthetic",
        "--assistant",
        "opencode",
    ],
    "real-with-paper": [
        "--name",
        "Golden Paper Study",
        "--slug",
        "golden_paper_study",
        "--description",
        "A normalized real-data Paper golden project.",
        "--researcher",
        "Grace Paper",
        "--domain",
        "Bioinformatics",
        "--phase",
        "real",
        "--assistant",
        "claude-code",
        "--paper",
    ],
    "downloaded-with-hpc": [
        "--name",
        "Golden HPC Study",
        "--slug",
        "golden_hpc_study",
        "--description",
        "A normalized downloaded-data HPC golden project.",
        "--researcher",
        "Katherine Cluster",
        "--domain",
        "Data science",
        "--phase",
        "downloaded",
        "--assistant",
        "opencode",
        "--hpc",
    ],
}


def test_installed_command_matches_full_normalized_golden_projects(tmp_path: Path) -> None:
    smairt = Path(sys.executable).with_name("smairt")
    for case, case_arguments in CASES.items():
        destination = tmp_path / case
        created = subprocess.run(
            [
                str(smairt),
                "new",
                str(destination),
                *case_arguments,
                "--license",
                "MIT",
                "--accept-license",
                "--no-git",
            ],
            check=False,
            capture_output=True,
            text=True,
            env={**os.environ, "XDG_DATA_HOME": str(tmp_path / ".local")},
        )
        assert created.returncode == 0, created.stderr
        contract = yaml.safe_load((destination / "smairt.yaml").read_text())
        assert contract["scaffold_version"] == __version__
        normalize(destination, contract["license_year"])
        assert tree(destination) == tree(GOLDEN_ROOT / case)


def normalize(root: Path, year: int) -> None:
    contract = root / "smairt.yaml"
    contract.write_text(
        contract.read_text().replace(f"license_year: {year}", "license_year: <YEAR>")
    )
    license_path = root / "LICENSE"
    license_path.write_text(license_path.read_text().replace(str(year), "<YEAR>"))


def tree(root: Path) -> dict[str, bytes | None]:
    return {
        path.relative_to(root).as_posix(): None if path.is_dir() else path.read_bytes()
        for path in sorted(root.rglob("*"))
    }
