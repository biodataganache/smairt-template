from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Callable

import typer
import yaml
from prompt_toolkit import PromptSession
from prompt_toolkit.input.defaults import create_input
from prompt_toolkit.output.defaults import create_output
from pydantic import ValidationError
from rich.console import Console

from smairt import __version__
from smairt.generator import GenerationError, generate_project, validate_destination
from smairt.models import (
    Assistant,
    CodeConvention,
    License,
    ProjectContract,
    ProjectIdentity,
    ProjectOptions,
    PromptConvention,
    Researcher,
    StartingPhase,
)
from smairt.project import (
    LICENSE_EXPLANATIONS,
    ProjectError,
    apply_repairs,
    change_license,
    detected_tools,
    disable_capability,
    enable_capability,
    launch_assistant,
    license_preview,
    load_contract,
    local_preferences,
    managed_asset_paths,
    managed_asset_previews,
    managed_file_statuses,
    open_folder,
    prepare_assistant,
    project_check,
    recent_projects,
    record_recent,
    regenerate_managed_assets,
    repair_previews,
    resolve_project,
    save_local_preferences,
    update_collaborator,
    update_settings,
)

app = typer.Typer(no_args_is_help=False, invoke_without_command=True)

_SKIP = ":skip"
_BACK = ":back"
_CANCEL = ":cancel"
_WIZARD_STEPS = 15


class WizardCancelled(Exception):
    """Raised when the user intentionally leaves guided project creation."""


class Wizard:
    def __init__(self) -> None:
        motion = _interactive_motion_enabled()
        self.console = Console(force_interactive=motion, force_terminal=motion)
        self.session: PromptSession[str] = PromptSession(
            input=create_input(sys.stdin),
            output=create_output(sys.stdout),
        )
        self.answers: dict[str, str | bool] = {
            "phase": StartingPhase.SYNTHETIC.value,
            "assistant": Assistant.OPENCODE.value,
            "license": License.MIT.value,
            "license_confirmation": "",
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
            self.console.print(
                "Please enter a value, or use :skip for this optional question.", style="yellow"
            )

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
        if current not in mapping.values():
            current = "custom" if key == "domain" and self.answers.get("custom_domain") else default
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
            answer = self.session.prompt("Optional capabilities [Enter to skip]: ").strip().lower()
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
        previous_license = str(self.answers["license"])
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
        if str(self.answers["license"]) != previous_license:
            self.answers["license_confirmation"] = ""

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
                self.answers["license_confirmation"] = str(self.answers["license"])
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
                if self.answers["license_confirmation"] != self.answers["license"]:
                    self.console.print(
                        "Confirm the final selected license before creating the project.",
                        style="yellow",
                    )
                    self._confirm_license()
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
            "destination",
            "name",
            "slug",
            "description",
            "domain",
            "question",
            "researcher",
            "email",
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
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the SMAIRT version and exit.",
    ),
) -> None:
    """Create and manage SMAIRT research workspaces."""
    if ctx.invoked_subcommand is None:
        _home()


def _project_or_exit(path: Path | None, *, remember: bool = True) -> Path:
    try:
        root = resolve_project(path)
    except ProjectError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1) from error
    if remember:
        record_recent(root)
    return root


def _command_error(error: ProjectError) -> None:
    typer.echo(f"Error: {error}", err=True)
    raise typer.Exit(code=1) from error


@app.command()
def open(
    path: Path = typer.Argument(..., help="Existing SMAIRT project directory."),
    launch: bool = typer.Option(
        False, help="Launch the project's selected assistant when available."
    ),
    folder: bool = typer.Option(False, help="Open the project folder in the file manager."),
) -> None:
    """Open a SMAIRT project and remember it locally."""
    root = _project_or_exit(path)
    if launch:
        success, message = launch_assistant(root)
        typer.echo(message)
        if not success:
            raise typer.Exit(code=1)
    elif folder:
        typer.echo(open_folder(root))
    else:
        typer.echo(f"Opened SMAIRT project: {root}")


