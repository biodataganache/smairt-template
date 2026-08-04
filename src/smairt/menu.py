"""The action-token contract shared by framed menus and deterministic listings.

A menu row is addressed by its stable token. The displayed number is a
convenience that may be renumbered whenever a menu is regrouped, so nothing
should depend on it. See ADR 0002.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from smairt.terminal import SEPARATOR

_LEAVE_HABITS = frozenset({"q", "quit", "exit"})
_BACK_HABITS = frozenset({"q", "quit", "back", ""})
_ESCAPES = ("back", "exit")

_DIVIDER_TOKEN = ""
"""Reserved for dividers, which are presentation and answer to nothing."""


@dataclass(frozen=True)
class Action:
    """One menu row: a stable token plus the words the researcher reads."""

    token: str
    label: str

    @property
    def is_divider(self) -> bool:
        """Report whether this row only groups the rows around it."""
        return self.token == _DIVIDER_TOKEN


def divider(label: str = "") -> Action:
    """Return a row that groups the rows around it and can never be chosen."""
    return Action(_DIVIDER_TOKEN, label)


def addressable(actions: Sequence[Action]) -> tuple[Action, ...]:
    """Return only the rows a researcher can actually choose."""
    return tuple(action for action in actions if not action.is_divider)


class MenuChoice:
    """Adapters between a declared menu and the shapes its presentations need."""

    @staticmethod
    def rows(actions: Sequence[Action]) -> list[tuple[Any, str]]:
        """Return value and label pairs in declared order for a framed screen."""
        tokens_of(actions)
        return [
            (SEPARATOR if action.is_divider else action.token, action.label) for action in actions
        ]


def tokens_of(actions: Sequence[Action]) -> tuple[str, ...]:
    """Return every addressable token, refusing an ambiguously addressed menu."""
    tokens = tuple(action.token for action in addressable(actions))
    if len(set(tokens)) != len(tokens):
        raise ValueError(f"menu tokens must be unique: {tokens}")
    numeric = [token for token in tokens if token.isdigit()]
    if numeric:
        raise ValueError(f"menu tokens must not look like displayed numbers: {numeric}")
    return tokens


def numbered_lines(actions: Sequence[Action]) -> list[str]:
    """Return the deterministic listing, numbering only the addressable rows."""
    tokens_of(actions)
    lines: list[str] = []
    number = 0
    for action in actions:
        if action.is_divider:
            lines.append(f"   {action.label}")
            continue
        number += 1
        lines.append(f"{number}. {action.label} [{action.token}]")
    return lines


def escape_token(actions: Sequence[Action]) -> str | None:
    """Return the token that leaves this menu, if it offers one at all."""
    tokens = tokens_of(actions)
    for candidate in _ESCAPES:
        if candidate in tokens:
            return candidate
    return None


def resolve_action(answer: str, actions: Sequence[Action]) -> str | None:
    """Return the token an answer selects, or None when nothing matches.

    Tokens are the contract. Displayed numbers and habitual keys are accepted as
    conveniences, and an unrecognized answer is refused rather than guessed at.
    """
    tokens = tokens_of(actions)
    cleaned = answer.strip().lower()
    if cleaned in tokens:
        return cleaned
    choices = addressable(actions)
    if cleaned.isdigit():
        position = int(cleaned)
        if 1 <= position <= len(choices):
            return choices[position - 1].token
        return None
    escape = escape_token(actions)
    if escape is None:
        return None
    habits = _BACK_HABITS if escape == "back" else _LEAVE_HABITS
    return escape if cleaned in habits else None
