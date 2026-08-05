from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from platformdirs import user_data_path
from pydantic import ValidationError

from smairt import __version__
from smairt.messages import describe_validation_error
from smairt.models import (
    Assistant,
    Capability,
    CapabilityState,
    CodeConvention,
    ConventionSettings,
    License,
    ProjectContract,
    PromptConvention,
    Researcher,
    RigorSettings,
    StartingPhase,
)
from smairt.scaffold import (
    ASSISTANT_POINTERS,
    ScaffoldConflict,
    active_assets,
    asset_ownership,
    asset_path,
    materialize_template_assets,
    render_template_assets,
)

CONTRACT_PATH = Path("smairt.yaml")
LOCAL_PREFERENCES_PATH = Path(".smairt") / "preferences.yaml"
OPTIONAL_CAPABILITIES = ("paper", "hpc")
REQUIRED_DIRECTORIES = (
    "background",
    "hypotheses",
    "plans",
    "analysis",
    "results/logs",
    "results/figures",
    "prompts",
)
PHASE_DIRECTORIES = (
    "data/synthetic",
    "data/downloaded",
    "data/real",
    "experiments/01_synthetic",
    "experiments/02_downloaded",
    "experiments/03_real_data",
)
"""Every phase directory, present in every project regardless of its starting phase.

Not keyed by phase. `starting_phase` records where work began and `current_phase` records
where attention is now; neither decides which directories exist, because a project that
begins with synthetic data still needs somewhere to put real data when it gets there.

This replaced a phase-keyed map whose `downloaded` and `real` entries were unreachable, read
through a function that took a phase argument and deleted it. The behavior was right and the
route to it invited the belief that phase controlled layout."""
_MIT_TEXT = """\
MIT License

Copyright (c) {year} {holder}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

_BSD_3_CLAUSE_TEXT = """\
BSD 3-Clause License

Copyright (c) {year}, {holder}
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

LICENSE_TEXT = {
    License.MIT: _MIT_TEXT,
    License.BSD_3_CLAUSE: _BSD_3_CLAUSE_TEXT,
}
"""The complete official text of each license SMAIRT will write.

Held as readable blocks rather than escaped single lines, because the truncation these
replaced was invisible when the text was one long `\\n`-joined string. Every entry must be
the license verbatim: a shortened license is not the license it names, and a `LICENSE` file
is the one generated artifact whose exact words carry legal effect.
"""

LICENSE_EXPLANATIONS = {
    License.MIT: "Permissive reuse with attribution and no warranty.",
    License.BSD_3_CLAUSE: "Permissive reuse with attribution and no endorsement.",
}
EDITOR_COMMAND = ("code", ".")
"""Opening the workspace in VS Code, which is what launching an extension assistant means."""

ASSISTANT_COMMANDS = {
    Assistant.ZOO_CODE: EDITOR_COMMAND,
    Assistant.CLAUDE_CODE: ("claude",),
    Assistant.OPENCODE: ("opencode",),
    Assistant.CODEX: ("codex",),
    Assistant.PI: ("pi",),
    Assistant.CURSOR: ("cursor", "."),
}
"""How to start each assistant in a project directory.

Zoo Code runs inside VS Code rather than as its own executable, so opening the workspace
is the launch. The same command is the fallback for any assistant whose own executable is
missing but which can still be reached from an open editor.
"""
ASSISTANT_ALIASES = {assistant: ASSISTANT_POINTERS[assistant.value] for assistant in Assistant}


class ProjectError(Exception):
    """Raised when a command cannot safely manage a SMAIRT project."""


@dataclass(frozen=True)
class CheckIssue:
    code: str
    path: str
    message: str
    repair: str | None = None

    def as_dict(self) -> dict[str, str]:
        result = {"code": self.code, "path": self.path, "message": self.message}
        if self.repair is not None:
            result["repair"] = self.repair
        return result


def resolve_project(path: Path | None = None) -> Path:
    start = (path or Path.cwd()).expanduser().resolve()
    if not start.exists():
        raise ProjectError(f"Project path does not exist: {start}")
    if start.is_file():
        start = start.parent
    for candidate in (start, *start.parents):
        if (candidate / CONTRACT_PATH).is_file():
            return candidate
    raise ProjectError(f"Not a SMAIRT project: {start}")


def load_contract(root: Path) -> ProjectContract:
    try:
        data = yaml.safe_load((root / CONTRACT_PATH).read_text())
        if isinstance(data, dict) and "license_year" not in data:
            match = re.search(
                r"Copyright(?: \(C\)| \(c\))? (\d{4})", (root / "LICENSE").read_text()
            )
            if match is not None:
                data["license_year"] = int(match.group(1))
        return ProjectContract.model_validate(data)
    except ValidationError as error:
        # A contract can be unreadable for a dozen structural reasons at once. Reporting them
        # as pydantic does means a researcher reads ten stanzas of type tags and a URL to find
        # out that one file is malformed.
        raise ProjectError(describe_validation_error(error, source="smairt.yaml")) from error
    except yaml.YAMLError as error:
        raise ProjectError(
            f"smairt.yaml is not valid YAML, so SMAIRT cannot read this project: {error}"
        ) from error
    except OSError as error:
        raise ProjectError(f"Could not read smairt.yaml: {error}") from error


def save_contract(root: Path, contract: ProjectContract) -> None:
    data = contract.model_dump(mode="json", exclude_none=True)
    if not contract.conventions.model_dump(exclude_none=True):
        data.pop("conventions", None)
    if not any(contract.rigor.model_dump().values()):
        data.pop("rigor", None)
    (root / CONTRACT_PATH).write_text(yaml.safe_dump(data, sort_keys=False))


def record_recent(root: Path) -> None:
    entries = _load_recents()
    canonical = str(root.resolve())
    entries = [entry for entry in entries if entry["path"] != canonical]
    entries.insert(0, {"path": canonical, "opened_at": _timestamp()})
    _save_recents(entries[:10])


