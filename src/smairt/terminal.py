from __future__ import annotations

from collections.abc import Sequence
from typing import Any, TypeVar, cast

from prompt_toolkit import Application
from prompt_toolkit.application.current import get_app_session
from prompt_toolkit.filters import to_filter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout import HSplit, Layout, ScrollOffsets
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.widgets import Label, RadioList

T = TypeVar("T")

MINIMUM_MENU_ROWS = 3
"""Smallest scrolling viewport that still shows movement in either direction."""

CONTROLS_HINT = (
    "Up/Down or j/k move · PageUp/PageDown scroll · Enter select · Left/Esc back · Ctrl-C cancel"
)


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


def viewport_rows(item_count: int, chrome_rows: int, max_rows: int | None = None) -> int:
    """Return how many choice rows stay visible while the rest remain scrollable."""
    if max_rows is None:
        terminal_rows = get_app_session().output.get_size().rows
        max_rows = terminal_rows - chrome_rows
    return min(item_count, max(MINIMUM_MENU_ROWS, max_rows))


class _ChoiceList(RadioList[T]):
    def __init__(self, choices: list[tuple[T, str]], default: T, visible_rows: int) -> None:
        super().__init__(choices, default=default)
        self._visible_rows = visible_rows
        self.window.height = Dimension(min=1, preferred=visible_rows, max=visible_rows)
        self.window.dont_extend_height = to_filter(True)
        self.window.scroll_offsets = ScrollOffsets(top=1, bottom=1)
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

        @bindings.add("pageup", eager=True)
        def page_up(event: KeyPressEvent) -> None:
            del event
            self._page(-1)

        @bindings.add("pagedown", eager=True)
        def page_down(event: KeyPressEvent) -> None:
            del event
            self._page(1)

    def _move(self, amount: int) -> None:
        self._selected_index = (self._selected_index + amount) % len(self.values)
        self.current_value = self.values[self._selected_index][0]

    def _page(self, direction: int) -> None:
        """Jump one viewport of rows without wrapping past either end of the list."""
        target = self._selected_index + direction * self._visible_rows
        self._selected_index = min(max(target, 0), len(self.values) - 1)
        self.current_value = self.values[self._selected_index][0]


def _run_selector(
    message: str,
    choices: list[tuple[T, str]],
    default: T | None,
    details: Sequence[str],
    include_back: bool,
    max_rows: int | None,
) -> T:
    if not choices:
        raise ValueError("selection requires at least one choice")
    back_token = object()
    visible_choices: list[tuple[object, str]] = list(choices)
    if include_back:
        visible_choices.append((back_token, "← Back"))
    selected: object = default if default is not None else choices[0][0]
    chrome_rows = 2 + len(details)
    chooser = _ChoiceList(
        visible_choices,
        selected,
        viewport_rows(len(visible_choices), chrome_rows, max_rows),
    )
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
                    *[Label(detail) for detail in details],
                    chooser,
                    Label(CONTROLS_HINT),
                ]
            )
        ),
        key_bindings=bindings,
        full_screen=False,
        erase_when_done=True,
    )
    application.ttimeoutlen = 0.05
    return cast(T, application.run())


def select_choice(
    message: str,
    choices: list[tuple[T, str]],
    default: T | None = None,
    *,
    max_rows: int | None = None,
) -> T:
    """Return one terminal-native choice, scrolling long lists, without an alternate screen."""
    return _run_selector(message, choices, default, (), True, max_rows)


def select_menu(
    title: str,
    choices: list[tuple[T, str]],
    default: T | None = None,
    *,
    details: Sequence[str] = (),
    max_rows: int | None = None,
) -> T:
    """Return one scrollable menu action whose own list already provides Back or Exit."""
    return _run_selector(title, choices, default, details, False, max_rows)
