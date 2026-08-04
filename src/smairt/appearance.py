"""One semantic palette shared by framed screens and printed output.

Roles name what a fragment means rather than which color it uses, and every role
resolves to one of the terminal's own sixteen colors so SMAIRT inherits whatever
theme the researcher already runs. See ADR 0003.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass

from prompt_toolkit.styles import Style
from rich.theme import Theme

_RICH_COLOR = 0
_PROMPT_COLOR = 1

_COLORS: dict[str, tuple[str, str]] = {
    "inherit": ("", ""),
    "accent": ("cyan", "ansicyan"),
    "muted": ("bright_black", "ansibrightblack"),
    "caution": ("yellow", "ansiyellow"),
    "failure": ("red", "ansired"),
    "affirm": ("green", "ansigreen"),
}


@dataclass(frozen=True)
class Role:
    """One named interface role expressed as a terminal color plus attributes."""

    color: str
    attributes: tuple[str, ...] = ()

    def rendered(self, dialect: int) -> str:
        color = _COLORS[self.color][dialect]
        return " ".join([*self.attributes, color]).strip()


ROLES: dict[str, Role] = {
    "title": Role("accent", ("bold",)),
    "heading": Role("inherit", ("bold",)),
    "label": Role("inherit"),
    "value": Role("inherit", ("bold",)),
    "hint": Role("muted"),
    "footer": Role("muted"),
    "border": Role("muted"),
    "selected": Role("accent", ("bold",)),
    "checked": Role("affirm", ("bold",)),
    "caution": Role("caution"),
    "failure": Role("failure", ("bold",)),
    "affirm": Role("affirm"),
}

_PROMPT_CLASSES: dict[str, str] = {
    "frame.border": "border",
    "frame.label": "title",
    "smairt.title": "title",
    "smairt.hint": "hint",
    "smairt.footer": "footer",
    "smairt.detail": "hint",
    "smairt.action": "label",
    "option": "label",
    "option-selected": "selected",
    "option-checked": "checked",
    "radio": "label",
    "radio-selected": "selected",
    "radio-checked": "checked",
    "radio-list": "label",
    "scrollbar.background": "border",
    "scrollbar.button": "border",
}


def styling_enabled() -> bool:
    """Report whether styled output is both possible and wanted right now."""
    if os.environ.get("NO_COLOR") is not None:
        return False
    if os.environ.get("TERM", "") in {"", "dumb"}:
        return False
    return sys.stdout.isatty()


def rich_theme() -> Theme:
    """Return the palette as a rich-text theme for printed output."""
    return Theme({name: role.rendered(_RICH_COLOR) for name, role in ROLES.items()})


def prompt_style() -> Style:
    """Return the palette as an interaction-library style for framed screens."""
    return Style(
        [
            (class_name, ROLES[role].rendered(_PROMPT_COLOR))
            for class_name, role in _PROMPT_CLASSES.items()
        ]
    )