def recent_projects() -> list[dict[str, str]]:
    entries = _load_recents()
    _save_recents(entries)
    return entries


def _load_recents() -> list[dict[str, str]]:
    recents_path = _recents_path()
    try:
        raw: Any = json.loads(recents_path.read_text())
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(raw, list):
        return []
    entries: list[dict[str, str]] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        path = entry.get("path")
        opened_at = entry.get("opened_at")
        if (
            isinstance(path, str)
            and isinstance(opened_at, str)
            and (Path(path) / CONTRACT_PATH).is_file()
        ):
            entries.append({"path": path, "opened_at": opened_at})
    return entries[:10]


def _save_recents(entries: list[dict[str, str]]) -> None:
    recents_path = _recents_path()
    recents_path.parent.mkdir(parents=True, exist_ok=True)
    recents_path.write_text(json.dumps(entries, indent=2) + "\n")


def _recents_path() -> Path:
    return user_data_path("smairt", appauthor=False) / "recent-projects.json"


def local_preferences(root: Path) -> dict[str, str | bool]:
    try:
        data = yaml.safe_load((root / LOCAL_PREFERENCES_PATH).read_text())
    except (OSError, yaml.YAMLError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {key: value for key, value in data.items() if isinstance(value, (str, bool))}


def save_local_preferences(root: Path, preferences: dict[str, str | bool]) -> None:
    path = root / LOCAL_PREFERENCES_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(preferences, sort_keys=True))


@dataclass(frozen=True)
class CapabilityChange:
    """One capability whose state would change, and in which direction."""

    name: str
    label: str
    enabling: bool


@dataclass(frozen=True)
class CapabilityPlan:
    """What a capability selection would change, derived from the real operation."""

    requested: tuple[str, ...]
    changes: tuple[CapabilityChange, ...]
    creates: tuple[str, ...]

    @property
    def is_empty(self) -> bool:
        """Report whether applying this plan would change nothing at all."""
        return not self.changes


def capability_plan(root: Path, requested: Sequence[str]) -> CapabilityPlan:
    """Describe what enabling and disabling the requested capabilities would do.

    The created-file list is rendered from the same contract and templates the
    write itself uses, so a preview cannot describe something else. Enabling
    creates only missing files; disabling never removes any.
    """
    contract = load_contract(root)
    wanted = {name for name in requested}
    unknown = wanted - set(OPTIONAL_CAPABILITIES)
    if unknown:
        raise ProjectError(f"Unknown capability: {', '.join(sorted(unknown))}")
    changes: list[CapabilityChange] = []
    for name in OPTIONAL_CAPABILITIES:
        enabled = _capability(contract, name).state is CapabilityState.ENABLED
        if name in wanted and not enabled:
            changes.append(CapabilityChange(name, _capability_label(name), enabling=True))
        elif name not in wanted and enabled:
            changes.append(CapabilityChange(name, _capability_label(name), enabling=False))
    enabling = [change.name for change in changes if change.enabling]
    creates: list[str] = []
    if enabling:
        projected = contract.model_copy(
            update={
                "capabilities": {
                    **contract.capabilities,
                    **{name: Capability(state=CapabilityState.ENABLED) for name in enabling},
                }
            }
        )
        creates = sorted(
            relative
            for relative in render_template_assets(projected)
            if not (root / relative).exists()
        )
    return CapabilityPlan(tuple(sorted(wanted)), tuple(changes), tuple(creates))


def set_capabilities(root: Path, requested: Sequence[str]) -> list[str]:
    """Apply a capability selection, reporting what each capability did."""
    plan = capability_plan(root, requested)
    return [
        enable_capability(root, change.name)
        if change.enabling
        else disable_capability(root, change.name)
        for change in plan.changes
    ]


def enable_capability(root: Path, name: str) -> str:
    contract = load_contract(root)
    _require_current_scaffold(contract, f"enable {_capability_label(name)} support")
    capability = _capability(contract, name)
    if capability.state is CapabilityState.ENABLED:
        return f"{_capability_label(name)} support is already enabled."
    updated = contract.model_copy(
        update={
            "capabilities": {
                **contract.capabilities,
                name: Capability(state=CapabilityState.ENABLED),
            }
        }
    )
    _materialize(root, updated)
    save_contract(root, updated)
    return f"{_capability_label(name)} support enabled; existing project files were retained."


def disable_capability(root: Path, name: str) -> str:
    contract = load_contract(root)
    capability = _capability(contract, name)
    if capability.state is CapabilityState.NEVER_ENABLED:
        return f"{_capability_label(name)} support has not been enabled."
    if capability.state is CapabilityState.INACTIVE:
        return f"{_capability_label(name)} support is already inactive."
    contract.capabilities[name] = Capability(state=CapabilityState.INACTIVE)
    save_contract(root, contract)
    return f"{_capability_label(name)} support deactivated; no directories or files were deleted."


def _capability(contract: ProjectContract, name: str) -> Capability:
    if name not in {"paper", "hpc"}:
        raise ProjectError(f"Unknown capability: {name}")
    try:
        return contract.capabilities[name]
    except KeyError as error:
        raise ProjectError(f"smairt.yaml does not define {name} support") from error


def _capability_label(name: str) -> str:
    return "Paper" if name == "paper" else "HPC"


def _materialize(root: Path, contract: ProjectContract, *, missing_only: bool = True) -> None:
    """Write the contract's scaffold, reporting a project-side conflict as a project error.

    A file sitting where the scaffold needs a directory is the researcher's own file and a
    situation they can fix. Letting the scaffold layer's exception travel unchanged made it
    surface as an unexplained traceback in the middle of enabling a capability.
    """
    try:
        materialize_template_assets(root, contract, missing_only=missing_only)
    except ScaffoldConflict as error:
        raise ProjectError(str(error)) from error


def _create_directory(path: Path) -> None:
    if path.exists() and not path.is_dir():
        raise ProjectError(f"Cannot create directory because a file exists: {path}")
    path.mkdir(parents=True, exist_ok=True)


