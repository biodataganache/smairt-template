# Scientific Scaffold Restoration

Status: ready-for-agent

## Problem Statement

The installable SMAIRT CLI and TUI replaced much of the original generated scientific workspace with a smaller utility scaffold. Although the installed tool improved project creation and management, the migration silently removed detailed hypotheses, analysis, reporting, prompt, Paper, HPC, provenance, and helper guidance that researchers relied on.

The current generator and checker derive their expectations from the same package assets. A future change can therefore remove an asset from both implementations without an independent test noticing. The generated-project product surface is also encoded across template discovery, Python dictionaries, phase rules, and capability checks, making ownership and activation rules difficult to review.

Researchers need the complete scientific workflow restored without losing the installed CLI, TUI, project contract, atomic generation, dashboard, capability management, or safe project checks. Maintainers need an explicit and independently verified definition of the generated project so future refactors cannot silently repeat the loss.

## Solution

Restore the meaningful original scientific scaffold as the baseline for every generated project, with only the compatibility and safety changes required by the installed SMAIRT workflow.

Every project receives the complete synthetic, downloaded-data, and real-data phase structure. The starting and current phase remain provenance and status fields rather than directory filters. Detailed local Markdown makes the project understandable without external skills. Assistants read project files and execution logs directly; browser-paste and session-transfer compilation are retired.

Paper and HPC remain optional additive capabilities. Enabling them safely creates missing starter files. Deactivating them changes project state only and never moves or deletes retained files. Re-enabling preserves all researcher changes.

Introduce a readable scaffold blueprint that records each generated path's purpose, ownership, and activation condition. A single blueprint module uses this declaration for generation, checks, inspection, repair, and capability activation. Independently checked full-text golden projects protect representative base, Paper, and HPC outputs. CI presents intentional blueprint changes as a dedicated added, removed, renamed, ownership, or condition diff.

## User Stories

