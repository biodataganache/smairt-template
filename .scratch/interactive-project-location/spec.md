# Interactive Project Location and Visual Wizard Controls

Status: ready-for-agent

## Problem Statement

The interactive `smairt new` wizard asks where the new project folder should be created, but treats the answer as the complete destination. A researcher who enters an existing parent directory such as `~/Documents` reasonably expects SMAIRT to create a new project folder inside it. Instead, SMAIRT resolves that directory, identifies it as non-empty, and reports that the location is unsafe. Symlinked locations make the message more surprising because the reported path may differ from the path the researcher entered.

The same wizard relies on numbered textual choices and command tokens such as `:back`. This makes guided project creation less discoverable than a terminal-native selector and leaves final review dependent on remembering field numbers. Researchers need a clear distinction between a parent directory and a new project folder, while retaining SMAIRT's strict destination safety and support for deterministic non-visual input.

## Solution

Interactive project creation will ask the researcher whether to create a new child folder in the current workspace or choose another parent directory. The project folder will be a separate field, defaulted from the normalized project name. Before creation, the wizard will show the complete proposed destination and validate that the parent exists and that the child target does not exist.

In a capable interactive terminal, finite choices will use visual selectors with arrow-key and `j`/`k` navigation, Enter to select, a visible Back choice, Escape or Left Arrow to go back, Ctrl-C to cancel, and retained selections. Final review will itself be a selector: the researcher can create the generated project, edit any listed field and return to review, go back, or cancel.

When visual interaction is unavailable, including redirected input, CI, pytest command transcripts, or a dumb terminal, the wizard will retain a deterministic text interface. The text interface will expose equivalent choices and preserve scriptable installed-command tests.

The noninteractive `smairt new /complete/new/project/path ...` contract will not change. Both interactive and noninteractive paths will continue to pass one complete absent destination to the existing atomic generator.

## User Stories

1. As a researcher, I want to choose whether my generated project lives in the current workspace or another location, so that the wizard matches how I think about project placement.
2. As a researcher, I want “Create in this workspace” to create a new child folder, so that SMAIRT never attempts to initialize or overwrite my current workspace.
3. As a researcher, I want “Choose another location” to ask for a parent directory, so that entering `~/Documents` means what I expect.
4. As a researcher, I want the other-location parent to default to `~/Documents`, so that a common project location requires little typing.
5. As a researcher, I want to enter a project folder separately from its parent directory, so that the resulting target is unambiguous.
6. As a researcher, I want the project folder to default from my normalized project name, so that I do not need to repeat the same information.
7. As a researcher, I want the wizard to display the complete proposed destination, so that I can verify exactly where the generated project will be written.
8. As a researcher, I want symlinked parent directories to remain valid parent choices, so that normal operating-system shortcuts do not produce misleading non-empty-destination failures.
9. As a researcher, I want destination validation to describe problems with the resulting child target, so that errors identify the location SMAIRT would actually create.
10. As a researcher, I want SMAIRT to reject a missing parent directory, so that generation cannot silently create an unintended directory tree.
11. As a researcher, I want SMAIRT to reject a child target that already exists, even when empty, so that existing work is never reused or overwritten implicitly.
12. As a researcher, I want project generation to remain atomic, so that a failed generation does not expose a partial generated project.
13. As a researcher, I want finite wizard choices to be navigable with Up and Down arrows, so that the guided flow behaves like a native terminal application.
14. As a keyboard-oriented researcher, I want `j` and `k` to navigate selectors, so that I can use familiar terminal controls.
15. As a researcher, I want Enter to accept the focused selector item, so that selection is direct and predictable.
16. As a researcher, I want a visible `Back` item in selectors, so that backward navigation is discoverable without memorizing a command.
17. As a researcher, I want Escape or Left Arrow to return to the previous wizard step, so that terminal-standard back navigation works consistently.
18. As a researcher, I want Ctrl-C to cancel project creation, so that I can leave immediately without writing files.
19. As a researcher, I want my prior selection retained when I return to a selector, so that reviewing an earlier answer does not reset it.
20. As a researcher, I want earlier text answers retained when I go back, so that correcting one field does not require re-entering the rest.
21. As a researcher, I want final review to list the complete destination and every project option, so that I can verify the generated-project contract before writing files.
22. As a researcher, I want to select any field during final review, edit it, and return to final review, so that corrections are targeted.
23. As a researcher, I want Create, Cancel, and Back to be explicit final-review actions, so that every outcome is visible.
24. As a researcher, I want a changed license to require confirmation before creation, so that final review cannot bypass the legal acknowledgement.
25. As a researcher, I want cancellation from any supported wizard control to write no generated project, so that exploration is safe.
26. As a researcher using a basic terminal, I want an equivalent text wizard, so that visual terminal capabilities are not required.
27. As a researcher piping answers into the command, I want deterministic prompts and numbered choices, so that automation and reproducible tests remain possible.
28. As a maintainer, I want visual controls disabled in CI, pytest command transcripts, redirected streams, and `TERM=dumb`, so that tests do not depend on terminal rendering.
29. As a maintainer, I want real Prompt Toolkit key processing tested through pipe input, so that navigation behavior is verified without coupling tests to renderer bytes.
30. As a maintainer, I want installed-command tests to verify the generated project and project contract, so that tests cover the highest practical external seam.
31. As an automation author, I want the complete-path noninteractive `smairt new` interface unchanged, so that existing scripts remain compatible.
32. As a maintainer, I want the CLI and terminal UI to remain adapters over shared project operations, so that placement improvements do not redefine the scaffold.
33. As a maintainer, I want the generator to continue receiving one complete destination, so that atomic safety remains centralized.
34. As a maintainer, I want the Prompt Toolkit dependency constrained to the tested major version, so that selector behavior does not change through an unbounded upgrade.
35. As a researcher, I want all scientific scaffold assets and capabilities to remain unchanged by this UX improvement, so that project placement does not alter the generated scientific product.

