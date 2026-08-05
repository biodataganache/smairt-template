from __future__ import annotations

import os
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
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
from smairt.appearance import rich_theme, styling_enabled
from smairt.generator import (
    GenerationError,
    absolute_destination,
    generate_project,
    validate_destination,
)
from smairt.menu import (
    Action,
    MenuChoice,
    divider,
    escape_token,
    numbered_lines,
    resolve_action,
    tokens_of,
)
from smairt.messages import (
    describe_slug_rejection,
    describe_unexpected_error,
    describe_validation_error,
    slug_rejection_in,
)
from smairt.models import (
    Assistant,
    CapabilityState,
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
    OPTIONAL_CAPABILITIES,
    CapabilityPlan,
    ProjectError,
    apply_repairs,
    apply_upgrade,
    assistant_launch_status,
    capability_plan,
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
    next_workflow_action,
    open_folder,
    prepare_assistant,
    project_check,
    recent_projects,
    record_recent,
    regenerate_managed_assets,
    repair_previews,
    require_upgradable,
    resolve_project,
    save_local_preferences,
    set_capabilities,
    update_collaborator,
    update_settings,
    upgrade_plan,
)
from smairt.terminal import (
    BackRequested,
    SelectionCancelled,
    confirm,
    navigation_bindings,
    select_choice,
    select_many,
    select_menu,
)

app = typer.Typer(no_args_is_help=False, invoke_without_command=True)

_SKIP = ":skip"
_BACK = ":back"
_CANCEL = ":cancel"
_OPTIONAL_CAPABILITIES = {"paper", "hpc"}
_NO_CAPABILITIES = "none"
"""The mutually exclusive choice meaning a workspace with no optional capabilities."""


def _themed_console(motion: bool) -> Console:
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


def _parse_capabilities(answer: str) -> set[str]:
    """Split a comma-separated capability answer into a set of requested names."""
    return {item.strip() for item in answer.split(",") if item.strip()}


def _requested_capabilities(answer: str, console: Console) -> set[str] | None:
    """Return the capabilities a typed answer requests, or None when it is refused.

    The mutual exclusion the visual screen enforces by construction has to be
    enforced by hand here, in one place, so the two presentations cannot drift
    into disagreeing about what a contradictory answer means.
    """
    requested = _parse_capabilities(answer.lower())
    if _NO_CAPABILITIES in requested and requested != {_NO_CAPABILITIES}:
        console.print(
            "None means no optional capabilities, so it cannot be combined with one.",
            style="caution",
        )
        return None
    requested -= {_NO_CAPABILITIES}
    if not requested <= _OPTIONAL_CAPABILITIES:
        console.print("Use paper, hpc, paper,hpc, or none.", style="caution")
        return None
    return requested


class WizardCancelled(Exception):
    """Raised when the user intentionally leaves guided project creation."""


@dataclass(frozen=True)
class Step:
    """One wizard screen: what it is called, how it runs, and how it reviews."""

    token: str
    title: str
    run: Callable[[], None]
    summarize: Callable[[], str]