def update_settings(
    root: Path,
    *,
    name: str | None = None,
    description: str | None = None,
    domain: str | None = None,
    question: str | None = None,
    assistant: Assistant | None = None,
    phase: StartingPhase | None = None,
    researcher: str | None = None,
    email: str | None = None,
    prompt_convention: PromptConvention | None = None,
    code_convention: CodeConvention | None = None,
    declare_multiplicity_policy: bool | None = None,
    separate_discovery_validation: bool | None = None,
    declare_unit_of_inference: bool | None = None,
    track_per_probe_status: bool | None = None,
) -> None:
    contract = load_contract(root)
    project = contract.project.model_validate(
        {
            **contract.project.model_dump(),
            **{
                key: value
                for key, value in {
                    "name": name,
                    "description": description,
                    "domain": domain,
                    "research_question": question,
                }.items()
                if value is not None
            },
        }
    )
    updates: dict[str, Any] = {"project": project}
    if assistant is not None:
        updates["assistant"] = assistant
    if phase is not None:
        _require_current_scaffold(contract, "change the current phase")
        _create_phase_directories_non_destructively(root)
        updates["current_phase"] = phase
    if researcher is not None or email is not None:
        current = contract.people["researcher"]
        updates["people"] = {
            **contract.people,
            "researcher": Researcher(
                name=researcher if researcher is not None else current.name,
                email=email if email is not None else current.email,
            ),
        }
    if question is not None and question == "":
        project = project.model_copy(update={"research_question": None})
        updates["project"] = project
    conventions = contract.conventions.model_dump(exclude_none=True)
    if prompt_convention is not None:
        conventions["prompt"] = prompt_convention.value
    if code_convention is not None:
        conventions["code"] = code_convention.value
    if conventions:
        updates["conventions"] = ConventionSettings.model_validate(conventions)
    rigor_updates = {
        key: value
        for key, value in {
            "declare_multiplicity_policy": declare_multiplicity_policy,
            "separate_discovery_validation": separate_discovery_validation,
            "declare_unit_of_inference": declare_unit_of_inference,
            "track_per_probe_status": track_per_probe_status,
        }.items()
        if value is not None
    }
    if rigor_updates:
        _require_current_scaffold(contract, "change research rigor declarations")
        updates["rigor"] = RigorSettings.model_validate(
            {**contract.rigor.model_dump(), **rigor_updates}
        )
    updated_contract = contract.model_copy(update=updates)
    if researcher is not None:
        _refresh_managed_license_holder(root, updated_contract)
    save_contract(root, updated_contract)
    if rigor_updates and any(updated_contract.rigor.model_dump().values()):
        # Render through the blueprint, but create only this newly activated researcher
        # artifact. A settings change must not incidentally restore unrelated missing files.
        rigor_path = root / "analysis/RIGOR.md"
        if not rigor_path.exists():
            rigor_path.write_text(render_template_assets(updated_contract)["analysis/RIGOR.md"])
    if prompt_convention is not None or code_convention is not None:
        _apply_convention_guidance(root, updated_contract)
    if assistant is not None:
        prepare_assistant(root)


def _create_phase_directories_non_destructively(root: Path) -> None:
    """Ensure every phase directory and its shipped guidance exists, creating nothing else.

    The guidance comes from the scaffold templates rather than from text repeated here. A
    second copy wrote different words than the files a project is generated with, so a phase
    README restored by a phase change did not match the one every other project has.
    """
    for directory in PHASE_DIRECTORIES:
        _create_directory(root / directory)
    _materialize(root, load_contract(root))


def update_collaborator(root: Path, role: str, name: str, email: str | None) -> None:
    if role == "researcher":
        raise ProjectError("Use Project Settings to change the primary researcher.")
    contract = load_contract(root)
    save_contract(
        root,
        contract.model_copy(
            update={"people": {**contract.people, role: Researcher(name=name, email=email)}}
        ),
    )


def license_preview(root: Path, license: License) -> str:
    contract = load_contract(root)
    return _render_license(license, contract.people["researcher"].name, contract.license_year)


def change_license(root: Path, license: License) -> None:
    contract = load_contract(root)
    status = _managed_license_status(root)
    if status == "modified":
        raise ProjectError("LICENSE has been modified; SMAIRT will not replace custom legal text.")
    if status == "invalid":
        raise ProjectError(
            "SMAIRT cannot safely verify LICENSE ownership from the project contract."
        )
    _write_managed_license(
        root, _render_license(license, contract.people["researcher"].name, contract.license_year)
    )
    save_contract(root, contract.model_copy(update={"license": license}))


def _refresh_managed_license_holder(root: Path, contract: ProjectContract) -> None:
    if _managed_license_status(root) == "unchanged":
        _write_managed_license(
            root,
            _render_license(
                contract.license, contract.people["researcher"].name, contract.license_year
            ),
        )


def _write_managed_license(root: Path, content: str) -> None:
    license_path = root / "LICENSE"
    license_path.write_text(content)


def _managed_license_status(root: Path) -> str:
    canonical = managed_asset_contents(root).get("LICENSE")
    if canonical is None:
        return "invalid"
    license_path = root / "LICENSE"
    if not license_path.is_file():
        return "missing"
    return "unchanged" if license_path.read_text() == canonical else "modified"


def _render_license(license: License, holder: str, year: int | None = None) -> str:
    value = year if year is not None else datetime.now(tz=UTC).year
    return LICENSE_TEXT[license].format(year=value, holder=holder)


def prepare_assistant(root: Path) -> str:
    contract = load_contract(root)
    alias_path = ASSISTANT_ALIASES[contract.assistant]
    alias = root / alias_path
    contents = (
        "# SMAIRT AI Context\n\nRead `prompts/AI_CONTEXT.md` before working in this project.\n"
    )
    if alias.exists():
        if alias.read_text() != contents:
            return f"{alias.relative_to(root)} is researcher-modified and was left unchanged."
        return f"{alias.relative_to(root)} already points to the canonical SMAIRT AI context."
    alias.parent.mkdir(parents=True, exist_ok=True)
    alias.write_text(contents)
    return f"Created {alias.relative_to(root)} as a pointer to prompts/AI_CONTEXT.md."


