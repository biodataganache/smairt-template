# 05 - Ship a tested installable preview

**What to build:** Make SMAIRT Toolkit V0.1 ready for maintainers and preview users: canonical onboarding recommends the installed `smairt` flow, legacy Cookiecutter is documented accurately, package and platform claims are tested, generated guidance is internally consistent, and automated quality gates verify supported Python/macOS/Linux behavior before release.

**Blocked by:** 04 - Expose Advanced project controls.

**Status:** complete

- [x] Root onboarding, tutorials, contribution guidance, and generated documentation use canonical repository links, commands, terminology, and Standard/Advanced Mode names.
- [x] Installation documents `uv tool install` as primary and `pipx` as fallback for macOS, Linux, and WSL while explicitly deferring native Windows.
- [x] Legacy Cookiecutter has a dedicated compatibility README and is not presented as the normal onboarding path.
- [x] Documentation accurately describes Paper, HPC, assistants, Project Check, repairs, Git, animations, and V0.1 limitations.
- [x] Formatting, linting, strict typing, focused tests, the full test suite, builds, and clean installation smoke tests run in CI.
- [x] CI covers Python 3.11, 3.12, and 3.13 on Ubuntu and macOS.
- [x] Wheel and source-distribution smoke tests install the package and create/check a representative project.
- [x] No supported path relies on stale Cookiecutter repository names, browser-paste workflows, missing files, or invalid commands.
- [x] The complete branch passes a two-axis Standards and Spec code review and all resulting findings are resolved or explicitly documented.

## Verification

- TDD: added `tests/test_release.py` at the public build-artifact and installed-command seams; it failed before `scripts/smoke_install.py` existed, then passed after the clean-install implementation.
- Standards review: no unresolved findings. Ruff format/lint, strict mypy, existing public-seam tests, and the full suite pass. Formatting-only changes were applied by Ruff to files covered by the new formatter gate.
- Spec review: one documentation issue was found and resolved before completion. The tutorial now uses the dynamic `REPAIR_ID` placeholder rather than documenting a repair unavailable in a healthy project.
- Full local verification on macOS/Python 3.11.15: `uv run ruff format --check .`, `uv run ruff check .`, `uv run mypy src tests`, `uv run pytest tests/test_cli.py tests/test_legacy.py`, `uv run pytest`, `uv build`, and clean wheel/source-distribution `scripts/smoke_install.py` runs all passed.
- Legacy compatibility verification: `uv run --with cookiecutter cookiecutter . --no-input ...` created a project through the installed canonical package and reported the legacy compatibility message.