## Implementation Decisions

- The interactive location flow will have two concepts: a location mode and a project folder. The mode is either creation under the current working directory or creation under a researcher-selected parent directory.
- “Create in this workspace” means the current working directory is the parent. It never means initializing the current directory in place.
- “Choose another location” asks for an existing parent directory and recommends `~/Documents` as its initial value.
- The project name will be collected before the project folder is finalized so the folder can default from the same normalization used for project slugs.
- The project folder must be exactly one folder name rather than an absolute path or nested relative path. The complete destination is formed by joining the selected parent and folder.
- The wizard will retain the complete destination as derived state for validation, final review, and the generator boundary; parent and folder remain independently editable inputs.
- Existing destination validation and atomic generation remain authoritative. The interactive adapter will validate the derived destination before advancing, and generation will validate it again before materializing the scaffold.
- The CLI and terminal interaction remain adapters over shared project operations, consistent with the accepted generated-project-surface decision. The scaffold blueprint, scaffold assets, generated-project contract schema, and capability behavior will not change.
- A small local Prompt Toolkit selector will render finite choices. It will use a non-full-screen application, avoid the alternate screen, and return a selected value rather than exposing widget state to callers.
- Visual selector controls will include Up/Down and `k`/`j` movement, Enter acceptance, a visible Back item, Escape/Left back navigation, and Ctrl-C cancellation. Navigation wraps at the first and last items.
- A selector accepts a retained default value and initially focuses that value when revisited.
- The wizard will decide once whether visual interaction is supported using terminal streams and environment state. CI, pytest, redirected input/output, absent or dumb terminal types, and an explicitly disabled motion preference use deterministic text choices.
- The deterministic text fallback will present numbered finite choices and continue supporting explicit `:back` and `:cancel` tokens for text fields.
- Final review will be a finite selector in visual mode and an equivalent numbered action list in fallback mode. Field selection invokes the existing field editor and then returns to a refreshed review.
- Final review includes Create, every editable field, Back, and Cancel. License edits invalidate prior confirmation and must be reconfirmed before creation.
- Cancellation is represented by the existing wizard cancellation control flow and produces no files.
- The complete-path noninteractive command signature and required flags remain unchanged.
- Prompt Toolkit will be constrained to the tested 3.x API range, starting at the documented tested release.
- The implementation will reuse the current wizard rather than porting the broader terminal UI from another repository.

## Testing Decisions

- Good tests assert externally observable behavior: selected values, navigation outcomes, command exit status, created destination, generated project contents, retained project-contract values, safety errors, and absence of files after cancellation. They do not assert Prompt Toolkit's unstable terminal rendering bytes or private widget layout.
- The primary seam is the installed `smairt new` command. Existing PTY and subprocess helpers provide prior art for complete wizard transcripts, destination safety, retained answers, final-review edits, cancellation, generation failure, and the generated project contract.
- Installed-command fallback tests will cover creation under the current workspace, creation under a selected parent, the project-folder default, occupied and missing destinations, review edits, Back and Cancel, and continued noninteractive complete-path behavior.
- The supporting seam is the narrow selector function running through Prompt Toolkit's real input processing with pipe input, an application session, and dummy output. Prior art exists in the related SMAIRT terminal UI tests and follows Prompt Toolkit's documented unit-testing guidance.
- Selector tests will cover Up/Down, `j`/`k`, Enter, selectable Back, Escape, Left Arrow, Ctrl-C, wrapping navigation, retained focus, and avoidance of the alternate screen.
- Fallback-selection tests will verify deterministic numbered input and equivalent Back/Cancel outcomes without a capable terminal.
- Destination tests will verify the derived child path rather than treating the selected parent as the target. A symlinked parent will be included where the platform supports symlinks.
- Existing generator safety tests remain the authority for atomic creation and refusal to overwrite an existing destination.
- The full formatting, linting, type-checking, test, build, and isolated installed-package smoke checks will run before completion.

## Out of Scope

- Initializing an existing directory as a generated project.
- Allowing “Create in this workspace” to write directly into the current working directory.
- Creating missing parent directories automatically.
- Accepting nested paths in the project-folder field.
- Changing the noninteractive complete-destination command contract.
- Changing the generated-project contract schema.
- Changing the scaffold blueprint, scaffold assets, golden projects, scientific lifecycle, starting phase, current phase, or capability semantics.
- Porting environment management, safety modes, coding-harness configuration, contributor registration, collaborator workflows, appearance customization, or the broader schema from `smairt-toolkit`.
- Replacing all dashboard and settings menus with visual selectors.
- Adding a general-purpose terminal UI framework or reusable cross-application design system.

## Further Notes

- The motivating case is an existing `~/Documents` path that resolves through a OneDrive symlink. That path is a valid parent but an invalid complete destination because it already contains files.
- Prompt Toolkit 3.0.52 documentation confirms custom key bindings, `event.app.exit` return values, `PromptSession`, `RadioList`, and pipe-input plus dummy-output testing as supported patterns.
- The final generator call must continue receiving a complete absent child destination, preserving the existing project-safety invariant and the accepted architectural boundary.