def assistant_launch_status(root: Path) -> tuple[str, str | None, str]:
    """Return the assistant's name, the command that would start it, and a row label.

    The dashboard needs this before offering the row, because reporting "not available"
    only after a researcher chooses Launch tells them too late to choose otherwise. The
    label is phrased to follow the word "Launch" so a row reads as one sentence.
    """
    contract = load_contract(root)
    name = contract.assistant.value
    command = ASSISTANT_COMMANDS[contract.assistant]
    if shutil.which(command[0]) is not None:
        return name, command[0], f"{name} with `{' '.join(command)}`"
    if shutil.which(EDITOR_COMMAND[0]) is not None:
        return name, EDITOR_COMMAND[0], f"VS Code instead, because {name} is not installed"
    return name, None, f"{name} — not installed, and VS Code is unavailable"


def launch_assistant(root: Path) -> tuple[bool, str]:
    contract = load_contract(root)
    name = contract.assistant.value
    command = ASSISTANT_COMMANDS[contract.assistant]
    chosen = command if shutil.which(command[0]) is not None else EDITOR_COMMAND
    executable = shutil.which(chosen[0])
    if executable is None:
        return (
            False,
            f"{name} is not available and neither is VS Code. Install {name} using its "
            f"official instructions, then run `{command[0]}` in {root}. You can also open "
            "this folder in your file manager.",
        )
    try:
        subprocess.Popen([executable, *chosen[1:]], cwd=root)
    except OSError as error:
        return False, f"Could not launch {name}: {error}"
    if chosen is command:
        return True, f"Launched {name} in {root}."
    return True, f"{name} is not installed; opened {root} in VS Code instead."


def open_folder(root: Path) -> str:
    if sys.platform == "darwin":
        command = ["open", str(root)]
    elif sys.platform.startswith("linux"):
        command = ["xdg-open", str(root)]
    else:
        return f"Open this project folder in your file manager: {root}"
    if shutil.which(command[0]) is None:
        return f"Open this project folder in your file manager: {root}"
    try:
        subprocess.Popen(command)
    except OSError:
        return f"Open this project folder in your file manager: {root}"
    return f"Opened project folder: {root}"


def project_check(root: Path) -> list[CheckIssue]:
    issues: list[CheckIssue] = []
    try:
        contract = load_contract(root)
    except ProjectError as error:
        return [CheckIssue("invalid-contract", "smairt.yaml", str(error))]
    if contract.scaffold_version != __version__:
        issues.append(
            CheckIssue(
                "scaffold-version-mismatch",
                "smairt.yaml",
                f"Project scaffold {contract.scaffold_version} differs from installed SMAIRT "
                f"{__version__}. Run `smairt upgrade` to review and apply the difference.",
            )
        )
    for directory in REQUIRED_DIRECTORIES:
        path = root / directory
        if not path.is_dir():
            issues.append(
                CheckIssue(
                    "missing-directory",
                    directory,
                    f"Required SMAIRT directory is missing: {directory}",
                    f"create-directory:{directory}",
                )
            )
    for directory in PHASE_DIRECTORIES:
        if not (root / directory).is_dir():
            issues.append(
                CheckIssue(
                    "missing-phase-directory",
                    directory,
                    f"Directory required by the current phase is missing: {directory}",
                    f"create-directory:{directory}",
                )
            )
    for name, capability in contract.capabilities.items():
        if capability.state is CapabilityState.ENABLED:
            required_paths = ("paper", "paper/analysis") if name == "paper" else ("hpc",)
            if any(not (root / required).is_dir() for required in required_paths):
                required = next(
                    required for required in required_paths if not (root / required).is_dir()
                )
                issues.append(
                    CheckIssue(
                        "missing-capability-directory",
                        required,
                        f"{_capability_label(name)} support is enabled but {required}/ is missing.",
                        f"restore-capability:{name}",
                    )
                )
    if contract.git_initialized and not (root / ".git").is_dir():
        issues.append(
            CheckIssue(
                "missing-git-repository",
                ".git",
                "Project metadata says Git was initialized, but .git/ is missing.",
            )
        )
    alias_path = ASSISTANT_ALIASES.get(contract.assistant)
    alias = root / alias_path if alias_path is not None else None
    if alias is not None and not alias.is_file():
        issues.append(
            CheckIssue(
                "missing-assistant-pointer",
                alias.relative_to(root).as_posix(),
                "Selected assistant pointer is missing.",
                "create-assistant-pointer",
            )
        )
    issues.extend(_outcome_drift_issues(root))
    issues.extend(_dangling_hypothesis_issues(root))
    issues.extend(_manifest_reconciliation_issues(root, contract))
    if contract.scaffold_version == __version__:
        issues.extend(_managed_file_issues(root, contract))
        issues.extend(_unresolved_token_issues(root))
    return issues


def _outcome_drift_issues(root: Path) -> list[CheckIssue]:
    """Report iterations whose state row disagrees with the latest recorded outcome.

    The iteration log holds a scannable row per iteration and an append-only history of
    every outcome ever recorded. A helper fills the row once and then only ever appends,
    so a revised outcome deliberately leaves the row stale rather than overwriting the
    researcher's wording.

    Detecting that drift is structural, not scientific: this compares two strings and
    never judges which is right. There is no repair, because choosing the wording is the
    researcher's.
    """
    log_path = root / "analysis" / "ITERATION_LOG.md"
    if not log_path.is_file():
        return []
    rows, history = _iteration_log_records(log_path.read_text())
    relative = log_path.relative_to(root).as_posix()
    return [
        CheckIssue(
            "iteration-outcome-drift",
            relative,
            f"Iteration {number} records a later outcome than its row states: "
            f"row says {rows[number]!r}, history says {latest!r}.",
        )
        for number, latest in history.items()
        if number in rows and rows[number] != latest
    ]


