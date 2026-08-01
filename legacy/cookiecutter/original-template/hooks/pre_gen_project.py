#!/usr/bin/env python
"""
Pre-generation hook for SMAIRT template.

This script runs before cookiecutter generates the project structure.
It validates user input and checks prerequisites to ensure the project
can be created successfully.

"I don't know that I have the best practices. But I have a way that works
pretty well."
"""

import sys
import re
import shutil

def validate_project_slug():
    """
    Ensure project slug is valid for use as a directory name.

    Must:
    - Start with a lowercase letter
    - Contain only lowercase letters, numbers, and underscores
    - Not be empty
    """
    slug = "{{ cookiecutter.project_slug }}"

    if not slug:
        print("ERROR: Project slug cannot be empty")
        sys.exit(1)

    if not re.match(r'^[a-z][a-z0-9_]*$', slug):
        print(f"ERROR: Invalid project slug '{slug}'")
        print()
        print("Project slug must:")
        print("  - Start with a lowercase letter")
        print("  - Contain only lowercase letters, numbers, and underscores")
        print("  - Not contain spaces or special characters")
        print()
        print("This was derived from your project name: '{{ cookiecutter.project_name }}'")
        print("Consider using a simpler project name.")
        sys.exit(1)

def validate_research_question():
    """
    Check that a research question was provided.

    "How do you identify the questions that are really relevant and useful?
    How do you identify those gaps that are real gaps that haven't been
    addressed by someone before?"
    """
    question = "{{ cookiecutter.initial_research_question }}"

    default_question = "What is the main question you are trying to answer?"

    if not question or question == default_question:
        print("WARNING: You haven't specified a research question.")
        print()
        print("The research question is central to the SMAIRT workflow.")
        print("You can edit it later in: background/01_initial_question.md")
        print()
        print("Continuing with project generation...")
        print()

def check_python_version():
    """Ensure Python version is sufficient for SMAIRT scripts."""
    if sys.version_info < (3, 8):
        print("ERROR: SMAIRT requires Python 3.8 or higher")
        print(f"Current version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        sys.exit(1)

def check_git_available():
    """
    Check if git is available when user wants to create a git repo.
    """
    create_repo = "{{ cookiecutter.create_git_repo }}"

    if create_repo == "yes":
        if not shutil.which("git"):
            print("WARNING: Git is not installed or not in PATH")
            print("You requested git repository initialization, but git was not found.")
            print()
            print("Options:")
            print("  1. Install git and run 'git init' manually after project creation")
            print("  2. Continue without git initialization")
            print()
            print("Continuing with project generation...")
            print()

def validate_author_email():
    """Basic validation of author email format."""
    email = "{{ cookiecutter.author_email }}"

    # Very basic check - just ensure it has @ and .
    if email and email != "your.email@example.com":
        if "@" not in email or "." not in email:
            print(f"WARNING: '{email}' may not be a valid email address")
            print("Continuing with project generation...")
            print()

def print_pre_generation_summary():
    """Print summary of what will be created."""
    print("=" * 60)
    print("SMAIRT Pre-Generation Check")
    print("=" * 60)
    print()
    print(f"Project name:      {{ cookiecutter.project_name }}")
    print(f"Project slug:      {{ cookiecutter.project_slug }}")
    print(f"Author:            {{ cookiecutter.author_name }}")
    print(f"Project mode:      {{ cookiecutter.project_mode }}")
    print(f"Domain:            {{ cookiecutter.domain }}")
    print(f"Starting phase:    {{ cookiecutter.starting_phase }}")
    print(f"AI tool:           {{ cookiecutter.ai_tool }}")
    print(f"Create git repo:   {{ cookiecutter.create_git_repo }}")
    print()
    print("Research question:")
    print(f"  {{ cookiecutter.initial_research_question }}")
    print()
    print("-" * 60)
    print()

def main():
    """Main pre-generation hook."""

    print_pre_generation_summary()

    # Run all validations
    check_python_version()
    validate_project_slug()
    validate_research_question()
    validate_author_email()
    check_git_available()

    # If we get here, all critical checks passed
    print("✓ Pre-generation checks passed")
    print()
    
    project_mode = "{{ cookiecutter.project_mode }}"
    
    if project_mode == "paper_driven":
        print("Generating PAPER-DRIVEN SMAIRT project structure...")
        print()
        print("Paper-driven mode is for research starting with:")
        print("  - A paper outline or structure")
        print("  - Real datasets ready for analysis")
        print()
        print("Workflow:")
        print("  Paper outline + Data → Analysis plan → Iterative execution → Paper")
        print()
    else:
        print("Generating STANDARD SMAIRT project structure...")
        print()
        print("The template follows the scientific method in an iterative loop:")
        print("  Background → Hypothesis → Methods → Results → Analysis → Future Directions")
        print()
        starting_phase = "{{ cookiecutter.starting_phase }}"
        if starting_phase == "synthetic":
            print("Starting phase: synthetic (full data progression)")
            print("  1. Synthetic data   → Fast iteration, no dependencies")
            print("  2. Downloaded data  → Benchmark validation, robustness")
            print("  3. Real data        → Full test of approach")
        elif starting_phase == "downloaded":
            print("Starting phase: downloaded")
            print("  1. Downloaded data  → Benchmark validation, robustness")
            print("  2. Real data        → Full test of approach")
        else:
            print("Starting phase: real")
            print("  1. Real data        → Direct work on your target data")
        print()

if __name__ == "__main__":
    main()