1. As a researcher, I want a generated project to contain the complete SMAIRT scientific workflow, so that the installed tool does not trade scientific guidance for interface convenience.
2. As a researcher, I want detailed hypotheses guidance, so that I can state assumptions, predictions, alternatives, and rejection criteria before experiments.
3. As a researcher, I want detailed analysis guidance, so that results, limitations, decisions, and follow-up work remain connected.
4. As a researcher, I want a reusable study-report template, so that I can create a living synthesis at a major checkpoint rather than receiving an empty report prematurely.
5. As a researcher, I want all phase folders present from project creation, so that moving between synthetic, downloaded, and real data does not require structural migration.
6. As a researcher, I want starting phase recorded independently from current phase, so that provenance is preserved while work advances.
7. As a researcher, I want data folders to contain tracked provenance and inventory guidance while data files remain ignored by default, so that data lineage survives without committing datasets accidentally.
8. As a researcher, I want normal text logs tracked by default, so that execution evidence survives commits and clones.
9. As a researcher, I want ordinary text summaries and figures trackable by default, so that useful evidence is not silently excluded from version control.
10. As a researcher, I want to explicitly ignore sensitive or large outputs when needed, so that default traceability does not override project-specific constraints.
11. As a researcher, I want generated Markdown to stand alone, so that the workflow remains understandable before project-local skills are introduced in a future version.
12. As an assistant, I want complete local context and conventions, so that I can work from project files without browser-paste packages.
13. As an assistant, I want session-start and review guidance to point to current project files and logs, so that handoffs use durable evidence.
14. As a researcher, I want one scientific workflow with optional Paper support, so that publication planning does not create a competing project mode.
15. As a researcher, I want Paper support to add outline, analysis, draft, reviewer-feedback, figure, iteration-review, and provenance guidance, so that publication work remains tied to research evidence.
16. As a researcher, I want a Paper final manifest that maps claims and figures to evidence, so that manuscript assertions remain auditable.
17. As a researcher, I want Paper deactivation to retain every file in place, so that no publication work is moved or lost.
18. As a researcher, I want Paper reactivation to restore only missing starters, so that my edits are never overwritten.
19. As an HPC user, I want detailed configuration, logs, and SLURM template guidance, so that cluster execution is reproducible.
20. As an HPC user, I want SMAIRT to avoid claiming scheduler-management capabilities it does not provide, so that guidance is trustworthy.
21. As an HPC user, I want HPC deactivation and reactivation to preserve files exactly like Paper support, so that cluster work remains safe.
22. As a researcher, I want an experiment-script helper aligned with all phase folders, so that numbered scripts are created consistently.
23. As a researcher, I want stdout, stderr, warnings, and uncaught tracebacks in execution logs, so that failures are diagnosable from durable records.
24. As a researcher, I want a non-destructive monitoring template, so that long-running work can expose progress without SMAIRT managing processes or jobs.
25. As a researcher, I want a non-destructive summary and manifest helper, so that I can inventory existing evidence without rewriting it.
26. As a researcher, I want retired destructive or browser-oriented helpers kept out of active projects, so that obsolete workflows are not accidentally used.
27. As a maintainer, I want every scaffold asset assigned an ownership type, so that checks and repairs treat tool guidance, editable starters, researcher work, and historical reference differently.
28. As a maintainer, I want a readable tracked blueprint, so that generated-project changes are reviewable without tracing Python code.
29. As a maintainer, I want each blueprint entry to state its purpose, source, condition, and ownership, so that deletion and replacement decisions are explicit.
30. As a maintainer, I want one deep scaffold module, so that creation, checks, repairs, inspection, and capabilities use the same rules.
31. As a maintainer, I want the CLI and TUI to remain adapters over shared project operations, so that interface changes cannot redefine the scaffold.
32. As a maintainer, I want full normalized golden projects, so that generator and checker agreement cannot hide accidental asset deletion.
33. As a reviewer, I want representative base, Paper, and HPC golden projects, so that conditional output is visible as ordinary text.
34. As a reviewer, I want a dedicated blueprint diff, so that added, removed, renamed, ownership, and condition changes are prominent.
35. As a maintainer, I want a transition record for every meaningful original file, so that restored, replaced, and retired assets have an auditable disposition.
36. As a maintainer, I want operating-system junk excluded from the historical completeness claim, so that `.DS_Store` is not treated as product content.
37. As a maintainer, I want scaffold-version mismatches to block package-owned mutation, so that an installed version cannot silently rewrite an older project.
38. As a researcher, I want scaffold upgrades to require an explicit future upgrade flow, so that existing projects remain frozen until reviewed.
39. As a researcher, I want project checks to avoid judging scientific content, so that the tool validates structure and ownership only.
40. As a researcher, I want modified guidance and editable starters preserved, so that checks report differences without overwriting work.
41. As a maintainer, I want the restored scaffold packaged in wheels and source distributions, so that installed generation matches repository tests.
42. As a maintainer, I want isolated installation smoke tests to generate representative projects, so that missing package data is caught before release.
43. As a contributor, I want normal code review to approve scaffold changes with clear generated diffs, so that no special approval system is required.
44. As a future contributor, I want domain terms and an architectural decision record, so that the installed interface is not mistaken for the scientific product surface again.

## Implementation Decisions

