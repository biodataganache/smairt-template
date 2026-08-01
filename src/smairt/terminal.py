from __future__ import annotations

from typing import Any, TypeVar, cast

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout import HSplit, Layout
from prompt_toolkit.widgets import Label, RadioList

T = TypeVar("T")


class BackRequested(Exception):
    """Raised when a selector requests the preceding wizard screen."""


class SelectionCancelled(Exception):
    """Raised when a selector cancels the wizard."""


def navigation_bindings() -> KeyBindings:
    """Return consistent back and cancellation controls for editable prompts."""
    bindings = KeyBindings()

    @bindings.add("escape", eager=True)
    @bindings.add("left", eager=True)
    def go_back(event: KeyPressEvent) -> None:
        event.app.exit(exception=BackRequested())

    @bindings.add("c-c", eager=True)
    def cancel(event: KeyPressEvent) -> None:
        event.app.exit(exception=SelectionCancelled())

    return bindings


class _ChoiceList(RadioList[T]):
    def __init__(self, choices: list[tuple[T, str]], default: T) -> None:
        super().__init__(choices, default=default)
        bindings = cast(KeyBindings, self.control.key_bindings)

        @bindings.add("up", eager=True)
        @bindings.add("k", eager=True)
        def move_up(event: KeyPressEvent) -> None:
            del event
            self._move(-1)

        @bindings.add("down", eager=True)
        @bindings.add("j", eager=True)
        def move_down(event: KeyPressEvent) -> None:
            del event
            self._move(1)

    def _move(self, amount: int) -> None:
        self._selected_index = (self._selected_index + amount) % len(self.values)
        self.current_value = self.values[self._selected_index][0]


def select_choice(message: str, choices: list[tuple[T, str]], default: T | None = None) -> T:
    """Return one terminal-native choice without entering an alternate screen."""
    if not choices:
        raise ValueError("selection requires at least one choice")
    back_token = object()
    visible_choices: list[tuple[object, str]] = [*choices, (back_token, "← Back")]
    selected: object = default if default is not None else choices[0][0]
    chooser = _ChoiceList(visible_choices, selected)
    bindings = navigation_bindings()

    @bindings.add("enter", eager=True)
    def accept(event: KeyPressEvent) -> None:
        if chooser.current_value is back_token:
            event.app.exit(exception=BackRequested())
        else:
            event.app.exit(result=chooser.current_value)

    application: Application[Any] = Application(
        layout=Layout(
            HSplit(
                [
                    Label(message),
                    chooser,
                    Label("Up/Down or j/k move · Enter select · Left/Esc back · Ctrl-C cancel"),
                ]
            )
        ),
        key_bindings=bindings,
        full_screen=False,
        erase_when_done=True,
    )
    application.ttimeoutlen = 0.05
    return cast(T, application.run())
