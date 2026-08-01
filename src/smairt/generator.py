from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from smairt.models import ProjectContract, ProjectOptions, StartingPhase
from smairt.project import create_management_assets, hpc_asset_contents, phase_directories

MANIFEST_PATH = Path(".smairt") / "managed-files.yaml"


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
        _write_manifest(temporary, options)
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
    templates = Path(__file__).parent / "assets" / "scaffold"
    environment = Environment(
        loader=FileSystemLoader(str(templates)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )
    context: dict[str, Any] = {"project": options.project, "researcher": options.researcher}
    for path in templates.rglob("*"):
        if path.is_dir():
            continue
        relative_path = Path(str(path.relative_to(templates)))
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(environment.get_template(relative_path.as_posix()).render(context))

    _create_phase_directories(root, options.starting_phase)
    if options.paper:
        _create_paper_assets(root)
    if options.hpc:
        _create_hpc_assets(root, options.project.slug)


def _create_phase_directories(root: Path, phase: StartingPhase) -> None:
    for directory in phase_directories(phase):
        (root / directory).mkdir(parents=True)


def _create_paper_assets(root: Path) -> None:
    (root / "paper" / "analysis").mkdir(parents=True)
    (root / "paper" / "README.md").write_text(
        "# Paper Workspace\n\n"
        "Keep publication-focused analyses in `paper/analysis/` so they remain "
        "separate from exploratory `analysis/` work.\n"
    )
    (root / "paper" / "outline.md").write_text("# Paper Outline\n")


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


def _write_manifest(root: Path, options: ProjectOptions) -> None:
    managed: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "smairt.yaml":
            managed[path.relative_to(root).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    manifest = root / MANIFEST_PATH
    manifest.parent.mkdir()
    manifest.write_text(
        yaml.safe_dump(
            {"version": 1, "files": managed, "assets": _managed_assets(options)},
            sort_keys=True,
        )
    )


def _managed_assets(options: ProjectOptions) -> dict[str, str]:
    templates = Path(__file__).parent / "assets" / "scaffold"
    environment = Environment(
        loader=FileSystemLoader(str(templates)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )
    context: dict[str, Any] = {"project": options.project, "researcher": options.researcher}
    assets: dict[str, str] = {}
    for path in templates.rglob("*"):
        if path.is_file():
            relative = path.relative_to(templates).as_posix()
            assets[relative] = environment.get_template(relative).render(context)
    assets["LICENSE"] = _license_text(options)
    alias = _assistant_alias(options)
    if alias is not None:
        assets[alias] = (
            "# SMAIRT AI Context\n\nRead `prompts/AI_CONTEXT.md` before working in this project.\n"
        )
    if options.paper:
        assets.update(
            {
                "paper/README.md": "# Paper Workspace\n\nKeep publication-focused analyses in `paper/analysis/` so they remain separate from exploratory `analysis/` work.\n",
                "paper/outline.md": "# Paper Outline\n",
            }
        )
    if options.hpc:
        assets.update(hpc_asset_contents(options.project.slug))
    return assets


def _license_text(options: ProjectOptions) -> str:
    from smairt.project import _render_license

    return _render_license(options.license, options.researcher.name)


def _assistant_alias(options: ProjectOptions) -> str | None:
    from smairt.project import ASSISTANT_ALIASES

    return ASSISTANT_ALIASES.get(options.assistant)
