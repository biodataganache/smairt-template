#!/usr/bin/env python
"""
Finalize an iteration by copying results to the final/ directory.

Usage:
    python scripts/finalize_iteration.py --analysis 01_results/01_analysis --iteration 02

This:
1. Copies results and figures from iter_XX to final/
2. Creates SELECTED.md documenting the selection
3. Updates FINAL_MANIFEST.md
"""

import argparse
from pathlib import Path
from datetime import datetime
import shutil

SELECTED_TEMPLATE = '''# Selected Iteration

## Analysis: {analysis}

**Selected Iteration**: iter_{iteration}
**Date Finalized**: {date}

## Rationale

[Explain why this iteration was selected]

## Key Metrics

| Metric | Value |
|--------|-------|
| [Metric 1] | [Value] |
| [Metric 2] | [Value] |

## Files Included

### Results
{results_files}

### Figures
{figure_files}

## Notes

[Any additional notes about this selection]
'''


def finalize_iteration(analysis: str, iteration: str):
    """Finalize an iteration by copying to final/ directory."""
    analysis_dir = Path(f"analysis/{analysis}")
    iter_dir = analysis_dir / "iterations" / f"iter_{iteration}"
    final_dir = analysis_dir / "final"
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Validate paths
    if not analysis_dir.exists():
        print(f"ERROR: Analysis directory does not exist: {analysis_dir}")
        return
    
    if not iter_dir.exists():
        print(f"ERROR: Iteration directory does not exist: {iter_dir}")
        return
    
    # Clear existing final results (with confirmation)
    if (final_dir / "results").exists() and any((final_dir / "results").iterdir()):
        response = input("Final results already exist. Overwrite? [y/N]: ")
        if response.lower() != 'y':
            print("Aborted.")
            return
        shutil.rmtree(final_dir / "results")
        shutil.rmtree(final_dir / "figures")
    
    # Create final directories
    (final_dir / "results").mkdir(parents=True, exist_ok=True)
    (final_dir / "figures").mkdir(parents=True, exist_ok=True)
    
    # Copy results
    results_files = []
    if (iter_dir / "results").exists():
        for f in (iter_dir / "results").iterdir():
            if f.is_file():
                shutil.copy(f, final_dir / "results" / f.name)
                results_files.append(f"- {f.name}")
    
    # Copy figures
    figure_files = []
    if (iter_dir / "figures").exists():
        for f in (iter_dir / "figures").iterdir():
            if f.is_file():
                shutil.copy(f, final_dir / "figures" / f.name)
                figure_files.append(f"- {f.name}")
    
    # Create SELECTED.md
    selected_content = SELECTED_TEMPLATE.format(
        analysis=analysis,
        iteration=iteration,
        date=date,
        results_files="\n".join(results_files) if results_files else "- None",
        figure_files="\n".join(figure_files) if figure_files else "- None"
    )
    (final_dir / "SELECTED.md").write_text(selected_content)
    
    # Update FINAL_MANIFEST.md
    update_manifest(analysis, iteration, date, results_files, figure_files)
    
    print(f"✓ Finalized iteration {iteration} for {analysis}")
    print(f"  Results copied to: {final_dir}")
    print(f"  Created: {final_dir}/SELECTED.md")
    print(f"  Updated: FINAL_MANIFEST.md")
    print()
    print("Next steps:")
    print(f"  1. Edit {final_dir}/SELECTED.md with rationale")
    print("  2. Review FINAL_MANIFEST.md")


def update_manifest(analysis: str, iteration: str, date: str, results: list, figures: list):
    """Update FINAL_MANIFEST.md with the finalized iteration."""
    manifest_path = Path("FINAL_MANIFEST.md")
    
    # Create manifest if it doesn't exist
    if not manifest_path.exists():
        manifest_path.write_text("# Final Manifest\n\nThis file maps final results to their source iterations.\n\n---\n\n")
    
    # Append entry
    entry = f"""
## {analysis}

- **Iteration**: iter_{iteration}
- **Finalized**: {date}
- **Results**: {len(results)} files
- **Figures**: {len(figures)} files
- **Details**: `analysis/{analysis}/final/SELECTED.md`

---
"""
    
    with open(manifest_path, 'a') as f:
        f.write(entry)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Finalize an iteration by copying to final/ directory"
    )
    parser.add_argument(
        "--analysis",
        required=True,
        help="Path to analysis (e.g., 01_section/01_analysis)"
    )
    parser.add_argument(
        "--iteration",
        required=True,
        help="Iteration number to finalize (e.g., 02)"
    )
    args = parser.parse_args()
    
    finalize_iteration(args.analysis, args.iteration)
