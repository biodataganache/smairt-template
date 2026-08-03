from __future__ import annotations

import pytest
from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from smairt.terminal import (
    MINIMUM_MENU_ROWS,
    BackRequested,
    SelectionCancelled,
    select_choice,
    select_menu,
    viewport_rows,
)


def test_visual_choice_uses_arrow_keys_and_enter_without_an_alternate_screen() -> None:
    class TrackingOutput(DummyOutput):
        entered_alternate_screen = False

        def enter_alternate_screen(self) -> None:
            self.entered_alternate_screen = True

    output = TrackingOutput()
    with (
        create_pipe_input() as input_stream,
        create_app_session(input=input_stream, output=output),
    ):
        input_stream.send_text("\x1b[B\r")

        selected = select_choice("Location", [("workspace", "Workspace"), ("other", "Other")])

    assert selected == "other"
    assert not output.entered_alternate_screen


def test_visual_choice_supports_terminal_navigation_back_and_cancel() -> None:
    choices = [("first", "First"), ("second", "Second")]
    with (
        create_pipe_input() as input_stream,
        create_app_session(input=input_stream, output=DummyOutput()),
    ):
        input_stream.send_text("j\r")
        assert select_choice("Choose", choices) == "second"
        input_stream.send_text("k\r")
        assert select_choice("Choose", choices, default="second") == "first"
        input_stream.send_text("\x1b[B\x1b[B\r")
        with pytest.raises(BackRequested):
            select_choice("Choose", choices)
        input_stream.send_text("\x1b[D")
        with pytest.raises(BackRequested):
            select_choice("Choose", choices)
        input_stream.send_text("\x1b")
        with pytest.raises(BackRequested):
            select_choice("Choose", choices)
        input_stream.send_text("\x03")
        with pytest.raises(SelectionCancelled):
            select_choice("Choose", choices)


def test_visual_choice_retains_focus_and_wraps_navigation() -> None:
    choices = [("first", "First"), ("second", "Second")]
    with (
        create_pipe_input() as input_stream,
        create_app_session(input=input_stream, output=DummyOutput()),
    ):
        input_stream.send_text("\r")
        assert select_choice("Retain", choices, default="second") == "second"
        input_stream.send_text("k\r")
        with pytest.raises(BackRequested):
            select_choice("Wrap", choices)
        input_stream.send_text("\x1b[A\r")
        with pytest.raises(BackRequested):
            select_choice("Arrow up", choices)
        input_stream.send_text("\x1b[B\x1b[B\x1b[B\r")
        assert select_choice("Forward wrap", choices) == "first"


def _many_choices(count: int) -> list[tuple[str, str]]:
    return [(f"item-{number}", f"Item {number}") for number in range(count)]


def test_a_long_menu_bounds_its_viewport_instead_of_printing_every_row() -> None:
    assert viewport_rows(40, chrome_rows=3, max_rows=6) == 6


def test_a_short_menu_never_reserves_more_rows_than_it_has_items() -> None:
    assert viewport_rows(4, chrome_rows=3, max_rows=20) == 4


def test_a_cramped_terminal_still_leaves_a_usable_scrolling_viewport() -> None:
    assert viewport_rows(40, chrome_rows=3, max_rows=0) == MINIMUM_MENU_ROWS


def test_the_viewport_defaults_to_the_terminal_height_minus_menu_chrome() -> None:
    with (
        create_pipe_input() as input_stream,
        create_app_session(input=input_stream, output=DummyOutput()),
    ):
        rows = viewport_rows(500, chrome_rows=4)

    assert rows == DummyOutput().get_size().rows - 4


def test_a_long_menu_renders_only_its_viewport_rows() -> None:
    choices = _many_choices(40)
    with (
        create_pipe_input() as input_stream,
        create_app_session(input=input_stream, output=DummyOutput()),
    ):
        input_stream.send_text("\r")

        assert select_menu("Long menu", choices, max_rows=6) == "item-0"


def test_scrolling_menu_reaches_items_below_the_visible_viewport() -> None:
    choices = _many_choices(30)
    with (
        create_pipe_input() as input_stream,
        create_app_session(input=input_stream, output=DummyOutput()),
    ):
        input_stream.send_text("\x1b[B" * 25 + "\r")

        assert select_menu("Scroll down", choices, max_rows=5) == "item-25"


def test_scrolling_menu_wraps_at_the_ends_of_the_list() -> None:
    choices = _many_choices(30)
    with (
        create_pipe_input() as input_stream,
        create_app_session(input=input_stream, output=DummyOutput()),
    ):
        input_stream.send_text("k\r")
        assert select_menu("Wrap to end", choices, max_rows=5) == "item-29"


def test_page_navigation_moves_a_whole_viewport_and_stops_at_the_ends() -> None:
    choices = _many_choices(30)
    with (
        create_pipe_input() as input_stream,
        create_app_session(input=input_stream, output=DummyOutput()),
    ):
        input_stream.send_text("\x1b[6~\r")
        assert select_menu("Page down", choices, max_rows=5) == "item-5"
        input_stream.send_text("\x1b[6~\x1b[6~\x1b[5~\r")
        assert select_menu("Page up", choices, max_rows=5) == "item-5"
        input_stream.send_text("\x1b[5~\r")
        assert select_menu("Clamp at top", choices, max_rows=5) == "item-0"
        input_stream.send_text("\x1b[6~" * 12 + "\r")
        assert select_menu("Clamp at bottom", choices, max_rows=5) == "item-29"


def test_menu_without_a_back_item_still_cancels_and_goes_back() -> None:
    choices = [("run", "Run"), ("exit", "Exit")]
    with (
        create_pipe_input() as input_stream,
        create_app_session(input=input_stream, output=DummyOutput()),
    ):
        input_stream.send_text("\x03")
        with pytest.raises(SelectionCancelled):
            select_menu("Actions", choices)
        input_stream.send_text("\x1b")
        with pytest.raises(BackRequested):
            select_menu("Actions", choices)
        input_stream.send_text("j\r")
        assert select_menu("Actions", choices) == "exit"


def test_menu_shows_details_and_avoids_an_alternate_screen() -> None:
    class TrackingOutput(DummyOutput):
        entered_alternate_screen = False

        def enter_alternate_screen(self) -> None:
            self.entered_alternate_screen = True

    output = TrackingOutput()
    with (
        create_pipe_input() as input_stream,
        create_app_session(input=input_stream, output=output),
    ):
        input_stream.send_text("\r")
        selected = select_menu(
            "Dashboard",
            [("check", "Project Check"), ("exit", "Exit")],
            details=("Paper Support: enabled",),
        )

    assert selected == "check"
    assert not output.entered_alternate_screen