@app.command()
def check(
    path: Path | None = typer.Argument(
        None, help="SMAIRT project directory, or the current project."
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON diagnostics."),
    verbose: bool = typer.Option(False, help="Explain diagnostics and show detected local tools."),
) -> None:
    """Read-only Project Check for structural and configuration issues."""
    try:
        root = resolve_project(path)
    except ProjectError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=2) from error
    issues = project_check(root)
    payload = {
        "issues": [issue.as_dict() for issue in issues],
        "ok": not issues,
        "repairs": [issue.repair for issue in issues if issue.repair is not None],
    }
    if json_output:
        typer.echo(__import__("json").dumps(payload, sort_keys=True))
    elif issues:
        typer.echo("Project Check found structural issues:")
        for issue in issues:
            typer.echo(f"- [{issue.code}] {issue.message}")
            if verbose:
                typer.echo(f"  Artifact: {issue.path}")
                typer.echo(
                    "  Diagnostic is read-only; researcher content is never changed by Project Check."
                )
            if issue.repair is not None:
                typer.echo(f"  Safe repair available: {issue.repair}")
    else:
        typer.echo("Project Check passed: no structural or configuration issues found.")
    if verbose and not json_output:
        typer.echo("Detected local tools:")
        for label, executable in detected_tools(root).items():
            typer.echo(f"- {label}: {executable}")
    if issues:
        raise typer.Exit(code=1)


paper_app = typer.Typer(help="Enable or deactivate additive Paper support.")
hpc_app = typer.Typer(help="Enable or deactivate additive HPC support.")
app.add_typer(paper_app, name="paper")
app.add_typer(hpc_app, name="hpc")


def _capability_command(path: Path | None, name: str, enabled: bool) -> None:
    root = _project_or_exit(path)
    try:
        message = enable_capability(root, name) if enabled else disable_capability(root, name)
    except ProjectError as error:
        _command_error(error)
    typer.echo(message)


@paper_app.command("enable")
def paper_enable(
    path: Path | None = typer.Argument(None, help="Project directory or current project."),
) -> None:
    """Enable Paper guidance without touching existing work."""
    _capability_command(path, "paper", True)


@paper_app.command("disable")
def paper_disable(
    path: Path | None = typer.Argument(None, help="Project directory or current project."),
) -> None:
    """Deactivate Paper guidance without deleting files."""
    _capability_command(path, "paper", False)


@hpc_app.command("enable")
def hpc_enable(
    path: Path | None = typer.Argument(None, help="Project directory or current project."),
) -> None:
    """Enable HPC guidance without submitting jobs."""
    _capability_command(path, "hpc", True)


@hpc_app.command("disable")
def hpc_disable(
    path: Path | None = typer.Argument(None, help="Project directory or current project."),
) -> None:
    """Deactivate HPC guidance without deleting files."""
    _capability_command(path, "hpc", False)


@app.command("repair")
def repair(
    path: Path | None = typer.Argument(None, help="Project directory or current project."),
    select: list[str] = typer.Option([], "--select", help="Safe repair identifier to select."),
    confirm: bool = typer.Option(False, help="Apply the previewed selected repairs."),
) -> None:
    """Preview and explicitly apply deterministic tool-owned structural repairs."""
    root = _project_or_exit(path)
    try:
        if not select:
            available = [issue for issue in project_check(root) if issue.repair is not None]
            if not available:
                typer.echo("No safe repairs are available.")
                return
            typer.echo("Safe repairs available:")
            for issue in available:
                assert issue.repair is not None
                typer.echo(f"- {issue.repair}: {issue.message}")
            typer.echo(
                "Select repairs with --select REPAIR. Add --confirm only after reviewing the preview."
            )
            return
        preview = repair_previews(root, select)
    except ProjectError as error:
        _command_error(error)
        return
    typer.echo("Repair preview (only tool-owned structure will be created; no content is deleted):")
    for issue in preview:
        assert issue.repair is not None
        typer.echo(f"- {issue.repair}: {issue.message}")
    if not confirm:
        typer.echo("No changes made. Re-run with the same --select values and --confirm to apply.")
        return
    apply_repairs(root, select)
    typer.echo("Selected safe repairs applied.")


