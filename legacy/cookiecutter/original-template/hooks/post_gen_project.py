#!/usr/bin/env python
"""
Post-generation hook for SMAIRT template.

This script runs after cookiecutter generates the project structure.
It handles optional setup tasks like initializing a git repository
and prints mode-appropriate success messages.
"""

import os
import shutil
import subprocess
import sys

def init_git_repo():
    """Initialize a git repository and make initial commit."""
    try:
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial SMAIRT project structure"],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        # Git not installed
        return False

def remove_earlier_phases(starting_phase):
    """Remove experiment and data directories for phases before the starting phase.

    - synthetic: keep all three phases (full progression)
    - downloaded: remove 01_synthetic experiments and data/synthetic
    - real: remove 01_synthetic + 02_downloaded experiments and data/synthetic + data/downloaded
    """
    dirs_to_remove = []

    if starting_phase == "downloaded":
        dirs_to_remove = [
            os.path.join("experiments", "01_synthetic"),
            os.path.join("data", "synthetic"),
        ]
    elif starting_phase == "real":
        dirs_to_remove = [
            os.path.join("experiments", "01_synthetic"),
            os.path.join("experiments", "02_downloaded"),
            os.path.join("data", "synthetic"),
            os.path.join("data", "downloaded"),
        ]

    for d in dirs_to_remove:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"  Removed {d}/ (not needed for starting_phase={starting_phase})")


def remove_browser_paste_files():
    """Remove files that are only needed for browser-paste workflow."""
    # In ide_native mode, session_log.md is not needed (conversation IS the log)
    files_to_remove = [
        os.path.join("prompts", "session_log.md"),
    ]
    for f in files_to_remove:
        if os.path.exists(f):
            os.remove(f)

def print_ide_native_message():
    """Print success message for IDE-native workflow."""
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   🧪 SMAIRT Project Created Successfully! 🧪                          ║
║                                                                       ║
║   Scientific Method with AI Research Template                         ║
║   Workflow: IDE-Native (VSCode Roo/Zoo, Cursor, Windsurf)             ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║   Your AI has direct file access. No pasting needed!                  ║
║                                                                       ║
║   Next steps:                                                         ║
║                                                                       ║
║   1. Point your AI to:                                                ║
║      prompts/AI_CONTEXT.md — your AI's role and workflow              ║
║      prompts/CODE_CONVENTIONS.md — coding standards                   ║
║      prompts/CONTEXT_INDEX.md — what to read when                     ║
║                                                                       ║
║   2. Define your research question:                                   ║
║      background/01_initial_question.md                                ║
║                                                                       ║
║   3. Start experimenting:                                             ║
║      Ask your AI to create a hypothesis and first script              ║
║                                                                       ║
║   4. Track your intellectual contributions:                           ║
║      prompts/intellectual_contribution.md                             ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║   Key Directories:                                                    ║
║                                                                       ║
║   plans/          — Planning documents (create before complex work)   ║
║   hypotheses/     — Per-iteration hypothesis files                    ║
║   experiments/    — Scripts by data phase                              ║
║   analysis/       — Per-iteration analysis files                      ║
║   scripts/shared/ — Reusable utilities (logging, metrics, etc.)       ║
║   prompts/        — AI context, conventions, patterns                 ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║   The 4-Part Structure:                                               ║
║                                                                       ║
║   1. Background → 2. Hypothesis → 3. Methods → 4. Results            ║
║   Future directions feed back into Background for next cycle.         ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
""")

def print_browser_paste_message():
    """Print success message for browser-paste workflow."""
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   🧪 SMAIRT Project Created Successfully! 🧪                          ║
║                                                                       ║
║   Scientific Method with AI Research Template                         ║
║   Workflow: Browser-Paste (ChatGPT, Claude web, etc.)                 ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║   Next steps:                                                         ║
║                                                                       ║
║   1. Review the philosophy:                                           ║
║      docs/SMAIRT_PHILOSOPHY.md                                        ║
║                                                                       ║
║   2. Review the 12 steps:                                             ║
║      docs/12_STEPS.md                                                 ║
║                                                                       ║
║   3. Define your research question:                                   ║
║      background/01_initial_question.md                                ║
║                                                                       ║
║   4. Give these files to your AI:                                     ║
║      prompts/AI_CONTEXT.md                                            ║
║      prompts/CODE_CONVENTIONS.md                                      ║
║      prompts/KNOWN_PATTERNS.md                                        ║
║                                                                       ║
║   5. Use session start prompts:                                       ║
║      prompts/SESSION_START.md (copy-paste prompts)                    ║
║                                                                       ║
║   6. Track your intellectual contributions:                           ║
║      prompts/intellectual_contribution.md                             ║
║                                                                       ║
║   7. Compile context for new AI sessions:                             ║
║      python scripts/compile_for_ai.py                                 ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║   Data Progression (starting_phase: {{ cookiecutter.starting_phase }}):║
║                                                                       ║{% if cookiecutter.starting_phase == 'synthetic' %}
║   1. Synthetic   (experiments/01_synthetic/)  - Fast iteration        ║
║   2. Downloaded  (experiments/02_downloaded/) - Benchmark validation   ║
║   3. Real data   (experiments/03_real_data/)  - Full test             ║{% elif cookiecutter.starting_phase == 'downloaded' %}
║   1. Downloaded  (experiments/02_downloaded/) - Benchmark validation   ║
║   2. Real data   (experiments/03_real_data/)  - Full test             ║{% else %}
║   1. Real data   (experiments/03_real_data/)  - Direct work           ║{% endif %}
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
""")

