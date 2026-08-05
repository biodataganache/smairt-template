from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Literal, Mapping

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

AssetKind = Literal["directory", "file"]
AssetOwnership = Literal[
    "tool-guidance", "editable-starter", "researcher-work", "historical-reference"
]
AssetCondition = Literal["always", "paper", "hpc", "rigor"]


class ScaffoldConflict(Exception):
    """Raised when the project on disk cannot hold the scaffold the contract asks for.

    Distinct from the blueprint's own validation errors: those mean the package is
    misbuilt, which no researcher can act on, while this one names a file in the
    researcher's own project that they can move or rename.
    """


class ScaffoldAsset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    path: str
    kind: AssetKind
    purpose: str
    ownership: AssetOwnership
    condition: AssetCondition
    source: str | None = None

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        path = PurePosixPath(value)
        if path.is_absolute() or ".." in path.parts or value in {"", "."}:
            raise ValueError("scaffold asset paths must be safe relative paths")
        return value

    @model_validator(mode="after")
    def validate_source(self) -> ScaffoldAsset:
        if self.kind == "file" and self.source is None:
            raise ValueError("file assets require a source")
        if self.kind == "directory" and self.source is not None:
            raise ValueError("directory assets cannot define a source")
        return self


class ScaffoldBlueprint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    blueprint_version: int
    assets: list[ScaffoldAsset]

    @model_validator(mode="after")
    def validate_unique_identity_and_paths(self) -> ScaffoldBlueprint:
        ids = [asset.id for asset in self.assets]
        paths = [asset.path for asset in self.assets]
        if len(ids) != len(set(ids)):
            raise ValueError("scaffold asset ids must be unique")
        if len(paths) != len(set(paths)):
            raise ValueError("scaffold asset paths must be unique")
        return self


def load_blueprint() -> ScaffoldBlueprint:
    path = Path(__file__).parent / "assets" / "scaffold-blueprint.yaml"
    return ScaffoldBlueprint.model_validate(yaml.safe_load(path.read_text()))


ASSISTANT_POINTERS = {
    "zoo-code": "ZOO.md",
    "claude-code": "CLAUDE.md",
    "opencode": "AGENTS.md",
    "codex": "AGENTS.md",
    "pi": "AGENTS.md",
    "cursor": ".cursor/rules/smairt.mdc",
}


def active_assets(contract: object, *, include_inactive: bool = False) -> list[ScaffoldAsset]:
    capabilities = getattr(contract, "capabilities")

    def enabled(condition: AssetCondition) -> bool:
        if condition == "always":
            return True
        if condition == "rigor":
            return any(getattr(contract, "rigor").model_dump().values())
        state = capabilities[condition].state.value
        return state == "enabled" or (include_inactive and state == "inactive")

    return [asset for asset in load_blueprint().assets if enabled(asset.condition)]


def asset_path(asset: ScaffoldAsset, contract: object) -> str:
    if asset.path == "$assistant_pointer":
        return ASSISTANT_POINTERS[getattr(contract, "assistant").value]
    return asset.path


def asset_ownership(contract: object, *, include_inactive: bool = False) -> dict[str, str]:
    return {
        asset_path(asset, contract): asset.ownership
        for asset in active_assets(contract, include_inactive=include_inactive)
    }


def render_template_assets(contract: object, *, include_inactive: bool = False) -> dict[str, str]:
    templates = Path(__file__).parent / "assets" / "scaffold"
    environment = Environment(
        loader=FileSystemLoader(str(templates)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )
    people = getattr(contract, "people")
    context = {
        "project": getattr(contract, "project"),
        "researcher": people["researcher"],
        "rigor": getattr(contract, "rigor"),
    }
    rendered: dict[str, str] = {}
    for asset in active_assets(contract, include_inactive=include_inactive):
        if asset.kind != "file" or asset.source in {"contract", "license", "assistant-pointer"}:
            continue
        assert asset.source is not None
        source = templates / asset.source
        rendered[asset_path(asset, contract)] = (
            source.read_text()
            if source.suffix == ".py"
            else environment.get_template(asset.source).render(context)
        )
    return rendered


def materialize_template_assets(
    root: Path,
    contract: object,
    *,
    include_inactive: bool = False,
    missing_only: bool = True,
) -> None:
    for asset in active_assets(contract, include_inactive=include_inactive):
        path = root / asset_path(asset, contract)
        if asset.kind == "directory":
            if path.exists() and not path.is_dir():
                raise ScaffoldConflict(
                    f"SMAIRT needs {asset_path(asset, contract)}/ to be a directory, but a "
                    f"file exists there. Move or rename that file, then try again."
                )
            path.mkdir(parents=True, exist_ok=True)
    for relative, content in render_template_assets(
        contract, include_inactive=include_inactive
    ).items():
        path = root / relative
        if missing_only and path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def diff_blueprints(
    previous: Mapping[str, object], current: Mapping[str, object]
) -> dict[str, list[str]]:
    before = _entries_by_id(previous)
    after = _entries_by_id(current)
    before_ids = set(before)
    after_ids = set(after)
    shared = sorted(before_ids & after_ids)
    return {
        "added": sorted(str(after[item]["path"]) for item in after_ids - before_ids),
        "removed": sorted(str(before[item]["path"]) for item in before_ids - after_ids),
        "renamed": [
            f"{before[item]['path']} -> {after[item]['path']}"
            for item in shared
            if before[item]["path"] != after[item]["path"]
        ],
        "ownership_changed": [
            f"{after[item]['path']}: {before[item]['ownership']} -> {after[item]['ownership']}"
            for item in shared
            if before[item]["ownership"] != after[item]["ownership"]
        ],
        "condition_changed": [
            f"{after[item]['path']}: {before[item]['condition']} -> {after[item]['condition']}"
            for item in shared
            if before[item]["condition"] != after[item]["condition"]
        ],
    }


def _entries_by_id(data: Mapping[str, object]) -> dict[str, dict[str, str]]:
    raw = data.get("assets")
    if not isinstance(raw, list):
        raise ValueError("blueprint data must contain an assets list")
    result: dict[str, dict[str, str]] = {}
    for entry in raw:
        if not isinstance(entry, dict):
            raise ValueError("blueprint assets must be mappings")
        required = ("id", "path", "ownership", "condition")
        if not all(isinstance(entry.get(key), str) for key in required):
            raise ValueError("blueprint diff entries require id, path, ownership, and condition")
        result[str(entry["id"])] = {key: str(entry[key]) for key in required}
    return result