class Wizard:
    def __init__(self) -> None:
        motion = _interactive_motion_enabled()
        self.visual = motion
        self.console = _themed_console(motion)
        self.session: PromptSession[str] = PromptSession(
            input=create_input(sys.stdin),
            output=create_output(sys.stdout),
            key_bindings=navigation_bindings() if motion else None,
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
        self.steps: tuple[Step, ...] = (
            Step("name", "Project name", self._name, lambda: self._answer("name")),
            Step("location", "Location", self._location, self._location_summary),
            Step(
                "description", "Description", self._description, lambda: self._answer("description")
            ),
            Step("domain", "Domain", self._domain, lambda: self._answer("domain")),
            Step("question", "Research question", self._question, lambda: self._answer("question")),
            Step(
                "researcher",
                "Primary researcher",
                self._researcher,
                lambda: self._answer("researcher"),
            ),
            Step("email", "Email", self._email, lambda: self._answer("email")),
            Step(
                "capabilities",
                "Optional capabilities",
                self._capabilities,
                self._capability_summary,
            ),
            Step(
                "phase", "Starting phase", self._phase, lambda: _phase_label(self._answer("phase"))
            ),
            Step(
                "assistant",
                "Coding assistant",
                self._assistant,
                lambda: _assistant_label(self._answer("assistant")),
            ),
            Step("license", "License", self._license, lambda: self._answer("license")),
            Step(
                "license_confirmation",
                "License confirmation",
                self._confirm_license,
                lambda: self._answer("license"),
            ),
            Step("git", "Git", self._git, lambda: "Yes" if self.answers["git"] else "No"),
        )
        self.review_step = Step("review", "Final review", self._review, lambda: "")

    @property
    def total_steps(self) -> int:
        """Report how many screens a researcher walks through, review included."""
        return len(self.steps) + 1

    def run(self) -> tuple[Path, ProjectOptions]:
        index = 0
        while index <= len(self.steps):
            step = self.steps[index] if index < len(self.steps) else self.review_step
            self._screen(index, step.title)
            try:
                step.run()
            except BackRequested:
                if index == 0:
                    self.console.print("This is the first screen. Enter :cancel to leave setup.")
                else:
                    index -= 1
                    self.console.print("Back: your earlier answers are kept.")
                continue
            except SelectionCancelled as error:
                raise WizardCancelled from error
            index += 1
        return Path(str(self.answers["destination"])).expanduser(), self._options()

    def _screen(self, index: int, title: str) -> None:
        progress = f"Step {index + 1} of {self.total_steps}"
        self.console.rule(f"[title]{progress}: {title}[/]")
        self.console.print("You can change every answer during final review.", style="hint")

    def _answer(self, key: str) -> str:
        """Return a recorded answer, naming an intentionally blank one plainly."""
        return str(self.answers.get(key, "")) or "Skipped"

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
                "Please enter a value, or use :skip for this optional question.", style="caution"
            )

    def _choose(
        self,
        prompt: str,
        *,
        key: str,
        choices: tuple[tuple[str, str, str, str], ...],
        default: str,
    ) -> str:
        current = str(self.answers.get(key, default))
        values = {value for _, _, value, _ in choices}
        if current not in values:
            current = "custom" if key == "domain" and self.answers.get("custom_domain") else default
        if self.visual:
            try:
                selection = select_choice(
                    prompt,
                    [
                        (value, f"{label} - {explanation}")
                        for _, label, value, explanation in choices
                    ],
                    current,
                )
            except SelectionCancelled as error:
                raise WizardCancelled from error
            self.answers[key] = selection
            return selection
        self.console.print("Recommended choices are marked.")
        for number, label, value, explanation in choices:
            recommended = " [recommended]" if value == default else ""
            self.console.print(f"  {number}. {label}{recommended} - {explanation}")
        mapping = {number: value for number, _, value, _ in choices}
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
            self.console.print("Choose one of the listed numbers.", style="caution")

    def _location(self) -> None:
        """Confirm one folder name, deriving the immutable identifier from it.

        The folder and the identifier are two spellings of the same decision, so
        the researcher confirms the folder once and sees what it derives. Only the
        two short names are previewed; the absolute path is noise at this point.
        """
        mode = self._choose(
            "Where should this project live",
            key="location_mode",
            default="workspace",
            choices=(
                (
                    "1",
                    "Create in this workspace",
                    "workspace",
                    f"Create a new child folder under {Path.cwd()}.",
                ),
                (
                    "2",
                    "Choose another location",
                    "other",
                    "Choose an existing parent directory.",
                ),
            ),
        )
        if mode == "workspace":
            parent = Path.cwd()
        else:
            parent_text = self._ask(
                "Parent directory",
                key="other_parent",
                default=str(Path.home() / "Documents"),
            )
            parent = Path(parent_text).expanduser()
        while True:
            folder = self._ask(
                "Project folder name",
                key="folder",
                default=_folder_name(str(self.answers["name"])),
            )
            if Path(folder).name != folder or folder in {".", ".."}:
                self.console.print("Project folder must be one folder name.", style="caution")
                continue
            identifier = _slugify(folder)
            if not self._identifier_is_valid(identifier):
                continue
            destination = (parent / folder).expanduser()
            try:
                validate_destination(destination)
            except GenerationError as error:
                self.console.print(f"That location is not safe: {error}", style="caution")
                continue
            self.answers["destination"] = str(destination)
            self.answers["slug"] = identifier
            self.console.print(f"Folder: [value]{folder}[/]")
            self.console.print(f"Identifier: [value]{identifier}[/]")
            self.console.print(f"Will create: {destination}")
            return

    def _identifier_is_valid(self, identifier: str) -> bool:
        """Report whether a derived identifier satisfies the contract's rules."""
        try:
            ProjectIdentity(
                name=str(self.answers["name"]),
                slug=identifier,
                description="placeholder",
                domain="placeholder",
            )
        except ValidationError as error:
            rejected = slug_rejection_in(error)
            self.console.print(
                describe_slug_rejection(rejected)
                if rejected is not None
                else describe_validation_error(error),
                style="caution",
            )
            self.console.print(
                "Choose a folder name that starts with a letter and uses letters, "
                "digits, and hyphens.",
                style="hint",
            )
            return False
        return True

    def _location_summary(self) -> str:
        return f"{Path(self._answer('destination')).name} ({self._answer('slug')})"

    def _name(self) -> None:
        """Record the readable name, offering it as the folder default only.

        The folder is confirmed on its own screen and the identifier derives from
        it, so renaming the project later never silently moves a chosen folder or
        rewrites an identifier the researcher has already seen.
        """
        previous_default = _folder_name(str(self.answers.get("name", "")))
        name = self._ask("What is the human-readable project name", key="name")
        if self.answers.get("folder") in {None, previous_default}:
            self.answers["folder"] = _folder_name(name)

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
        """Check the capabilities this project expects, or the default workspace.

        Paper and HPC are independent, so the researcher checks each rather than
        picking from every combination. Default Workspace is mutually exclusive
        with both by construction, so a contradiction is unreachable.
        """
        if self.visual:
            try:
                selection = select_many(
                    "Optional capabilities",
                    [
                        (_NO_CAPABILITIES, "Default Workspace (no optional capabilities)"),
                        ("paper", "Do you expect to write a paper?"),
                        ("hpc", "Do you expect to use an HPC?"),
                    ],
                    self._checked_capabilities(),
                    details=(
                        "Both are additive and can be enabled or disabled later.",
                        "Space toggles a capability; choose Next when you are done.",
                    ),
                    exclusive=_NO_CAPABILITIES,
                )
            except SelectionCancelled as error:
                raise WizardCancelled from error
            self._record_capabilities(set(selection) - {_NO_CAPABILITIES})
            return
        self.console.print(
            "Paper and HPC support are optional and both start off for a default workspace."
        )
        self.console.print("Type paper, hpc, paper,hpc, none, or press Enter to skip.")
        while True:
            answer = self.session.prompt("Optional capabilities [Enter to skip]: ").strip()
            if answer == _CANCEL:
                raise WizardCancelled
            if answer == _BACK:
                raise BackRequested
            requested = _requested_capabilities(answer, self.console)
            if requested is not None:
                self._record_capabilities(requested)
                return

    def _checked_capabilities(self) -> list[str]:
        """Return the rows to start checked, naming the default workspace explicitly."""
        chosen = [name for name in ("paper", "hpc") if self.answers[name]]
        return chosen or [_NO_CAPABILITIES]

    def _record_capabilities(self, requested: set[str]) -> None:
        self.answers["paper"] = "paper" in requested
        self.answers["hpc"] = "hpc" in requested

    def _capability_summary(self) -> str:
        chosen = [_capability_label(name) for name in ("paper", "hpc") if self.answers[name]]
        return ", ".join(chosen) if chosen else "Default Workspace"

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
            default=License.MIT.value,
            # Derived from the License enum rather than restated, so a license can never be
            # offered here without shipped legal text behind it.
            choices=tuple(
                (str(number), item.value, item.value, LICENSE_EXPLANATIONS[item])
                for number, item in enumerate(License, start=1)
            ),
        )
        if str(self.answers["license"]) != previous_license:
            self.answers["license_confirmation"] = ""

    def _confirm_license(self) -> None:
        self.console.print(
            f"{self.answers['license']} controls how others may use this project. This is not legal advice."
        )
        if self.visual:
            try:
                confirmed = select_choice(
                    "Confirm this license",
                    [("yes", "Yes, confirm"), ("no", "No, choose another license")],
                    "yes" if self.answers["license_confirmation"] else "no",
                )
            except SelectionCancelled as error:
                raise WizardCancelled from error
            if confirmed == "yes":
                self.answers["license_confirmation"] = str(self.answers["license"])
                return
            raise BackRequested
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
            self.console.print("Please answer yes or no.", style="caution")

    def _git(self) -> None:
        self.console.print(
            "Git is recommended for history, but it is optional. SMAIRT will stage files and never commit."
        )
        if self.visual:
            try:
                requested = select_choice(
                    "Initialize Git",
                    [(False, "No"), (True, "Yes, initialize and stage files")],
                    bool(self.answers["git"]),
                )
            except SelectionCancelled as error:
                raise WizardCancelled from error
            self.answers["git"] = requested
            return
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
            self.console.print("Please answer yes or no.", style="caution")

    def _review_actions(self) -> tuple[Action, ...]:
        """Return the review rows: every answer first, then a divider, then the actions.

        Creating the project is kept away from the answers it would act on, so
        reviewing and committing are never one keystroke apart.
        """
        return (
            *(Action(step.token, f"{step.title}: {step.summarize()}") for step in self.steps),
            divider("─── Then ───"),
            Action("create", "Create project"),
            Action("cancel", "Cancel without creating files"),
        )

    def _review(self) -> None:
        actions = self._review_actions()
        if self.visual:
            self._visual_review()
            return
        while True:
            self._print_review(actions)
            typed = self.session.prompt("Review action: ").strip()
            if typed == _CANCEL:
                raise WizardCancelled
            if typed == _BACK:
                raise BackRequested
            answer = resolve_action(typed, actions)
            if answer == "cancel":
                raise WizardCancelled
            if answer == "create":
                self._ensure_license_confirmed()
                return
            if answer is None:
                self.console.print("Choose one of the listed actions.", style="caution")
                continue
            self._edit(answer)
            self._screen(len(self.steps), "Final review")

    def _visual_review(self) -> None:
        while True:
            actions = self._review_actions()
            try:
                answer = select_menu(
                    "Final review",
                    MenuChoice.rows(actions),
                    "create",
                    details=("Choose any answer to edit it, or Create project when ready.",),
                )
            except (BackRequested, SelectionCancelled) as error:
                raise WizardCancelled from error
            if answer == "create":
                self._ensure_license_confirmed()
                return
            if answer == "cancel":
                raise WizardCancelled
            self._edit(answer)
            self._screen(len(self.steps), "Final review")

    def _print_review(self, actions: tuple[Action, ...]) -> None:
        self.console.print("[heading]Final review[/]")
        for line in numbered_lines(actions):
            self.console.print(f"  {line}", markup=False)

    def _ensure_license_confirmed(self) -> None:
        if self.answers["license_confirmation"] != self.answers["license"]:
            self.console.print(
                "Confirm the final selected license before creating the project.",
                style="caution",
            )
            self._confirm_license()

    def _edit(self, token: str) -> None:
        index, step = next(
            (index, step) for index, step in enumerate(self.steps) if step.token == token
        )
        self._screen(index, f"Edit {step.title}")
        step.run()

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


