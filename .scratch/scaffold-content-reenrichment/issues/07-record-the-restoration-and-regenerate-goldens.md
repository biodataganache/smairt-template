# 07 - Record the restoration and regenerate goldens

Status: ready-for-agent
Type: task
Blocked by: 03, 04, 05, 06

## Question

Is the enriched scaffold independently recorded, and can this gap recur undetected?

## Context

Content edits in tickets 03 through 06 change generated output, so the three golden projects no longer match. ADR 0001 requires that golden output change intentionally and visibly rather than being absorbed silently — goldens are the independent record that generator-and-checker agreement cannot substitute for.

This ticket also closes the documentation loophole that allowed the gap. `docs/scaffold-transition.md` currently records disposition as "Restored at same path" for assets that retained 1 percent of their content. The record was accurate about paths and silent about substance. A content-fidelity column removes that ambiguity.

Regenerate goldens with `scripts/update_goldens.py`. Read the resulting diff rather than trusting it: the diff should show guidance growing and nothing else. Any structural change — a new path, a missing path, a changed contract field — means an earlier ticket did more than it should have.

## Acceptance

- `docs/scaffold-transition.md` gains a content-fidelity column recording original bytes, current bytes, and disposition of the difference for every retained asset.
- Assets that legitimately remain shorter than their originals state why, rather than being padded.
- The eight retired and archived-only assets remain marked as such.
- Goldens are regenerated for `base-synthetic`, `real-with-paper`, and `downloaded-with-hpc`.
- The golden diff shows content growth only: no added, removed, or renamed paths, and no changed `smairt.yaml` fields.
- `uv run python scripts/ci_scaffold_diff.py` reports no blueprint change.
- The fidelity and prohibition tests from ticket 02 pass.
- The full gate sequence passes: `ruff format --check`, `ruff check`, `mypy src tests`, `ci_scaffold_diff.py`, `pytest`, `uv build`, and both `smoke_install.py` artifact checks against the 0.2.0 wheel and sdist.
- `smairt check --json` exits `0` with no issues for all three generated configurations.
- The three upstream specs' `Status:` lines are updated to reflect landed work, per `docs/agents/issue-tracker.md`.

## Notes

Total scaffold content should move from 48,179 bytes toward the 194,401-byte original. The target is standalone comprehensibility, not byte parity — record the final total in the ticket comments as evidence.

Consider whether ADR 0001 warrants a short amendment noting that path-level restoration is insufficient evidence of content restoration. If so, flag it rather than editing the ADR silently.
