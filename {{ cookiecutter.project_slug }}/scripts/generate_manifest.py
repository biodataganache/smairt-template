#!/usr/bin/env python
"""Generate FINAL_MANIFEST.md from paper-driven analysis directories."""

import re
from datetime import datetime
from pathlib import Path


PROJECT_NAME = "{{ cookiecutter.project_name }}"


def is_analysis_dir(path):
    """Return whether a directory has the paper-driven analysis structure."""
    return path.is_dir() and (
        (path / "iterations").is_dir() or (path / "final").is_dir()
    )


def discover_analyses(analysis_root):
    """Discover canonical flat analyses and legacy nested analyses."""
    analyses = []

    for child in sorted(analysis_root.iterdir()):
        if not child.is_dir() or child.name.startswith("XX_"):
            continue

        if is_analysis_dir(child):
            analyses.append(child)
            continue

        for nested in sorted(child.iterdir()):
            if is_analysis_dir(nested):
                analyses.append(nested)

    return analyses


def selected_iteration(selected_file):
    """Read the selected iteration identifier from SELECTED.md."""
    match = re.search(
        r"^\*\*Selected Iteration\*\*:\s*(iter_\d+)\s*$",
        selected_file.read_text(),
        re.MULTILINE,
    )
    return match.group(1) if match else "Unknown"


def count_files(directory):
    """Count direct files in an output directory."""
    return sum(1 for path in directory.iterdir() if path.is_file()) if directory.exists() else 0


def generate_manifest():
    """Generate FINAL_MANIFEST.md from all discovered analyses."""
    analysis_root = Path("analysis")
    if not analysis_root.exists():
        print("ERROR: analysis/ directory not found")
        return

    analyses = []
    for analysis_dir in discover_analyses(analysis_root):
        relative_path = analysis_dir.relative_to(analysis_root).as_posix()
        final_dir = analysis_dir / "final"
        selected_file = final_dir / "SELECTED.md"
        finalized = selected_file.exists()
        analyses.append(
            {
                "path": relative_path,
                "iteration": selected_iteration(selected_file) if finalized else "-",
                "results": count_files(final_dir / "results") if finalized else "-",
                "figures": count_files(final_dir / "figures") if finalized else "-",
                "finalized": finalized,
            }
        )

    date = datetime.now().strftime("%Y-%m-%d")
    lines = [
        "# Final Manifest",
        "",
        f"**Generated**: {date}",
        f"**Project**: {PROJECT_NAME}",
        "",
        "This file maps all final results to their source analyses and iterations.",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Analysis | Selected Iteration | Results | Figures | Status |",
        "|----------|--------------------|---------|---------|--------|",
    ]

    for item in analyses:
        status = "Finalized" if item["finalized"] else "In progress"
        lines.append(
            f"| {item['path']} | {item['iteration']} | {item['results']} | "
            f"{item['figures']} | {status} |"
        )

    lines.extend(["", "---", "", "## Detailed Entries", ""])
    for item in analyses:
        if not item["finalized"]:
            continue
        lines.extend(
            [
                f"### {item['path']}",
                "",
                f"- **Selected Iteration**: {item['iteration']}",
                f"- **Results**: {item['results']} files",
                f"- **Figures**: {item['figures']} files",
                f"- **Details**: `analysis/{item['path']}/final/SELECTED.md`",
                "",
                "---",
                "",
            ]
        )

    Path("FINAL_MANIFEST.md").write_text("\n".join(lines))
    finalized = [item for item in analyses if item["finalized"]]
    print("Generated FINAL_MANIFEST.md")
    print(f"  Finalized analyses: {len(finalized)}")
    for item in finalized:
        print(
            f"  - {item['path']}: {item['results']} results, "
            f"{item['figures']} figures"
        )


if __name__ == "__main__":
    generate_manifest()