# Exit codes are a contract with scripts, so they mean one thing each across every command:
#   0  the command did what it said
#   1  the project was found, and the operation failed or reported findings
#   2  the command could not be carried out as asked: no project, or unusable arguments
# `check` established this split deliberately, and every other command now follows it, so a
# script can tell "this is not a project" from "this project has problems" without parsing text.
CANNOT_PROCEED = 2
OPERATION_FAILED = 1


def _project_or_exit(path: Path | None, *, remember: bool = True) -> Path:
    try:
        root = resolve_project(path)
    except ProjectError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=CANNOT_PROCEED) from error
    if remember:
        record_recent(root)
    return root


def _command_error(error: ProjectError) -> None:
    typer.echo(f"Error: {error}", err=True)
    raise typer.Exit(code=OPERATION_FAILED) from error


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
            raise typer.Exit(code=OPERATION_FAILED)
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
    # A read-only diagnostic does not count as opening a project, so it is not remembered.
    root = _project_or_exit(path, remember=False)
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
        raise typer.Exit(code=OPERATION_FAILED)


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
            # Checked before listing, because an out-of-date project would otherwise be told
            # "No safe repairs are available" and exit 0 while every repair is in fact blocked.
            require_upgradable(root, "repair package-owned structure")
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
    # Guarded, because this is the write. A disk-full or permissions failure here used to
    # produce a traceback at the exact moment a researcher most needs to know what state their
    # project is in.
    try:
        apply_repairs(root, select)
    except (ProjectError, OSError) as error:
        typer.echo(f"Error: repair failed partway; run `smairt check` to see the result: {error}")
        raise typer.Exit(code=OPERATION_FAILED) from error
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
    declare_multiplicity_policy: bool | None = typer.Option(
        None, help="Add multiplicity-policy prompts to newly created research files."
    ),
    separate_discovery_validation: bool | None = typer.Option(
        None, help="Add discovery/validation-role prompts to newly created research files."
    ),
    declare_unit_of_inference: bool | None = typer.Option(
        None, help="Add unit-of-inference prompts to newly created research files."
    ),
    track_per_probe_status: bool | None = typer.Option(
        None, help="Add per-probe hypothesis-status prompts to newly created research files."
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
            declare_multiplicity_policy=declare_multiplicity_policy,
            separate_discovery_validation=separate_discovery_validation,
            declare_unit_of_inference=declare_unit_of_inference,
            track_per_probe_status=track_per_probe_status,
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
                declare_multiplicity_policy,
                separate_discovery_validation,
                declare_unit_of_inference,
                track_per_probe_status,
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


@app.command("upgrade")
def upgrade(
    path: Path | None = typer.Argument(None, help="Project directory or current project."),
    confirm: bool = typer.Option(False, help="Apply the previewed upgrade."),
) -> None:
    """Preview and apply moving a project onto the installed scaffold version."""
    root = _project_or_exit(path)
    try:
        plan = upgrade_plan(root)
    except ProjectError as error:
        _command_error(error)
        return
    if plan.is_current:
        typer.echo(f"Project is already on the installed SMAIRT {plan.to_version}.")
        return
    typer.echo(f"Upgrade preview: scaffold {plan.from_version} to {plan.to_version}")
    for label, changes in (
        ("Would be updated to the installed guidance", plan.updates),
        ("Would be created", plan.creates),
    ):
        if changes:
            typer.echo(f"{label}:")
            for change in changes:
                typer.echo(f"- {change.path}")
    if plan.preserved:
        # Deliberately not called "modified": for an editable starter, a difference from the
        # installed text may be the researcher's edit or may be a change the newer scaffold
        # made to the starter itself. SMAIRT cannot tell those apart, so it keeps the file
        # either way and says so without asserting who changed it.
        typer.echo("Differs from the installed version, so kept exactly as it is:")
        for change in plan.preserved:
            typer.echo(f"- {change.path}")
    typer.echo(
        f"Already current: {len(plan.unchanged)} file(s). "
        "Researcher work is never read, rewritten, or judged by an upgrade."
    )
    if not confirm:
        typer.echo("No changes made. Re-run with --confirm to apply this upgrade.")
        return
    try:
        apply_upgrade(root)
    except (ProjectError, OSError) as error:
        typer.echo(f"Error: upgrade failed and the project stays on {plan.from_version}: {error}")
        raise typer.Exit(code=OPERATION_FAILED) from error
    typer.echo(f"Project upgraded to scaffold {plan.to_version}.")


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
            # Checked before listing, because an out-of-date project would otherwise be shown
            # every managed asset as "eligible" and then refused on --confirm.
            require_upgradable(root, "regenerate managed assets")
            statuses = {item["path"]: item["status"] for item in managed_file_statuses(root)}
            actionable = [
                relative
                for relative in managed_asset_paths(root)
                if statuses.get(relative) in {"missing", "unchanged"}
            ]
            if not actionable:
                typer.echo("No managed assets are eligible for regeneration.")
                return
            typer.echo("Managed assets eligible for regeneration:")
            for relative in actionable:
                typer.echo(f"- {relative}: {statuses[relative]}")
            preserved = sorted(
                relative
                for relative in managed_asset_paths(root)
                if statuses.get(relative) == "modified"
            )
            if preserved:
                typer.echo("Modified and preserved, so not eligible:")
                for relative in preserved:
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
    # Guarded for the same reason as repair: this is the write, and a failure here needs to
    # say what to do rather than print a traceback.
    try:
        regenerate_managed_assets(root, select)
    except (ProjectError, OSError) as error:
        typer.echo(
            f"Error: regeneration failed partway; run `smairt check` to see the result: {error}"
        )
        raise typer.Exit(code=OPERATION_FAILED) from error
    typer.echo("Selected managed assets regenerated.")


class Dashboard:
    def __init__(self, root: Path) -> None:
        self.root = root
        motion = _interactive_motion_enabled(root)
        self.visual = motion
        self.console = _themed_console(motion)
        self.session: PromptSession[str] = PromptSession(
            input=create_input(sys.stdin), output=create_output(sys.stdout)
        )

    def _home_actions(self, contract: ProjectContract, advanced: bool) -> tuple[Action, ...]:
        """Return the Dashboard rows, folding the advanced tools behind one row.

        Advanced work is one row rather than six, so the everyday menu stays the
        length of the everyday tasks. The row is only offered when the local
        preference asks for it, and a hint names it when it is not.
        """
        summary = ", ".join(
            _capability_label(name)
            for name in OPTIONAL_CAPABILITIES
            if contract.capabilities[name].state is CapabilityState.ENABLED
        )
        state, _ = next_workflow_action(self.root)
        _, _, launch = assistant_launch_status(self.root)
        return (
            Action("next", f"Where the work stands: {state}"),
            Action("assistant", f"Launch {launch}, or open the folder"),
            Action("settings", "Project Settings"),
            Action("capabilities", f"Optional capabilities: {summary or 'Default Workspace'}"),
            Action("check", "Project Check"),
            Action("help", "Help"),
            *((Action("advanced", "Advanced ▸"),) if advanced else ()),
            Action("exit", "Exit"),
        )

    def run(self) -> None:
        while True:
            contract, advanced = self._load()
            mode = "Advanced" if advanced else "Standard"
            actions = self._home_actions(contract, advanced)
            self.console.rule(f"[title]SMAIRT {mode} Mode: {contract.project.name}[/]")
            if not advanced:
                self.console.print(
                    "Advanced mode adds contract inspection, asset regeneration, and "
                    "convention controls. Turn it on in Project Settings.",
                    style="hint",
                )
            action = self._menu("Choose an action", actions)
            if action == "next":
                self._orientation()
            elif action == "assistant":
                self._assistant()
            elif action == "settings":
                self._settings()
            elif action == "capabilities":
                self._capabilities()
            elif action == "check":
                self._check()
            elif action == "help":
                self.console.print(
                    "SMAIRT manages project utilities only. Conduct scientific work in your "
                    "selected assistant."
                )
                self.console.print(
                    "The workflow itself is documented in docs/12_STEPS.md, the files to read "
                    "for a given task in prompts/CONTEXT_INDEX.md, and the helpers in "
                    "scripts/README.md."
                )
            elif action == "advanced":
                self._advanced()
            elif action == "exit":
                return

    def _load(self) -> tuple[ProjectContract, bool]:
        """Read the contract and the local experience preference for one pass."""
        if _interactive_motion_enabled(self.root):
            with self.console.status("Loading project dashboard...", spinner="dots"):
                return (
                    load_contract(self.root),
                    local_preferences(self.root).get("experience") == "advanced",
                )
        return (
            load_contract(self.root),
            local_preferences(self.root).get("experience") == "advanced",
        )

    def _advanced(self) -> None:
        """Offer the advanced tools as their own screen rather than six home rows."""
        while True:
            action = self._menu(
                "Advanced",
                (
                    Action("inspect", "Inspect project contract"),
                    Action("verbose", "Verbose Project Check"),
                    Action("regenerate", "Regenerate managed assets"),
                    Action("conventions", "Customize prompt and code conventions"),
                    Action("rigor", "Configure research rigor declarations"),
                    Action("tools", "Detected local tools"),
                    Action("back", "← Back"),
                ),
            )
            if action == "inspect":
                self._inspect()
            elif action == "verbose":
                self._check(verbose=True)
            elif action == "regenerate":
                self._regenerate()
            elif action == "conventions":
                self._conventions()
            elif action == "rigor":
                self._rigor()
            elif action == "tools":
                self._tools()
            else:
                return

    def _menu(self, title: str, actions: Sequence[Action]) -> str:
        """Return a chosen action token from a framed screen or a numbered fallback.

        Tokens are the contract in both presentations. Leaving a menu without
        choosing resolves to its own escape row, so a caller never sees a
        non-answer.
        """
        escape = escape_token(actions) or tokens_of(actions)[-1]
        if self.visual:
            try:
                return str(select_menu(title, MenuChoice.rows(actions)))
            except (BackRequested, SelectionCancelled):
                return escape
        while True:
            for line in numbered_lines(actions):
                self.console.print(line, markup=False)
            answer = resolve_action(self.session.prompt(f"{title}: "), actions)
            if answer is not None:
                return answer
            self.console.print("Choose a listed action.", style="caution")

    def _orientation(self) -> None:
        """Report where the record stands and the command that moves it forward.

        This states what the project contains, never what the science should be. The
        scientific decisions stay with the researcher; what the tool can honestly supply
        is that the workflow starts in `docs/12_STEPS.md` and that these files exist,
        which is otherwise discoverable only by opening `scripts/README.md` unprompted.
        """
        state, command = next_workflow_action(self.root)
        self.console.print(f"[heading]{state}[/]")
        self.console.print(f"Next: [value]{command}[/]")
        self.console.print(
            "Read docs/12_STEPS.md for the workflow and who owns which decision, "
            "prompts/CONTEXT_INDEX.md for what to read for a given task, and "
            "scripts/README.md for the helpers.",
            style="hint",
        )
        self.console.print(
            "SMAIRT reports what the project contains. What to test, and what a result "
            "means, are yours.",
            style="hint",
        )

    def _assistant(self) -> None:
        self.console.print(prepare_assistant(self.root))
        _, _, launch = assistant_launch_status(self.root)
        action = self._menu(
            "Assistant",
            (
                Action("launch", f"Launch {launch}"),
                Action("folder", "Open the project folder"),
                Action("back", "← Back"),
            ),
        )
        if action == "launch":
            _, message = launch_assistant(self.root)
            self.console.print(message)
        elif action == "folder":
            self.console.print(open_folder(self.root))

    def _capabilities(self) -> None:
        """Choose every capability at once, previewing the change before writing.

        Enabling and disabling are one decision about which capabilities this
        project has, so they are one screen. Nothing is written until the preview
        of the real operation has been accepted.
        """
        contract = load_contract(self.root)
        enabled = [
            name
            for name in OPTIONAL_CAPABILITIES
            if contract.capabilities[name].state is CapabilityState.ENABLED
        ]
        requested = self._choose_capabilities(enabled)
        if requested is None:
            return
        try:
            plan = capability_plan(self.root, requested)
        except ProjectError as error:
            self.console.print(str(error), style="caution")
            return
        if plan.is_empty:
            self.console.print("No capability changes requested.")
            return
        self._preview_capability_plan(plan)
        if not self._confirmed("Apply these capability changes"):
            self.console.print("No changes made.")
            return
        for message in set_capabilities(self.root, requested):
            self.console.print(message)

    def _choose_capabilities(self, enabled: Sequence[str]) -> list[str] | None:
        """Return the requested capabilities, or None when the researcher backs out."""
        if self.visual:
            try:
                selection = select_many(
                    "Optional capabilities",
                    [
                        (_NO_CAPABILITIES, "Default Workspace (no optional capabilities)"),
                        *((name, _capability_label(name)) for name in OPTIONAL_CAPABILITIES),
                    ],
                    list(enabled) or [_NO_CAPABILITIES],
                    details=(
                        "Enabling creates only missing files; disabling never removes any.",
                        "Space toggles a capability; choose Next to preview the change.",
                    ),
                    exclusive=_NO_CAPABILITIES,
                )
            except (BackRequested, SelectionCancelled):
                return None
            return [name for name in selection if name != _NO_CAPABILITIES]
        self.console.print(f"Currently enabled: {', '.join(enabled) or 'none'}")
        answer = self.session.prompt(
            "Capabilities to have enabled [paper, hpc, comma separated, none, or back]: "
        ).strip()
        if answer.lower() in {"back", ""}:
            return None
        requested = _requested_capabilities(answer, self.console)
        return None if requested is None else sorted(requested)

    def _preview_capability_plan(self, plan: CapabilityPlan) -> None:
        """Describe exactly what the pending write would change and create."""
        self.console.print("[heading]Pending capability changes[/]")
        for change in plan.changes:
            verb = "Enable" if change.enabling else "Disable"
            self.console.print(f"- {verb} {change.label} Support")
        if plan.creates:
            self.console.print("Files that would be created:")
            for relative in plan.creates:
                self.console.print(f"  + {relative}")
        else:
            self.console.print("No files would be created.")
        if any(not change.enabling for change in plan.changes):
            self.console.print(
                "Disabling only marks a capability inactive; your files stay exactly as they are.",
                style="hint",
            )

    def _confirmed(self, question: str, *, details: Sequence[str] = ()) -> bool:
        """Return whether the researcher explicitly agreed, defaulting to refusal."""
        if self.visual:
            try:
                return confirm(question, details=details)
            except (BackRequested, SelectionCancelled):
                return False
        return self.session.prompt(f"{question} [yes/no]: ").strip().lower() in {"yes", "y"}

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
            stale = any(issue.code == "scaffold-version-mismatch" for issue in issues)
            repairable = [] if stale else [issue for issue in issues if issue.repair is not None]
            if stale:
                self.console.print(
                    "This project records an older scaffold version, so repairs and "
                    "regeneration are refused to protect it. Nothing is wrong with the "
                    "project; an upgrade flow does not exist yet. Keep working, or create a "
                    "new project with this version and move work across deliberately.",
                    style="caution",
                )
            if repairable:
                self.console.print("Safe repairs available:")
                for issue in repairable:
                    assert issue.repair is not None
                    self.console.print(f"- {issue.repair}: {issue.message}")
                selected = self._select_items(
                    "Safe repairs",
                    [
                        (str(issue.repair), f"{issue.repair}: {issue.message}")
                        for issue in repairable
                    ],
                    details=("Check every repair to apply, then choose Next.",),
                    prompt="Enter repair identifiers separated by commas, or back",
                )
                if selected:
                    self._repair(selected)
        if verbose:
            self._tools()

    def _select_items(
        self,
        title: str,
        choices: list[tuple[str, str]],
        *,
        details: Sequence[str] = (),
        prompt: str,
    ) -> list[str]:
        """Return chosen identifiers from a checkbox screen or a comma-separated answer.

        The visual screen offers only identifiers that actually exist right now, so
        a typo cannot reach the operation at all.
        """
        if not choices:
            return []
        if self.visual:
            try:
                return [str(value) for value in select_many(title, choices, details=details)]
            except (BackRequested, SelectionCancelled):
                return []
        answer = self.session.prompt(f"{prompt}: ").strip()
        if answer.lower() in {"", "back"}:
            return []
        return [item.strip() for item in answer.split(",") if item.strip()]

    def _repair(self, identifiers: list[str]) -> None:
        try:
            preview = repair_previews(self.root, identifiers)
        except ProjectError as error:
            self.console.print(str(error), style="caution")
            return
        for issue in preview:
            assert issue.repair is not None
            self.console.print(f"Preview: {issue.repair}: {issue.message}")
        if not self._confirmed("Apply these safe repairs"):
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
            self.console.print(str(error), style="caution")

    def _tools(self) -> None:
        self.console.print("Detected local tools:")
        for label, executable in detected_tools(self.root).items():
            self.console.print(f"- {label}: {executable}")

    def _regenerate(self) -> None:
        try:
            available = managed_asset_paths(self.root)
        except ProjectError as error:
            self.console.print(str(error), style="caution")
            return
        self.console.print("Managed assets:")
        for relative in available:
            self.console.print(f"- {relative}")
        selected = self._select_items(
            "Managed assets",
            [(relative, relative) for relative in available],
            details=("Only missing or unmodified assets are restored.",),
            prompt="Asset paths to regenerate separated by commas, or back",
        )
        if not selected:
            return
        try:
            preview = managed_asset_previews(self.root, selected)
        except ProjectError as error:
            self.console.print(str(error), style="caution")
            return
        for entry in preview:
            self.console.print(f"Preview: {entry['path']} is {entry['status']}.")
        if self._confirmed("Regenerate these managed assets"):
            regenerate_managed_assets(self.root, selected)
            self.console.print("Managed asset regenerated.")
        else:
            self.console.print("No changes made.")

    def _conventions(self) -> None:
        contract = load_contract(self.root)
        prompt = self._choose_value(
            "Prompt convention",
            [
                ("plan-first", "Plan first - draft a plan before complex work"),
                ("direct-task", "Direct task - act on the request as given"),
            ],
            _set_value(contract.conventions.prompt),
        )
        code = self._choose_value(
            "Code convention",
            [
                ("typed-python", "Typed Python - annotate public functions"),
                ("standard-python", "Standard Python - annotations optional"),
            ],
            _set_value(contract.conventions.code),
        )
        try:
            update_settings(
                self.root,
                prompt_convention=PromptConvention(prompt) if prompt else None,
                code_convention=CodeConvention(code) if code else None,
            )
        except (ProjectError, ValueError):
            self.console.print("Use only the listed prompt and code conventions.", style="caution")
        else:
            self.console.print("Conventions updated.")

    def _rigor(self) -> None:
        """Choose declaration prompts, never the scientific policies themselves."""
        contract = load_contract(self.root)
        choices = [
            ("multiplicity", "Declare a multiplicity policy"),
            ("discovery-validation", "Separate discovery and validation roles"),
            ("unit-of-inference", "Declare the unit of inference"),
            ("per-probe-status", "Track hypothesis status for each panel probe"),
        ]
        current = [
            token
            for token, enabled in (
                ("multiplicity", contract.rigor.declare_multiplicity_policy),
                ("discovery-validation", contract.rigor.separate_discovery_validation),
                ("unit-of-inference", contract.rigor.declare_unit_of_inference),
                ("per-probe-status", contract.rigor.track_per_probe_status),
            )
            if enabled
        ]
        if self.visual:
            try:
                selected = [
                    str(value)
                    for value in select_many(
                        "Research rigor declarations",
                        choices,
                        checked=current,
                        details=(
                            "These settings add blank fields to new files; they never choose a method.",
                            "Enabling creates analysis/RIGOR.md once. Disabling removes nothing.",
                        ),
                    )
                ]
            except (BackRequested, SelectionCancelled):
                return
        else:
            allowed = {token for token, _ in choices}
            self.console.print(f"Currently enabled: {', '.join(current) or 'none'}")
            answer = self.session.prompt(
                "Enabled declarations separated by commas, none, or back: "
            ).strip()
            if answer.lower() in {"", "back"}:
                return
            selected = (
                []
                if answer.lower() == "none"
                else [item.strip() for item in answer.split(",") if item.strip()]
            )
            unknown = set(selected) - allowed
            if unknown:
                self.console.print(
                    f"Unknown declarations: {', '.join(sorted(unknown))}.", style="caution"
                )
                return
        enabled = [label for token, label in choices if token in selected]
        disabled = [label for token, label in choices if token not in selected]
        self.console.print("Pending research rigor declaration changes:")
        self.console.print(f"- Enabled: {', '.join(enabled) or 'none'}")
        self.console.print(f"- Disabled: {', '.join(disabled) or 'none'}")
        will_create = bool(selected) and not (self.root / "analysis/RIGOR.md").exists()
        if will_create:
            self.console.print("- Create: analysis/RIGOR.md")
        self.console.print("- Existing research files: unchanged")
        if set(selected) == set(current):
            self.console.print("No rigor declaration changes requested.")
            return
        if not self._confirmed(
            "Apply these research rigor declaration changes",
            details=(
                "The settings affect only helper output created afterward.",
                "Disabling never removes analysis/RIGOR.md or prior declarations.",
            ),
        ):
            self.console.print("No changes made.")
            return
        update_settings(
            self.root,
            declare_multiplicity_policy="multiplicity" in selected,
            separate_discovery_validation="discovery-validation" in selected,
            declare_unit_of_inference="unit-of-inference" in selected,
            track_per_probe_status="per-probe-status" in selected,
        )
        self.console.print("Research rigor declarations updated; existing files were unchanged.")

    def _choose_value(self, title: str, choices: list[tuple[str, str]], current: str) -> str:
        """Return one value from a finite set, or empty when nothing is to change.

        An unset value is shown as unset rather than defaulted, so the screen never
        implies a decision the project has not recorded.
        """
        if self.visual:
            try:
                return str(select_choice(title, choices, current or None))
            except (BackRequested, SelectionCancelled):
                return ""
        values = [value for value, _ in choices]
        self.console.print(f"Available: {', '.join(values)}")
        answer = (
            self.session.prompt(f"{title} [Enter to keep {current or 'unset'}]: ").strip().lower()
        )
        if answer in values:
            return answer
        if answer:
            self.console.print(f"Choose one of: {', '.join(values)}.", style="caution")
        return ""

    def _settings(self) -> None:
        while True:
            action = self._menu(
                "Project Settings",
                (
                    divider("─── Recorded in the project contract ───"),
                    Action("name", "Project name"),
                    Action("description", "Description"),
                    Action("domain", "Domain"),
                    Action("question", "Research question"),
                    Action("researcher", "Primary researcher"),
                    Action("assistant", "Assistant"),
                    Action("phase", "Current phase"),
                    Action("collaborator", "Collaborator"),
                    Action("license", "License"),
                    divider("─── This checkout only, never committed ───"),
                    Action("preferences", "Local experience and motion"),
                    Action("back", "← Back"),
                ),
            )
            contract = load_contract(self.root)
            if action == "name":
                update_settings(self.root, name=self._required("Project name"))
            elif action == "description":
                update_settings(self.root, description=self._required("Description"))
            elif action == "domain":
                update_settings(self.root, domain=self._required("Domain"))
            elif action == "question":
                update_settings(
                    self.root,
                    question=self.session.prompt("Research question (blank clears it): ").strip(),
                )
            elif action == "researcher":
                update_settings(self.root, researcher=self._required("Primary researcher"))
            elif action == "assistant":
                selected = self._choose_value(
                    "Assistant",
                    [(item.value, _assistant_label(item.value)) for item in Assistant],
                    contract.assistant.value,
                )
                if selected:
                    update_settings(self.root, assistant=Assistant(selected))
            elif action == "phase":
                self.console.print("Existing directories are never deleted.", style="hint")
                selected = self._choose_value(
                    "Current phase",
                    [(item.value, _phase_label(item.value)) for item in StartingPhase],
                    contract.current_phase.value,
                )
                if selected:
                    update_settings(self.root, phase=StartingPhase(selected))
            elif action == "collaborator":
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
                    self.console.print(str(error), style="caution")
            elif action == "license":
                self._license(contract)
            elif action == "preferences":
                self._preferences()
            else:
                return

    def _required(self, label: str) -> str:
        while True:
            value = self.session.prompt(f"{label}: ").strip()
            if value:
                return value
            self.console.print(f"{label} is required.", style="caution")

    def _license(self, contract: ProjectContract) -> None:
        self.console.print("License changes can affect legal rights. This is not legal advice.")
        if not self.visual:
            for number, license in enumerate(License, start=1):
                self.console.print(f"{number}. {license.value} - {LICENSE_EXPLANATIONS[license]}")
            choice = self.session.prompt("Choose a license or press Enter to cancel: ").strip()
            if not choice.isdigit() or not 1 <= int(choice) <= len(License):
                return
            selected = tuple(License)[int(choice) - 1]
        else:
            try:
                chosen = select_choice(
                    "Choose a license",
                    [
                        (item.value, f"{item.value} - {LICENSE_EXPLANATIONS[item]}")
                        for item in License
                    ],
                    contract.license.value,
                    details=("Only unmodified legal text is ever replaced.",),
                )
            except (BackRequested, SelectionCancelled):
                return
            selected = License(chosen)
        self.console.print("Preview:")
        self.console.out(license_preview(self.root, selected), end="")
        if not self._confirmed("Replace unmodified legal text"):
            self.console.print("No license change made.")
            return
        try:
            change_license(self.root, selected)
        except ProjectError as error:
            self.console.print(str(error), style="caution")
        else:
            self.console.print(f"License changed to {selected.value}.")

    def _preferences(self) -> None:
        """Adjust the preferences that belong to this checkout and are never committed."""
        preferences = local_preferences(self.root)
        experience = self._choose_value(
            "Experience",
            [
                ("standard", "Standard - the everyday tasks only"),
                ("advanced", "Advanced - adds contract, asset, and convention tools"),
            ],
            str(preferences.get("experience", "standard")),
        )
        motion = self._choose_value(
            "Motion",
            [
                ("yes", "Yes - framed screens and spinners"),
                ("no", "No - plain numbered listings"),
            ],
            "no" if preferences.get("motion") is False else "yes",
        )
        if experience:
            preferences["experience"] = experience
        if motion:
            preferences["motion"] = motion == "yes"
        save_local_preferences(self.root, preferences)


def _capability_label(name: str) -> str:
    return "Paper" if name == "paper" else "HPC"


def _created_summary(
    console: Console, root: Path, options: ProjectOptions, messages: Sequence[str]
) -> None:
    """Report what creation actually produced, rather than only that it finished.

    The write itself is atomic and takes well under a second, so a progress bar
    would be theater. What a researcher needs afterwards is what exists now and
    what to do next.
    """
    files = sum(1 for path in root.rglob("*") if path.is_file())
    capabilities = [
        _capability_label(name)
        for name, enabled in (("paper", options.paper), ("hpc", options.hpc))
        if enabled
    ]
    console.rule("[title]Project created[/]")
    console.print(f"Location: [value]{root}[/]")
    console.print(f"Files written: [value]{files}[/]")
    console.print(f"Capabilities: [value]{', '.join(capabilities) or 'Default Workspace'}[/]")
    console.print(f"Git: [value]{'initialized and staged' if options.initialize_git else 'off'}[/]")
    for message in messages:
        console.print(message, style="caution" if "failed" in message.lower() else "hint")
    console.print(
        "Next: read docs/12_STEPS.md in the project, then start a track with "
        "scripts/new_track.py. The Dashboard below reports where the work stands.",
        style="hint",
    )


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
    console = _themed_console(motion)
    actions = (
        Action("create", "Create New Project"),
        Action("recents", "Recent Projects"),
        Action("open", "Open Existing Project"),
        Action("help", "Help"),
        Action("exit", "Exit"),
    )
    while True:
        console.rule("[title]SMAIRT Home[/]")
        if motion:
            try:
                action = str(select_menu("Choose an action", MenuChoice.rows(actions)))
            except (BackRequested, SelectionCancelled):
                return
        else:
            for line in numbered_lines(actions):
                console.print(line, markup=False)
            resolved = resolve_action(session.prompt("Choose an action: "), actions)
            if resolved is None:
                console.print("Choose a listed action.", style="caution")
                continue
            action = resolved
        if action == "create":
            try:
                destination, options = Wizard().run()
                messages = _generate_with_progress(console, destination, options, motion)
            except WizardCancelled:
                console.print("Project creation cancelled. No files were written.")
            except (GenerationError, ValidationError, OSError) as error:
                console.print(f"Could not create the project: {error}", style="failure")
                console.print(
                    "Generation is atomic, so no partial project was left behind.",
                    style="hint",
                )
            else:
                root = destination.resolve()
                record_recent(root)
                _created_summary(console, root, options, messages)
                Dashboard(root).run()
        elif action == "recents":
            recents = recent_projects()
            if not recents:
                console.print("No recent SMAIRT projects.")
                continue
            if motion:
                try:
                    chosen = select_choice(
                        "Recent Projects",
                        [(str(entry["path"]), _recent_label(entry)) for entry in recents],
                    )
                except (BackRequested, SelectionCancelled):
                    continue
                _open_recent(console, Path(chosen))
                continue
            for index, entry in enumerate(recents, start=1):
                console.print(f"{index}. {_recent_label(entry)}")
            selection = session.prompt(
                "Select a project number, or press Enter to go back: "
            ).strip()
            if selection.isdigit() and 1 <= int(selection) <= len(recents):
                _open_recent(console, Path(recents[int(selection) - 1]["path"]))
        elif action == "open":
            try:
                root = _project_or_exit(Path(session.prompt("Project folder: ").strip()))
            except (ProjectError, typer.Exit):
                continue
            Dashboard(root).run()
        elif action == "help":
            console.print(
                "SMAIRT creates and safely manages workspace utilities. It does not conduct scientific work."
            )
        else:
            return


def _recent_label(entry: dict[str, str]) -> str:
    """Return a recent project as its name and location rather than a bare path.

    A list of paths alone makes two projects with similar directory names hard to tell
    apart, and the name is what the researcher actually calls the project.
    """
    path = Path(str(entry["path"]))
    try:
        name = load_contract(path).project.name
    except ProjectError:
        return f"{path} (no longer a SMAIRT project)"
    return f"{name} - {path}"


def _open_recent(console: Console, path: Path) -> None:
    """Open a recent project, staying on Home when it can no longer be opened.

    A project that moved is an ordinary situation, not a reason to end the session. The
    shared `_project_or_exit` raises to leave the process, which is right for a direct
    command and wrong inside a menu the researcher is still using.
    """
    try:
        root = resolve_project(path)
    except ProjectError as error:
        console.print(str(error), style="caution")
        console.print("It may have moved or been deleted. Choose another project.", style="hint")
        return
    record_recent(root)
    Dashboard(root).run()


def _generate_with_progress(
    console: Console, destination: Path, options: ProjectOptions, motion: bool
) -> list[str]:
    """Create the project, showing a spinner only while work is actually running."""
    if not motion:
        return generate_project(destination, options)
    with console.status("Creating your SMAIRT project...", spinner="dots"):
        return generate_project(destination, options)


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
            raise typer.Exit(code=OPERATION_FAILED)
    if not wizard_mode and (
        name is None or slug is None or description is None or researcher is None or domain is None
    ):
        typer.echo(
            "Error: --name, --slug, --description, --researcher, and --domain are required with a destination.",
            err=True,
        )
        raise typer.Exit(code=CANNOT_PROCEED)
    if not wizard_mode and not accept_license:
        typer.echo(
            "Error: review the selected license and pass --accept-license to create the project.",
            err=True,
        )
        raise typer.Exit(code=CANNOT_PROCEED)
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
        # Resolved before generation, not after. Creation replaces the destination directory,
        # so when the destination is the working directory itself — `smairt new .` — the
        # process's own cwd is swapped out and a later `.resolve()` raises FileNotFoundError
        # on a project that was in fact created successfully.
        created = absolute_destination(destination)
        motion = wizard_mode and _interactive_motion_enabled()
        console = _themed_console(motion)
        messages = _generate_with_progress(console, destination, options, motion)
    except (GenerationError, OSError) as error:
        prefix = "Could not create the project" if wizard_mode else "Error"
        typer.echo(f"{prefix}: {error}", err=True)
        raise typer.Exit(code=OPERATION_FAILED) from error
    except ValidationError as error:
        typer.echo(_describe_rejected_input(error), err=True)
        raise typer.Exit(code=CANNOT_PROCEED) from error
    typer.echo(f"Created SMAIRT project at {created}")
    record_recent(created)
    if motion:
        _created_summary(console, created, options, messages)
        return
    for message in messages:
        typer.echo(message)


def _describe_rejected_input(error: ValidationError) -> str:
    """Return why supplied values were rejected, in one voice for every command.

    A rejected slug is answered with the rule and a usable suggestion, because it is the most
    common way creation fails and a rule alone leaves the researcher guessing.
    """
    rejected_slug = slug_rejection_in(error)
    if rejected_slug is not None:
        return f"Error: {describe_slug_rejection(rejected_slug)}"
    return f"Error: {describe_validation_error(error)}"


def _optional_answer(answers: dict[str, str | bool], key: str) -> str | None:
    value = str(answers.get(key, ""))
    return value or None


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug if slug and slug[0].isalpha() else f"project_{slug or 'workspace'}"


def _set_value(convention: PromptConvention | CodeConvention | None) -> str:
    """Return a recorded convention's value, or empty when the project has none."""
    return convention.value if convention is not None else ""


def _folder_name(value: str) -> str:
    """Return the folder spelling of a name, from which the identifier derives."""
    return _slugify(value).replace("_", "-")


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
    """Run the CLI, translating any unanticipated failure into something actionable.

    This is the console-script entry point, so it sits outside Click's own exception handling
    and has to exit the process itself rather than raise `typer.Exit` — raising here would
    escape as the very traceback this boundary exists to prevent.

    `SystemExit` passes through, because that is how every command has already reported its
    own outcome by the time control returns here. `KeyboardInterrupt` is the researcher
    deliberately stopping, and is not an error. Everything else is a failure SMAIRT did not
    anticipate, where a traceback is the worst available answer: it implies the project may be
    damaged while offering no way to find out. Full detail stays behind SMAIRT_DEBUG.
    """
    try:
        app()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        typer.echo("Cancelled.", err=True)
        sys.exit(130)
    except Exception as error:
        if os.environ.get("SMAIRT_DEBUG"):
            raise
        typer.echo(describe_unexpected_error(error), err=True)
        sys.exit(OPERATION_FAILED)
