# Prove the supported platform matrix before the pull request

Type: task
Status: claimed
Blocked by: None

## Question

Can the exact locked project pass its production gates on every supported interpreter and operating-system family before the final pull request is opened?

## Work

- Reproduce Python 3.11, 3.12, and 3.13 checks on macOS and Linux without weakening `.github/workflows/ci.yml`.
- On every environment, run the locked install, format check, Ruff, strict mypy, scaffold diff, all tests, build, and wheel/sdist smoke installs that CI declares.
- Exercise upgrade symlink containment and atomic replacement on Linux specifically; those filesystem semantics are the risk not covered by the existing macOS run.
- Record exact commands, environment versions, and results in the answer. File defects as newly unblocked tickets rather than hiding them in this ticket.

## Resolution

Resolve only when all six cells pass or every failing cell has a precise blocking ticket. Local reproduction does not replace the final GitHub Actions run; it makes opening that pull request an informed act.
