# 05 - Ship a tested installable preview

**What to build:** Make SMAIRT Toolkit V0.1 ready for maintainers and preview users: canonical onboarding recommends the installed `smairt` flow, legacy Cookiecutter is documented accurately, package and platform claims are tested, generated guidance is internally consistent, and automated quality gates verify supported Python/macOS/Linux behavior before release.

**Blocked by:** 04 - Expose Advanced project controls.

**Status:** ready-for-agent

- [ ] Root onboarding, tutorials, contribution guidance, and generated documentation use canonical repository links, commands, terminology, and Standard/Advanced Mode names.
- [ ] Installation documents `uv tool install` as primary and `pipx` as fallback for macOS, Linux, and WSL while explicitly deferring native Windows.
- [ ] Legacy Cookiecutter has a dedicated compatibility README and is not presented as the normal onboarding path.
- [ ] Documentation accurately describes Paper, HPC, assistants, Project Check, repairs, Git, animations, and V0.1 limitations.
- [ ] Formatting, linting, strict typing, focused tests, the full test suite, builds, and clean installation smoke tests run in CI.
- [ ] CI covers Python 3.11, 3.12, and 3.13 on Ubuntu and macOS.
- [ ] Wheel and source-distribution smoke tests install the package and create/check a representative project.
- [ ] No supported path relies on stale Cookiecutter repository names, browser-paste workflows, missing files, or invalid commands.
- [ ] The complete branch passes a two-axis Standards and Spec code review and all resulting findings are resolved or explicitly documented.
