from __future__ import annotations

from pathlib import Path

import typer
from pydantic import ValidationError

from smairt import __version__
from smairt.generator import GenerationError, generate_project
from smairt.models import Assistant, License, ProjectIdentity, ProjectOptions, Researcher, StartingPhase

app = typer.Typer(no_args_is_help=True)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"smairt {__version__}")
        raise typer.Exit()


@app.callback()
def smairt(
    version: bool = typer.Option(
        False,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the SMAIRT version and exit.",
    ),
) -> None:
    """Create and manage SMAIRT research workspaces."""


@app.command()
def new(
    destination: Path = typer.Argument(..., help="New project directory."),
    name: str = typer.Option(..., help="Human-readable project name."),
    slug: str = typer.Option(..., help="Immutable lowercase project slug."),
    description: str = typer.Option(..., help="Short project description."),
    researcher: str = typer.Option(..., help="Primary researcher's name."),
    domain: str = typer.Option(..., help="Research domain or Not sure yet."),
    phase: StartingPhase = typer.Option(StartingPhase.SYNTHETIC, help="Starting data phase."),
    assistant: Assistant = typer.Option(Assistant.OPENCODE, help="Selected coding assistant."),
    license: License = typer.Option(License.MIT, help="Project license."),
    question: str | None = typer.Option(None, help="Optional research question."),
    email: str | None = typer.Option(None, help="Optional researcher email."),
    paper: bool = typer.Option(False, help="Include additive Paper support."),
    hpc: bool = typer.Option(False, help="Include additive HPC guidance."),
    initialize_git: bool = typer.Option(False, "--git/--no-git", help="Initialize and stage Git files."),
) -> None:
    """Create a SMAIRT project without interactive prompts."""
    try:
        options = ProjectOptions(
            project=ProjectIdentity(
                name=name,
                slug=slug,
                description=description,
                domain=domain,
                research_question=question,
            ),
            researcher=Researcher(name=researcher, email=email),
            assistant=assistant,
            starting_phase=phase,
            license=license,
            initialize_git=initialize_git,
            paper=paper,
            hpc=hpc,
        )
        messages = generate_project(destination, options)
    except (GenerationError, ValidationError) as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1) from error
    typer.echo(f"Created SMAIRT project at {destination.resolve()}")
    for message in messages:
        typer.echo(message)


def main() -> None:
    app()
