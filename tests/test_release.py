from __future__ import annotations

import subprocess
import sys
import tarfile
from pathlib import Path
from zipfile import ZipFile

from smairt import __version__

REPOSITORY_ROOT = Path(__file__).parents[1]


def test_built_wheel_and_sdist_install_into_clean_environments_and_create_projects(
    tmp_path: Path,
) -> None:
    distribution_directory = tmp_path / "dist"
    built = subprocess.run(
        ["uv", "build", "--out-dir", str(distribution_directory)],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert built.returncode == 0, built.stderr
    artifacts = sorted(
        [
            *distribution_directory.glob("smairt-*.whl"),
            *distribution_directory.glob("smairt-*.tar.gz"),
        ]
    )
    assert len(artifacts) == 2
    wheel = next(artifact for artifact in artifacts if artifact.suffix == ".whl")
    source_distribution = next(artifact for artifact in artifacts if artifact.suffix == ".gz")
    with ZipFile(wheel) as archive:
        wheel_files = set(archive.namelist())
    with tarfile.open(source_distribution) as archive:
        source_files = {
            member.name.split("/", 1)[1] for member in archive.getmembers() if "/" in member.name
        }
    assert "smairt/assets/scaffold/prompts/AI_CONTEXT.md" in wheel_files
    assert "smairt/assets/scaffold-blueprint.yaml" in wheel_files
    assert "smairt/assets/scaffold/scripts/new_iteration.py" in wheel_files
    assert "smairt/assets/scaffold/scripts/new_utility.py" in wheel_files
    assert "smairt/assets/scaffold/scripts/generate_manifest.py" in wheel_files
    assert "smairt/assets/scaffold/scripts/monitor_template.py" in wheel_files
    assert "smairt/assets/scaffold/scripts/shared/logging.py" in wheel_files
    assert f"smairt-{__version__}.dist-info/METADATA" in wheel_files
    assert any(path.endswith(".dist-info/licenses/LICENSE") for path in wheel_files)
    # A gitignored file is invisible in review but still on disk for the build to copy, so
    # operating-system metadata must be excluded by the build rather than by tidiness.
    assert not [path for path in wheel_files if ".DS_Store" in path]
    assert not [path for path in source_files if ".DS_Store" in path]
    assert {
        "LICENSE",
        "README.md",
    } <= source_files
    protected_workspace = tmp_path / "protected-workspace"
    protected_workspace.mkdir()
    sentinel = protected_workspace / "research-notes.txt"
    sentinel.write_text("do not delete\n")
    unsafe_workspace = subprocess.run(
        [
            sys.executable,
            "scripts/smoke_install.py",
            "--artifact",
            str(wheel),
            "--workspace",
            str(protected_workspace),
        ],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert unsafe_workspace.returncode == 1
    assert "must be absent or empty" in unsafe_workspace.stderr
    assert sentinel.read_text() == "do not delete\n"
    # Exercised the way CI addresses artifacts: by kind, so no caller carries the version.
    for kind, artifact in (("wheel", wheel), ("sdist", source_distribution)):
        workspace = tmp_path / f"smoke-{kind}"
        if kind == "wheel":
            workspace.mkdir()
        smoke = subprocess.run(
            [
                sys.executable,
                "scripts/smoke_install.py",
                "--artifact",
                str(distribution_directory),
                "--kind",
                kind,
                "--workspace",
                str(workspace),
            ],
            cwd=REPOSITORY_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        assert smoke.returncode == 0, f"{artifact.name}:\n{smoke.stdout}\n{smoke.stderr}"