def _manifest_reconciliation_issues(root: Path, contract: ProjectContract) -> list[CheckIssue]:
    """Report selected-result records absent from an active Paper manifest.

    This is a filename/heading reconciliation only. It does not decide whether a claim
    belongs in a paper, whether a hypothesis is supported, or how manifest prose should
    read. Consequently it has no automatic repair.
    """
    paper = contract.capabilities.get("paper")
    if paper is None or paper.state is not CapabilityState.ENABLED:
        return []
    manifest = root / "FINAL_MANIFEST.md"
    if not manifest.is_file():
        return []  # The managed-file check reports the missing capability artifact.
    recorded = {
        int(number)
        for number in re.findall(
            r"^### Selected Result: Iteration (\d+)\s*$", manifest.read_text(), re.MULTILINE
        )
    }
    issues: list[CheckIssue] = []
    for selected in sorted((root / "analysis").glob("SELECTED_[0-9]*.md")):
        match = re.fullmatch(r"SELECTED_(\d+)\.md", selected.name)
        if match is None or int(match.group(1)) in recorded:
            continue
        number = int(match.group(1))
        relative = selected.relative_to(root).as_posix()
        issues.append(
            CheckIssue(
                "manifest-selection-drift",
                relative,
                f"Iteration {number:02d} has a selected-result record but no matching "
                "selected-result heading in FINAL_MANIFEST.md.",
            )
        )
    return issues


def _dangling_hypothesis_issues(root: Path) -> list[CheckIssue]:
    """Report iteration rows naming a hypothesis file the project does not contain.

    The whole value of the record is that one number joins hypothesis, script, log, and
    analysis. A typo in `--hypothesis` used to write a row pointing at nothing, and the
    project still reported clean — so the broken link surfaced months later, if ever.

    `new_iteration.py` now refuses an unknown hypothesis, but a project may already carry
    such a row, and a hypothesis file can be renamed or deleted afterwards. This is a
    filename comparison and nothing more: whether a hypothesis is well posed is the
    researcher's judgment. There is no repair, because only the researcher knows whether the
    reference or the filename is the mistake.
    """
    log_path = root / "analysis" / "ITERATION_LOG.md"
    if not log_path.is_file():
        return []
    relative = log_path.relative_to(root).as_posix()
    existing = {path.stem for path in (root / "hypotheses").glob("HYPOTHESIS_[0-9]*.md")}
    issues: list[CheckIssue] = []
    for number, referenced in sorted(_iteration_hypotheses(log_path.read_text()).items()):
        missing = sorted(name for name in referenced if name not in existing)
        if missing:
            issues.append(
                CheckIssue(
                    "dangling-hypothesis-reference",
                    relative,
                    f"Iteration {number} names a hypothesis with no file: {', '.join(missing)}.",
                )
            )
    return issues


def _iteration_hypotheses(content: str) -> dict[str, set[str]]:
    """Return the hypothesis identifiers each iteration's state row references.

    Read from the state table only. The outcome history has a different shape and records
    prose rather than references.
    """
    references: dict[str, set[str]] = {}
    in_history = False
    for line in content.splitlines():
        if line.startswith("## "):
            in_history = line.strip() == "## Outcome history"
            continue
        if in_history or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and re.fullmatch(r"\d+", cells[0]):
            named = set(re.findall(r"HYPOTHESIS_\d+", cells[3]))
            if named:
                references[cells[0]] = named
    return references


def _iteration_log_records(content: str) -> tuple[dict[str, str], dict[str, str]]:
    """Return each iteration's stated outcome and its most recently recorded one.

    The two tables are told apart by which heading precedes them, so a researcher adding
    prose or their own sections between them does not confuse the reading.
    """
    rows: dict[str, str] = {}
    history: dict[str, str] = {}
    in_history = False
    for line in content.splitlines():
        if line.startswith("## "):
            in_history = line.strip() == "## Outcome history"
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 3:
            if in_history and re.fullmatch(r"\d+", cells[1]):
                history[cells[1]] = cells[2]
            elif not in_history and re.fullmatch(r"\d+", cells[0]):
                rows[cells[0]] = cells[-1]
    return rows, history


def _managed_file_issues(root: Path, contract: ProjectContract) -> list[CheckIssue]:
    assets = managed_asset_contents(root)
    issues: list[CheckIssue] = []
    ownership = asset_ownership(contract)
    for relative, expected in sorted(assets.items()):
        path = root / relative
        if not path.is_file():
            capability = next(
                (
                    asset.condition
                    for asset in active_assets(contract)
                    if asset_path(asset, contract) == relative
                    and asset.condition in {"paper", "hpc"}
                ),
                None,
            )
            issues.append(
                CheckIssue(
                    "missing-managed-file",
                    relative,
                    f"Managed file is missing: {relative}",
                    f"restore-capability:{capability}" if capability is not None else None,
                )
            )
        elif path.read_text() != expected and ownership[relative] == "tool-guidance":
            issues.append(
                CheckIssue(
                    "modified-managed-file",
                    relative,
                    f"Managed file was modified and will be preserved: {relative}",
                )
            )
    return issues


def _unresolved_token_issues(root: Path) -> list[CheckIssue]:
    try:
        files = managed_asset_contents(root)
    except ProjectError:
        return []
    issues: list[CheckIssue] = []
    for relative in sorted(files):
        if Path(relative).suffix == ".py":
            continue
        path = root / relative
        if not path.is_file():
            continue
        try:
            contents = path.read_text()
        except UnicodeDecodeError:
            continue
        if "{{" in contents or "}}" in contents:
            issues.append(
                CheckIssue(
                    "unresolved-template-token",
                    relative,
                    f"Managed file contains an unresolved template token: {relative}",
                )
            )
    return issues


