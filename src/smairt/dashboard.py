"""Managing an existing project: the Home screen and the Standard/Advanced dashboard.

Split out of `cli.py` alongside the wizard. This module manages a project that already exists;
`wizard.py` creates one. They meet only at the command surface, and neither imports the other —
except that Home offers creation, so this module imports the wizard and not the reverse.

The dashboard manages workspace utilities only. Scientific work stays with the researcher and
their coding assistant, and the one orientation row reports what the contract and the files say
is missing without ever recommending what to conclude.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

import typer
import yaml
from prompt_toolkit import PromptSession
from prompt_toolkit.input.defaults import create_input
from prompt_toolkit.output.defaults import create_output
from pydantic import ValidationError
from rich.console import Console

from smairt.generator import GenerationError
from smairt.menu import (
    Action,
    MenuChoice,
    divider,
    escape_token,
    numbered_lines,
    resolve_action,
    tokens_of,
)
from smairt.models import (
    Assistant,
    CapabilityState,
    CodeConvention,
    License,
    ProjectContract,
    ProjectOptions,
    PromptConvention,
    StartingPhase,
)
from smairt.presentation import (
    NO_CAPABILITIES,
    OPTIONAL_CAPABILITIES,
    assistant_label,
    capability_label,
    convention_value,
    generate_with_progress,
    interactive_motion_enabled,
    phase_label,
    project_or_exit,
    requested_capabilities,
    themed_console,
)
from smairt.project import (
    LICENSE_EXPLANATIONS,
    CapabilityPlan,
    ProjectError,
    apply_repairs,
    assistant_launch_status,
    capability_plan,
    change_license,
    detected_tools,
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
    resolve_project,
    save_local_preferences,
    set_capabilities,
    update_collaborator,
    update_settings,
)
from smairt.terminal import (
    BackRequested,
    SelectionCancelled,
    confirm,
    select_choice,
    select_many,
    select_menu,
)
from smairt.wizard import Wizard, WizardCancelled


class Dashboard:
    def __init__(self, root: Path) -> None:
        self.root = root
        motion = interactive_motion_enabled(root)
        self.visual = motion
        self.console = themed_console(motion)
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
            capability_label(name)
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
        if interactive_motion_enabled(self.root):
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
                        (NO_CAPABILITIES, "Default Workspace (no optional capabilities)"),
                        *((name, capability_label(name)) for name in OPTIONAL_CAPABILITIES),
                    ],
                    list(enabled) or [NO_CAPABILITIES],
                    details=(
                        "Enabling creates only missing files; disabling never removes any.",
                        "Space toggles a capability; choose Next to preview the change.",
                    ),
                    exclusive=NO_CAPABILITIES,
                )
            except (BackRequested, SelectionCancelled):
                return None
            return [name for name in selection if name != NO_CAPABILITIES]
        self.console.print(f"Currently enabled: {', '.join(enabled) or 'none'}")
        answer = self.session.prompt(
            "Capabilities to have enabled [paper, hpc, comma separated, none, or back]: "
        ).strip()
        if answer.lower() in {"back", ""}:
            return None
        requested = requested_capabilities(answer, self.console)
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
            convention_value(contract.conventions.prompt),
        )
        code = self._choose_value(
            "Code convention",
            [
                ("typed-python", "Typed Python - annotate public functions"),
                ("standard-python", "Standard Python - annotations optional"),
            ],
            convention_value(contract.conventions.code),
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
                    [(item.value, assistant_label(item.value)) for item in Assistant],
                    contract.assistant.value,
                )
                if selected:
                    update_settings(self.root, assistant=Assistant(selected))
            elif action == "phase":
                self.console.print("Existing directories are never deleted.", style="hint")
                selected = self._choose_value(
                    "Current phase",
                    [(item.value, phase_label(item.value)) for item in StartingPhase],
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


def created_summary(
    console: Console, root: Path, options: ProjectOptions, messages: Sequence[str]
) -> None:
    """Report what creation actually produced, rather than only that it finished.

    The write itself is atomic and takes well under a second, so a progress bar
    would be theater. What a researcher needs afterwards is what exists now and
    what to do next.
    """
    files = sum(1 for path in root.rglob("*") if path.is_file())
    capabilities = [
        capability_label(name)
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


def home() -> None:
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
    motion = interactive_motion_enabled()
    console = themed_console(motion)
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
                messages = generate_with_progress(console, destination, options, motion)
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
                created_summary(console, root, options, messages)
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
                root = project_or_exit(Path(session.prompt("Project folder: ").strip()))
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
    shared `project_or_exit` raises to leave the process, which is right for a direct
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
