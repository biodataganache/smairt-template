"""Turn library and filesystem failures into sentences a researcher can act on.

SMAIRT's users are researchers, not necessarily people who read stack traces. Two things
were reaching them unchanged: pydantic's structured validation output, complete with
`[type=value_error]` tags and `errors.pydantic.dev` URLs, and bare Python tracebacks from
any failure nobody had anticipated.

Both are failures of translation rather than of logic. The underlying diagnosis is usually
correct and often precise; it is simply addressed to the wrong reader. This module is the one
place that rewording happens, so a message cannot be phrased well on one code path and
badly on another.
"""

from __future__ import annotations

import re
from collections.abc import Mapping

from pydantic import ValidationError

# Field names as a researcher would say them, rather than as the contract spells them.
#
# Keyed by the fully qualified location wherever a bare key would be ambiguous. `name` belongs
# to both the project and the researcher, so a bare `name` is qualified using the model that
# rejected it rather than guessed at — labelling a rejected researcher name "project name"
# points the reader at the wrong input.
_FIELD_LABELS = {
    "project.name": "project name",
    "project.slug": "project slug",
    "project.description": "project description",
    "project.domain": "research domain",
    "project.research_question": "research question",
    "researcher.name": "researcher name",
    "researcher.email": "researcher email",
    "slug": "project slug",
    "description": "project description",
    "domain": "research domain",
    "research_question": "research question",
    "people": "project people",
    "assistant": "coding assistant",
    "starting_phase": "starting phase",
    "current_phase": "current phase",
    "license": "license",
    "license_year": "license year",
    "capabilities": "capabilities",
    "git_requested": "whether Git was requested",
    "git_initialized": "whether Git was initialized",
    "conventions": "project conventions",
    "rigor": "rigor declarations",
    "scaffold_version": "scaffold version",
    "schema_version": "contract schema version",
}

# How each validated model refers to itself when one of its own fields is reported bare.
_MODEL_PREFIXES = {
    "ProjectIdentity": "project",
    "Researcher": "researcher",
    "ProjectOptions": "project",
    "ProjectContract": "project",
}


def suggest_slug(value: str) -> str:
    """Return a valid slug derived from arbitrary text, or an empty string if none exists.

    Offered alongside a rejected slug because "here is the rule" is a worse answer than
    "here is the rule, and here is what you probably meant".
    """
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    slug = re.sub(r"_+", "_", slug)
    if not slug:
        return ""
    if not slug[0].isalpha():
        slug = f"project_{slug}"
    return slug


def describe_validation_error(error: ValidationError, *, source: str | None = None) -> str:
    """Return a plain-language account of why input or a contract was rejected.

    Every reported problem is kept. Dropping all but the first would hide the rest behind a
    sequence of one-at-a-time corrections, which is its own kind of unhelpful.
    """
    lines: list[str] = []
    for entry in error.errors():
        location = ".".join(str(part) for part in entry["loc"])
        lines.append(f"- {_label_for(location, error.title)}: {_describe_one(entry)}")
    if source is not None:
        heading = f"{source} could not be read:"
    else:
        heading = "Some values could not be accepted:"
    return "\n".join([heading, *lines])


def _label_for(location: str, model: str) -> str:
    """Return how to name the rejected field, in the words a researcher would use.

    Resolution goes from most specific to least: the exact location, then the location
    qualified by the model that rejected it, then the longest recognized suffix. The suffix
    step is what handles nesting — a contract reports a bad researcher name as
    `people.researcher.name`, and only its tail is meaningful to the reader.
    """
    if location in _FIELD_LABELS:
        return _FIELD_LABELS[location]
    prefix = _MODEL_PREFIXES.get(model)
    if prefix is not None and f"{prefix}.{location}" in _FIELD_LABELS:
        return _FIELD_LABELS[f"{prefix}.{location}"]
    parts = location.split(".")
    for start in range(1, len(parts)):
        suffix = ".".join(parts[start:])
        if suffix in _FIELD_LABELS:
            return _FIELD_LABELS[suffix]
    return location or "value"


def _describe_one(entry: Mapping[str, object]) -> str:
    """Return one problem in plain language, without pydantic's type tags or URLs."""
    kind = str(entry.get("type", ""))
    message = str(entry.get("msg", "is not valid"))
    if kind == "missing":
        return "is required but was not provided"
    if kind == "extra_forbidden":
        return "is not a setting SMAIRT recognizes"
    if kind == "string_too_short":
        return "cannot be empty"
    if kind == "value_error":
        # A custom validator's own wording is already aimed at the researcher; pydantic only
        # prefixes it with "Value error, ".
        return message.removeprefix("Value error, ")
    if kind.startswith("enum") or "permitted" in message:
        return message
    return message


def describe_slug_rejection(value: str) -> str:
    """Return the slug rule plus a usable alternative, as one short paragraph."""
    message = (
        f'"{value}" cannot be a project slug. A slug starts with a lowercase letter and '
        "uses only lowercase letters, numbers, and underscores."
    )
    suggestion = suggest_slug(value)
    if suggestion and suggestion != value:
        message += f" Try: {suggestion}"
    return message


def slug_rejection_in(error: ValidationError) -> str | None:
    """Return the offending slug when a validation failure is specifically about a slug.

    A rejected slug is worth answering with a suggestion rather than a rule restatement, and
    it is by far the most common way creating a project fails.
    """
    for entry in error.errors():
        if entry["loc"] and str(entry["loc"][-1]) == "slug":
            given = entry.get("input")
            if isinstance(given, str):
                return given
    return None


def describe_unexpected_error(error: BaseException) -> str:
    """Return what to tell a researcher about a failure SMAIRT did not anticipate.

    A traceback tells them their work may be damaged and gives them nothing to do about it.
    This says what happened and how to find out where the project stands.

    It deliberately makes no promise about the files. The boundary has no idea how far an
    operation got, so "your files were not deleted" would be a guess presented as a guarantee —
    which for a non-expert reader is worse than the traceback it replaced.
    """
    return "\n".join(
        [
            f"SMAIRT stopped because of an unexpected error: {type(error).__name__}: {error}",
            "",
            "Run `smairt check` to see what the project looks like now. If the command was",
            "writing files, some of that work may be incomplete.",
            "",
            "Re-run with SMAIRT_DEBUG=1 for the full technical detail, and include that",
            "output when reporting this.",
        ]
    )
