from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml

from smairt.models import ProjectContract, ProjectOptions, StartingPhase
from smairt.project import (
    create_management_assets,
    hpc_asset_contents,
    phase_asset_contents,
    phase_directories,
)
from smairt.scaffold import materialize_template_assets


class GenerationError(Exception):
    """Raised when a project cannot be safely generated."""


def generate_project(destination: Path, options: ProjectOptions) -> list[str]:
    """Render a complete project into a temporary sibling then rename it into place."""
    destination = destination.resolve()
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


def validate_destination(destination: Path) -> None:
    if destination.exists():
        if destination.is_dir() and not any(destination.iterdir()):
            raise GenerationError(f"Destination already exists: {destination}")
        raise GenerationError(f"Destination is not empty: {destination}")
    if not destination.parent.is_dir():
        raise GenerationError(f"Destination parent does not exist: {destination.parent}")


def _generate_into(root: Path, options: ProjectOptions) -> None:
    contract = ProjectContract.from_options(options, git_initialized=False)
    materialize_template_assets(root, contract, missing_only=False)


def _create_phase_directories(root: Path, phase: StartingPhase) -> None:
    for directory in phase_directories(phase):
        (root / directory).mkdir(parents=True)
    for relative, content in phase_asset_contents(phase).items():
        (root / relative).write_text(content)


def _create_paper_assets(root: Path) -> None:
    from smairt.project import paper_asset_contents

    for relative, content in paper_asset_contents().items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def _create_hpc_assets(root: Path, project_slug: str) -> None:
    for relative, content in hpc_asset_contents(project_slug).items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


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
    (root / "smairt.yaml").write_text(yaml.safe_dump(data, sort_keys=False))
