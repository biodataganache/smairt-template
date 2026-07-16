#!/usr/bin/env python
"""
Generate a manifest of all final results and their sources.

Usage:
    python scripts/generate_manifest.py

This scans all analysis directories and creates/updates FINAL_MANIFEST.md
with information about which iterations produced the final results.
"""

from pathlib import Path
from datetime import datetime


def generate_manifest():
    """Generate FINAL_MANIFEST.md from all finalized analyses."""
    analysis_dir = Path("analysis")
    date = datetime.now().strftime("%Y-%m-%d")
    
    if not analysis_dir.exists():
        print("ERROR: analysis/ directory not found")
        return
    
    # Collect all finalized analyses
    finalized = []
    
    for section_dir in sorted(analysis_dir.iterdir()):
        if not section_dir.is_dir():
            continue
        if section_dir.name.startswith('XX_'):
            continue  # Skip figures directory
        
        # Check for nested analysis directories
        for analysis_subdir in sorted(section_dir.iterdir()):
            if not analysis_subdir.is_dir():
                continue
            
            final_dir = analysis_subdir / "final"
            selected_file = final_dir / "SELECTED.md"
            
            if selected_file.exists():
                # Read selected iteration info
                content = selected_file.read_text()
                
                # Count files
                results_count = len(list((final_dir / "results").glob("*"))) if (final_dir / "results").exists() else 0
                figures_count = len(list((final_dir / "figures").glob("*"))) if (final_dir / "figures").exists() else 0
                
                finalized.append({
                    "path": f"{section_dir.name}/{analysis_subdir.name}",
                    "results": results_count,
                    "figures": figures_count,
                    "selected_file": selected_file
                })
    
    # Generate manifest
    manifest_content = f"""# Final Manifest

**Generated**: {date}
**Project**: {{ cookiecutter.project_name }}

This file maps all final results to their source analyses and iterations.

---

## Summary

| Analysis | Results | Figures | Status |
|----------|---------|---------|--------|
"""
    
    for item in finalized:
        manifest_content += f"| {item['path']} | {item['results']} | {item['figures']} | ✓ Finalized |\n"
    
    # Add not-finalized analyses
    for section_dir in sorted(analysis_dir.iterdir()):
        if not section_dir.is_dir():
            continue
        if section_dir.name.startswith('XX_'):
            continue
        
        for analysis_subdir in sorted(section_dir.iterdir()):
            if not analysis_subdir.is_dir():
                continue
            
            path = f"{section_dir.name}/{analysis_subdir.name}"
            if not any(f["path"] == path for f in finalized):
                manifest_content += f"| {path} | - | - | ⏳ In progress |\n"
    
    manifest_content += "\n---\n\n## Detailed Entries\n\n"
    
    for item in finalized:
        manifest_content += f"""### {item['path']}

- **Results**: {item['results']} files
- **Figures**: {item['figures']} files
- **Details**: `analysis/{item['path']}/final/SELECTED.md`

---

"""
    
    # Write manifest
    manifest_path = Path("FINAL_MANIFEST.md")
    manifest_path.write_text(manifest_content)
    
    print(f"✓ Generated FINAL_MANIFEST.md")
    print(f"  Finalized analyses: {len(finalized)}")
    print()
    print("Contents:")
    for item in finalized:
        print(f"  - {item['path']}: {item['results']} results, {item['figures']} figures")


if __name__ == "__main__":
    generate_manifest()
