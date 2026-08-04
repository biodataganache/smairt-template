from __future__ import annotations

import pytest
from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from smairt.appearance import ROLES, prompt_style, rich_theme
from smairt.terminal import (
    FRAME_ROWS,
    MINIMUM_MENU_ROWS,
    BackRequested,
    SelectionCancelled,
    confirm,
    plan_screen,
    select_choice,
    select_many,
    select_menu,
)

DOWN = "\x1b[B"
UP = "\x1b[A"
PAGE_DOWN = "\x1b[6~"
PAGE_UP = "\x1b[5~"
ENTER = "\r"
ESCAPE = "\x1b"
CTRL_C = "\x03"


def many_choices(count: int) -> list[tuple[str, str]]:
    return [(f"item-{index}", f"Item {index}") for index in range(count)]


def test_a_screen_never_renders_taller_than_the_terminal() -> None:
    """A screen taller than the terminal cannot repaint cleanly, so it must not happen."""
    overflowing = [
        rows
        for rows in range(3, 60)
        for plan in [plan_screen(20, detail_count=3, terminal_rows=rows)]
        if plan.total_rows(3) > rows
    ]
    assert overflowing == []


def test_a_screen_surrenders_ornament_before_it_surrenders_options() -> None:
    roomy = plan_screen(6, detail_count=2, terminal_rows=40)
    assert (roomy.details_shown, roomy.footer_shown, roomy.spacer_shown) == (True, True, True)
    assert roomy.rows == 6

    cramped = plan_screen(6, detail_count=2, terminal_rows=7)
    assert cramped.rows >= MINIMUM_MENU_ROWS
    assert cramped.spacer_shown is False
    assert cramped.total_rows(2) <= 7

    starved = plan_screen(6, detail_count=4, terminal_rows=6)
    assert starved.details_shown is False
    assert starved.footer_shown is False
    assert starved.rows >= MINIMUM_MENU_ROWS
    assert starved.total_rows(4) <= 6


def test_a_single_row_screen_still_fits_an_absurdly_short_terminal() -> None:
    plan = plan_screen(20, detail_count=4, terminal_rows=FRAME_ROWS + 1)
    assert plan.rows == 1
    assert plan.total_rows(4) == FRAME_ROWS + 1


def test_a_row_limit_caps_options_without_counting_frame_or_footer() -> None:
    plan = plan_screen(40, detail_count=2, terminal_rows=40, max_rows=6)
    assert plan.rows == 6
    assert plan.footer_shown is True


def test_a_short_menu_never_reserves_more_rows_than_it_has_options() -> None:
    assert plan_screen(4, terminal_rows=40, max_rows=20).rows == 4


def test_the_palette_defines_every_role_in_both_dialects() -> None:
    theme = rich_theme()
    assert set(theme.styles) >= set(ROLES)
    prompt_colors = {value for _, value in prompt_style().style_rules}
    assert prompt_colors
    assert all(not value.startswith("#") for value in prompt_colors)


def test_the_palette_uses_only_terminal_relative_colors() -> None:
    """Absolute colors would clash with the researcher's own terminal theme."""
    for _, value in prompt_style().style_rules:
        for word in value.split():
            assert word in {"bold", "italic", "underline"} or word.startswith("ansi")


def test_choosing_an_option_returns_its_value_without_an_alternate_screen() -> None:
    entered_alternate_screen = False

    class TrackingOutput(DummyOutput):
        def enter_alternate_screen(self) -> None:
            nonlocal entered_alternate_screen
            entered_alternate_screen = True

    with (
        create_pipe_input() as pipe,
        create_app_session(input=pipe, output=TrackingOutput()),
    ):
        pipe.send_text(DOWN + ENTER)
        assert select_menu("Pick", [("a", "Alpha"), ("b", "Beta")]) == "b"
    assert entered_alternate_screen is False


def test_navigation_wraps_and_accepts_vi_keys() -> None:
    choices = [("a", "Alpha"), ("b", "Beta"), ("c", "Gamma")]
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        pipe.send_text("k" + ENTER)
        assert select_menu("Pick", choices) == "c"
        pipe.send_text("j" + ENTER)
        assert select_menu("Pick", choices) == "b"


