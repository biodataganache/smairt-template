"""Framed terminal screens for finite choices.

One screen presents a title, an optional detail block, a scrollable list of
options, and a footer of controls. Screens repaint in place and never enter the
alternate screen, so scrollback and copy remain the terminal's own. See ADR 0002.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, cast

from prompt_toolkit import Application
from prompt_toolkit.application.current import get_app_session
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout import HSplit, Layout, ScrollOffsets, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.layout.margins import ScrollbarMargin
from prompt_toolkit.widgets import Box, Frame, Label

from smairt.appearance import prompt_style

T = TypeVar("T")

MINIMUM_MENU_ROWS = 3
"""Smallest scrolling viewport that still shows movement in either direction."""

FRAME_ROWS = 2
"""Rows the frame border itself occupies above and below the screen body."""

CONTROLS_HINT = (
    "Up/Down or j/k move · PageUp/PageDown scroll · Enter select · Left/Esc back · Ctrl-C cancel"
)

MULTIPLE_CONTROLS_HINT = (
    "Up/Down or j/k move · Space or Enter toggle · Enter on Next continues · "
    "Left/Esc back · Ctrl-C cancel"
)

SEPARATOR = object()
"""A divider row that groups options visually and can never be landed on."""

_CHECKED_MARKER = "[x]"
_UNCHECKED_MARKER = "[ ]"
_CHOSEN_MARKER = "(*)"
_UNCHOSEN_MARKER = "( )"
_ACTION_MARKER = "   "


class BackRequested(Exception):
    """Raised when the researcher asks to return to the previous screen."""


class SelectionCancelled(Exception):
    """Raised when the researcher abandons the current interaction."""


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


@dataclass(frozen=True)
class ScreenPlan:
    """How much of a screen fits in the terminal without overflowing it."""

    rows: int
    details_shown: bool
    footer_shown: bool
    spacer_shown: bool

    def total_rows(self, detail_count: int) -> int:
        """Report the full rendered height including the frame border."""
        details = detail_count if self.details_shown else 0
        return FRAME_ROWS + details + self.rows + int(self.footer_shown) + int(self.spacer_shown)


def plan_screen(
    item_count: int,
    detail_count: int = 0,
    terminal_rows: int | None = None,
    max_rows: int | None = None,
) -> ScreenPlan:
    """Fit a screen into the terminal, dropping ornament before losing options.

    A screen taller than the terminal cannot repaint cleanly, so decoration is
    surrendered in order of expendability: spacing, then the controls footer,
    then the detail block, and only then the visible option rows. `max_rows`
    caps the option rows themselves and never counts frame or footer height.
    """
    if terminal_rows is None:
        terminal_rows = get_app_session().output.get_size().rows
    wanted = item_count if max_rows is None else min(item_count, max_rows)
    for details_shown, footer_shown, spacer_shown in (
        (True, True, True),
        (True, True, False),
        (True, False, False),
        (False, False, False),
    ):
        chrome = (
            FRAME_ROWS
            + (detail_count if details_shown else 0)
            + int(footer_shown)
            + int(spacer_shown)
        )
        rows = min(wanted, terminal_rows - chrome)
        if rows >= min(wanted, MINIMUM_MENU_ROWS):
            return ScreenPlan(rows, details_shown, footer_shown, spacer_shown)
    return ScreenPlan(
        max(1, min(wanted, terminal_rows - FRAME_ROWS)),
        details_shown=False,
        footer_shown=False,
        spacer_shown=False,
    )


def viewport_rows(item_count: int, chrome_rows: int, max_rows: int | None = None) -> int:
    """Return how many option rows stay visible while the rest remain scrollable."""
    if max_rows is None:
        terminal_rows = get_app_session().output.get_size().rows
        max_rows = terminal_rows - chrome_rows
    return min(item_count, max(MINIMUM_MENU_ROWS, max_rows))


@dataclass(frozen=True)
class Option(Generic[T]):
    """One row of a screen: a value to choose, an action to invoke, or a divider."""

    value: T
    label: str
    is_action: bool = False
    is_separator: bool = False

    @property
    def is_selectable(self) -> bool:
        """Report whether the cursor may rest on this row at all."""
        return not self.is_separator


def _as_options(choices: Sequence[tuple[Any, str]]) -> list[Option[Any]]:
    """Turn caller choices into rows, recognizing the divider sentinel."""
    return [Option(value, label, is_separator=value is SEPARATOR) for value, label in choices]


class _OptionList(Generic[T]):
    """A scrolling list of options that marks chosen, checked, and action rows."""

    def __init__(
        self,
        options: Sequence[Option[T]],
        *,
        visible_rows: int,
        multiple: bool,
        chosen: T | None = None,
        checked: Sequence[T] = (),
    ) -> None:
        if not any(option.is_selectable for option in options):
            raise ValueError("a screen requires at least one selectable option")
        self.options = list(options)
        self.multiple = multiple
        self.checked: list[T] = [
            option.value for option in self.options if option.value in tuple(checked)
        ]
        self._visible_rows = visible_rows
        self._index = self._initial_index(chosen)
        self.control = FormattedTextControl(
            self._fragments,
            key_bindings=self._bindings(),
            focusable=True,
            show_cursor=False,
        )
        self.window = Window(
            content=self.control,
            height=Dimension(min=1, preferred=visible_rows, max=visible_rows),
            dont_extend_height=True,
            scroll_offsets=ScrollOffsets(top=1, bottom=1),
            right_margins=[ScrollbarMargin(display_arrows=True)],
        )

    @property
    def focused(self) -> Option[T]:
        """Return the option the cursor currently rests on."""
        return self.options[self._index]

    def _initial_index(self, chosen: T | None) -> int:
        preferred = self.checked[0] if self.checked else chosen
        for index, option in enumerate(self.options):
            if option.is_selectable and not option.is_action and option.value == preferred:
                return index
        return next(index for index, option in enumerate(self.options) if option.is_selectable)

    def _bindings(self) -> KeyBindings:
        bindings = KeyBindings()

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

        return bindings

    def _move(self, amount: int) -> None:
        """Step to the next selectable row, wrapping past dividers and both ends."""
        step = 1 if amount > 0 else -1
        index = self._index
        for _ in range(len(self.options)):
            index = (index + step) % len(self.options)
            if self.options[index].is_selectable:
                self._index = index
                return

    def _page(self, direction: int) -> None:
        """Jump one viewport of rows without wrapping past either end."""
        target = self._index + direction * self._visible_rows
        self._index = self._nearest_selectable(
            min(max(target, 0), len(self.options) - 1), direction
        )

    def _nearest_selectable(self, index: int, direction: int) -> int:
        """Return the closest selectable row to an index, preferring one direction."""
        for step in (direction, -direction):
            candidate = index
            while 0 <= candidate < len(self.options):
                if self.options[candidate].is_selectable:
                    return candidate
                candidate += step
        return self._index

    def toggle_focused(self, exclusive: T | None = None) -> None:
        """Check or uncheck the focused option, keeping an exclusive choice alone."""
        option = self.focused
        if option.is_action:
            return
        if option.value in self.checked:
            self.checked.remove(option.value)
            return
        if exclusive is not None:
            if option.value == exclusive:
                self.checked = [option.value]
                return
            self.checked = [value for value in self.checked if value != exclusive]
        self.checked.append(option.value)

    def _marker(self, option: Option[T], index: int) -> tuple[str, str]:
        if option.is_action or option.is_separator:
            return ("class:option", _ACTION_MARKER)
        if self.multiple:
            checked = option.value in self.checked
            marker = _CHECKED_MARKER if checked else _UNCHECKED_MARKER
        else:
            checked = index == self._index
            marker = _CHOSEN_MARKER if checked else _UNCHOSEN_MARKER
        return ("class:option-checked" if checked else "class:option", marker)

    def _fragments(self) -> StyleAndTextTuples:
        fragments: StyleAndTextTuples = []
        for index, option in enumerate(self.options):
            marker_style, marker = self._marker(option, index)
            if option.is_separator:
                label_style = "class:option-separator"
            elif index == self._index:
                label_style = "class:option-selected"
            else:
                label_style = "class:option"
            if index == self._index:
                fragments.append(("[SetCursorPosition]", ""))
            fragments.append((marker_style, marker))
            fragments.append((label_style, f" {option.label}"))
            fragments.append(("", "\n"))
        fragments.pop()
        return fragments


def _screen_application(
    title: str,
    details: Sequence[str],
    options: _OptionList[T],
    plan: ScreenPlan,
    footer: str,
    bindings: KeyBindings,
) -> Application[Any]:
    body: list[Any] = []
    if plan.details_shown:
        body.extend(Label(detail, style="class:smairt.detail") for detail in details)
    if plan.spacer_shown:
        body.append(Label("", style="class:smairt.detail"))
    body.append(options.window)
    if plan.footer_shown:
        body.append(Label(footer, style="class:smairt.footer"))
    application: Application[Any] = Application(
        layout=Layout(
            Frame(
                Box(
                    HSplit(body),
                    padding=0,
                    padding_left=1,
                    padding_right=1,
                ),
                title=title,
            ),
            focused_element=options.window,
        ),
        key_bindings=bindings,
        style=prompt_style(),
        full_screen=False,
        erase_when_done=True,
    )
    application.ttimeoutlen = 0.05
    return application


def _run_choice(
    title: str,
    options: Sequence[Option[T]],
    details: Sequence[str],
    chosen: T | None,
    max_rows: int | None,
) -> T:
    plan = plan_screen(len(options), len(details), max_rows=max_rows)
    option_list = _OptionList(
        options,
        visible_rows=plan.rows,
        multiple=False,
        chosen=chosen,
    )
    bindings = navigation_bindings()

    @bindings.add("enter", eager=True)
    def accept(event: KeyPressEvent) -> None:
        event.app.exit(result=option_list.focused.value)

    application = _screen_application(title, details, option_list, plan, CONTROLS_HINT, bindings)
    return cast(T, application.run())


def select_choice(
    message: str,
    choices: list[tuple[T, str]],
    default: T | None = None,
    *,
    details: Sequence[str] = (),
    max_rows: int | None = None,
) -> T:
    """Return one choice from a framed screen that offers an explicit Back row."""
    if not choices:
        raise ValueError("selection requires at least one choice")
    back = object()
    options: list[Option[Any]] = _as_options(choices)
    options.append(Option(back, "← Back", is_action=True))
    selected = _run_choice(
        message,
        options,
        details,
        default if default is not None else choices[0][0],
        max_rows,
    )
    if selected is back:
        raise BackRequested
    return cast(T, selected)


def select_menu(
    title: str,
    choices: list[tuple[T, str]],
    default: T | None = None,
    *,
    details: Sequence[str] = (),
    max_rows: int | None = None,
) -> T:
    """Return one menu action from a screen whose own list already offers Back or Exit."""
    if not choices:
        raise ValueError("a menu requires at least one action")
    return cast(
        T,
        _run_choice(
            title,
            _as_options(choices),
            details,
            default if default is not None else choices[0][0],
            max_rows,
        ),
    )


def select_many(
    title: str,
    choices: list[tuple[T, str]],
    checked: Sequence[T] = (),
    *,
    details: Sequence[str] = (),
    exclusive: T | None = None,
    continue_label: str = "Next →",
    max_rows: int | None = None,
) -> list[T]:
    """Return every checked value once the researcher chooses the continue row.

    Space and Enter both toggle the focused option, so no key is inert. Advancing
    requires deliberately choosing the continue row. An exclusive value clears the
    others and is cleared by them, so a contradictory selection cannot be reached.
    """
    if not choices:
        raise ValueError("a selection requires at least one choice")
    proceed = object()
    options: list[Option[Any]] = _as_options(choices)
    options.append(Option(proceed, continue_label, is_action=True))
    plan = plan_screen(len(options), len(details), max_rows=max_rows)
    option_list = _OptionList(
        options,
        visible_rows=plan.rows,
        multiple=True,
        checked=checked,
    )
    bindings = navigation_bindings()

    @bindings.add("enter", eager=True)
    def activate(event: KeyPressEvent) -> None:
        if option_list.focused.value is proceed:
            event.app.exit(result=list(option_list.checked))
        else:
            option_list.toggle_focused(exclusive)

    @bindings.add(" ", eager=True)
    def toggle(event: KeyPressEvent) -> None:
        del event
        option_list.toggle_focused(exclusive)

    application = _screen_application(
        title, details, option_list, plan, MULTIPLE_CONTROLS_HINT, bindings
    )
    return cast(list[T], application.run())


def confirm(question: str, *, details: Sequence[str] = (), affirm: str = "Yes") -> bool:
    """Return whether the researcher explicitly agreed, defaulting to refusal."""
    return select_menu(
        question,
        [(False, "No, leave everything unchanged"), (True, affirm)],
        False,
        details=details,
    )