@app.command("settings")
def settings(
    path: Path | None = typer.Argument(None, help="Project directory or current project."),
    name: str | None = typer.Option(None, help="Human-readable project name."),
    description: str | None = typer.Option(None, help="Project description."),
    domain: str | None = typer.Option(None, help="Research domain."),
    question: str | None = typer.Option(None, help="Research question."),
    assistant: Assistant | None = typer.Option(None, help="Selected coding assistant."),
    phase: StartingPhase | None = typer.Option(
        None, help="Current phase; directories are never deleted."
    ),
    researcher: str | None = typer.Option(None, help="Primary researcher name."),
    email: str | None = typer.Option(None, help="Primary researcher email."),
    collaborator_role: str | None = typer.Option(None, help="Collaborator role identifier."),
    collaborator_name: str | None = typer.Option(None, help="Collaborator name."),
    collaborator_email: str | None = typer.Option(None, help="Optional collaborator email."),
    experience: str | None = typer.Option(None, help="Local Standard or Advanced preference."),
    motion: bool | None = typer.Option(None, help="Local motion preference."),
    prompt_convention: PromptConvention | None = typer.Option(
        None, help="Prompt convention: plan-first or direct-task."
    ),
    code_convention: CodeConvention | None = typer.Option(
        None, help="Code convention: typed-python or standard-python."
    ),
    license: License | None = typer.Option(None, help="License to preview or change."),
    confirm_license: bool = typer.Option(False, help="Confirm the previewed license replacement."),
) -> None:
    """Show or safely update approved project settings; slug and folder stay immutable."""
    root = _project_or_exit(path)
    try:
        if license is not None:
            typer.echo("License changes can affect legal rights. This is not legal advice.")
            typer.echo(f"{license.value}: {LICENSE_EXPLANATIONS[license]}")
            typer.echo("Preview:")
            typer.echo(license_preview(root, license), nl=False)
            if not confirm_license:
                typer.echo(
                    "No license change made. Re-run with --confirm-license to replace unmodified legal text."
                )
                return
            change_license(root, license)
            typer.echo(f"License changed to {license.value}.")
        if (
            collaborator_role is not None
            or collaborator_name is not None
            or collaborator_email is not None
        ):
            if collaborator_role is None or collaborator_name is None:
                raise ProjectError(
                    "--collaborator-role and --collaborator-name must be provided together."
                )
            update_collaborator(root, collaborator_role, collaborator_name, collaborator_email)
        update_settings(
            root,
            name=name,
            description=description,
            domain=domain,
            question=question,
            assistant=assistant,
            phase=phase,
            researcher=researcher,
            email=email,
            prompt_convention=prompt_convention,
            code_convention=code_convention,
        )
        preferences = local_preferences(root)
        if experience is not None:
            if experience not in {"standard", "advanced"}:
                raise ProjectError("Experience must be standard or advanced.")
            preferences["experience"] = experience
        if motion is not None:
            preferences["motion"] = motion
        if experience is not None or motion is not None:
            save_local_preferences(root, preferences)
        if all(
            value is None
            for value in (
                name,
                description,
                domain,
                question,
                assistant,
                phase,
                researcher,
                email,
                collaborator_role,
                experience,
                motion,
                prompt_convention,
                code_convention,
                license,
            )
        ):
            contract = load_contract(root)
            typer.echo(f"Project Settings: {contract.project.name}")
            typer.echo(f"Slug (immutable): {contract.project.slug}")
            typer.echo(f"Starting phase: {contract.starting_phase.value}")
            typer.echo(f"Current phase: {contract.current_phase.value}")
            typer.echo(f"Assistant: {contract.assistant.value}")
            typer.echo(f"License: {contract.license.value}")
            typer.echo(f"Collaborators: {', '.join(contract.people)}")
        elif license is None:
            typer.echo("Project Settings updated. The project slug and folder were unchanged.")
    except ProjectError as error:
        _command_error(error)