def print_paper_driven_message():
    """Print success message for paper-driven mode."""
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   📄 SMAIRT Project Created Successfully! 📄                          ║
║                                                                       ║
║   Scientific Method with AI Research Template - PAPER-DRIVEN MODE     ║
║                                                                       ║
║   For research starting with a paper outline and real datasets.       ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║   Next steps:                                                         ║
║                                                                       ║
║   1. Add your paper outline:                                          ║
║      paper/outline.md                                                 ║
║                                                                       ║
║   2. Add your datasets:                                               ║
║      data/                                                            ║
║                                                                       ║
║   3. Review/update the analysis plan:                                 ║
║      analysis/ANALYSIS_PLAN.md                                        ║
║                                                                       ║
║   4. Start your AI session with:                                      ║
║      prompts/InitialPrompt_paper_driven.md                            ║
║                                                                       ║
║   5. Create your first analysis:                                      ║
║      python scripts/new_experiment.py --section 01 --name my_analysis ║
║                                                                       ║
║   6. Track iterations:                                                ║
║      python scripts/new_iteration.py --analysis 01_*/01_* --iter 02   ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║   Paper-Driven Workflow:                                              ║
║                                                                       ║
║   Paper outline + Data → Analysis plan → Iterative execution → Paper  ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
""")


def main():
    """Main post-generation hook."""

    # Initialize git repo if requested
    if "{{ cookiecutter.create_git_repo }}" == "yes":
        if init_git_repo():
            print("✓ Git repository initialized")
        else:
            print("✗ Could not initialize git repository (is git installed?)")

    # Handle starting phase — remove directories for phases before the chosen start
    starting_phase = "{{ cookiecutter.starting_phase }}"
    if starting_phase != "synthetic":
        remove_earlier_phases(starting_phase)

    # Handle workflow mode
    workflow_mode = "{{ cookiecutter.workflow_mode }}"
    if workflow_mode == "ide_native":
        remove_browser_paste_files()

    # Print success message based on mode
    project_mode = "{{ cookiecutter.project_mode }}"

    if project_mode == "paper_driven":
        print_paper_driven_message()
    elif workflow_mode == "ide_native":
        print_ide_native_message()
    else:
        print_browser_paste_message()

if __name__ == "__main__":
    main()
