from __future__ import annotations

from pathlib import Path

from smairt.scaffold import diff_blueprints, load_blueprint


def test_scaffold_blueprint_is_a_complete_readable_asset_declaration() -> None:
    blueprint = load_blueprint()

    ids = [asset.id for asset in blueprint.assets]
    paths = [asset.path for asset in blueprint.assets]
    assert len(ids) == len(set(ids))
    assert len(paths) == len(set(paths))
    assert {asset.condition for asset in blueprint.assets} == {"always", "paper", "hpc"}
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
