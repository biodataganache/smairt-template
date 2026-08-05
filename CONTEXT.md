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
| Screen | One unit of terminal interaction presenting a title, a body, and the controls available. Screens replace one another rather than accumulating. |
| Framed screen | A screen drawn as a bounded region that repaints in place, never entering the alternate screen and never exceeding the terminal's height. |
| Semantic palette | The single style definition naming interface roles rather than colors, shared by framed screens and printed output, expressed in the terminal's own colors. |
| Action token | The stable name identifying a menu action. Tokens are the addressing contract; displayed numbers are a renumberable convenience. |
| Capability selection | A multi-selection of optional capabilities in which a deliberate none is mutually exclusive with any capability. |
| Diff preview | The statement of exactly which changes an operation would make, derived from the operation itself and shown before anything is written. |
| Scaffold upgrade | Moving a project onto the installed scaffold version. Rewrites tool-owned guidance, creates missing declared assets, and preserves researcher work and modified editable starters. |

## Core Relationships

- The scaffold blueprint declares scaffold assets.
- A generated project materializes all always-active scaffold assets and any enabled capability assets.
- The project contract records starting phase, current phase, and capability state.
- Package-derived checks compare tool guidance with the installed scaffold version while preserving modifications.
- Golden projects independently record complete representative generated output.
- Framed screens and printed output both derive their styling from the semantic palette.
- A capability selection produces a diff preview, and only an explicit confirmation applies it.
- Creating a project and managing one are separate modules that meet only at the command surface: `wizard.py` creates, `dashboard.py` manages, `presentation.py` holds what both need to speak the same way, and `cli.py` is the adapter over them.

## Invariants

- The installed `smairt` command is the only supported generator.
- Every generated project contains all synthetic, downloaded-data, and real-data phase directories.
- Generated Markdown must explain the scientific workflow without requiring external skills.
- Capability activation creates missing starters only.
- Capability deactivation changes contract state only.
- Researcher work is never overwritten, regenerated, or semantically assessed.
- A scaffold-version mismatch blocks package-owned mutations, and every refusal names the upgrade that resolves it.
- A scaffold upgrade never reads, rewrites, or judges researcher work, and preserves a modified editable starter.
- Every command a researcher is told to run must exist on a supported platform without extra setup.
- A project created successfully passes its own Project Check.
- An iteration may only reference a hypothesis file that exists, so the number joining hypothesis, script, log, and analysis always resolves.
- No failure reaches a researcher as a traceback or as library-formatted output.
- Interactive presentation never enters the alternate screen and never exceeds the terminal's height.
- Color is never the only signal; markers and words carry every meaning color carries.
- A diff preview reflects the operation that would run, never a fixed description of it.
- Every finite choice is addressable by a stable action token without a capable terminal.
