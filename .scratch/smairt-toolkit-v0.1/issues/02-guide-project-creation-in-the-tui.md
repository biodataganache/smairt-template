# 02 - Guide project creation in the TUI

**What to build:** Make `smairt new` approachable through a polished linear terminal wizard that gathers all agreed project choices one screen at a time, explains them in plain language, retains answers when navigating Back, shows predictable progress and subtle animation, and presents an editable final checklist before invoking the trusted generator.

**Blocked by:** 01 - Create a project from the installed CLI.

**Status:** ready-for-agent

- [ ] The wizard covers destination, name, editable slug, description, domain/custom domain, optional question, researcher, optional email, capabilities, phase, assistant, license, Git, and review.
- [ ] Every screen contributes to progress and optional choices can be skipped or accept a recommended default.
- [ ] Back navigation retains prior values and each screen explains that final review can correct mistakes.
- [ ] Domain, phase, assistant, capability, and license choices use the approved wording and plain-language descriptions.
- [ ] The final checklist can edit any answer and cancellation writes no project files.
- [ ] Interactive TTY progress/success motion is enabled by default while tests, redirected output, dumb terminals, and machine-readable output remain deterministic.
- [ ] Prompt Toolkit input-driven tests cover the complete happy path, Back/edit behavior, validation, cancellation, and generation failure without mocking private helpers.
