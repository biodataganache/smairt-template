"""Guided project creation: fourteen screens, every answer editable until the last.

Split out of `cli.py`, which had grown to hold the command surface, this wizard, the
dashboard, and the helpers all three shared. Creation and management are separate concerns
that only meet at the command surface, so they are now separate modules and each can be read
without the other.

Every screen exists in two presentations that must agree: a framed screen that repaints, and a
numbered listing for a terminal that cannot repaint, redirected input, and CI. Both address the
same actions through the same tokens, so neither presentation is the real one.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.input.defaults import create_input
from prompt_toolkit.output.defaults import create_output
from pydantic import ValidationError

from smairt.generator import GenerationError, validate_destination
from smairt.menu import Action, MenuChoice, divider, numbered_lines, resolve_action
from smairt.messages import (
    describe_slug_rejection,
    describe_validation_error,
    slug_rejection_in,
)
from smairt.models import (
    Assistant,
    License,
    ProjectIdentity,
    ProjectOptions,
    Researcher,
    StartingPhase,
)
from smairt.presentation import (
    BACK,
    CANCEL,
    NO_CAPABILITIES,
    SKIP,
    assistant_label,
    capability_label,
    folder_name,
    interactive_motion_enabled,
    optional_answer,
    phase_label,
    requested_capabilities,
    slugify,
    themed_console,
)
from smairt.project import LICENSE_EXPLANATIONS
from smairt.terminal import (
    BackRequested,
    SelectionCancelled,
    navigation_bindings,
    select_choice,
    select_many,
    select_menu,
)


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
        motion = interactive_motion_enabled()
        self.visual = motion
        self.console = themed_console(motion)
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
                "phase", "Starting phase", self._phase, lambda: phase_label(self._answer("phase"))
            ),
            Step(
                "assistant",
                "Coding assistant",
                self._assistant,
                lambda: assistant_label(self._answer("assistant")),
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
            if answer == CANCEL:
                raise WizardCancelled
            if answer == BACK:
                raise BackRequested
            if optional and answer == SKIP:
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
            if answer == CANCEL:
                raise WizardCancelled
            if answer == BACK:
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
                default=folder_name(str(self.answers["name"])),
            )
            if Path(folder).name != folder or folder in {".", ".."}:
                self.console.print("Project folder must be one folder name.", style="caution")
                continue
            identifier = slugify(folder)
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
        previous_default = folder_name(str(self.answers.get("name", "")))
        name = self._ask("What is the human-readable project name", key="name")
        if self.answers.get("folder") in {None, previous_default}:
            self.answers["folder"] = folder_name(name)

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
                        (NO_CAPABILITIES, "Default Workspace (no optional capabilities)"),
                        ("paper", "Do you expect to write a paper?"),
                        ("hpc", "Do you expect to use an HPC?"),
                    ],
                    self._checked_capabilities(),
                    details=(
                        "Both are additive and can be enabled or disabled later.",
                        "Space toggles a capability; choose Next when you are done.",
                    ),
                    exclusive=NO_CAPABILITIES,
                )
            except SelectionCancelled as error:
                raise WizardCancelled from error
            self._record_capabilities(set(selection) - {NO_CAPABILITIES})
            return
        self.console.print(
            "Paper and HPC support are optional and both start off for a default workspace."
        )
        self.console.print("Type paper, hpc, paper,hpc, none, or press Enter to skip.")
        while True:
            answer = self.session.prompt("Optional capabilities [Enter to skip]: ").strip()
            if answer == CANCEL:
                raise WizardCancelled
            if answer == BACK:
                raise BackRequested
            requested = requested_capabilities(answer, self.console)
            if requested is not None:
                self._record_capabilities(requested)
                return

    def _checked_capabilities(self) -> list[str]:
        """Return the rows to start checked, naming the default workspace explicitly."""
        chosen = [name for name in ("paper", "hpc") if self.answers[name]]
        return chosen or [NO_CAPABILITIES]

    def _record_capabilities(self, requested: set[str]) -> None:
        self.answers["paper"] = "paper" in requested
        self.answers["hpc"] = "hpc" in requested

    def _capability_summary(self) -> str:
        chosen = [capability_label(name) for name in ("paper", "hpc") if self.answers[name]]
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
            if answer == CANCEL:
                raise WizardCancelled
            if answer == BACK:
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
            if answer == CANCEL:
                raise WizardCancelled
            if answer == BACK:
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
            if typed == CANCEL:
                raise WizardCancelled
            if typed == BACK:
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
                research_question=optional_answer(self.answers, "question"),
            ),
            researcher=Researcher(
                name=str(self.answers["researcher"]),
                email=optional_answer(self.answers, "email"),
            ),
            assistant=Assistant(str(self.answers["assistant"])),
            starting_phase=StartingPhase(str(self.answers["phase"])),
            license=License(str(self.answers["license"])),
            initialize_git=bool(self.answers["git"]),
            paper=bool(self.answers["paper"]),
            hpc=bool(self.answers["hpc"]),
        )
