# 05 - Re-enrich helpers and project documentation

Status: ready-for-agent
Type: task
Blocked by: 02

## Question

Can a researcher use the generated helper scripts without reading their source?

## Context

This group differs from the prose tickets: it contains executable Python. `scripts/README.md` fell from 11,585 bytes to 973, so the helper set is effectively undocumented, and the helpers themselves lost roughly half to two-thirds of their implementations.

| Asset | Original | Current | Retained |
|---|---|---|---|
| `docs/12_STEPS.md` | 9619 | 567 | 5% |
| `docs/SMAIRT_PHILOSOPHY.md` | 3080 | 250 | 8% |
| `scripts/README.md` | 11585 | 973 | 8% |
| `README.md` | 5680 | 522 | 9% |
| `docs/README.md` | 681 | 93 | 13% |
| `scripts/shared/__init__.py` | 877 | 141 | 16% |
| `docs/BEST_PRACTICE_COLLABORATIVE.md` | 4819 | 1452 | 30% |
| `scripts/new_script.py` | 6039 | 2311 | 38% |
| `scripts/generate_manifest.py` | 3689 | 1644 | 44% |
| `scripts/monitor_template.py` | 3496 | 1743 | 49% |
| `scripts/shared/README.md` | 1132 | 636 | 56% |

`docs/12_STEPS.md` currently lists twelve step titles with no explanation — 567 bytes for what was a 9,619-byte teaching document.

The active helper set is exactly four: experiment creation, shared logging, progress monitoring, and non-destructive manifest generation. Four originals are archived-only and must not reappear as working code: `compile_for_ai.py`, `new_experiment.py`, `new_iteration.py`, `finalize_iteration.py`. Note that `scripts/new_script.py` must cover all three phase directories, and `scripts/generate_manifest.py` and `scripts/monitor_template.py` must remain strictly non-destructive — they inventory and observe, they do not rewrite.

`docs/BEST_PRACTICE_SINGLE.md` stays retired; the collaborative guide is canonical.

## Acceptance

- Each asset above meets its declared fidelity floor from ticket 02.
- `docs/12_STEPS.md` explains each step, not just names it.
- `scripts/README.md` documents each of the four active helpers: purpose, invocation, inputs, and outputs.
- Restored Python executes. Helpers run from a generated project and are exercised by tests, not merely imported.
- `scripts/new_script.py` handles all three phase directories.
- `scripts/generate_manifest.py` and `scripts/monitor_template.py` make no destructive writes.
- `scripts/shared/logging.py` continues to capture stdout, stderr, warnings, and uncaught tracebacks; a test proves each.
- The generated project `README.md` describes one workflow with optional capabilities and links only to files that exist.
- No retired helper is reintroduced under any name.
- `uv run ruff format --check .`, `uv run ruff check .`, and `uv run mypy src tests` pass over the restored helper code.

## Notes

Generated helper scripts live under `src/smairt/assets/scaffold/scripts/` and are copied byte-for-byte rather than Jinja-rendered. Keep them free of template placeholders.

Ruff's configured `include` covers `src/**/*.py`, so scaffold helper sources are linted. Restored code must satisfy the repo's lint and format rules.