def repair_previews(root: Path, identifiers: list[str]) -> list[CheckIssue]:
    _require_current_scaffold(load_contract(root), "repair package-owned structure")
    repairable = {issue.repair: issue for issue in project_check(root) if issue.repair is not None}
    selected: list[CheckIssue] = []
    for identifier in identifiers:
        if identifier not in repairable:
            raise ProjectError(f"No safe repair is available for: {identifier}")
        selected.append(repairable[identifier])
    return selected


def apply_repairs(root: Path, identifiers: list[str]) -> list[CheckIssue]:
    selected = repair_previews(root, identifiers)
    for issue in selected:
        assert issue.repair is not None
        if issue.repair.startswith("create-directory:"):
            _create_directory(root / issue.repair.removeprefix("create-directory:"))
        elif issue.repair == "create-assistant-pointer":
            prepare_assistant(root)
        elif issue.repair.startswith("restore-capability:"):
            # Both capabilities restore the same way: write whatever the contract's enabled
            # capabilities declare and is missing. The two wrappers this replaced differed
            # only in an argument one of them deleted.
            _materialize(root, load_contract(root))
    return selected


def managed_file_statuses(root: Path) -> list[dict[str, str]]:
    contract = load_contract(root)
    files = managed_asset_contents(root, include_inactive=True)
    statuses: list[dict[str, str]] = []
    for relative, expected in sorted(files.items()):
        path = root / relative
        if contract.scaffold_version != __version__:
            status = "version-mismatch"
        else:
            status = (
                "missing"
                if not path.is_file()
                else "unchanged"
                if path.read_text() == expected
                else "modified"
            )
        statuses.append({"path": relative, "status": status, "expected_hash": _hash_text(expected)})
    return statuses


def managed_asset_previews(root: Path, paths: list[str]) -> list[dict[str, str]]:
    contract = load_contract(root)
    _require_current_scaffold(contract, "regenerate managed assets")
    assets = managed_asset_contents(root)
    statuses = {item["path"]: item for item in managed_file_statuses(root)}
    previews: list[dict[str, str]] = []
    for relative in paths:
        status = statuses.get(relative)
        if status is None or relative not in assets:
            raise ProjectError(f"No managed asset is available for regeneration: {relative}")
        if status["status"] == "modified":
            raise ProjectError(f"Managed file was modified and will be preserved: {relative}")
        previews.append({"path": relative, "status": status["status"]})
    return previews


def regenerate_managed_assets(root: Path, paths: list[str]) -> list[dict[str, str]]:
    previews = managed_asset_previews(root, paths)
    assets = managed_asset_contents(root)
    for preview in previews:
        path = root / preview["path"]
        content = assets[preview["path"]]
        assert isinstance(content, str)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return previews


def managed_asset_paths(root: Path) -> list[str]:
    return sorted(managed_asset_contents(root))


@dataclass(frozen=True)
class UpgradeChange:
    """One tool-owned asset an upgrade would write, create, or leave alone."""

    path: str
    action: str
    """One of `update`, `create`, `unchanged`, `preserve`, or `outside`."""

    @property
    def writes(self) -> bool:
        return self.action in {"update", "create"}


@dataclass(frozen=True)
class UpgradePlan:
    """What moving a project onto the installed scaffold version would do.

    Every entry is derived from the same rendering the write itself uses, so the preview
    cannot describe an operation other than the one that would run.
    """

    from_version: str
    to_version: str
    changes: tuple[UpgradeChange, ...]

    @property
    def is_current(self) -> bool:
        return self.from_version == self.to_version

    @property
    def updates(self) -> tuple[UpgradeChange, ...]:
        return tuple(change for change in self.changes if change.action == "update")

    @property
    def creates(self) -> tuple[UpgradeChange, ...]:
        return tuple(change for change in self.changes if change.action == "create")

    @property
    def preserved(self) -> tuple[UpgradeChange, ...]:
        """Assets that differ from the installed version and are kept exactly as they are.

        Deliberately not called "researcher-modified": a difference in an editable starter may
        be the researcher's edit or a change the newer scaffold made to the starter itself, and
        SMAIRT cannot tell those apart.
        """
        return tuple(change for change in self.changes if change.action == "preserve")

    @property
    def outside(self) -> tuple[UpgradeChange, ...]:
        """Managed paths that resolve outside the project and are therefore never touched."""
        return tuple(change for change in self.changes if change.action == "outside")

    @property
    def unchanged(self) -> tuple[UpgradeChange, ...]:
        return tuple(change for change in self.changes if change.action == "unchanged")

    @property
    def writes_nothing(self) -> bool:
        return not any(change.writes for change in self.changes)


def upgrade_plan(root: Path) -> UpgradePlan:
    """Describe what upgrading this project to the installed version would change.

    Only tool-owned assets are considered, and a difference in anything the package does not
    own is reported as kept rather than rewritten. Researcher work is never in this plan and
    is never written by an upgrade: the blueprint classifies it as `researcher-work`, and
    `_managed_assets_for()` excludes it.

    This exists because tying a project to its recorded scaffold version, as ADR 0001
    requires, left every project created by an earlier release unable to change its own
    settings, capabilities, or structure. Refusing a mutation is correct; refusing it with
    no route forward makes the tool read-only the moment it is updated.
    """
    contract = load_contract(root)
    # Rendered from the contract as it will be after the version moves, so an asset that
    # only exists in the newer scaffold appears as a creation rather than being missed.
    projected = contract.model_copy(update={"scaffold_version": __version__})
    assets = _managed_assets_for(projected)
    ownership = asset_ownership(projected)
    changes: list[UpgradeChange] = []
    for relative, expected in sorted(assets.items()):
        path = root / relative
        if _escapes_project(root, relative):
            # A managed path that reaches outside the project, through a symlinked file or a
            # symlinked parent, is never written or read. Following it would let an upgrade
            # modify a file that is not part of this project at all.
            changes.append(UpgradeChange(relative, "outside"))
            continue
        if not path.exists():
            changes.append(UpgradeChange(relative, "create"))
            continue
        current = path.read_text()
        if current == expected:
            changes.append(UpgradeChange(relative, "unchanged"))
        elif ownership[relative] == "tool-guidance":
            changes.append(UpgradeChange(relative, "update"))
        else:
            # Anything the package does not own is kept. An editable starter is meant to be
            # edited, so a difference may be the researcher's work or a change the newer
            # scaffold made to the starter; SMAIRT cannot tell those apart, and keeping the
            # file is correct either way.
            changes.append(UpgradeChange(relative, "preserve"))
    return UpgradePlan(contract.scaffold_version, __version__, tuple(changes))


