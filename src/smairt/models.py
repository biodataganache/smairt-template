from __future__ import annotations

import re
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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
    MIT = "MIT"
    BSD_3_CLAUSE = "BSD-3-Clause"
    APACHE_2_0 = "Apache-2.0"
    GPL_3_0 = "GPL-3.0"
    PROPRIETARY = "proprietary"


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

    @field_validator("research_question")
    @classmethod
    def normalize_question(cls, value: str | None) -> str | None:
        return value or None


class Researcher(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    email: str | None = None

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
    scaffold_version: str = "0.3.0"
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
