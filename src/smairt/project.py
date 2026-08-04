from __future__ import annotations

import hashlib
import json
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
    StartingPhase,
)
from smairt.scaffold import (
    ASSISTANT_POINTERS,
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
PHASE_DIRECTORIES = {
    StartingPhase.SYNTHETIC: (
        "data/synthetic",
        "data/downloaded",
        "data/real",
        "experiments/01_synthetic",
        "experiments/02_downloaded",
        "experiments/03_real_data",
    ),
    StartingPhase.DOWNLOADED: (
        "data/downloaded",
        "data/real",
        "experiments/02_downloaded",
        "experiments/03_real_data",
    ),
    StartingPhase.REAL: ("data/real", "experiments/03_real_data"),
}
LICENSE_TEXT = {
    License.MIT: 'MIT License\n\nCopyright (c) {year} {holder}\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.\n',
    License.BSD_3_CLAUSE: 'BSD 3-Clause License\n\nCopyright (c) {year}, {holder}\nAll rights reserved.\n\nRedistribution and use in source and binary forms, with or without\nmodification, are permitted provided that the following conditions are met:\n\n1. Redistributions of source code must retain the above copyright notice, this\n   list of conditions and the following disclaimer.\n2. Redistributions in binary form must reproduce the above copyright notice,\n   this list of conditions and the following disclaimer in the documentation\n   and/or other materials provided with the distribution.\n3. Neither the name of the copyright holder nor the names of its contributors\n   may be used to endorse or promote products derived from this software\n   without specific prior written permission.\n\nTHIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"\nAND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE\nIMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE\nDISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE\nFOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL\nDAMAGES.\n',
    License.APACHE_2_0: 'Apache License\nVersion 2.0, January 2004\nhttp://www.apache.org/licenses/\n\nCopyright {year} {holder}\n\nLicensed under the Apache License, Version 2.0 (the "License");\nyou may not use this file except in compliance with the License.\nYou may obtain a copy of the License at\n\n    http://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software\ndistributed under the License is distributed on an "AS IS" BASIS,\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\nSee the License for the specific language governing permissions and\nlimitations under the License.\n',
    License.GPL_3_0: "GNU GENERAL PUBLIC LICENSE\nVersion 3, 29 June 2007\n\nCopyright (C) {year} {holder}\n\nThis program is free software: you can redistribute it and/or modify\nit under the terms of the GNU General Public License as published by\nthe Free Software Foundation, either version 3 of the License, or\n(at your option) any later version.\n\nThis program is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without even the implied warranty of\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the\nGNU General Public License for more details.\n",
    License.PROPRIETARY: "All rights reserved.\n\nCopyright (c) {year} {holder}\n\nNo permission is granted to use, copy, modify, distribute, or sublicense this\nproject except with the prior written permission of the copyright holder.\n",
}
LICENSE_EXPLANATIONS = {
    License.MIT: "Permissive reuse with attribution and no warranty.",
    License.BSD_3_CLAUSE: "Permissive reuse with attribution and no endorsement.",
    License.APACHE_2_0: "Permissive reuse with patent terms and notices.",
    License.GPL_3_0: "Reuse and distribution requires sharing covered source changes.",
    License.PROPRIETARY: "Reserve reuse rights unless you grant permission.",
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
    except (OSError, ValidationError, yaml.YAMLError) as error:
        raise ProjectError(f"Invalid smairt.yaml: {error}") from error


def save_contract(root: Path, contract: ProjectContract) -> None:
    data = contract.model_dump(mode="json", exclude_none=True)
    if not contract.conventions.model_dump(exclude_none=True):
        data.pop("conventions", None)
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
    materialize_template_assets(root, updated, missing_only=True)
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


def _create_paper_assets_safely(root: Path) -> None:
    materialize_template_assets(root, load_contract(root), missing_only=True)


def _create_hpc_assets_safely(root: Path, slug: str) -> None:
    del slug
    materialize_template_assets(root, load_contract(root), missing_only=True)


def hpc_asset_contents(slug: str) -> dict[str, str]:
    return {
        "hpc/README.md": "# HPC Guidance\n\n"
        "Run `sbatch hpc/slurm_job.sh <experiment-command> [arguments...]` from the project root "
        "after adapting the scheduler directives to your cluster. Choose a command that uses "
        "paths created for the project's current phase. SMAIRT does not submit or manage jobs.\n",
        "hpc/slurm_job.sh": "#!/usr/bin/env bash\n"
        f"#SBATCH --job-name={slug}\n"
        "#SBATCH --output=results/logs/%x-%j.out\n\n"
        "set -eu\n\n"
        'if [ "$#" -eq 0 ]; then\n'
        '  echo "Usage: sbatch hpc/slurm_job.sh <experiment-command> [arguments...]" >&2\n'
        '  echo "Choose a command and paths appropriate for the current project phase." >&2\n'
        "  exit 2\n"
        "fi\n\n"
        '"$@"\n',
    }


def paper_asset_contents() -> dict[str, str]:
    return {
        "paper/README.md": "# Paper Workspace\n\n"
        "Paper support is an optional publication overlay on the standard SMAIRT audit trail. "
        "Use `paper/analysis/` for publication-focused interpretation and `paper/outline.md` "
        "for the evolving manuscript structure. Check `capabilities.paper.state` in "
        "`smairt.yaml`: retained files are researcher-owned history while Paper is inactive.\n",
        "paper/outline.md": "# Paper Outline\n",
        "paper/analysis/README.md": "# Paper Analysis\n\n"
        "Connect results from the standard research workflow to claims in the paper outline.\n",
    }


def phase_asset_contents(phase: StartingPhase) -> dict[str, str]:
    guidance = {
        "data/synthetic": "Generated data used to test assumptions before external data is introduced.",
        "data/downloaded": "Public or benchmark data, with provenance recorded alongside retrieval steps.",
        "data/real": "Collected or operational data; document access, provenance, and transformations.",
        "experiments/01_synthetic": "Scripts and notes for experiments against synthetic data.",
        "experiments/02_downloaded": "Scripts and notes for experiments against downloaded data.",
        "experiments/03_real_data": "Scripts and notes for experiments against real data.",
    }
    return {
        f"{directory}/README.md": f"# {directory}\n\n{guidance[directory]}\n"
        for directory in phase_directories(phase)
    }


def _create_directory(path: Path) -> None:
    if path.exists() and not path.is_dir():
        raise ProjectError(f"Cannot create directory because a file exists: {path}")
    path.mkdir(parents=True, exist_ok=True)


def _write_if_missing_and_track(root: Path, path: Path, content: str) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


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
        _create_phase_directories_non_destructively(root, phase)
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
    updated_contract = contract.model_copy(update=updates)
    if researcher is not None:
        _refresh_managed_license_holder(root, updated_contract)
    save_contract(root, updated_contract)
    if prompt_convention is not None or code_convention is not None:
        _apply_convention_guidance(root, updated_contract)
    if assistant is not None:
        prepare_assistant(root)


def _create_phase_directories_non_destructively(root: Path, phase: StartingPhase) -> None:
    for directory in phase_directories(phase):
        _create_directory(root / directory)
    for relative, content in phase_asset_contents(phase).items():
        _write_if_missing_and_track(root, root / relative, content)


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
                f"Project scaffold {contract.scaffold_version} differs from installed SMAIRT {__version__}.",
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
    for directory in _phase_directories(contract.current_phase):
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
    if contract.scaffold_version == __version__:
        issues.extend(_managed_file_issues(root, contract))
        issues.extend(_unresolved_token_issues(root))
    return issues


def _phase_directories(phase: StartingPhase) -> tuple[str, ...]:
    return phase_directories(phase)


def phase_directories(phase: StartingPhase) -> tuple[str, ...]:
    del phase
    return PHASE_DIRECTORIES[StartingPhase.SYNTHETIC]


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
            name = issue.repair.removeprefix("restore-capability:")
            contract = load_contract(root)
            if name == "paper":
                _create_paper_assets_safely(root)
            else:
                _create_hpc_assets_safely(root, contract.project.slug)
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
            "python scripts/new_track.py '<the question>' <phase>",
        )
    if not sorted((root / "experiments").glob("*/script_*.py")):
        return (
            "Hypothesis recorded, no iteration yet",
            "commit the criteria, then python scripts/new_iteration.py",
        )
    unrecorded = _iterations_awaiting_an_outcome(root)
    if unrecorded:
        listed = ", ".join(f"{number:02d}" for number in unrecorded)
        return (
            f"Iterations awaiting an interpretation: {listed}",
            "read the log in results/logs/, then write analysis/ANALYSIS_NN.md",
        )
    return (
        "Every iteration is interpreted",
        "python scripts/new_iteration.py for the next attempt, or select_result.py to report one",
    )


def _iterations_awaiting_an_outcome(root: Path) -> list[int]:
    """Return iterations that have a script but no interpretation written yet."""
    numbers = sorted(
        int(match.group(1))
        for script in (root / "experiments").glob("*/script_*.py")
        if (match := re.match(r"script_(\d+)", script.name))
    )
    return [
        number
        for number in numbers
        if not (root / "analysis" / f"ANALYSIS_{number:02d}.md").exists()
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
    assets["LICENSE"] = _render_license(
        contract.license, contract.people["researcher"].name, contract.license_year
    )
    assets[ASSISTANT_ALIASES[contract.assistant]] = (
        "# SMAIRT AI Context\n\nRead `prompts/AI_CONTEXT.md` before working in this project.\n"
    )
    _apply_contract_conventions(assets, contract)
    return assets


def _require_current_scaffold(contract: ProjectContract, action: str) -> None:
    if contract.scaffold_version != __version__:
        raise ProjectError(
            f"Cannot {action}: project scaffold {contract.scaffold_version} differs from installed "
            f"SMAIRT {__version__}. An explicit upgrade flow is not available yet."
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