@app.command("inspect")
def inspect(
    path: Path | None = typer.Argument(None, help="Project directory or current project."),
    hashes: bool = typer.Option(False, help="Include expected managed-file SHA-256 hashes."),
) -> None:
    """Show the project contract, managed-file ownership, and local tool paths."""
    root = _project_or_exit(path, remember=False)
    try:
        contract = load_contract(root)
        typer.echo("Full project contract:")
        typer.echo(
            yaml.safe_dump(contract.model_dump(mode="json", exclude_none=True), sort_keys=False),
            nl=False,
        )
        typer.echo("Managed files:")
        for status in managed_file_statuses(root):
            line = f"- {status['path']}: {status['status']}"
            if hashes:
                line += f" (expected SHA-256: {status['expected_hash']})"
            typer.echo(line)
        typer.echo("Detected local tools:")
        for label, executable in detected_tools(root).items():
            typer.echo(f"- {label}: {executable}")
    except ProjectError as error:
        _command_error(error)


@app.command("regenerate")
def regenerate(
    path: Path | None = typer.Argument(None, help="Project directory or current project."),
    select: list[str] = typer.Option(
        [], "--select", help="Missing or unchanged managed asset path."
    ),
    confirm: bool = typer.Option(False, help="Write the previewed managed assets."),
) -> None:
    """Preview and restore only missing or unmodified managed guidance and templates."""
    root = _project_or_exit(path)
    try:
        if not select:
            typer.echo("Managed assets eligible for regeneration:")
            for relative in managed_asset_paths(root):
                typer.echo(f"- {relative}")
            typer.echo(
                "Select paths with --select PATH. Add --confirm only after reviewing the preview."
            )
            return
        preview = managed_asset_previews(root, select)
    except ProjectError as error:
        _command_error(error)
        return
    typer.echo("Regeneration preview (modified files are refused and preserved):")
    for item in preview:
        typer.echo(f"- {item['path']}: {item['status']}")
    if not confirm:
        typer.echo(
            "No changes made. Re-run with the same --select values and --confirm to regenerate."
        )
        return
    regenerate_managed_assets(root, select)
    typer.echo("Selected managed assets regenerated.")


