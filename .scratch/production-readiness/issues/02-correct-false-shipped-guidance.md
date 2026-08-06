# Correct false statements in shipped guidance

Type: task
Status: resolved
Blocked by: None

## Question

Do the generated project and portable skills tell researchers only to run behavior the installed toolkit actually provides?

## Work

- Reconcile `src/smairt/assets/scaffold/prompts/CONTEXT_INDEX.md`, which says `new_track.py` creates the first iteration, with the helper's actual interface: it creates a plan and hypothesis, then requires criteria before `new_iteration.py` creates a script.
- Reconcile the generated `src/smairt/assets/scaffold/README.md` claim that `smairt open` reports project status and the next command with the actual command interface. Either make the claim true through the right module or state what `open` really does; do not duplicate dashboard logic in an adapter.
- Reconcile `skills/smairt-paper-driven/SKILL.md` telling users to run `smairt new --paper` with wizard mode currently ignoring that flag. Prefer one truthful interface over documenting a surprising exception.
- Update source assets and golden projects through the repository's established generation seam, not by allowing fixtures to drift independently.
- Add tests through the public interface where behavior changes. For prose-only corrections, add the smallest fidelity assertion that prevents the exact regression.

## Resolution

Resolve when every command and workflow described by these three shipped files works as written and the generated-project fidelity checks pass.

## Answer

All three statements were false in different ways, and each was fixed at the level where the
falsehood lived rather than by softening the prose.

**`smairt open` now reports where the project stands.** The claim in the generated
`README.md` was the correct ambition; the command was the thing that fell short. `open` now
calls the same `next_workflow_action()` the dashboard uses, so one module owns "what comes
next" and both surfaces read it. Weakening the README instead would have removed a real
promise to preserve an accidental limitation, and duplicating the logic in the adapter would
have created a second answer that could drift.

**Guided creation refuses `--paper` and `--hpc` rather than discarding them.** Three options
existed: honour the flag in the wizard, document the exception, or refuse. Honouring it would
put the same decision in two places; documenting it would ask researchers to remember a
surprise. Refusing names the conflict while nothing has been written, and points at both
working forms. `smairt new ./project --paper ...` was already correct and stays correct.

**`prompts/CONTEXT_INDEX.md` no longer promises a first iteration.** `new_track.py` stops
after the plan and hypothesis on purpose, because committing criteria before a script exists
is what keeps the test a test. The line now matches `scripts/README.md`, which was already
authoritative.

### Verification

- 6 new tests, written failing first. 184 pass, up from 178, with no test weakened.
- One existing test in `test_cli.py` asserted `open`'s exact old output while its real subject
  was recents tracking; it now asserts the behaviour it is named for.
- Goldens regenerated through `scripts/update_goldens.py`. The diff is the one intended line
  in all three fixtures, which is how the fixtures proved they were doing their job.
- `ruff format`, `ruff check`, strict `mypy`, and the full suite are green.
- Verified by hand from a fresh install: `open` reports state on a new project, and
  `smairt new --paper` with no destination exits `2` and writes nothing.

### Follow-up surfaced, not resolved here

Two tests now guard classes of defect rather than single lines: no shipped guidance may claim
`new_track.py` creates a script, and no skill may document a capability flag on `smairt new`
without a destination. Both would have caught these regressions at the source.
