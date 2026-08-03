# 01 - Restore a green baseline

Status: ready-for-agent
Type: task
Blocked by: none

## Question

Can the release gates pass before any content work begins?

## Context

`uv run mypy src tests` currently fails with two errors in one file, so the branch is not green. Re-enrichment must not begin on a red baseline, because a later failure would be ambiguous between the pre-existing defect and the new work.

`src/smairt/cli.py` binds `requested` twice in the optional-capabilities wizard step. Line 351 binds it as a `str` returned by `select_choice(...)` on the visual path. Line 373 rebinds it as a `set[str]` built from the text-fallback answer. Both branches behave correctly at runtime because `"paper" in requested` is meaningful for both a string and a set, but the types collide under strict checking.

```
src/smairt/cli.py:373: error: Incompatible types in assignment (expression has type "set[str]", variable has type "str")
src/smairt/cli.py:374: error: Unsupported operand types for <= ("str" and "set[str]")
```

Note that CI runs mypy as a hard gate and `uv.lock` pins mypy 2.3.0, which is stricter than the `>=1.13` floor declared in `pyproject.toml`. This will fail CI as-is.

## Acceptance

- The two names are distinct; neither branch reuses the other's binding.
- Both the visual selector path and the text fallback path still set `paper` and `hpc` answers correctly.
- `uv run mypy src tests` reports no errors.
- `uv run ruff format --check .`, `uv run ruff check .`, and `uv run pytest` all pass.
- No behavior change is observable through the installed command.

## Notes

Renaming the visual-path binding to something like `selection` is the smaller edit and leaves the set-based fallback logic untouched.