def _escapes_project(root: Path, relative: str) -> bool:
    """Report whether a managed path resolves outside the project directory.

    Blueprint paths are validated as lexically safe, which says nothing about the filesystem:
    a researcher, a sync client, or a build step can replace any managed file or one of its
    parent directories with a symlink. `write_text` follows both, so without this check an
    upgrade could rewrite an arbitrary file elsewhere on the machine — verified by pointing
    `docs/12_STEPS.md` at an unrelated file and watching an upgrade destroy it.

    A path that does not exist yet is judged by its nearest existing ancestor, so a dangling
    symlink cannot be used to create a file outside the project either.
    """
    try:
        anchor = root.resolve(strict=True)
    except OSError:
        return True
    candidate = root / relative
    existing = candidate
    while not existing.exists() and existing != root:
        existing = existing.parent
    try:
        resolved = existing.resolve(strict=True)
    except OSError:
        return True
    return resolved != anchor and anchor not in resolved.parents


def apply_upgrade(root: Path) -> UpgradePlan:
    """Move the project onto the installed scaffold version.

    Writes exactly what the plan reports as a write, and nothing else. Earlier this also ran
    a general materialize pass afterwards, which created any missing active asset — including
    the blueprint's `researcher-work` records. That meant a researcher who had deliberately
    deleted `analysis/BREADCRUMB_TRAIL.md` silently got a fresh package template back, from an
    operation whose preview never mentioned the file. A preview that omits a write is not a
    preview, so the pass is gone.

    Each file is written to a temporary neighbour and moved into place, so an interruption or
    a full disk leaves the previous content intact rather than a half-written file. The
    contract is saved last, so an interrupted upgrade stays on its old version and the same
    command can simply be run again.
    """
    contract = load_contract(root)
    plan = upgrade_plan(root)
    if plan.is_current:
        raise ProjectError(
            f"Project is already on the installed SMAIRT {__version__}; nothing to upgrade."
        )
    projected = contract.model_copy(update={"scaffold_version": __version__})
    assets = _managed_assets_for(projected)
    for change in plan.changes:
        if not change.writes:
            continue
        if _escapes_project(root, change.path):
            # Re-checked immediately before writing, because the plan was built earlier and a
            # path can be replaced with a symlink in between.
            raise ProjectError(
                f"{change.path} resolves outside the project, so SMAIRT will not write it. "
                "Replace the symbolic link with an ordinary file and run the upgrade again."
            )
        _replace_atomically(root / change.path, assets[change.path])
    save_contract(root, projected)
    return plan