def test_a_long_menu_scrolls_past_its_visible_viewport() -> None:
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        pipe.send_text(DOWN * 25 + ENTER)
        assert select_menu("Pick", many_choices(30), max_rows=5) == "item-25"


def test_page_navigation_moves_a_viewport_and_clamps_at_both_ends() -> None:
    choices = many_choices(30)
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        pipe.send_text(PAGE_DOWN + ENTER)
        assert select_menu("Pick", choices, max_rows=5) == "item-5"
        pipe.send_text(PAGE_UP + ENTER)
        assert select_menu("Pick", choices, max_rows=5) == "item-0"
        pipe.send_text(PAGE_DOWN * 12 + ENTER)
        assert select_menu("Pick", choices, max_rows=5) == "item-29"


def test_a_choice_screen_offers_back_and_cancellation() -> None:
    choices = [("a", "Alpha"), ("b", "Beta")]
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        pipe.send_text(UP + ENTER)
        with pytest.raises(BackRequested):
            select_choice("Pick", choices)
        pipe.send_text(ESCAPE)
        with pytest.raises(BackRequested):
            select_choice("Pick", choices)
        pipe.send_text(CTRL_C)
        with pytest.raises(SelectionCancelled):
            select_choice("Pick", choices)


def test_a_menu_retains_the_previously_chosen_value_as_its_starting_row() -> None:
    choices = [("a", "Alpha"), ("b", "Beta"), ("c", "Gamma")]
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        pipe.send_text(ENTER)
        assert select_menu("Pick", choices, "c") == "c"


CAPABILITIES = [("none", "Default Workspace"), ("paper", "Paper"), ("hpc", "HPC")]
TO_CONTINUE = DOWN * 3


def test_space_checks_options_and_the_continue_row_returns_them() -> None:
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        pipe.send_text(DOWN + " " + DOWN + " " + DOWN + ENTER)
        assert select_many("Extras", CAPABILITIES, exclusive="none") == ["paper", "hpc"]


def test_enter_toggles_a_focused_option_so_no_key_is_inert() -> None:
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        pipe.send_text(DOWN + ENTER + DOWN + DOWN + ENTER)
        assert select_many("Extras", CAPABILITIES, exclusive="none") == ["paper"]


def test_an_exclusive_option_clears_the_others_and_is_cleared_by_them() -> None:
    """A contradictory selection is unreachable, so it never needs to be refused."""
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        pipe.send_text(DOWN + " " + UP + " " + TO_CONTINUE + ENTER)
        assert select_many("Extras", CAPABILITIES, exclusive="none") == ["none"]

        pipe.send_text(" " + DOWN + " " + DOWN + DOWN + ENTER)
        assert select_many("Extras", CAPABILITIES, exclusive="none") == ["paper"]


def test_continuing_with_nothing_checked_returns_no_values() -> None:
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        pipe.send_text(TO_CONTINUE + ENTER)
        assert select_many("Extras", CAPABILITIES, exclusive="none") == []


def test_a_selection_starts_from_the_values_already_in_effect() -> None:
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        pipe.send_text(DOWN * 2 + ENTER)
        assert select_many("Extras", CAPABILITIES, ["paper"], exclusive="none") == ["paper"]


def test_a_selection_can_be_abandoned_without_returning_values() -> None:
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        pipe.send_text(CTRL_C)
        with pytest.raises(SelectionCancelled):
            select_many("Extras", CAPABILITIES, exclusive="none")


def test_confirmation_refuses_by_default_and_agrees_only_deliberately() -> None:
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        pipe.send_text(ENTER)
        assert confirm("Apply?") is False
        pipe.send_text(DOWN + ENTER)
        assert confirm("Apply?") is True


def test_an_empty_screen_is_a_programming_error_rather_than_an_empty_frame() -> None:
    with pytest.raises(ValueError):
        select_menu("Pick", [])
    with pytest.raises(ValueError):
        select_many("Extras", [])
