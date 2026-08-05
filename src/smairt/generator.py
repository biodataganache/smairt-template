from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml

from smairt.models import ProjectContract, ProjectOptions
from smairt.project import create_management_assets
from smairt.scaffold import materialize_template_assets


class GenerationError(Exception):
    """Raised when a project cannot be safely generated."""


def generate_project(destination: Path, options: ProjectOptions) -> list[str]:
    """Render a complete project into a temporary sibling then rename it into place."""
    # Made absolute before anything else looks at it, because a relative path like `.` has no
    # usable name and reports itself as its own parent — which put the temporary directory
    # *inside* the destination and made the rename impossible.
    #
    # Deliberately not `resolve()`: that follows symlinks, so a destination that is a symlink
    # would arrive here already replaced by its target and the refusal below could never fire.
    destination = absolute_destination(destination)
    validate_destination(destination)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.smairt-", dir=destination.parent)
    )
    messages: list[str] = []
    try:
        _generate_into(temporary, options)
        _write_contract(temporary, options, git_initialized=False)
        create_management_assets(temporary, options.assistant, options.license, options.researcher)
        git_initialized = False
        if options.initialize_git:
            git_initialized = _initialize_git(temporary, messages)
            if git_initialized:
                _write_contract(temporary, options, git_initialized=True)
                _stage_contract(temporary, messages)
        os.replace(temporary, destination)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return messages


def absolute_destination(destination: Path) -> Path:
    """Return an absolute, normalized path that still points at any symlink itself.

    `resolve()` cannot be used here: it follows symlinks, which would silently retarget a
    destination and defeat the refusal in `validate_destination`. The parent is resolved
    instead, so `.` and `..` in the path a researcher typed are still normalized away.
    """
    if destination.is_absolute():
        return destination
    absolute = Path.cwd() / destination
    return absolute.parent.resolve() / absolute.name


def validate_destination(destination: Path) -> None:
    """Refuse a destination that could not be created without risking existing files.

    An existing empty directory is allowed. It is the most common shape a researcher arrives
    in — make a folder, `cd` into it, run `smairt new .` — and refusing it with "Destination
    already exists" told them something they knew and nothing they could act on.

    Allowing it is safe rather than merely convenient: `os.replace` replaces an empty
    directory atomically, and the operating system itself refuses to replace a non-empty one,
    so a directory that gains a file mid-generation still cannot be overwritten.
    """
    if destination.is_symlink():
        # A symlink is never followed, because replacing it would write through to whatever it
        # points at, which may be anywhere.
        raise GenerationError(
            f"Destination is a symbolic link, which SMAIRT will not replace: {destination}"
        )
    reported = absolute_destination(destination)
    if destination.exists():
        if not destination.is_dir():
            raise GenerationError(f"Destination is a file, not a directory: {reported}")
        if any(destination.iterdir()):
            raise GenerationError(
                f"Destination already contains files, so SMAIRT will not write into it: {reported}"
            )
    if not destination.parent.is_dir():
        raise GenerationError(f"Destination parent does not exist: {reported.parent}")


def _generate_into(root: Path, options: ProjectOptions) -> None:
    contract = ProjectContract.from_options(options, git_initialized=False)
    materialize_template_assets(root, contract, missing_only=False)


def _initialize_git(root: Path, messages: list[str]) -> bool:
    if shutil.which("git") is None:
        messages.append("Git was requested but is unavailable; project files were not initialized.")
        return False
    try:
        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        messages.append(f"Git initialization failed: {error.stderr.strip()}")
        return False
    messages.append(
        "Git repository initialized and files staged. Run `git commit -m 'Initial SMAIRT project'` when ready."
    )
    return True


def _stage_contract(root: Path, messages: list[str]) -> None:
    try:
        subprocess.run(
            ["git", "add", "smairt.yaml"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        messages.append(f"Could not stage updated project metadata: {error.stderr.strip()}")


def _write_contract(root: Path, options: ProjectOptions, git_initialized: bool) -> None:
    contract = ProjectContract.from_options(options, git_initialized)
    data = contract.model_dump(mode="json", exclude_none=True)
    data.pop("conventions", None)
    # False rigor declarations are the default behavior, not four decisions the
    # researcher made. Omit the block until at least one declaration is enabled so a
    # default project's contract remains byte-for-byte stable.
    if not any(contract.rigor.model_dump().values()):
        data.pop("rigor", None)
    (root / "smairt.yaml").write_text(yaml.safe_dump(data, sort_keys=False))
