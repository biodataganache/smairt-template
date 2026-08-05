# Changelog

Notable changes to SMAIRT, newest first.

A project records the `scaffold_version` that created it. When you update SMAIRT, an existing
project reports `scaffold-version-mismatch` and waits for `smairt upgrade`, which previews the
difference before writing anything and never rewrites researcher work. See
[docs/scaffold-transition.md](docs/scaffold-transition.md) for what each scaffold version
changed.

## Unreleased

### Licensing

- **Removed Apache-2.0, GPL-3.0, and the proprietary notice from the license picker.** All
  three shipped as abbreviations rather than licenses: GPL-3.0 rendered as fourteen lines
  against a ~674-line license, and Apache-2.0 as a seventeen-line stub. An abbreviated license
  is not the license it names. MIT and BSD-3-Clause remain, now byte-for-byte complete —
  BSD-3-Clause previously stopped mid-sentence at `DAMAGES.`, dropping its entire
  limitation-of-liability clause.
- Generated guidance explains how to supply a different license yourself, and states that
  `smairt check` will then report `LICENSE` as researcher-modified and never replace it.

  *If you generated a project with Apache-2.0, GPL-3.0, or Proprietary, its `LICENSE` file is
  incomplete. Replace it with the full official text.*

### Upgrading existing projects

- **Added `smairt upgrade`.** Previously, any version bump left every existing project
  read-only: `settings`, `paper`, `hpc`, `repair`, and `regenerate` all refused with "An
  explicit upgrade flow is not available yet", and the documented answer was to generate a new
  project. `smairt upgrade` previews which tool-owned guidance would change, which files would
  be created, and which are kept untouched, then writes only with `--confirm`. It never writes
  researcher-owned records, never follows a symbolic link out of the project, and replaces each
  file atomically so an interruption cannot truncate one.
- Every refusal now names `smairt upgrade`, including the Project Check diagnostic.
- `smairt repair` no longer prints "No safe repairs are available" and exits `0` on an
  out-of-date project while every repair is in fact blocked.
- `smairt regenerate` no longer lists every managed asset as eligible and then refuses on
  `--confirm`.

### Errors and messages

- **Unexpected failures no longer surface as tracebacks.** A boundary reports what happened,
  what it means for your files, and how to get the detail a bug report needs. Set
  `SMAIRT_DEBUG=1` for the full traceback.
- Validation failures are reported in plain sentences instead of pydantic output with
  `[type=...]` tags and `errors.pydantic.dev` links. A rejected slug now gets the rule plus a
  suggestion derived from what you typed.
- A file sitting where a capability directory must go is reported with the path and what to do,
  rather than raising.
- `repair` and `regenerate` writes report a partial failure and point at `smairt check`.

### Creating and running projects

- **Generated guidance says `python3` rather than `python`.** `python` does not exist on a
  stock macOS, so the first command in the project README failed at the point of first
  contact. Thirty-eight occurrences across the README, `docs/12_STEPS.md`,
  `scripts/README.md`, the phase READMEs, the priming prompts, the SLURM template, two
  helpers' own output, and the dashboard's suggested next action.
- **An existing empty directory is now a valid destination**, so `smairt new .` works from
  inside a folder you have already made. A destination holding files is still refused.
- **Project metadata containing a template marker (`{{`, `}}`, `{%`, `%}`) is refused at
  entry.** Such a project used to be created successfully and then fail its own Project Check
  with unresolved template tokens in files you never touched.
- `new_iteration.py` refuses a `--hypothesis` with no matching file, and lists the ones that
  exist. A typo previously wrote an iteration row pointing at nothing while the project still
  reported clean.
- New `dangling-hypothesis-reference` check for rows already written, or hypotheses renamed
  after the fact.
- `smairt regenerate` leads with what is missing instead of listing all forty-three managed
  assets. `--all` shows everything.

### Exit codes

- **Standardized across every command**, so a script can tell the cases apart without reading
  messages: `0` did what it said, `1` the project was found and the operation failed or
  reported findings, `2` the command could not be carried out. Previously only `check` made
  this distinction, and `settings`, `open`, `inspect`, `repair`, and `regenerate` returned `1`
  for a path that was not a project.

### Internal

- One source of truth for the version: `pyproject.toml`. `__version__` reads the installed
  distribution metadata and `scaffold_version` derives from it. Previously three files held it
  by hand, and bumping one but not another made every freshly generated project fail its own
  check.
- CI and the documented release gates select build artifacts by kind rather than by filename,
  so a version bump no longer breaks the build on a missing file.
- `.DS_Store` is excluded from the build, so a wheel built on macOS cannot ship it into a
  generated project.
- Removed three unreachable functions from `generator.py` and two divergent second copies of
  shipped guidance text from `project.py`, one of which wrote different phase-README wording
  than every generated project has.
- `PHASE_DIRECTORIES` is one tuple naming what every project contains, rather than a
  phase-keyed map with two unreachable entries read through a function that discarded its
  argument.
- Split `cli.py` (2,267 lines) into four modules along the seams that were already there:
  `presentation.py` for what every surface needs to speak the same way, `wizard.py` for guided
  creation, `dashboard.py` for managing an existing project, and `cli.py` for the command
  surface alone. The dependency graph is strictly layered with no cycles, and no behavior
  changed — the same 178 tests pass before and after.

## 0.4.0

Workflow contracts for the recorded scientific loop: one numbering authority, append-only
outcome history, structural result selection, self-contained run provenance, project-level
rigor declarations, and a dashboard that hands off into the workflow rather than stopping at
utilities.

## 0.3.0

Restored the scientific scaffold in substance and readopted the iteration workflow the
original template had: `new_track.py`, `new_iteration.py`, `select_result.py`, and the shared
numbering module.

## 0.2.0

First installable preview. `smairt new` became the only supported generator, with the guided
wizard, the Standard Mode dashboard, framed keyboard screens, action tokens, and
preview-before-write for capabilities, repairs, regeneration, and license changes.
