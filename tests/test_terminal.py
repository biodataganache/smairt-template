from __future__ import annotations

import pytest
from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from smairt.terminal import BackRequested, SelectionCancelled, select_choice


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