class Dashboard:
    def __init__(self, root: Path) -> None:
        self.root = root
        motion = _interactive_motion_enabled(root)
        self.console = Console(force_interactive=motion, force_terminal=motion)
        self.session: PromptSession[str] = PromptSession(
            input=create_input(sys.stdin), output=create_output(sys.stdout)
        )

    def run(self) -> None:
        while True:
            if _interactive_motion_enabled(self.root):
                with self.console.status("Loading project dashboard...", spinner="dots"):
                    contract = load_contract(self.root)
                    advanced = local_preferences(self.root).get("experience") == "advanced"
            else:
                contract = load_contract(self.root)
                advanced = local_preferences(self.root).get("experience") == "advanced"
            mode = "Advanced" if advanced else "Standard"
            self.console.rule(f"[bold cyan]SMAIRT {mode} Mode: {contract.project.name}[/]")
            self.console.print("1. Launch assistant or open folder")
            self.console.print("2. Project Settings")
            self.console.print(f"3. Paper Support: {contract.capabilities['paper'].state.value}")
            self.console.print(f"4. HPC Support: {contract.capabilities['hpc'].state.value}")
            self.console.print("5. Project Check")
            self.console.print("6. Help")
            if advanced:
                self.console.print("7. Inspect project contract")
                self.console.print("8. Verbose Project Check")
                self.console.print("9. Regenerate managed assets")
                self.console.print("10. Customize prompt and code conventions")
                self.console.print("11. Detected local tools")
                self.console.print("12. Exit")
            else:
                self.console.print("7. Exit")
            action = self.session.prompt("Choose an action: ").strip()
            if action == "1":
                self._assistant()
            elif action == "2":
                self._settings()
            elif action in {"3", "4"}:
                self._capability("paper" if action == "3" else "hpc")
            elif action == "5":
                self._check()
            elif action == "6":
                self.console.print(
                    "SMAIRT manages project utilities only. Conduct scientific work in your selected assistant."
                )
            elif advanced and action == "7":
                self._inspect()
            elif advanced and action == "8":
                self._check(verbose=True)
            elif advanced and action == "9":
                self._regenerate()
            elif advanced and action == "10":
                self._conventions()
            elif advanced and action == "11":
                self._tools()
            elif action in ({"12", "exit", "q"} if advanced else {"7", "exit", "q"}):
                return
            else:
                self.console.print("Choose a listed action.", style="yellow")

    def _assistant(self) -> None:
        message = prepare_assistant(self.root)
        self.console.print(message)
        action = self.session.prompt("Enter launch, folder, or back: ").strip().lower()
        if action == "launch":
            _, message = launch_assistant(self.root)
            self.console.print(message)
        elif action == "folder":
            self.console.print(open_folder(self.root))

    def _capability(self, name: str) -> None:
        action = (
            self.session.prompt(f"Enter enable, disable, or back for {_capability_label(name)}: ")
            .strip()
            .lower()
        )
        if action == "enable":
            self.console.print(enable_capability(self.root, name))
        elif action == "disable":
            self.console.print(disable_capability(self.root, name))

    def _check(self, *, verbose: bool = False) -> None:
        issues = project_check(self.root)
        if not issues:
            self.console.print("Project Check passed: no structural or configuration issues found.")
        else:
            for issue in issues:
                self.console.print(f"- [{issue.code}] {issue.message}")
                if verbose:
                    self.console.print(f"  Artifact: {issue.path}")
                    self.console.print(
                        "  Diagnostic is read-only; researcher content is never changed by Project Check."
                    )
            repairable = [issue for issue in issues if issue.repair is not None]
            if repairable:
                self.console.print("Safe repairs available:")
                for issue in repairable:
                    assert issue.repair is not None
                    self.console.print(f"- {issue.repair}: {issue.message}")
                selection = self.session.prompt(
                    "Enter repair identifiers separated by commas, or back: "
                ).strip()
                if selection not in {"", "back"}:
                    self._repair([item.strip() for item in selection.split(",") if item.strip()])
        if verbose:
            self._tools()

    def _repair(self, identifiers: list[str]) -> None:
        try:
            preview = repair_previews(self.root, identifiers)
        except ProjectError as error:
            self.console.print(str(error), style="yellow")
            return
        for issue in preview:
            assert issue.repair is not None
            self.console.print(f"Preview: {issue.repair}: {issue.message}")
        confirmed = self.session.prompt("Apply these safe repairs [yes/no]: ").strip().lower()
        if confirmed not in {"yes", "y"}:
            self.console.print("No changes made.")
            return
        apply_repairs(self.root, identifiers)
        self.console.print("Selected safe repairs applied.")

    def _inspect(self) -> None:
        contract = load_contract(self.root)
        self.console.print("Full project contract:")
        self.console.print(
            yaml.safe_dump(contract.model_dump(mode="json", exclude_none=True), sort_keys=False)
        )
        self.console.print("Managed files:")
        try:
            for status in managed_file_statuses(self.root):
                self.console.print(f"- {status['path']}: {status['status']}")
        except ProjectError as error:
            self.console.print(str(error), style="yellow")

    def _tools(self) -> None:
        self.console.print("Detected local tools:")
        for label, executable in detected_tools(self.root).items():
            self.console.print(f"- {label}: {executable}")

    def _regenerate(self) -> None:
        try:
            available = managed_asset_paths(self.root)
        except ProjectError as error:
            self.console.print(str(error), style="yellow")
            return
        self.console.print("Managed assets:")
        for relative in available:
            self.console.print(f"- {relative}")
        relative = self.session.prompt("Asset path to regenerate, or back: ").strip()
        if relative in {"", "back"}:
            return
        try:
            preview = managed_asset_previews(self.root, [relative])
        except ProjectError as error:
            self.console.print(str(error), style="yellow")
            return
        self.console.print(f"Preview: {preview[0]['path']} is {preview[0]['status']}.")
        if self.session.prompt("Regenerate this managed asset [yes/no]: ").strip().lower() in {
            "yes",
            "y",
        }:
            regenerate_managed_assets(self.root, [relative])
            self.console.print("Managed asset regenerated.")
        else:
            self.console.print("No changes made.")

    def _conventions(self) -> None:
        prompt = self.session.prompt(
            "Prompt convention [plan-first/direct-task, Enter to keep]: "
        ).strip()
        code = self.session.prompt(
            "Code convention [typed-python/standard-python, Enter to keep]: "
        ).strip()
        try:
            update_settings(
                self.root,
                prompt_convention=PromptConvention(prompt) if prompt else None,
                code_convention=CodeConvention(code) if code else None,
            )
        except (ProjectError, ValueError):
            self.console.print("Use only the listed prompt and code conventions.", style="yellow")
        else:
            self.console.print("Conventions updated.")

    def _settings(self) -> None:
        while True:
            self.console.print("Project Settings")
            self.console.print("1. Project name")
            self.console.print("2. Description")
            self.console.print("3. Domain")
            self.console.print("4. Research question")
            self.console.print("5. Primary researcher")
            self.console.print("6. Assistant")
            self.console.print("7. Current phase")
            self.console.print("8. Collaborator")
            self.console.print("9. License")
            self.console.print("10. Local experience and motion")
            self.console.print("11. Back")
            action = self.session.prompt("Choose a setting: ").strip()
            contract = load_contract(self.root)
            if action == "1":
                update_settings(self.root, name=self._required("Project name"))
            elif action == "2":
                update_settings(self.root, description=self._required("Description"))
            elif action == "3":
                update_settings(self.root, domain=self._required("Domain"))
            elif action == "4":
                update_settings(
                    self.root,
                    question=self.session.prompt("Research question (blank clears it): ").strip(),
                )
            elif action == "5":
                update_settings(self.root, researcher=self._required("Primary researcher"))
            elif action == "6":
                self.console.print("Available: zoo-code, claude-code, opencode, codex, pi, cursor")
                try:
                    update_settings(self.root, assistant=Assistant(self._required("Assistant")))
                except ValueError:
                    self.console.print("Choose one of the listed assistants.", style="yellow")
            elif action == "7":
                self.console.print(
                    "Available: synthetic, downloaded, real. Existing directories are never deleted."
                )
                try:
                    update_settings(self.root, phase=StartingPhase(self._required("Current phase")))
                except ValueError:
                    self.console.print("Choose synthetic, downloaded, or real.", style="yellow")
            elif action == "8":
                role = self._required("Collaborator role")
                try:
                    update_collaborator(
                        self.root,
                        role,
                        self._required("Collaborator name"),
                        self.session.prompt("Collaborator email (blank omits it): ").strip()
                        or None,
                    )
                except ProjectError as error:
                    self.console.print(str(error), style="yellow")
            elif action == "9":
                self._license(contract)
            elif action == "10":
                self._preferences()
            elif action in {"11", "back", "q"}:
                return
            else:
                self.console.print("Choose a listed setting.", style="yellow")

    def _required(self, label: str) -> str:
        while True:
            value = self.session.prompt(f"{label}: ").strip()
            if value:
                return value
            self.console.print(f"{label} is required.", style="yellow")

    def _license(self, contract: ProjectContract) -> None:
        self.console.print("License changes can affect legal rights. This is not legal advice.")
        for number, license in enumerate(License, start=1):
            self.console.print(f"{number}. {license.value} - {LICENSE_EXPLANATIONS[license]}")
        choice = self.session.prompt("Choose a license or press Enter to cancel: ").strip()
        if not choice.isdigit() or not 1 <= int(choice) <= len(License):
            return
        selected = tuple(License)[int(choice) - 1]
        self.console.print("Preview:")
        self.console.out(license_preview(self.root, selected), end="")
        confirmed = self.session.prompt("Replace unmodified legal text [yes/no]: ").strip().lower()
        if confirmed not in {"yes", "y"}:
            self.console.print("No license change made.")
            return
        try:
            change_license(self.root, selected)
        except ProjectError as error:
            self.console.print(str(error), style="yellow")
        else:
            self.console.print(f"License changed to {selected.value}.")

    def _preferences(self) -> None:
        preferences = local_preferences(self.root)
        experience = (
            self.session.prompt("Experience [standard/advanced, Enter to keep]: ").strip().lower()
        )
        motion = self.session.prompt("Motion [yes/no, Enter to keep]: ").strip().lower()
        if experience:
            if experience not in {"standard", "advanced"}:
                self.console.print("Experience must be standard or advanced.", style="yellow")
                return
            preferences["experience"] = experience
        if motion:
            if motion not in {"yes", "y", "no", "n"}:
                self.console.print("Motion must be yes or no.", style="yellow")
                return
            preferences["motion"] = motion in {"yes", "y"}
        save_local_preferences(self.root, preferences)


