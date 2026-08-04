# ADR 0002: Present One Repainting Inline Terminal Screen

Status: Accepted

Supersedes the non-full-screen selector and dashboard-menu exclusions recorded in `.scratch/interactive-project-location/spec.md`.

## Context

The first visual pass added a scrollable selector that rendered inline beneath ordinary printed output. Each screen printed a rule, then a selector, then more output, so an interactive session accumulated a stack of unrelated fragments. The interface read as a transcript of boxes rather than one application, and researchers described it as tight and hard to interact with.

Two earlier decisions constrained that pass. The selector was required to avoid the alternate screen, and replacing dashboard and settings menus with visual selectors was explicitly out of scope. Both decisions were reasonable when the selector was one small widget inside a mostly printed interface. Neither survives a request for a coherent experience across creation and management.

A full-screen application would own the whole viewport and produce a stable frame. It would also discard scrollback, break copy and paste of assistant priming text, remove the transcript that installed-command tests observe, and end each session by erasing everything the researcher just read.

## Decision

Interactive screens are framed Prompt Toolkit layouts that repaint in place. A screen owns its title, its padded body, and a footer describing available controls. Successive screens replace one another instead of stacking.

SMAIRT does not enter the alternate screen. Scrollback, selection, and copy remain the terminal's own. Non-interactive output stays ordinary printed output and remains in the transcript after the interactive screen finishes.

Dashboard, Settings, Home, and wizard screens all use this presentation. Every finite choice is a selection rather than typed free text. Choices over independent values are multi-selections.

Every interactive screen bounds its total height, including title, body, and footer, to the current terminal. Content beyond that height scrolls inside the body rather than overflowing the screen, because a screen taller than the terminal cannot repaint cleanly.

A deterministic text presentation remains available and authoritative for non-interactive use. Menus are addressed by stable action tokens; displayed numbers are a convenience that may be renumbered. Multi-selection degrades to the existing comma-separated token syntax.

The CLI and terminal modules remain adapters over shared project operations. This decision changes presentation and input only.

## Consequences

- The selector may no longer assert that it avoids full-screen behavior; it must instead assert that it avoids the alternate screen.
- Chrome moves inside Prompt Toolkit layouts, so Rich renders only non-interactive output. A single palette definition must serve both, or framed screens and printed output will diverge.
- Screen height is a first-class constraint. Short terminals are a supported case and are tested.
- Tests address menus by action token, so reordering or regrouping a menu no longer breaks unrelated tests.
- Operations that write files keep an explicit preview and confirmation. A multi-selection never applies changes as a side effect of toggling.
