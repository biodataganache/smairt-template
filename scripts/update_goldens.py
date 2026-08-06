#!/usr/bin/env python3
"""Regenerate normalized full-text golden SMAIRT projects through the installed command."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
GOLDEN_ROOT = ROOT / "tests" / "fixtures" / "golden"
CASES = {
    "base-synthetic": {
        "name": "Golden Synthetic Study",
        "slug": "golden_synthetic_study",
        "description": "A normalized synthetic-phase golden project.",
        "researcher": "Ada Synthetic",
        "domain": "Computational biology",
        "phase": "synthetic",
        "assistant": "opencode",
        "flags": [],
    },
    "real-with-paper": {
        "name": "Golden Paper Study",
        "slug": "golden_paper_study",
        "description": "A normalized real-data Paper golden project.",
        "researcher": "Grace Paper",
        "domain": "Bioinformatics",
        "phase": "real",
        "assistant": "claude-code",
        "flags": ["--paper"],
    },
    "downloaded-with-hpc": {
        "name": "Golden HPC Study",
        "slug": "golden_hpc_study",
        "description": "A normalized downloaded-data HPC golden project.",
        "researcher": "Katherine Cluster",
        "domain": "Data science",
        "phase": "downloaded",
        "assistant": "opencode",
        "flags": ["--hpc"],
    },
}


def main() -> None:
    command = Path(sys.executable).with_name("smairt")
    GOLDEN_ROOT.mkdir(parents=True, exist_ok=True)
    # Prove the installed command can generate a project before deleting the fixtures it is
    # about to replace. A blueprint the package cannot parse made every generation fail, and
    # because each case removed its golden first, the run left no fixtures behind at all.
    verified = subprocess.run(
        [str(command), "--version"],
        check=False,
        capture_output=True,
        text=True,
    )
    if verified.returncode:
        raise SystemExit(
            "Refusing to replace the goldens: the installed command is not usable.\n"
            + (verified.stderr or verified.stdout)
        )
    for case, options in CASES.items():
        destination = GOLDEN_ROOT / case
        shutil.rmtree(destination, ignore_errors=True)
        arguments = [
            str(command),
            "new",
            str(destination),
            "--name",
            str(options["name"]),
            "--slug",
            str(options["slug"]),
            "--description",
            str(options["description"]),
            "--researcher",
            str(options["researcher"]),
            "--domain",
            str(options["domain"]),
            "--phase",
            str(options["phase"]),
            "--assistant",
            str(options["assistant"]),
            "--license",
            "MIT",
            "--accept-license",
            "--no-git",
            *list(options["flags"]),
        ]
        result = subprocess.run(
            arguments,
            check=False,
            capture_output=True,
            text=True,
            env={**os.environ, "XDG_DATA_HOME": str(GOLDEN_ROOT / ".local")},
        )
        if result.returncode:
            raise SystemExit(result.stderr or result.stdout)
        normalize(destination)
    shutil.rmtree(GOLDEN_ROOT / ".local", ignore_errors=True)


def normalize(root: Path) -> None:
    contract = root / "smairt.yaml"
    text = contract.read_text()
    for year in range(2000, 10000):
        marker = f"license_year: {year}"
        if marker in text:
            text = text.replace(marker, "license_year: <YEAR>")
            (root / "LICENSE").write_text(
                (root / "LICENSE").read_text().replace(str(year), "<YEAR>")
            )
            break
    contract.write_text(text)


if __name__ == "__main__":
    main()