def _capability_label(name: str) -> str:
    return "Paper" if name == "paper" else "HPC"


def _home() -> None:
    try:
        root = resolve_project()
    except ProjectError:
        root = None
    if root is not None:
        record_recent(root)
        Dashboard(root).run()
        return
    session: PromptSession[str] = PromptSession(
        input=create_input(sys.stdin), output=create_output(sys.stdout)
    )
    motion = _interactive_motion_enabled()
    console = Console(force_interactive=motion, force_terminal=motion)
    while True:
        console.rule("[bold cyan]SMAIRT Home[/]")
        console.print("1. Create New Project")
        console.print("2. Recent Projects")
        console.print("3. Open Existing Project")
        console.print("4. Help")
        console.print("5. Exit")
        action = session.prompt("Choose an action: ").strip()
        if action == "1":
            try:
                destination, options = Wizard().run()
                messages = generate_project(destination, options)
            except (WizardCancelled, GenerationError, ValidationError, OSError) as error:
                console.print(f"Project creation cancelled or failed: {error}", style="yellow")
            else:
                root = destination.resolve()
                record_recent(root)
                console.print(f"Created SMAIRT project at {root}")
                for message in messages:
                    console.print(message)
                Dashboard(root).run()
        elif action == "2":
            recents = recent_projects()
            if not recents:
                console.print("No recent SMAIRT projects.")
                continue
            for index, entry in enumerate(recents, start=1):
                console.print(f"{index}. {entry['path']}")
            selection = session.prompt(
                "Select a project number, or press Enter to go back: "
            ).strip()
            if selection.isdigit() and 1 <= int(selection) <= len(recents):
                root = _project_or_exit(Path(recents[int(selection) - 1]["path"]))
                Dashboard(root).run()
        elif action == "3":
            try:
                root = _project_or_exit(Path(session.prompt("Project folder: ").strip()))
            except (ProjectError, typer.Exit):
                continue
            Dashboard(root).run()
        elif action == "4":
            console.print(
                "SMAIRT creates and safely manages workspace utilities. It does not conduct scientific work."
            )
        elif action in {"5", "exit", "q"}:
            return
        else:
            console.print("Choose a listed action.", style="yellow")


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
    accept_license: bool = typer.Option(
        False,
        "--accept-license",
        help="Confirm the selected license for noninteractive creation.",
    ),
    question: str | None = typer.Option(None, help="Optional research question."),
    email: str | None = typer.Option(None, help="Optional researcher email."),
    paper: bool = typer.Option(False, help="Include additive Paper support."),
    hpc: bool = typer.Option(False, help="Include additive HPC guidance."),
    initialize_git: bool = typer.Option(
        False, "--git/--no-git", help="Initialize and stage Git files."
    ),
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
        name is None or slug is None or description is None or researcher is None or domain is None
    ):
        typer.echo(
            "Error: --name, --slug, --description, --researcher, and --domain are required with a destination.",
            err=True,
        )
        raise typer.Exit(code=2)
    if not wizard_mode and not accept_license:
        typer.echo(
            "Error: review the selected license and pass --accept-license to create the project.",
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
    record_recent(destination.resolve())
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


def _interactive_motion_enabled(root: Path | None = None) -> bool:
    motion = local_preferences(root).get("motion") if root is not None else None
    return (
        motion is not False
        and sys.stdin.isatty()
        and sys.stdout.isatty()
        and os.environ.get("TERM", "") not in {"", "dumb"}
        and not os.environ.get("CI")
        and not os.environ.get("PYTEST_CURRENT_TEST")
    )


def main() -> None:
    app()
