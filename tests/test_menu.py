from __future__ import annotations

import pytest

from smairt.menu import (
    Action,
    MenuChoice,
    divider,
    numbered_lines,
    resolve_action,
    tokens_of,
)
from smairt.terminal import SEPARATOR

GROUPED = (
    Action("name", "Project name"),
    Action("domain", "Domain"),
    divider("Actions"),
    Action("create", "Create project"),
    Action("cancel", "Cancel without creating files"),
)

DASHBOARD = (
    Action("assistant", "Launch assistant or open folder"),
    Action("settings", "Project Settings"),
    Action("capabilities", "Optional capabilities"),
    Action("check", "Project Check"),
    Action("help", "Help"),
    Action("exit", "Exit"),
)


def test_a_menu_is_addressed_by_its_stable_token() -> None:
    assert resolve_action("settings", DASHBOARD) == "settings"
    assert resolve_action("check", DASHBOARD) == "check"


def test_a_displayed_number_remains_a_convenience() -> None:
    assert resolve_action("1", DASHBOARD) == "assistant"
    assert resolve_action("6", DASHBOARD) == "exit"


def test_renumbering_a_menu_does_not_change_its_token_contract() -> None:
    """Tokens survive reordering, so tests never depend on presentation order."""
    reordered = (DASHBOARD[-1], *DASHBOARD[:-1])
    assert set(tokens_of(reordered)) == set(tokens_of(DASHBOARD))
    for action in DASHBOARD:
        assert resolve_action(action.token, reordered) == action.token
    assert resolve_action("1", DASHBOARD) == "assistant"
    assert resolve_action("1", reordered) == "exit"


def test_tokens_are_matched_without_regard_to_case_or_padding() -> None:
    assert resolve_action("  Settings  ", DASHBOARD) == "settings"
    assert resolve_action("EXIT", DASHBOARD) == "exit"


def test_leaving_is_reachable_by_habit_as_well_as_by_token() -> None:
    assert resolve_action("q", DASHBOARD) == "exit"
    assert resolve_action("quit", DASHBOARD) == "exit"


def test_going_back_is_reachable_by_habit_when_a_menu_offers_it() -> None:
    settings = (Action("name", "Project name"), Action("back", "Back"))
    assert resolve_action("q", settings) == "back"
    assert resolve_action("", settings) == "back"


def test_a_menu_without_an_escape_refuses_a_bare_habit_key() -> None:
    """Inventing an exit a menu never offered would leave the caller nowhere to go."""
    fields = (Action("name", "Project name"), Action("domain", "Domain"))
    assert resolve_action("q", fields) is None
    assert resolve_action("", fields) is None


def test_an_unknown_answer_is_refused_rather_than_guessed() -> None:
    assert resolve_action("plausible", DASHBOARD) is None
    assert resolve_action("99", DASHBOARD) is None
    assert resolve_action("0", DASHBOARD) is None


def test_a_number_beyond_the_menu_is_refused_rather_than_clamped() -> None:
    assert resolve_action("7", DASHBOARD) is None


def test_the_deterministic_listing_shows_both_number_and_token() -> None:
    lines = numbered_lines(DASHBOARD)
    assert lines[0] == "1. Launch assistant or open folder [assistant]"
    assert lines[5] == "6. Exit [exit]"


def test_a_menu_offers_its_choices_as_visual_rows_in_declared_order() -> None:
    assert MenuChoice.rows(DASHBOARD)[:2] == [
        ("assistant", "Launch assistant or open folder"),
        ("settings", "Project Settings"),
    ]


def test_duplicate_tokens_are_a_programming_error() -> None:
    with pytest.raises(ValueError):
        tokens_of((Action("same", "One"), Action("same", "Two")))


def test_a_token_may_not_look_like_a_displayed_number() -> None:
    """A numeric token would collide with the number that addresses another row."""
    with pytest.raises(ValueError):
        tokens_of((Action("2", "Two"),))


def test_a_divider_groups_rows_without_becoming_addressable() -> None:
    """A divider is presentation, so it owns no token and answers to no number."""
    assert tokens_of(GROUPED) == ("name", "domain", "create", "cancel")
    assert resolve_action("Actions", GROUPED) is None


def test_numbering_counts_only_addressable_rows_across_a_divider() -> None:
    """A researcher counts choices, not the lines drawn between them."""
    lines = numbered_lines(GROUPED)
    assert lines == [
        "1. Project name [name]",
        "2. Domain [domain]",
        "   Actions",
        "3. Create project [create]",
        "4. Cancel without creating files [cancel]",
    ]
    assert resolve_action("3", GROUPED) == "create"
    assert resolve_action("4", GROUPED) == "cancel"
    assert resolve_action("5", GROUPED) is None


def test_a_grouped_menu_renders_its_divider_as_a_screen_separator() -> None:
    """The visual screen needs the sentinel its own list refuses to land on."""
    assert MenuChoice.rows(GROUPED)[2] == (SEPARATOR, "Actions")
