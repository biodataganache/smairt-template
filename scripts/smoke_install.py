from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install a release artifact and smoke-test its public command."
    )
    parser.add_argument(
        "--artifact", type=Path, required=True, help="Built wheel or source distribution."
    )
    parser.add_argument(
        "--workspace", type=Path, required=True, help="Empty directory for the isolated smoke test."
    )
    arguments = parser.parse_args()
    artifact = arguments.artifact.resolve()
    workspace = arguments.workspace.resolve()
    if not artifact.is_file():
        raise SystemExit(f"Artifact does not exist: {artifact}")
    if workspace.exists() and (not workspace.is_dir() or any(workspace.iterdir())):
        raise SystemExit(f"Workspace must be absent or empty: {workspace}")
    workspace.mkdir(parents=True, exist_ok=True)
    environment = workspace / "environment"
    created = run([sys.executable, "-m", "venv", str(environment)])
    if created.returncode:
        raise SystemExit(created.stderr)
    python = environment / "bin" / "python"
    installed = run([str(python), "-m", "pip", "install", str(artifact)])
    if installed.returncode:
        raise SystemExit(installed.stderr)
    smairt = environment / "bin" / "smairt"
    destination = workspace / "representative-project"
    created = run(
        [
            str(smairt),
            "new",
            str(destination),
            "--name",
            "Release Smoke Project",
            "--slug",
            "release_smoke_project",
            "--description",
            "A representative isolated release smoke project.",
            "--researcher",
            "Release Tester",
            "--domain",
            "Not sure yet",
            "--phase",
            "downloaded",
            "--assistant",
            "opencode",
            "--paper",
            "--hpc",
            "--no-git",
        ]
    )
    if created.returncode:
        raise SystemExit(created.stderr)
    checked = run([str(smairt), "check", str(destination), "--json"])
    if checked.returncode:
        raise SystemExit(checked.stderr or checked.stdout)
    try:
        check_payload = json.loads(checked.stdout)
    except json.JSONDecodeError as error:
        raise SystemExit(f"Project Check did not return JSON: {error}") from error
    if check_payload != {"issues": [], "ok": True, "repairs": []}:
        raise SystemExit(f"Unexpected Project Check result: {checked.stdout}")


if __name__ == "__main__":
    main()
