#!/usr/bin/env python3
"""Print or write a non-destructive inventory of project research artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

AREAS = ("hypotheses", "experiments", "results/logs", "results/figures", "analysis", "paper")


def build_manifest(root: Path) -> str:
    lines = [
        "# Project Evidence Inventory",
        "",
        "Generated from existing files; no evidence was modified.",
        "",
    ]
    for area in AREAS:
        directory = root / area
        if not directory.is_dir():
            continue
        lines.extend((f"## {area}", ""))
        files = sorted(path for path in directory.rglob("*") if path.is_file())
        if files:
            lines.extend(f"- `{path.relative_to(root).as_posix()}`" for path in files)
        else:
            lines.append("- No files recorded.")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional new output file.")
    arguments = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest = build_manifest(root)
    if arguments.output is None:
        print(manifest, end="")
        return
    output = arguments.output if arguments.output.is_absolute() else root / arguments.output
    if output.exists():
        parser.error(f"refusing to overwrite existing file: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(manifest)
    print(f"Created {output.relative_to(root)}")


if __name__ == "__main__":
    main()
