from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from platformdirs import user_data_path
from pydantic import ValidationError

from smairt.models import (
    Assistant,
    Capability,
    CapabilityState,
    License,
    ProjectContract,
    Researcher,
    StartingPhase,
)

CONTRACT_PATH = Path("smairt.yaml")
MANIFEST_PATH = Path(".smairt") / "managed-files.yaml"
LOCAL_PREFERENCES_PATH = Path(".smairt") / "preferences.yaml"
REQUIRED_DIRECTORIES = (
    "background",
    "hypotheses",
    "plans",
    "analysis",
    "results/logs",
    "results/figures",
    "prompts",
)
LICENSE_TEXT = {
    License.MIT: "MIT License\n\nCopyright (c) {year} {holder}\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the \"Software\"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.\n",
    License.BSD_3_CLAUSE: "BSD 3-Clause License\n\nCopyright (c) {year}, {holder}\nAll rights reserved.\n\nRedistribution and use in source and binary forms, with or without\nmodification, are permitted provided that the following conditions are met:\n\n1. Redistributions of source code must retain the above copyright notice, this\n   list of conditions and the following disclaimer.\n2. Redistributions in binary form must reproduce the above copyright notice,\n   this list of conditions and the following disclaimer in the documentation\n   and/or other materials provided with the distribution.\n3. Neither the name of the copyright holder nor the names of its contributors\n   may be used to endorse or promote products derived from this software\n   without specific prior written permission.\n\nTHIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS \"AS IS\"\nAND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE\nIMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE\nDISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE\nFOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL\nDAMAGES.\n",
    License.APACHE_2_0: "Apache License\nVersion 2.0, January 2004\nhttp://www.apache.org/licenses/\n\nCopyright {year} {holder}\n\nLicensed under the Apache License, Version 2.0 (the \"License\");\nyou may not use this file except in compliance with the License.\nYou may obtain a copy of the License at\n\n    http://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software\ndistributed under the License is distributed on an \"AS IS\" BASIS,\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\nSee the License for the specific language governing permissions and\nlimitations under the License.\n",
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
ASSISTANT_COMMANDS = {
    Assistant.CLAUDE_CODE: ("claude",),
    Assistant.OPENCODE: ("opencode",),
    Assistant.CODEX: ("codex",),
    Assistant.PI: ("pi",),
    Assistant.CURSOR: ("cursor", "."),
}
ASSISTANT_ALIASES = {
    Assistant.CLAUDE_CODE: "CLAUDE.md",
    Assistant.OPENCODE: "AGENTS.md",
    Assistant.CODEX: "AGENTS.md",
    Assistant.PI: "AGENTS.md",
    Assistant.CURSOR: ".cursor/rules/smairt.mdc",
}


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
        return ProjectContract.model_validate(data)
    except (OSError, ValidationError, yaml.YAMLError) as error:
        raise ProjectError(f"Invalid smairt.yaml: {error}") from error


def save_contract(root: Path, contract: ProjectContract) -> None:
    (root / CONTRACT_PATH).write_text(
        yaml.safe_dump(contract.model_dump(mode="json", exclude_none=True), sort_keys=False)
    )


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
        if isinstance(path, str) and isinstance(opened_at, str) and Path(path).is_dir():
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


def enable_capability(root: Path, name: str) -> str:
    contract = load_contract(root)
    capability = _capability(contract, name)
    if capability.state is CapabilityState.ENABLED:
        return f"{_capability_label(name)} support is already enabled."
    if name == "paper":
        _create_paper_assets_safely(root)
    else:
        _create_hpc_assets_safely(root, contract.project.slug)
    contract.capabilities[name] = Capability(state=CapabilityState.ENABLED)
    save_contract(root, contract)
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
    _create_directory(root / "paper" / "analysis")
    _write_if_missing_and_track(
        root,
        root / "paper" / "README.md",
        "# Paper Workspace\n\n"
        "Keep publication-focused analyses in `paper/analysis/` so they remain "
        "separate from exploratory `analysis/` work.\n",
    )
    _write_if_missing_and_track(root, root / "paper" / "outline.md", "# Paper Outline\n")


def _create_hpc_assets_safely(root: Path, slug: str) -> None:
    _create_directory(root / "hpc")
    _write_if_missing_and_track(
        root,
        root / "hpc" / "README.md",
        "# HPC Guidance\n\n"
        "Adapt `slurm_job.sh` to your cluster, then submit it with your cluster's "
        "documented scheduler command. SMAIRT does not submit or manage jobs.\n",
    )
    _write_if_missing_and_track(
        root,
        root / "hpc" / "slurm_job.sh",
        "#!/usr/bin/env bash\n"
        f"#SBATCH --job-name={slug}\n"
        "#SBATCH --output=results/logs/%x-%j.out\n\n"
        "python experiments/03_real_data/run.py\n",
    )


def _create_directory(path: Path) -> None:
    if path.exists() and not path.is_dir():
        raise ProjectError(f"Cannot create directory because a file exists: {path}")
    path.mkdir(parents=True, exist_ok=True)


def _write_if_missing_and_track(root: Path, path: Path, content: str) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        _update_manifest_for(path, root)


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
        _create_phase_directories_non_destructively(root, phase)
        updates["starting_phase"] = phase
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
    updated_contract = contract.model_copy(update=updates)
    save_contract(root, updated_contract)
    if assistant is not None:
        prepare_assistant(root)


def _create_phase_directories_non_destructively(root: Path, phase: StartingPhase) -> None:
    directories = {
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
    for directory in directories[phase]:
        _create_directory(root / directory)


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
    return _render_license(license, contract.people["researcher"].name)


def change_license(root: Path, license: License) -> None:
    contract = load_contract(root)
    license_path = root / "LICENSE"
    if license_path.exists() and license_path.read_text() != _render_license(
        contract.license, contract.people["researcher"].name
    ):
        raise ProjectError("LICENSE has been modified; SMAIRT will not replace custom legal text.")
    license_path.write_text(_render_license(license, contract.people["researcher"].name))
    _update_manifest_for(license_path, root)
    save_contract(root, contract.model_copy(update={"license": license}))


def _render_license(license: License, holder: str) -> str:
    return LICENSE_TEXT[license].format(year=datetime.now(tz=UTC).year, holder=holder)


def prepare_assistant(root: Path) -> str:
    contract = load_contract(root)
    alias_path = ASSISTANT_ALIASES.get(contract.assistant)
    if alias_path is None:
        return (
            "Zoo Code has no verified SMAIRT project-alias convention. "
            "Open the project folder and consult Zoo Code's current official documentation."
        )
    alias = root / alias_path
    contents = "# SMAIRT AI Context\n\nRead `prompts/AI_CONTEXT.md` before working in this project.\n"
    if alias.exists():
        if alias.read_text() != contents:
            return f"{alias.relative_to(root)} is researcher-modified and was left unchanged."
        return f"{alias.relative_to(root)} already points to the canonical SMAIRT AI context."
    alias.parent.mkdir(parents=True, exist_ok=True)
    alias.write_text(contents)
    _update_manifest_for(alias, root)
    return f"Created {alias.relative_to(root)} as a pointer to prompts/AI_CONTEXT.md."


def launch_assistant(root: Path) -> tuple[bool, str]:
    contract = load_contract(root)
    command = ASSISTANT_COMMANDS.get(contract.assistant)
    if command is None:
        return (
            False,
            "SMAIRT cannot safely verify a Zoo Code launch command. Open the project folder "
            "and use Zoo Code's current official launch guidance.",
        )
    executable = shutil.which(command[0])
    if executable is None:
        return (
            False,
            f"{contract.assistant.value} is not available. Install it using its official instructions, "
            f"then run `{command[0]}` in {root}. You can also open this folder in your file manager.",
        )
    try:
        subprocess.Popen([executable, *command[1:]], cwd=root)
    except OSError as error:
        return False, f"Could not launch {contract.assistant.value}: {error}"
    return True, f"Launched {contract.assistant.value} in {root}."


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
    for directory in _phase_directories(contract.starting_phase):
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
            required = "paper" if name == "paper" else "hpc"
            if not (root / required).is_dir():
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
    issues.extend(_managed_file_issues(root))
    issues.extend(_unresolved_token_issues(root))
    return issues


def _phase_directories(phase: StartingPhase) -> tuple[str, ...]:
    return {
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
    }[phase]


def _managed_file_issues(root: Path) -> list[CheckIssue]:
    manifest_path = root / MANIFEST_PATH
    try:
        manifest = yaml.safe_load(manifest_path.read_text())
        files = manifest["files"]
    except (OSError, KeyError, TypeError, yaml.YAMLError):
        return [
            CheckIssue(
                "invalid-managed-manifest",
                MANIFEST_PATH.as_posix(),
                "Managed-file bookkeeping is missing or invalid.",
            )
        ]
    if not isinstance(files, dict):
        return [
            CheckIssue(
                "invalid-managed-manifest",
                MANIFEST_PATH.as_posix(),
                "Managed-file bookkeeping is missing or invalid.",
            )
        ]
    issues: list[CheckIssue] = []
    for relative, expected_hash in sorted(files.items()):
        if not isinstance(relative, str) or not isinstance(expected_hash, str):
            continue
        path = root / relative
        if not path.is_file():
            issues.append(CheckIssue("missing-managed-file", relative, f"Managed file is missing: {relative}"))
        elif _hash_file(path) != expected_hash:
            issues.append(
                CheckIssue(
                    "modified-managed-file",
                    relative,
                    f"Managed file was modified and will be preserved: {relative}",
                )
            )
    return issues


def _unresolved_token_issues(root: Path) -> list[CheckIssue]:
    manifest_path = root / MANIFEST_PATH
    try:
        manifest = yaml.safe_load(manifest_path.read_text())
        files = manifest["files"]
    except (OSError, KeyError, TypeError, yaml.YAMLError):
        return []
    if not isinstance(files, dict):
        return []
    issues: list[CheckIssue] = []
    for relative in sorted(files):
        if not isinstance(relative, str):
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


def _update_manifest_for(path: Path, root: Path) -> None:
    manifest_path = root / MANIFEST_PATH
    try:
        manifest = yaml.safe_load(manifest_path.read_text())
        files = manifest["files"]
    except (OSError, KeyError, TypeError, yaml.YAMLError):
        return
    if isinstance(files, dict):
        files[path.relative_to(root).as_posix()] = _hash_file(path)
        manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=True))


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _timestamp() -> str:
    return datetime.now(tz=UTC).isoformat()


def create_management_assets(
    root: Path, assistant: Assistant, license: License, researcher: Researcher
) -> None:
    """Create the initial tool-owned utility files before the manifest is written."""
    (root / "LICENSE").write_text(_render_license(license, researcher.name))
    alias_path = ASSISTANT_ALIASES.get(assistant)
    if alias_path is not None:
        alias = root / alias_path
        alias.parent.mkdir(parents=True, exist_ok=True)
        alias.write_text("# SMAIRT AI Context\n\nRead `prompts/AI_CONTEXT.md` before working in this project.\n")
