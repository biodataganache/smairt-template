# Prove the supported platform matrix before the pull request

Type: task
Status: resolved
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

## Answer

All six cells pass on real GitHub runners: Ubuntu and macOS on Python 3.11, 3.12, and 3.13.
Evidence: `sarodarte2/smairt-lab` run `31059884112`, every job `success`.

Local reproduction was not sufficient, and proving that was the value of this ticket. macOS
3.11, 3.12, and 3.13 all passed here — full suite, lint, strict mypy — and then the first real
CI run failed **all six cells**, Linux and macOS alike.

### What it caught

`scripts/utilities` was a declared scaffold directory containing nothing. Git does not track an
empty directory, so it was missing from every clone, including the three golden fixtures. The
comparison whose whole job is catching scaffold drift was incomplete in the repository and
complete only in the working tree that had generated it. It could pass on this machine and
nowhere else.

Not a platform bug. A repository-state bug that only a clean checkout can see, which is
precisely the class of defect local verification cannot reach.

### What changed

- `scripts/utilities/README.md` now ships, stating the utility/iteration distinction that had
  no home. A placeholder would have satisfied Git; the directory needed the explanation anyway.
- Scaffold bumped to `0.5.0`, because the blueprint gained a declared asset. Verified: at
  `0.4.0` a project reported the missing file while `upgrade` and `repair` both declined, since
  the installed version already matched. After the bump, mismatch is reported, `upgrade`
  previews exactly that one file, and applying it leaves the project passing its own check.
- A test asserts no declared directory ships empty — the class, not the instance.
- `.github/workflows/ci.yml` also runs on `verify/**` pushes and `workflow_dispatch`, so the
  matrix is reachable before a pull request. Kept deliberately: it found a bug six local runs
  could not, and the final pull request remains the authoritative run.

### Method note

Verification ran on the fork rather than the production repository, so proving the matrix cost
nothing on `origin` and left no throwaway branch or failed check there.
