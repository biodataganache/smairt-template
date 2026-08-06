# Decide whether Run History is a declared scaffold asset

Type: grilling
Status: resolved
Blocked by: None

## Question

Should `analysis/RUN_HISTORY.md` be a declared scaffold asset created with every generated project, or an intentionally emergent researcher-work record created by the first iteration run?

## Known friction

- `analysis/ITERATION_LOG.md` is declared in the scaffold blueprint and exists at project creation.
- `scripts/shared/iterations.py` silently creates `analysis/RUN_HISTORY.md` on first execution.
- Because Run History is undeclared, Project Check, inspect, upgrade, and scaffold documentation do not treat it as part of the generated-project surface.
- The record is append-only scientific provenance, so its ownership and lifecycle must be explicit. Do not expose helper internals merely to make this testable: the chosen module interface should be the test surface.

## Resolution

Choose and document one lifecycle, ownership category, upgrade behavior, and test surface. If declared, identify the blueprint and golden-project changes. If emergent, explain why emergence is part of the interface and where a researcher learns that fact. Add the decision to current documentation before historical plans are removed.

## Answer

**Declared, as `researcher-work`, shipping with every project.**

Emergence was the weaker option once ADR 0001 is taken seriously: the blueprint is the
*authoritative* declaration of generated paths, and a file that appears in a project without
the blueprint knowing about it is a second, quieter definition of what a project contains.
Run History is not incidental output — the scaffold calls it part of the evidence, and says a
traceback that appeared only in a terminal is not evidence. A record with that job should not be
invisible to `check`, `inspect`, and `upgrade`.

Ownership is `researcher-work`, matching `ITERATION_LOG.md`: scientific provenance SMAIRT
writes on the researcher's behalf but never reads, judges, or rewrites. Upgrade creates it when
absent and never touches it once present.

`record_run_status()` still recreates the header if the file is missing. That is not dead code:
losing the header should not also lose the ability to record runs, and a researcher who deletes
it mid-study gets appends anyway. The interface is unchanged; only the file's declared status is.

### Two defects found while resolving this

An unquoted comma inside the new asset's `purpose` split the YAML flow mapping into extra keys,
so `load_blueprint()` raised and every generation failed. Two things followed:

1. **The golden updater deleted all three fixtures.** It removed each golden *before* generating
   its replacement, so one malformed line destroyed every fixture and left nothing behind. It now
   proves the installed command is usable before deleting anything.
2. **Nothing asserted the blueprint was loadable.** Tests checked what it said, never that the
   package could read it. A test now does, ahead of its contents.

The failure surfaced as plain language rather than a traceback — `assets.18.its status: is not a
setting SMAIRT recognizes` — so the error boundary did its job on a defect it was never written
for.

### Verification

- Ships with new projects; two consecutive runs append distinct log paths with no duplicated header.
- A `0.4.0` project reports the mismatch, `upgrade` previews creating exactly this file, and the
  project passes its own check afterwards.
- A test asserts every file the helpers create is declared — the class, not this instance.
- 187 pass, up from 185. Format, lint, strict mypy green.
