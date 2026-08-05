"""What the wizard, the dashboard, and the commands all need to say things the same way.

These are the pieces of presentation that more than one interactive surface depends on:
whether the terminal can carry a repainting screen, how a console is styled, and how a stored
enum value is spelled for a reader. They live here rather than in `cli.py` so that the wizard
and the dashboard can be read separately without either importing the other, and so that a
label cannot be spelled one way in guided creation and another in the dashboard.

Nothing here decides anything. Every function maps an input to a presentation of it.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import typer
from rich.console import Console

from smairt.appearance import rich_theme, styling_enabled
from smairt.generator import generate_project
from smairt.models import CodeConvention, ProjectOptions, PromptConvention
from smairt.project import ProjectError, local_preferences, record_recent, resolve_project

# Exit codes are a contract with scripts, so they mean one thing each across every command:
#   0  the command did what it said
#   1  the project was found, and the operation failed or reported findings
#   2  the command could not be carried out as asked: no project, or unusable arguments
# `check` established this split deliberately, and every other command now follows it, so a
# script can tell "this is not a project" from "this project has problems" without parsing text.
CANNOT_PROCEED = 2
OPERATION_FAILED = 1

SKIP = ":skip"
BACK = ":back"
CANCEL = ":cancel"
"""The typed answers that mean skip, go back, and leave, in the plain-text presentation."""

OPTIONAL_CAPABILITIES = {"paper", "hpc"}
NO_CAPABILITIES = "none"
"""The mutually exclusive choice meaning a workspace with no optional capabilities."""

PHASE_LABELS = {
    "synthetic": "Synthetic",
    "downloaded": "Downloaded/benchmark",
    "real": "Real",
}

ASSISTANT_LABELS = {
    "zoo-code": "Zoo Code",
    "claude-code": "Claude Code",
    "opencode": "OpenCode",
    "codex": "Codex",
    "pi": "Pi",
    "cursor": "Cursor",
}


def interactive_motion_enabled(root: Path | None = None) -> bool:
    """Report whether a repainting framed screen can be drawn right now.

    Every condition is a reason the screen would be wrong rather than merely plain: no
    terminal to repaint, a terminal that cannot address itself, an automated run whose output
    is a transcript, or a local preference asking for the plain presentation.
    """
    motion = local_preferences(root).get("motion") if root is not None else None
    return (
        motion is not False
        and sys.stdin.isatty()
        and sys.stdout.isatty()
        and os.environ.get("TERM", "") not in {"", "dumb"}
        and not os.environ.get("CI")
        and not os.environ.get("PYTEST_CURRENT_TEST")
    )


def themed_console(motion: bool) -> Console:
    """Return a console whose styles come from the one semantic palette.

    Styling is suppressed when the researcher has asked for no color or the stream cannot
    carry it. ADR 0003 requires that request be honored, and wording never changes with
    it, so a plain-text session says exactly what a styled one says.
    """
    return Console(
        force_interactive=motion,
        force_terminal=motion,
        no_color=not styling_enabled(),
        theme=rich_theme(),
    )


def parse_capabilities(answer: str) -> set[str]:
    """Split a comma-separated capability answer into a set of requested names."""
    return {item.strip() for item in answer.split(",") if item.strip()}


def requested_capabilities(answer: str, console: Console) -> set[str] | None:
    """Return the capabilities a typed answer requests, or None when it is refused.

    The mutual exclusion the visual screen enforces by construction has to be
    enforced by hand here, in one place, so the two presentations cannot drift
    into disagreeing about what a contradictory answer means.
    """
    requested = parse_capabilities(answer.lower())
    if NO_CAPABILITIES in requested and requested != {NO_CAPABILITIES}:
        console.print(
            "None means no optional capabilities, so it cannot be combined with one.",
            style="caution",
        )
        return None
    requested -= {NO_CAPABILITIES}
    if not requested <= OPTIONAL_CAPABILITIES:
        console.print("Use paper, hpc, paper,hpc, or none.", style="caution")
        return None
    return requested


def capability_label(name: str) -> str:
    return "Paper" if name == "paper" else "HPC"


def phase_label(value: str) -> str:
    return PHASE_LABELS[value]


def assistant_label(value: str) -> str:
    return ASSISTANT_LABELS[value]


def slugify(value: str) -> str:
    """Return the immutable identifier form of arbitrary text."""
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug if slug and slug[0].isalpha() else f"project_{slug or 'workspace'}"


def folder_name(value: str) -> str:
    """Return the folder spelling of a name, from which the identifier derives."""
    return slugify(value).replace("_", "-")


def convention_value(convention: PromptConvention | CodeConvention | None) -> str:
    """Return a recorded convention's value, or empty when the project has none."""
    return convention.value if convention is not None else ""


def optional_answer(answers: dict[str, str | bool], key: str) -> str | None:
    """Return a collected answer, or None when the researcher left it blank."""
    value = str(answers.get(key, ""))
    return value or None


def project_or_exit(path: Path | None, *, remember: bool = True) -> Path:
    """Resolve a project or leave the process saying why, in one voice for every command."""
    try:
        root = resolve_project(path)
    except ProjectError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=CANNOT_PROCEED) from error
    if remember:
        record_recent(root)
    return root


def generate_with_progress(
    console: Console, destination: Path, options: ProjectOptions, motion: bool
) -> list[str]:
    """Create the project, showing a spinner only while work is actually running."""
    if not motion:
        return generate_project(destination, options)
    with console.status("Creating your SMAIRT project...", spinner="dots"):
        return generate_project(destination, options)
