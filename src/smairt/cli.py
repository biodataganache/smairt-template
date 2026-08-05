"""The command surface: every `smairt` subcommand, and the boundary around all of them.

This module is the adapter, not the application. Commands validate what they were given, call
one project operation, and report the outcome; the interactive surfaces live in `wizard.py` and
`dashboard.py`, and the operations themselves in `project.py`. ADR 0001 requires the CLI be an
adapter over shared operations rather than a second definition of them.

It used to hold the command surface, the wizard, the dashboard, and everything the three
shared — 2,267 lines in which `self.visual` was re-branched in every interactive method.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import typer
import yaml
from pydantic import ValidationError

from smairt import __version__
from smairt.dashboard import created_summary, home
from smairt.generator import GenerationError, absolute_destination
from smairt.messages import (
    describe_unexpected_error,
    describe_validation_error,
    slug_rejection_in,
    suggest_slug,
)
from smairt.models import (
    Assistant,
    CodeConvention,
    License,
    ProjectIdentity,
    ProjectOptions,
    PromptConvention,
    Researcher,
    StartingPhase,
)
from smairt.presentation import (
    CANNOT_PROCEED,
    OPERATION_FAILED,
    generate_with_progress,
    interactive_motion_enabled,
    project_or_exit,
    themed_console,
)
from smairt.project import (
    LICENSE_EXPLANATIONS,
    ProjectError,
    apply_repairs,
    apply_upgrade,
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
    project_check,
    record_recent,
    regenerate_managed_assets,
    repair_previews,
    require_upgradable,
    save_local_preferences,
    update_collaborator,
    update_settings,
    upgrade_plan,
)
from smairt.wizard import Wizard, WizardCancelled

app = typer.Typer(no_args_is_help=False, invoke_without_command=True)


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
        home()


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
    root = project_or_exit(path)
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
    root = project_or_exit(path, remember=False)
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
    root = project_or_exit(path)
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
    root = project_or_exit(path)
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
    root = project_or_exit(path)
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
    root = project_or_exit(path, remember=False)
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
    root = project_or_exit(path)
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
    if plan.outside:
        typer.echo("Resolves outside the project, so left untouched:")
        for change in plan.outside:
            typer.echo(f"- {change.path}")
        typer.echo(
            "  Replace each with an ordinary file inside the project to have SMAIRT manage it."
        )
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
    show_all: bool = typer.Option(
        False, "--all", help="List every eligible asset, including those already current."
    ),
    confirm: bool = typer.Option(False, help="Write the previewed managed assets."),
) -> None:
    """Preview and restore only missing or unmodified managed guidance and templates."""
    root = project_or_exit(path)
    try:
        if not select:
            # Checked before listing, because an out-of-date project would otherwise be shown
            # every managed asset as "eligible" and then refused on --confirm.
            require_upgradable(root, "regenerate managed assets")
            statuses = {item["path"]: item["status"] for item in managed_file_statuses(root)}
            paths = managed_asset_paths(root)
            missing = [relative for relative in paths if statuses.get(relative) == "missing"]
            current = [relative for relative in paths if statuses.get(relative) == "unchanged"]
            # Missing files are the reason to run this command. Listing forty already-current
            # files alongside them means a researcher has to diff the output against
            # `smairt check` by eye to find the one row that matters.
            if missing:
                typer.echo("Missing, so regenerating would restore them:")
                for relative in missing:
                    typer.echo(f"- {relative}")
            if show_all and current:
                typer.echo("Already current, and may be regenerated anyway:")
                for relative in current:
                    typer.echo(f"- {relative}")
            elif current:
                typer.echo(
                    f"{len(current)} managed file(s) are already current. Use --all to list them."
                )
            preserved = [relative for relative in paths if statuses.get(relative) == "modified"]
            if preserved:
                typer.echo("Differ from the installed version, so not eligible:")
                for relative in preserved:
                    typer.echo(f"- {relative}")
            if not missing and not current:
                typer.echo("No managed assets are eligible for regeneration.")
                return
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
        motion = wizard_mode and interactive_motion_enabled()
        console = themed_console(motion)
        messages = generate_with_progress(console, destination, options, motion)
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
        created_summary(console, created, options, messages)
        return
    for message in messages:
        typer.echo(message)


def _describe_rejected_input(error: ValidationError) -> str:
    """Return why supplied values were rejected, in one voice for every command.

    A rejected slug additionally gets a usable suggestion, because it is the most common way
    creation fails and a rule alone leaves the researcher guessing. The suggestion is added to
    the full report rather than replacing it: hiding the other failures would force a
    correct-one-thing-and-retry loop, which is its own kind of unhelpful.
    """
    lines = [f"Error: {describe_validation_error(error)}"]
    rejected_slug = slug_rejection_in(error)
    if rejected_slug is not None:
        suggestion = suggest_slug(rejected_slug)
        if suggestion and suggestion != rejected_slug:
            lines.append(f"  For the slug, try: {suggestion}")
    return "\n".join(lines)


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
