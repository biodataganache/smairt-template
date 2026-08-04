"""The action-token contract shared by framed menus and deterministic listings.

A menu row is addressed by its stable token. The displayed number is a
convenience that may be renumbered whenever a menu is regrouped, so nothing
should depend on it. See ADR 0002.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

_LEAVE_HABITS = frozenset({"q", "quit", "exit"})
_BACK_HABITS = frozenset({"q", "quit", "back", ""})
_ESCAPES = ("back", "exit")


@dataclass(frozen=True)
class Action:
    """One menu row: a stable token plus the words the researcher reads."""

    token: str
    label: str


class MenuChoice:
    """Adapters between a declared menu and the shapes its presentations need."""

    @staticmethod
    def rows(actions: Sequence[Action]) -> list[tuple[str, str]]:
        """Return token and label pairs in declared order for a framed screen."""
        tokens_of(actions)
        return [(action.token, action.label) for action in actions]


def tokens_of(actions: Sequence[Action]) -> tuple[str, ...]:
    """Return every token, refusing a menu that could not be addressed unambiguously."""
    tokens = tuple(action.token for action in actions)
    if len(set(tokens)) != len(tokens):
        raise ValueError(f"menu tokens must be unique: {tokens}")
    numeric = [token for token in tokens if token.isdigit()]
    if numeric:
        raise ValueError(f"menu tokens must not look like displayed numbers: {numeric}")
    return tokens


def numbered_lines(actions: Sequence[Action]) -> list[str]:
    """Return the deterministic listing, showing both the number and the token."""
    return [
        f"{index}. {action.label} [{action.token}]" for index, action in enumerate(actions, start=1)
    ]


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
    if cleaned.isdigit():
        position = int(cleaned)
        if 1 <= position <= len(actions):
            return actions[position - 1].token
        return None
    escape = escape_token(actions)
    if escape is None:
        return None
    habits = _BACK_HABITS if escape == "back" else _LEAVE_HABITS
    return escape if cleaned in habits else None
