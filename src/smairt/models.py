from __future__ import annotations

import re
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from smairt import __version__


class StartingPhase(StrEnum):
    SYNTHETIC = "synthetic"
    DOWNLOADED = "downloaded"
    REAL = "real"


class Assistant(StrEnum):
    ZOO_CODE = "zoo-code"
    CLAUDE_CODE = "claude-code"
    OPENCODE = "opencode"
    CODEX = "codex"
    PI = "pi"
    CURSOR = "cursor"


class License(StrEnum):
    """The licenses SMAIRT will write for a project.

    Only licenses whose complete official text SMAIRT ships are offered. A truncated
    license is not the license it names, so an abbreviated Apache-2.0, GPL-3.0, or
    bespoke proprietary notice was removed rather than shortened. A researcher who
    needs one of those writes `LICENSE` themselves; `smairt check` reports a
    researcher-authored `LICENSE` as modified and never replaces it.
    """

    MIT = "MIT"
    BSD_3_CLAUSE = "BSD-3-Clause"


class CapabilityState(StrEnum):
    NEVER_ENABLED = "never_enabled"
    ENABLED = "enabled"
    INACTIVE = "inactive"


class PromptConvention(StrEnum):
    PLAN_FIRST = "plan-first"
    DIRECT_TASK = "direct-task"


class CodeConvention(StrEnum):
    TYPED_PYTHON = "typed-python"
    STANDARD_PYTHON = "standard-python"


class ConventionSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: PromptConvention | None = None
    code: CodeConvention | None = None


class RigorSettings(BaseModel):
    """Optional declarations that add structure without choosing scientific policy.

    Every value answers only whether newly created research files should ask the
    researcher to state a decision. The contract deliberately stores no method name or
    policy text; those words belong to the researcher in ``analysis/RIGOR.md``.
    """

    model_config = ConfigDict(extra="forbid")

    declare_multiplicity_policy: bool = False
    separate_discovery_validation: bool = False
    declare_unit_of_inference: bool = False
    track_per_probe_status: bool = False


_TEMPLATE_MARKERS = ("{{", "}}", "{%", "%}")


def reject_template_markers(value: str) -> str:
    """Refuse text that would leave a template marker in a generated file.

    Generated guidance is rendered from Jinja templates, and `smairt check` reports any
    managed file still containing `{{` or `}}` as an unresolved token. Substituted metadata
    was not screened, so a project named `Study {{ n }}` was created successfully and then
    immediately failed its own check with five errors about files the researcher never
    touched. Refusing at the point of entry is the only place the message can name the value
    that caused it.

    The message is phrased without repeating the field name, because the reporting layer
    already prefixes each problem with the field it belongs to.
    """
    for marker in _TEMPLATE_MARKERS:
        if marker in value:
            raise ValueError(
                f"cannot contain {marker}, because SMAIRT renders project files from templates "
                "and would leave that text unresolved. Remove the braces."
            )
    return value


class ProjectIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    slug: str
    description: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    research_question: str | None = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", value):
            message = (
                "Slug must start with a lowercase letter and contain only "
                "lowercase letters, numbers, and underscores."
            )
            raise ValueError(message)
        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return reject_template_markers(value)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        return reject_template_markers(value)

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, value: str) -> str:
        return reject_template_markers(value)

    @field_validator("research_question")
    @classmethod
    def normalize_question(cls, value: str | None) -> str | None:
        if value:
            reject_template_markers(value)
        return value or None


class Researcher(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    email: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return reject_template_markers(value)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        return value or None


class ProjectOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project: ProjectIdentity
    researcher: Researcher
    assistant: Assistant
    starting_phase: StartingPhase
    license: License
    initialize_git: bool = False
    paper: bool = False
    hpc: bool = False


class Capability(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: CapabilityState


class ProjectContract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: int = 1
    scaffold_version: str = __version__
    """The installed version that generated this project.

    Derived from `__version__` rather than restated, because `project_check()` decides
    whether a project is current by comparing this string to the installed version. When
    the two were maintained separately, bumping one and forgetting the other made every
    freshly generated project fail its own check.
    """
    project: ProjectIdentity
    people: dict[str, Researcher]
    assistant: Assistant
    starting_phase: StartingPhase
    current_phase: StartingPhase
    license_year: int = Field(ge=2000, le=9999)
    license: License
    git_requested: bool
    git_initialized: bool
    capabilities: dict[str, Capability]
    conventions: ConventionSettings = Field(default_factory=ConventionSettings)
    rigor: RigorSettings = Field(default_factory=RigorSettings)

    @model_validator(mode="before")
    @classmethod
    def migrate_current_phase(cls, data: object) -> object:
        if isinstance(data, dict):
            migrated = dict(data)
            if "current_phase" not in migrated and "starting_phase" in migrated:
                migrated["current_phase"] = migrated["starting_phase"]
            migrated.setdefault("license_year", datetime.now().year)
            return migrated
        return data

    @classmethod
    def from_options(cls, options: ProjectOptions, git_initialized: bool) -> ProjectContract:
        return cls(
            project=options.project,
            people={"researcher": options.researcher},
            assistant=options.assistant,
            starting_phase=options.starting_phase,
            current_phase=options.starting_phase,
            license_year=datetime.now().year,
            license=options.license,
            git_requested=options.initialize_git,
            git_initialized=git_initialized,
            capabilities={
                "paper": Capability(
                    state=(
                        CapabilityState.ENABLED if options.paper else CapabilityState.NEVER_ENABLED
                    )
                ),
                "hpc": Capability(
                    state=(
                        CapabilityState.ENABLED if options.hpc else CapabilityState.NEVER_ENABLED
                    )
                ),
            },
        )
