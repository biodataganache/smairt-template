from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)


def resolve_artifact(artifact: Path, kind: str | None) -> Path:
    """Return the artifact to install, discovering it by kind when given a directory.

    Callers name a kind rather than a filename so that no caller carries the version in a
    path. A hardcoded `smairt-0.3.0-py3-none-any.whl` breaks the build on the next bump,
    which is a release failure caused entirely by how the artifact was addressed.
    """
    if artifact.is_file():
        return artifact.resolve()
    if not artifact.is_dir():
        raise SystemExit(f"Artifact does not exist: {artifact}")
    if kind is None:
        raise SystemExit(f"--artifact is a directory, so --kind is required: {artifact}")
    suffix = "*.whl" if kind == "wheel" else "*.tar.gz"
    matches = sorted(artifact.glob(suffix))
    if not matches:
        raise SystemExit(f"No {kind} found in {artifact}")
    if len(matches) > 1:
        names = ", ".join(match.name for match in matches)
        raise SystemExit(f"Expected exactly one {kind} in {artifact}, found: {names}")
    return matches[0].resolve()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install a release artifact and smoke-test its public command."
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        required=True,
        help="Built wheel or source distribution, or the directory holding them.",
    )
    parser.add_argument(
        "--kind",
        choices=("wheel", "sdist"),
        help="Which artifact to select when --artifact names a directory.",
    )
    parser.add_argument(
        "--workspace", type=Path, required=True, help="Empty directory for the isolated smoke test."
    )
    arguments = parser.parse_args()
    artifact = resolve_artifact(arguments.artifact, arguments.kind)
    workspace = arguments.workspace.resolve()
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
            "--accept-license",
            "--paper",
            "--hpc",
            "--no-git",
        ]
    )
    if created.returncode:
        raise SystemExit(created.stderr)
    for helper in ("new_iteration.py", "new_track.py", "select_result.py", "new_utility.py"):
        helped = run([str(python), f"scripts/{helper}", "--help"], cwd=destination)
        if helped.returncode:
            raise SystemExit(helped.stderr or helped.stdout)
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
