# ADR 0001: Protect the Generated-Project Surface

Status: Accepted

## Context

The first installed SMAIRT generator replaced a detailed scientific scaffold with a much smaller set of utility assets. The CLI and TUI improved onboarding, but generator and checker expectations came from the same package implementation. Removing an asset from both could therefore pass tests while silently reducing the generated scientific product.

The restored product must retain the installed interface while making scaffold changes explicit and independently reviewable.

## Decision

The meaningful original scaffold is the restoration baseline. During restoration, content changes are limited to installed-CLI compatibility, direct project-file workflows, capability toggles, evidence tracking, and safety corrections.

A readable tracked scaffold blueprint is the authoritative declaration of generated paths, purposes, ownership, and activation conditions. One scaffold module interprets that declaration for generation, checking, inspection, repair, regeneration, and capability activation.

Three complete normalized golden projects independently record representative base, Paper, and HPC output. CI and code review must show scaffold blueprint changes separately from ordinary implementation changes.

The CLI and TUI are adapters over shared project operations. They do not define or replace the scientific scaffold.

Existing projects remain tied to their recorded scaffold version. Package-owned mutation requires an explicit future upgrade flow when versions differ.

## Consequences

- Adding, removing, renaming, reclassifying, or changing the activation of an asset requires a visible blueprint change.
- Generator and checker agreement is insufficient by itself; golden output must also change intentionally.
- The package must include the blueprint and every declared source asset.
- Capability deactivation retains files and changes only project-contract state.
- Scientific content remains readable ordinary files and is not moved into the application or hidden bookkeeping.
