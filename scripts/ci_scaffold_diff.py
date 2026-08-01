#!/usr/bin/env python3
"""Show the scaffold blueprint product-surface diff against the target branch."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from scaffold_diff import main as print_diff

BLUEPRINT = Path("src/smairt/assets/scaffold-blueprint.yaml")


def main() -> None:
    base_ref = os.environ.get("GITHUB_BASE_REF")
    if not base_ref:
        print("Scaffold blueprint diff: no pull-request base branch; skipped.")
        return
    base = f"origin/{base_ref}"
    fetched = subprocess.run(
        ["git", "fetch", "--no-tags", "origin", base_ref],
        check=False,
        capture_output=True,
        text=True,
    )
    if fetched.returncode:
        raise SystemExit(fetched.stderr)
    shown = subprocess.run(
        ["git", "show", f"{base}:{BLUEPRINT.as_posix()}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if shown.returncode:
        print("Scaffold blueprint is new in this change.")
        return
    with tempfile.NamedTemporaryFile("w", suffix=".yaml") as previous:
        previous.write(shown.stdout)
        previous.flush()
        import sys

        sys.argv = ["scaffold_diff.py", previous.name, str(BLUEPRINT)]
        print_diff()


if __name__ == "__main__":
    main()