- The original generated scaffold is the restoration baseline. Scientific content is preserved in full unless a compatibility or safety correction is necessary.
- The installed `smairt` command is the only supported generator. Cookiecutter remains historical reference material only.
- Project modes are retired. Every project follows one research workflow; Paper is an additive capability.
- Browser-paste and compiler workflows are retired. Generated guidance directs assistants to project files and tracked logs.
- Every project contains all synthetic, downloaded-data, and real-data phase directories. Starting phase is immutable provenance; current phase is mutable status and guidance.
- The study-report template is always generated. A living study report is created later at a researcher-requested checkpoint.
- Root analysis planning, breadcrumb, and repository-planning starters are always generated.
- Paper-specific files include the final provenance manifest, Paper workspace guidance, outline, analysis, drafts, reviewer feedback, initial prompt, figure guidance, and iteration-review guidance.
- The duplicate historical Paper draft directory is retired.
- HPC-specific files include detailed workspace guidance, editable configuration, log guidance, a basic SLURM template, and an editable job script. No scheduler management is claimed.
- Capability deactivation changes contract state only. Retained files remain visible and untouched. Inactive capability files are not treated as active guidance by checks.
- Capability activation and reactivation write missing files only.
- Four ownership types define behavior: tool guidance, editable starter, researcher work, and historical reference.
- Tool guidance is package-maintained but researcher modifications are reported and preserved.
- Editable starters may be changed freely and are restored only when missing and explicitly requested.
- Researcher work is never generated over, rewritten, or semantically assessed.
- Historical reference never participates in active generation or checks.
- A readable tracked blueprint is the authoritative asset declaration. Entries include path, purpose, ownership, activation condition, source, and whether the path is a file or directory.
- A single scaffold module loads and validates the blueprint, renders assets, computes active assets, materializes missing assets, and exposes expected assets to checks and inspection.
- Initial generation, safe capability activation, project checking, repair previews, repairs, inspection, and regeneration consume the scaffold module rather than maintaining separate asset dictionaries.
- Template files remain package resources. Python files are copied byte-for-byte; text templates are rendered with strict undefined-variable handling.
- Normal logs, text summaries, and ordinary figures are tracked by default. Dataset contents, local preferences, environments, caches, and operating-system junk are ignored by default.
- Data README files serve as tracked provenance and inventory records.
- The active helper set consists of experiment creation, shared logging, progress monitoring, and non-destructive manifest generation.
- Browser compiler and destructive or obsolete iteration helpers remain archived only.
- Existing projects are never automatically upgraded. Scaffold-version mismatch reporting and mutation guards remain in force.
- The package and scaffold version advance together for this restoration.
- Domain vocabulary and an architectural decision record capture the generated-project product surface and independent verification requirement.
- A transition record classifies every meaningful original asset as restored, replaced, or retired and documents compatibility corrections.
- Three deterministic full-text golden projects represent base synthetic research, real-data research with Paper, and downloaded-data research with HPC.
- Golden fixtures normalize time- and machine-dependent values while preserving complete generated file contents.
- A dedicated blueprint comparison reports added, removed, renamed, ownership-changed, and condition-changed entries during review and CI.

## Testing Decisions

- Good tests observe public command behavior, exit status, project contracts, and generated files rather than private implementation details.
- The primary test seam is the installed `smairt` command. Creation and management commands produce durable workspaces that tests inspect.
- Existing installed-command integration tests are prior art and remain the primary suite.
- Blueprint validation tests prove every active file source exists, every ownership and condition is valid, paths are unique, and required directories are declared.
- Generation tests prove all phases exist for every starting phase while starting and current phase metadata retain the selected value.
- Capability tests prove independent creation, non-destructive deactivation, preserved modifications, missing-starter restoration, reactivation, and idempotency.
- Ownership tests prove modified tool guidance is reported but preserved, editable starter changes are accepted, missing editable starters can be explicitly restored, and researcher work is not managed.
- Logging tests execute a generated script and prove stdout, stderr, warnings, and uncaught traceback text are retained.
- Helper tests exercise command help and representative non-destructive behavior from a generated project.
- Golden tests generate projects through the installed command and compare every normalized file and directory against checked-in fixtures.
- Golden tests compare full content rather than only file lists.
- Blueprint diff tests verify clear categories for additions, removals, renames, ownership changes, and condition changes.
- Release tests inspect built wheel and source-distribution contents for the blueprint, templates, and helper scripts.
- Isolated smoke tests install both artifacts and generate representative projects.
- CI continues to run formatting, linting, strict typing, tests, builds, and isolated artifact smoke tests.

## Out of Scope

- Automatic migration or upgrade of existing projects.
- Turning generated context or workflow documents into project-local skills; that work belongs on a later branch.
- A scientific state machine, scientific approval gates, or automated research decisions.
- Creating hypotheses, analyses, reports, manuscript claims, or figures on behalf of the researcher.
- Judging scientific validity, quality, novelty, or reproducibility.
- HPC submission, cancellation, monitoring, synchronization, SSH orchestration, or scheduler management.
- Restoring browser-paste compilation, separate workflow modes, or separate Paper project modes.
- Restoring destructive iteration-finalization helpers.
- Restoring the duplicate Paper draft directory, the single-user practice guide, or operating-system metadata.
- Special maintainer approval rules beyond normal code review and visible scaffold diffs.
- PyPI publication.

## Further Notes

- The restoration follows recovery commit `9b56735` and the decisions documented in the adversarial migration review.
- The meaningful historical scaffold remains available under the legacy archive for comparison.
- The installed CLI and TUI, project contract, atomic generation, dashboard, capability state, package-derived checking, and explicit version guard must remain intact.
- The implementation should use small auditable commits and push each completed checkpoint to the active branch.
