from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Callable

import typer
from pydantic import ValidationError
from prompt_toolkit import PromptSession
from prompt_toolkit.input.defaults import create_input
from prompt_toolkit.output.defaults import create_output
from rich.console import Console

from smairt import __version__
from smairt.generator import GenerationError, generate_project, validate_destination
from smairt.models import Assistant, License, ProjectIdentity, ProjectOptions, Researcher, StartingPhase

app = typer.Typer(no_args_is_help=True)

_SKIP = ":skip"
_BACK = ":back"
_CANCEL = ":cancel"
_WIZARD_STEPS = 15


class WizardCancelled(Exception):
    """Raised when the user intentionally leaves guided project creation."""


class Wizard:
    def __init__(self) -> None:
        self.console = Console(force_interactive=_interactive_motion_enabled())
        self.session: PromptSession[str] = PromptSession(
            input=create_input(sys.stdin),
            output=create_output(sys.stdout),
        )
        self.answers: dict[str, str | bool] = {
            "phase": StartingPhase.SYNTHETIC.value,
            "assistant": Assistant.OPENCODE.value,
            "license": License.MIT.value,
            "paper": False,
            "hpc": False,
            "git": False,
        }
        self.steps: tuple[tuple[str, Callable[[], None]], ...] = (
            ("Destination", self._destination),
            ("Project name", self._name),
            ("Project slug", self._slug),
            ("Description", self._description),
            ("Domain", self._domain),
            ("Research question", self._question),
            ("Primary researcher", self._researcher),
            ("Email", self._email),
            ("Optional capabilities", self._capabilities),
            ("Starting phase", self._phase),
            ("Coding assistant", self._assistant),
            ("License", self._license),
            ("License confirmation", self._confirm_license),
            ("Git", self._git),
            ("Final review", self._review),
        )

    def run(self) -> tuple[Path, ProjectOptions]:
        index = 0
        while index < len(self.steps):
            title, step = self.steps[index]
            self._screen(index, title)
            try:
                step()
            except BackRequested:
                if index == 0:
                    self.console.print("This is the first screen. Enter :cancel to leave setup.")
                else:
                    index -= 1
                    self.console.print("Back: your earlier answers are kept.")
                continue
            index += 1
        return Path(str(self.answers["destination"])).expanduser(), self._options()

    def _screen(self, index: int, title: str) -> None:
        progress = f"Step {index + 1} of {_WIZARD_STEPS}"
        self.console.rule(f"[bold cyan]{progress}: {title}[/]")
        self.console.print("You can change every answer during final review.", style="dim")

    def _ask(
        self,
        prompt: str,
        *,
        key: str,
        default: str | None = None,
        optional: bool = False,
    ) -> str:
        retained = str(self.answers.get(key, default or ""))
        suffix = " [Enter for recommended default]" if default is not None else ""
        if key in self.answers and default is None:
            suffix = " [Enter to keep current answer]"
        if optional:
            suffix += " [:skip to leave blank]"
        while True:
            answer = self.session.prompt(f"{prompt}{suffix}: ").strip()
            if answer == _CANCEL:
                raise WizardCancelled
            if answer == _BACK:
                raise BackRequested
            if optional and answer == _SKIP:
                self.answers[key] = ""
                return ""
            if not answer:
                answer = retained
            if answer:
                self.answers[key] = answer
                return answer
            self.console.print("Please enter a value, or use :skip for this optional question.", style="yellow")

    def _choose(
        self,
        prompt: str,
        *,
        key: str,
        choices: tuple[tuple[str, str, str, str], ...],
        default: str,
    ) -> str:
        self.console.print("Recommended choices are marked.")
        for number, label, value, explanation in choices:
            recommended = " [recommended]" if value == default else ""
            self.console.print(f"  {number}. {label}{recommended} - {explanation}")
        mapping = {number: value for number, _, value, _ in choices}
        current = str(self.answers.get(key, default))
        while True:
            answer = self.session.prompt(f"{prompt} [Enter for {default}]: ").strip()
            if answer == _CANCEL:
                raise WizardCancelled
            if answer == _BACK:
                raise BackRequested
            if not answer:
                answer = current
            selection = mapping.get(answer, answer if answer in mapping.values() else "")
            if selection:
                self.answers[key] = selection
                return selection
            self.console.print("Choose one of the listed numbers.", style="yellow")

    def _destination(self) -> None:
        while True:
            text = self._ask("Where should the new project folder be created", key="destination")
            try:
                validate_destination(Path(text).expanduser().resolve())
            except GenerationError as error:
                self.console.print(f"That location is not safe: {error}", style="yellow")
            else:
                self.answers["destination"] = str(Path(text).expanduser())
                return

    def _name(self) -> None:
        self._ask("What is the human-readable project name", key="name")

    def _slug(self) -> None:
        default = _slugify(str(self.answers.get("name", "project")))
        while True:
            slug = self._ask(
                "Project slug (used in stable identifiers)", key="slug", default=default
            )
            try:
                ProjectIdentity(
                    name=str(self.answers["name"]),
                    slug=slug,
                    description="placeholder",
                    domain="placeholder",
                )
            except ValidationError as error:
                self.console.print(str(error.errors()[0]["msg"]), style="yellow")
            else:
                return

    def _description(self) -> None:
        self._ask("Briefly describe this project", key="description")

    def _domain(self) -> None:
        choices = (
            (
                "1",
                "Computational biology",
                "Computational biology",
                "Biological data, methods, and models.",
            ),
            (
                "2",
                "Biomedical research",
                "Biomedical research",
                "Health, disease, and clinical research.",
            ),
            (
                "3",
                "Ecology and environmental science",
                "Ecology and environmental science",
                "Environmental systems and field data.",
            ),
            (
                "4",
                "Chemistry and materials science",
                "Chemistry and materials science",
                "Molecules, materials, and measurements.",
            ),
            (
                "5",
                "Not sure yet",
                "Not sure yet",
                "Choose this if the project is still taking shape.",
            ),
            ("6", "Type my own", "custom", "Use a domain not listed here."),
        )
        choice = self._choose(
            "Choose a domain", key="domain", choices=choices, default="Not sure yet"
        )
        if choice == "custom":
            self.answers["domain"] = self._ask("Type your research domain", key="custom_domain")

    def _question(self) -> None:
        self.console.print("Optional. Skip this if the research question is still developing.")
        self._ask("What question will this project explore", key="question", optional=True)

    def _researcher(self) -> None:
        self._ask("Who is the primary researcher", key="researcher")

    def _email(self) -> None:
        self.console.print("Optional. Skipping keeps personal contact information out of metadata.")
        self._ask("Researcher email", key="email", optional=True)

    def _capabilities(self) -> None:
        self.console.print(
            "Paper and HPC support are optional and both start off for a focused workspace."
        )
        self.console.print("Type paper, hpc, paper,hpc, or press Enter to skip.")
        while True:
            answer = self.session.prompt(
                "Optional capabilities [Enter to skip]: "
            ).strip().lower()
            if answer == _CANCEL:
                raise WizardCancelled
            if answer == _BACK:
                raise BackRequested
            requested = {item.strip() for item in answer.split(",") if item.strip()}
            if requested <= {"paper", "hpc"}:
                self.answers["paper"] = "paper" in requested
                self.answers["hpc"] = "hpc" in requested
                return
            self.console.print("Use paper, hpc, or paper,hpc.", style="yellow")

    def _phase(self) -> None:
        self._choose(
            "Choose a starting phase",
            key="phase",
            default="synthetic",
            choices=(
                (
                    "1",
                    "Synthetic",
                    "synthetic",
                    "Start with generated data; safest for learning and testing.",
                ),
                (
                    "2",
                    "Downloaded/benchmark",
                    "downloaded",
                    "Start with public or benchmark data.",
                ),
                (
                    "3",
                    "Real",
                    "real",
                    "Start with your own collected or operational data.",
                ),
            ),
        )

    def _assistant(self) -> None:
        self._choose(
            "Choose your coding assistant",
            key="assistant",
            default="opencode",
            choices=(
                ("1", "Zoo Code", "zoo-code", "Use SMAIRT guidance with Zoo Code."),
                (
                    "2",
                    "Claude Code",
                    "claude-code",
                    "Use SMAIRT guidance with Claude Code.",
                ),
                ("3", "OpenCode", "opencode", "Use SMAIRT guidance with OpenCode."),
                ("4", "Codex", "codex", "Use SMAIRT guidance with Codex."),
                ("5", "Pi", "pi", "Use SMAIRT guidance with Pi."),
                ("6", "Cursor", "cursor", "Use SMAIRT guidance with Cursor."),
            ),
        )

    def _license(self) -> None:
        self._choose(
            "Choose a license",
            key="license",
            default="MIT",
            choices=(
                ("1", "MIT", "MIT", "Permissive reuse with attribution and no warranty."),
                (
                    "2",
                    "BSD-3-Clause",
                    "BSD-3-Clause",
                    "Permissive reuse with attribution and no endorsement.",
                ),
                (
                    "3",
                    "Apache-2.0",
                    "Apache-2.0",
                    "Permissive reuse with patent terms and notices.",
                ),
                (
                    "4",
                    "GPL-3.0",
                    "GPL-3.0",
                    "Reuse and distribution requires sharing covered source changes.",
                ),
                (
                    "5",
                    "Proprietary",
                    "proprietary",
                    "Reserve reuse rights unless you grant permission.",
                ),
            ),
        )

    def _confirm_license(self) -> None:
        self.console.print(
            f"{self.answers['license']} controls how others may use this project. This is not legal advice."
        )
        while True:
            answer = self.session.prompt("Confirm this license [yes/no]: ").strip().lower()
            if answer == _CANCEL:
                raise WizardCancelled
            if answer == _BACK:
                raise BackRequested
            if answer in {"yes", "y"}:
                return
            if answer in {"no", "n"}:
                raise BackRequested
            self.console.print("Please answer yes or no.", style="yellow")

    def _git(self) -> None:
        self.console.print(
            "Git is recommended for history, but it is optional. SMAIRT will stage files and never commit."
        )
        while True:
            answer = self.session.prompt("Initialize Git [yes/no, Enter for no]: ").strip().lower()
            if answer == _CANCEL:
                raise WizardCancelled
            if answer == _BACK:
                raise BackRequested
            if answer in {"", "no", "n"}:
                self.answers["git"] = False
                return
            if answer in {"yes", "y"}:
                self.answers["git"] = True
                return
            self.console.print("Please answer yes or no.", style="yellow")

    def _review(self) -> None:
        self.console.print("[bold]Final review[/]")
        for index, (title, _) in enumerate(self.steps[:-1], start=1):
            self.console.print(f"  {index}. {title}: {self._review_value(index)}")
        self.console.print(
            "Enter a number to edit it, create to write the project, or cancel to leave without files."
        )
        while True:
            answer = self.session.prompt("Review action: ").strip().lower()
            if answer in {"cancel", _CANCEL}:
                raise WizardCancelled
            if answer in {"create", "c"}:
                return
            if answer.isdigit() and 1 <= int(answer) < _WIZARD_STEPS:
                self._edit(int(answer) - 1)
                self._screen(_WIZARD_STEPS - 1, "Final review")
                self.console.print("[bold]Final review[/]")
                for index, (title, _) in enumerate(self.steps[:-1], start=1):
                    self.console.print(f"  {index}. {title}: {self._review_value(index)}")
                continue
            self.console.print("Enter a listed number, create, or cancel.", style="yellow")

    def _edit(self, index: int) -> None:
        title, step = self.steps[index]
        self._screen(index, f"Edit {title}")
        step()

    def _review_value(self, index: int) -> str:
        keys = (
            "destination", "name", "slug", "description", "domain", "question", "researcher", "email",
        )
        if index <= len(keys):
            value = str(self.answers.get(keys[index - 1], ""))
            return value or "Skipped"
        if index == 9:
            selected = [name for name in ("paper", "hpc") if self.answers[name]]
            return ", ".join(selected) if selected else "Off"
        if index == 10:
            return _phase_label(str(self.answers["phase"]))
        if index == 11:
            return _assistant_label(str(self.answers["assistant"]))
        if index in {12, 13}:
            return str(self.answers["license"])
        return "Yes" if self.answers["git"] else "No"

    def _options(self) -> ProjectOptions:
        return ProjectOptions(
            project=ProjectIdentity(
                name=str(self.answers["name"]),
                slug=str(self.answers["slug"]),
                description=str(self.answers["description"]),
                domain=str(self.answers["domain"]),
                research_question=_optional_answer(self.answers, "question"),
            ),
            researcher=Researcher(
                name=str(self.answers["researcher"]),
                email=_optional_answer(self.answers, "email"),
            ),
            assistant=Assistant(str(self.answers["assistant"])),
            starting_phase=StartingPhase(str(self.answers["phase"])),
            license=License(str(self.answers["license"])),
            initialize_git=bool(self.answers["git"]),
            paper=bool(self.answers["paper"]),
            hpc=bool(self.answers["hpc"]),
        )


