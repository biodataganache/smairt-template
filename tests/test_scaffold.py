from __future__ import annotations

import re
from pathlib import Path

from smairt.scaffold import diff_blueprints, load_blueprint


def test_scaffold_blueprint_is_a_complete_readable_asset_declaration() -> None:
    blueprint = load_blueprint()

    ids = [asset.id for asset in blueprint.assets]
    paths = [asset.path for asset in blueprint.assets]
    assert len(ids) == len(set(ids))
    assert len(paths) == len(set(paths))
    assert {asset.condition for asset in blueprint.assets} == {"always", "paper", "hpc", "rigor"}
    assert {asset.ownership for asset in blueprint.assets} == {
        "tool-guidance",
        "editable-starter",
        "researcher-work",
    }
    assert {asset.path for asset in blueprint.assets} >= {
        "README.md",
        "smairt.yaml",
        "data/synthetic",
        "data/downloaded",
        "data/real",
        "experiments/01_synthetic",
        "experiments/02_downloaded",
        "experiments/03_real_data",
        "analysis/RIGOR.md",
        "FINAL_MANIFEST.md",
        "hpc/templates/slurm_basic.sh",
    }


def test_every_blueprint_file_source_exists_in_the_installed_package() -> None:
    blueprint = load_blueprint()
    source_root = Path(__file__).parents[1] / "src" / "smairt" / "assets" / "scaffold"

    missing = []
    for asset in blueprint.assets:
        if asset.kind != "file" or asset.source in {"contract", "license", "assistant-pointer"}:
            continue
        assert asset.source is not None
        if not (source_root / asset.source).is_file():
            missing.append(asset.source)

    assert missing == []

    declared_directories = {asset.path for asset in blueprint.assets if asset.kind == "directory"}
    undeclared_parents = []
    for asset in blueprint.assets:
        if asset.path.startswith("$") or "/" not in asset.path:
            continue
        parent = str(Path(asset.path).parent).replace("\\", "/")
        if parent not in declared_directories:
            undeclared_parents.append(f"{asset.path} -> {parent}")
    assert undeclared_parents == []


def test_blueprint_diff_calls_out_product_surface_changes() -> None:
    previous = {
        "assets": [
            {
                "id": "readme",
                "path": "README.md",
                "ownership": "tool-guidance",
                "condition": "always",
            },
            {
                "id": "outline",
                "path": "paper/outline.md",
                "ownership": "editable-starter",
                "condition": "paper",
            },
            {
                "id": "removed",
                "path": "old.md",
                "ownership": "tool-guidance",
                "condition": "always",
            },
        ]
    }
    current = {
        "assets": [
            {
                "id": "readme",
                "path": "GUIDE.md",
                "ownership": "editable-starter",
                "condition": "always",
            },
            {
                "id": "outline",
                "path": "paper/outline.md",
                "ownership": "editable-starter",
                "condition": "always",
            },
            {"id": "added", "path": "new.md", "ownership": "tool-guidance", "condition": "always"},
        ]
    }

    assert diff_blueprints(previous, current) == {
        "added": ["new.md"],
        "removed": ["old.md"],
        "renamed": ["README.md -> GUIDE.md"],
        "ownership_changed": ["GUIDE.md: tool-guidance -> editable-starter"],
        "condition_changed": ["paper/outline.md: paper -> always"],
    }


def test_every_declared_directory_arrives_with_something_in_it() -> None:
    """An empty directory does not survive Git, so it cannot be part of a shared record.

    `scripts/utilities` shipped empty. A researcher who committed a new project pushed a tree
    without it, and the golden fixtures silently lost it too, so the comparison that exists to
    catch drift passed locally and failed on a fresh clone. Every other declared directory
    either carries its own README or holds declared children that do.
    """
    blueprint = load_blueprint()
    declared = {asset.path for asset in blueprint.assets}
    empty: list[str] = []
    for asset in blueprint.assets:
        if asset.kind != "directory":
            continue
        if any(other.startswith(f"{asset.path}/") for other in declared):
            continue
        empty.append(asset.path)
    assert not empty, (
        "declared directories that ship with no content and cannot survive Git:\n"
        + "\n".join(empty)
    )


def test_every_file_the_helpers_create_is_declared() -> None:
    """The blueprint is the authoritative declaration of generated paths (ADR 0001).

    `analysis/RUN_HISTORY.md` was created by `scripts/shared/iterations.py` on the first run
    and declared nowhere, so the record the scaffold calls part of the evidence was invisible
    to check, inspect, and upgrade. A file that appears in a project without the blueprint
    knowing about it is a second, quieter definition of what a project contains.
    """
    blueprint = load_blueprint()
    declared = {asset.path for asset in blueprint.assets}
    helpers = Path(__file__).parents[1] / "src" / "smairt" / "assets" / "scaffold" / "scripts"
    written = re.findall(
        r'root / "(\w+)" / "([\w.]+\.md)"',
        "\n".join(path.read_text() for path in sorted(helpers.rglob("*.py"))),
    )
    assert written, "expected to find helper-created project files to check"
    undeclared = sorted(
        f"{directory}/{name}"
        for directory, name in written
        if f"{directory}/{name}" not in declared
    )
    assert not undeclared, (
        "helpers create project files the scaffold blueprint does not declare:\n"
        + "\n".join(undeclared)
    )


def test_the_blueprint_parses_as_the_package_reads_it() -> None:
    """A blueprint the package cannot load is worse than a wrong one.

    An unquoted comma inside a `purpose` split one flow mapping into extra keys, so
    `load_blueprint()` raised and every generation failed. Because the golden updater removed
    each fixture before generating its replacement, one malformed line deleted all three
    fixtures. This asserts the declaration is loadable at all, ahead of what it says.
    """
    blueprint = load_blueprint()

    assert blueprint.assets
    for asset in blueprint.assets:
        assert asset.path
        assert asset.purpose.endswith("."), f"{asset.path}: purpose is not a sentence"
        assert asset.kind in {"file", "directory"}