def _replace_atomically(path: Path, content: str) -> None:
    """Write content to path so that a failure leaves the previous file intact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.smairt-tmp")
    try:
        temporary.write_text(content)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _managed_assets_for(contract: ProjectContract) -> dict[str, str]:
    """Return tool-owned asset content for a contract that is not yet saved.

    `managed_asset_contents()` reloads the contract from disk, which cannot describe a
    version the project has not moved to yet. This renders the same assets from a projected
    contract so the preview and the write agree on what the upgraded project contains.
    """
    assets = render_template_assets(contract)
    ownership = asset_ownership(contract)
    assets = {
        relative: content
        for relative, content in assets.items()
        if ownership[relative] != "researcher-work"
    }
    _add_contract_derived_assets(assets, contract)
    return assets


def next_workflow_action(root: Path) -> tuple[str, str]:
    """Return what the project is missing next, and the command that addresses it.

    Derived from the contract and from which files exist, so it reports the state of the
    record rather than offering a scientific opinion. It never says which hypothesis to
    form or whether a result is good; those decisions are the researcher's, and a tool
    that nudged them would be overstepping.

    The gap this closes is that a generated project's entry points are discoverable only
    by opening `scripts/README.md`, so a researcher who does not think to look finds a
    dashboard of utilities and no route into the workflow at all.
    """
    contract = load_contract(root)
    if not contract.project.research_question:
        return (
            "No research question recorded yet",
            "smairt settings --question '...', then expand on it in background/",
        )
    if not sorted((root / "hypotheses").glob("HYPOTHESIS_[0-9]*.md")):
        return (
            "No hypothesis yet",
            "python3 scripts/new_track.py '<the question>' <phase>",
        )
    if not sorted((root / "experiments").glob("*/script_*.py")):
        return (
            "Hypothesis recorded, no iteration yet",
            "commit the criteria, then python3 scripts/new_iteration.py",
        )
    uninterpreted = _iterations_missing(root, "analysis/ANALYSIS_{:02d}.md")
    if uninterpreted:
        listed = ", ".join(f"{number:02d}" for number in uninterpreted)
        return (
            f"Iterations awaiting an interpretation: {listed}",
            "read the log in results/logs/, then write analysis/ANALYSIS_NN.md",
        )
    unrecorded = _iterations_without_a_recorded_outcome(root)
    if unrecorded:
        listed = ", ".join(f"{number:02d}" for number in unrecorded)
        return (
            f"Interpreted but the outcome is not recorded: {listed}",
            "python3 scripts/record_outcome.py NN --outcome '...'",
        )
    return (
        "Every iteration is interpreted and recorded",
        "python3 scripts/new_iteration.py for the next attempt, or select_result.py to report one",
    )


def _iteration_numbers(root: Path) -> list[int]:
    """Return every iteration number that has a script, in order."""
    return sorted(
        int(match.group(1))
        for script in (root / "experiments").glob("*/script_*.py")
        if (match := re.match(r"script_(\d+)", script.name))
    )


def _iterations_missing(root: Path, template: str) -> list[int]:
    """Return iterations for which the file named by the template does not exist."""
    return [
        number
        for number in _iteration_numbers(root)
        if not (root / template.format(number)).exists()
    ]


def _iterations_without_a_recorded_outcome(root: Path) -> list[int]:
    """Return interpreted iterations whose outcome cell still holds its placeholder.

    An interpretation that never reaches the log leaves the scannable record saying
    nothing came of the attempt, which is the gap the log exists to close.
    """
    log_path = root / "analysis" / "ITERATION_LOG.md"
    if not log_path.is_file():
        return []
    rows, _ = _iteration_log_records(log_path.read_text())
    return [
        number
        for number in _iteration_numbers(root)
        if rows.get(f"{number:02d}", "").startswith("[Record after")
    ]


def detected_tools(root: Path) -> dict[str, str]:
    contract = load_contract(root)
    command = ASSISTANT_COMMANDS.get(contract.assistant)
    assistant_path = (
        "not applicable" if command is None else shutil.which(command[0]) or "not found"
    )
    return {
        "Python": sys.executable,
        "Git": shutil.which("git") or "not found",
        f"Selected assistant ({contract.assistant.value})": assistant_path,
    }


def managed_asset_contents(root: Path, *, include_inactive: bool = False) -> dict[str, str]:
    contract = load_contract(root)
    assets = render_template_assets(contract, include_inactive=include_inactive)
    ownership = asset_ownership(contract, include_inactive=include_inactive)
    assets = {
        relative: content
        for relative, content in assets.items()
        if ownership[relative] != "researcher-work"
    }
    _add_contract_derived_assets(assets, contract)
    return assets


def _add_contract_derived_assets(assets: dict[str, str], contract: ProjectContract) -> None:
    """Add the assets rendered from the contract rather than from a template file."""
    assets["LICENSE"] = _render_license(
        contract.license, contract.people["researcher"].name, contract.license_year
    )
    assets[ASSISTANT_ALIASES[contract.assistant]] = (
        "# SMAIRT AI Context\n\nRead `prompts/AI_CONTEXT.md` before working in this project.\n"
    )
    _apply_contract_conventions(assets, contract)


def require_upgradable(root: Path, action: str) -> None:
    """Refuse an action that a scaffold-version difference blocks, before listing anything.

    Commands that preview before writing have to check this at the point they start
    describing the operation, not only at the point they would write. `smairt repair` on an
    out-of-date project used to report "No safe repairs are available" and exit 0 while every
    repair was blocked, and `smairt regenerate` listed all forty-three assets as eligible
    before refusing on confirm. Both statements were false in a way that reads as success.
    """
    _require_current_scaffold(load_contract(root), action)


def _require_current_scaffold(contract: ProjectContract, action: str) -> None:
    """Refuse a package-owned mutation on an out-of-date project, and say what to run.

    ADR 0001 ties a project to its recorded scaffold version, so refusing here is correct.
    Refusing without naming a route forward is not: it left every project created by an
    earlier release unable to change its settings, capabilities, or structure, with the only
    documented answer being to start a new project.
    """
    if contract.scaffold_version != __version__:
        raise ProjectError(
            f"Cannot {action}: project scaffold {contract.scaffold_version} differs from installed "
            f"SMAIRT {__version__}. Run `smairt upgrade` to review the changes and move this "
            "project onto the installed version; researcher work is never rewritten."
        )


def _apply_contract_conventions(assets: dict[str, str], contract: ProjectContract) -> None:
    prompt_additions = {
        PromptConvention.PLAN_FIRST: "\nProject prompt convention: create a plan before complex work.\n",
        PromptConvention.DIRECT_TASK: "\nProject prompt convention: state the concrete task and constraints before work.\n",
    }
    code_additions = {
        CodeConvention.TYPED_PYTHON: "\nProject code convention: use type annotations for public functions and data boundaries.\n",
        CodeConvention.STANDARD_PYTHON: "\nProject code convention: favor readable standard Python with documented inputs and outputs.\n",
    }
    if contract.conventions.prompt is not None:
        assets["prompts/AI_CONTEXT.md"] = (
            assets["prompts/AI_CONTEXT.md"].rstrip("\n")
            + prompt_additions[contract.conventions.prompt]
        )
    if contract.conventions.code is not None:
        assets["prompts/CODE_CONVENTIONS.md"] = (
            assets["prompts/CODE_CONVENTIONS.md"].rstrip("\n")
            + code_additions[contract.conventions.code]
        )


def _apply_convention_guidance(root: Path, contract: ProjectContract) -> None:
    templates = Path(__file__).parent / "assets" / "scaffold"
    targets = {
        "prompt": Path("prompts/AI_CONTEXT.md"),
        "code": Path("prompts/CODE_CONVENTIONS.md"),
    }
    for name in contract.conventions.model_dump(exclude_none=True):
        relative = targets[name]
        path = root / relative
        base = (templates / relative).read_text()
        if path.read_text().rstrip("\n") != base.rstrip("\n"):
            continue
        content = managed_asset_contents(root).get(relative.as_posix())
        if content is not None:
            path.write_text(content)


def _managed_asset_content(root: Path, relative: str) -> str | None:
    return managed_asset_contents(root).get(relative)


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_text(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def _timestamp() -> str:
    return datetime.now(tz=UTC).isoformat()


def create_management_assets(
    root: Path, assistant: Assistant, license: License, researcher: Researcher
) -> None:
    """Create the initial tool-owned utility files before the manifest is written."""
    (root / "LICENSE").write_text(_render_license(license, researcher.name))
    alias = root / ASSISTANT_ALIASES[assistant]
    alias.parent.mkdir(parents=True, exist_ok=True)
    alias.write_text(
        "# SMAIRT AI Context\n\nRead `prompts/AI_CONTEXT.md` before working in this project.\n"
    )
