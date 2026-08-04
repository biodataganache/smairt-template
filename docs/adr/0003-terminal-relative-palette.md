# ADR 0003: Draw the Terminal Interface With the Terminal's Own Palette

Status: Accepted

## Context

SMAIRT's terminal interface had no palette. The console was constructed without a theme and styles were inline literals scattered across the CLI, so hierarchy was inconsistent and unreviewable. The selector had no style at all and relied on the widget library's default reverse-video highlight, which read as a rendering glitch rather than a selected row.

A designed fixed palette would give precise control, but it bets on the researcher's background color. A tool that chooses specific foreground and background colors looks deliberate in the terminal it was tuned in and looks broken elsewhere. Researchers run SMAIRT in whatever terminal their institution gave them, on light and dark themes, over SSH, and inside editor terminals.

Interactive screens are drawn by the interaction library while non-interactive output is printed by the rich-text library. Two independent style definitions would drift, and the resulting mismatch between a framed screen and the output printed beneath it is the same incoherence a palette is meant to remove.

## Decision

SMAIRT styles its interface using only the terminal's own sixteen ANSI colors. It does not specify absolute colors and does not set a background except to mark the focused row. Hierarchy comes from weight, dimming, and spacing before it comes from hue, so the interface inherits whatever theme the researcher already trusts.

One semantic palette is the single definition. Names describe roles rather than colors, and the same definition is exported both as a rich-text theme and as an interaction-library style. Modules reference semantic names and never literal colors.

Color is never the only carrier of meaning. Selected and checked states keep textual markers, and warnings and failures keep an explanatory word. The interface remains fully usable with color disabled, in monochrome terminals, and for colorblind researchers.

When color is unavailable or unwanted, the interface degrades to plain text. An explicit no-color request and a non-terminal stream both disable styling without changing behavior or wording.

## Consequences

- The palette cannot be visually tuned to one preferred terminal, and exact appearance varies by theme. That variation is accepted in exchange for never clashing.
- Adding a styled element requires adding or reusing a semantic name, not choosing a color at the call site.
- Style changes are reviewable in one place, and the framed screens cannot drift from printed output.
- Tests assert markers and wording rather than color, so they remain valid under any terminal theme.
- A future opt-in theme preference remains possible, because call sites depend on semantic names rather than the palette's contents.