class BackRequested(Exception):
    """Raised to move to the preceding wizard screen."""


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
    destination: Path | None = typer.Argument(None, help="New project directory."),
    name: str | None = typer.Option(None, help="Human-readable project name."),
    slug: str | None = typer.Option(None, help="Immutable lowercase project slug."),
    description: str | None = typer.Option(None, help="Short project description."),
    researcher: str | None = typer.Option(None, help="Primary researcher's name."),
    domain: str | None = typer.Option(None, help="Research domain or Not sure yet."),
    phase: StartingPhase = typer.Option(StartingPhase.SYNTHETIC, help="Starting data phase."),
    assistant: Assistant = typer.Option(Assistant.OPENCODE, help="Selected coding assistant."),
    license: License = typer.Option(License.MIT, help="Project license."),
    question: str | None = typer.Option(None, help="Optional research question."),
    email: str | None = typer.Option(None, help="Optional researcher email."),
    paper: bool = typer.Option(False, help="Include additive Paper support."),
    hpc: bool = typer.Option(False, help="Include additive HPC guidance."),
    initialize_git: bool = typer.Option(False, "--git/--no-git", help="Initialize and stage Git files."),
) -> None:
    """Create a SMAIRT project interactively or with complete noninteractive flags."""
    wizard_mode = destination is None
    options: ProjectOptions | None = None
    if destination is None:
        try:
            destination, options = Wizard().run()
        except WizardCancelled:
            typer.echo("Project creation cancelled. No files were written.")
            raise typer.Exit(code=1)
    if not wizard_mode and (
        name is None
        or slug is None
        or description is None
        or researcher is None
        or domain is None
    ):
        typer.echo(
            "Error: --name, --slug, --description, --researcher, and --domain are required with a destination.",
            err=True,
        )
        raise typer.Exit(code=2)
    try:
        if options is None:
            assert destination is not None
            assert name is not None
            assert slug is not None
            assert description is not None
            assert researcher is not None
            assert domain is not None
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
        assert destination is not None
        if wizard_mode and _interactive_motion_enabled():
            console = Console()
            with console.status("Creating your SMAIRT project...", spinner="dots"):
                messages = generate_project(destination, options)
        else:
            messages = generate_project(destination, options)
    except (GenerationError, ValidationError, OSError) as error:
        prefix = "Could not create the project" if wizard_mode else "Error"
        typer.echo(f"{prefix}: {error}", err=True)
        raise typer.Exit(code=1) from error
    typer.echo(f"Created SMAIRT project at {destination.resolve()}")
    for message in messages:
        typer.echo(message)


def _optional_answer(answers: dict[str, str | bool], key: str) -> str | None:
    value = str(answers.get(key, ""))
    return value or None


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug if slug and slug[0].isalpha() else f"project_{slug or 'workspace'}"


def _phase_label(value: str) -> str:
    return {
        "synthetic": "Synthetic",
        "downloaded": "Downloaded/benchmark",
        "real": "Real",
    }[value]


def _assistant_label(value: str) -> str:
    return {
        "zoo-code": "Zoo Code",
        "claude-code": "Claude Code",
        "opencode": "OpenCode",
        "codex": "Codex",
        "pi": "Pi",
        "cursor": "Cursor",
    }[value]


def _interactive_motion_enabled() -> bool:
    return (
        sys.stdin.isatty()
        and sys.stdout.isatty()
        and os.environ.get("TERM", "") not in {"", "dumb"}
        and not os.environ.get("CI")
        and not os.environ.get("PYTEST_CURRENT_TEST")
    )


def main() -> None:
    app()
