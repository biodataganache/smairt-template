# Decide whether Run History is a declared scaffold asset

Type: grilling
Status: unclaimed
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
