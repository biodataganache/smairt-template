"""One version, derived everywhere it is needed.

`project_check()` decides whether a project is current by comparing the `scaffold_version`
recorded in `smairt.yaml` to the installed `__version__`. When those two strings were
maintained by hand in separate files, bumping one and forgetting the other made every
freshly generated project fail its own check on creation. These tests make that class of
release mistake impossible to ship.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path

import yaml

from smairt import __version__
from smairt.models import ProjectContract

REPOSITORY_ROOT = Path(__file__).parents[1]


def installed_smairt() -> Path:
    return Path(sys.executable).with_name("smairt")


def test_the_contract_default_is_the_installed_version() -> None:
    """A new project records the version that made it, without a second source to update."""
    default = ProjectContract.model_fields["scaffold_version"].default
    assert default == __version__


def test_the_packaged_version_is_the_installed_version() -> None:
    """`pyproject.toml` is the only place a version number is written."""
    packaged = tomllib.loads((REPOSITORY_ROOT / "pyproject.toml").read_text())
    assert packaged["project"]["version"] == __version__


def test_no_source_file_restates_the_version_as_a_literal() -> None:
    """Every version reference derives from `__version__` rather than repeating it.

    A literal version string in the package is the defect this guards: it compiles, passes
    every other test, and silently orphans projects one release later.
    """
    offenders = []
    for path in sorted((REPOSITORY_ROOT / "src").rglob("*.py")):
        if path.name == "__init__.py" and path.parent.name == "smairt":
            continue
        if __version__ in path.read_text():
            offenders.append(path.relative_to(REPOSITORY_ROOT).as_posix())
    assert not offenders, f"version literal found in: {', '.join(offenders)}"


def test_no_release_gate_addresses_an_artifact_by_version() -> None:
    """CI and the documented gates select artifacts by kind, never by filename.

    A hardcoded `smairt-0.4.0-py3-none-any.whl` fails the build on the next bump, and the
    failure is a missing file rather than anything about the release. Three files had to be
    edited purely to carry the version forward; they now carry no version at all.
    """
    gates = (
        REPOSITORY_ROOT / ".github" / "workflows" / "ci.yml",
        REPOSITORY_ROOT / "README.md",
        REPOSITORY_ROOT / ".github" / "CONTRIBUTING.md",
    )
    for path in gates:
        contents = path.read_text()
        assert "smairt-0." not in contents, (
            f"{path.relative_to(REPOSITORY_ROOT)} addresses a build artifact by version"
        )
        assert __version__ not in contents, (
            f"{path.relative_to(REPOSITORY_ROOT)} restates the version as a literal"
        )


def test_a_freshly_generated_project_passes_its_own_check(tmp_path: Path) -> None:
    """Creation and verification must agree the moment a project exists.

    This is the end-to-end statement of the invariant. It fails if the contract default and
    the installed version ever drift, whatever the cause.
    """
    destination = tmp_path / "fresh_project"
    created = subprocess.run(
        [
            str(installed_smairt()),
            "new",
            str(destination),
            "--name",
            "Fresh Project",
            "--slug",
            "fresh_project",
            "--description",
            "A project created to verify it passes its own check.",
            "--researcher",
            "Ada Researcher",
            "--domain",
            "Computational biology",
            "--accept-license",
            "--no-git",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert created.returncode == 0, created.stderr
    contract = yaml.safe_load((destination / "smairt.yaml").read_text())
    assert contract["scaffold_version"] == __version__

    checked = subprocess.run(
        [str(installed_smairt()), "check", str(destination), "--json"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert checked.returncode == 0, checked.stdout
    payload = json.loads(checked.stdout)
    assert payload["ok"] is True, payload["issues"]
    assert payload["issues"] == []
