# 01 - Restore a green baseline

Status: resolved
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

## Answer

Yes. All eight release gates pass.

The two bindings were separated rather than merely renamed. The visual path now binds `selection` (a `str` from `select_choice`); the text-fallback path keeps `requested` (a `set[str]`). Both funnel into one `_record_capabilities(requested: set[str])` method, so the answer-setting logic exists once instead of twice. A module-level `_parse_capabilities()` helper and `_OPTIONAL_CAPABILITIES` constant replace the duplicated comma-splitting expression and the inline `{"paper", "hpc"}` literal.

The visual path subtracts `{"off"}` before recording, so the sentinel choice cannot be mistaken for a capability name.

Gate results:

| Gate | Result |
|---|---|
| `ruff format --check .` | 36 files already formatted |
| `ruff check .` | All checks passed |
| `mypy src tests` | Success: no issues found in 17 source files |
| `ci_scaffold_diff.py` | no blueprint change |
| `pytest` | 48 passed |
| `uv build` | wheel + sdist built |
| `smoke_install.py` wheel | exit 0 |
| `smoke_install.py` sdist | exit 0 |

Behavior was verified unchanged across both paths, including the whitespace case `" hpc , paper "` and rejection of invalid input:

- visual `off`/`paper`/`hpc`/`paper,hpc` → correct `paper`/`hpc` answers
- fallback `""`/`paper`/`hpc`/`paper,hpc`/`" hpc , paper "` → correct answers
- fallback `nonsense` → rejected, re-prompts

Diff is 15 insertions and 7 deletions in one file.
