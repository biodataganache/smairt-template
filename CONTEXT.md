# SMAIRT Domain Context

SMAIRT creates and manages readable, file-based scientific research workspaces.

## Glossary

| Term | Meaning |
|---|---|
| Generated project | The research workspace produced by `smairt new`. |
| Project contract | The tracked `smairt.yaml` record describing project identity, provenance, current status, and optional capabilities. |
| Scaffold | The files and directories SMAIRT supplies to start a generated project. |
| Scaffold blueprint | The tracked declaration of the scaffold's protected paths, purposes, ownership, and activation conditions. |
| Scaffold asset | One generated file or required directory declared by the scaffold blueprint. |
| Tool guidance | Package-maintained instructions or helpers. Researcher modifications are reported and preserved. |
| Editable starter | An initial artifact intended for researcher editing. Its content is not enforced after creation. |
| Researcher work | Scientific content owned entirely by the researcher and never regenerated or judged by SMAIRT. |
| Historical reference | Archived material that does not participate in active generation or project checks. |
| Golden project | A checked-in normalized generated project used as an independent expected-output record. |
| Starting phase | Immutable provenance recording where a project began. It does not control which phase directories exist. |
| Current phase | Mutable project status indicating the phase receiving current attention. It does not control which phase directories exist. |
| Capability | An additive optional guidance bundle, currently Paper or HPC. Deactivation never removes retained files. |

## Core Relationships

- The scaffold blueprint declares scaffold assets.
- A generated project materializes all always-active scaffold assets and any enabled capability assets.
- The project contract records starting phase, current phase, and capability state.
- Package-derived checks compare tool guidance with the installed scaffold version while preserving modifications.
- Golden projects independently record complete representative generated output.

## Invariants

- The installed `smairt` command is the only supported generator.
- Every generated project contains all synthetic, downloaded-data, and real-data phase directories.
- Generated Markdown must explain the scientific workflow without requiring external skills.
- Capability activation creates missing starters only.
- Capability deactivation changes contract state only.
- Researcher work is never overwritten, regenerated, or semantically assessed.
- A scaffold-version mismatch blocks package-owned mutations until an explicit upgrade flow exists.
