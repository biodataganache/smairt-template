# SMAIRT Toolkit V0.1

Status: ready-for-agent

## Problem Statement

SMAIRT currently provides a valuable scientific-research project template, but creating and configuring a project requires users to understand Cookiecutter, terminal commands, template options, filesystem conventions, and several overlapping workflow concepts.

This creates unnecessary onboarding friction for researchers who are comfortable conducting scientific work but are not experienced software developers. Existing setup choices are technical, some generated documentation and behavior have drifted apart, and the distinction between exploratory and paper-driven projects forces users to make a structural decision too early.

The project maintainers want SMAIRT to become an approachable installed tool without replacing its existing scientific workflow. Researchers should be able to install one command, answer understandable questions, review their choices, and receive a trustworthy project that they can open in their preferred coding assistant.

After creation, users need a small terminal dashboard for managing project metadata and optional capabilities. The dashboard should remain a utility layer over the SMAIRT template. It must not attempt to conduct research, decide scientific next steps, or absorb the separate scientific lifecycle developed in the `smairt-toolkit` fork.

Experienced users need access to additional diagnostics and customization without making the Standard experience overwhelming. Paper and HPC support must be additive and reversible at the configuration level without deleting research artifacts.

## Solution

Create an installable Python application named `smairt` that becomes the recommended way to create and manage SMAIRT projects.

Running `smairt` opens an approachable terminal interface. New users are guided through a linear project-creation wizard with plain-language explanations, visible progress, safe defaults, Back navigation, and an editable final review.

Every generated project remains a readable, file-based SMAIRT research workspace. It receives a versioned `smairt.yaml` project contract and local managed-file bookkeeping so the application can validate and safely maintain tool-owned assets without taking ownership of scientific content.

The application provides two interface experiences:

- **Standard Mode** offers a comprehensive but approachable utility dashboard.
- **Advanced Mode** adds diagnostics, managed-file inspection, explicit convention customization, and lower-level project information.

The dashboard launches or provides guidance for the selected coding assistant, edits project settings, manages collaborators, enables or deactivates Paper and HPC support, changes licenses through a guarded workflow, and runs `Project Check`.

Scientific work continues in the selected coding assistant using the generated SMAIRT instructions and project files. The dashboard does not create hypotheses, infer scientific next steps, execute experiments, or judge research quality.

Paper support becomes an additive capability rather than a permanently separate project type. It can be selected during project creation or enabled later. Its analysis workflow remains separate under a Paper-specific analysis area so enabling it does not restructure exploratory work.

HPC support also becomes an additive capability. It supplies corrected SLURM templates and guidance but does not submit or manage jobs in V0.1.

The existing Cookiecutter interface remains available as a legacy compatibility path. It is moved under a clearly labeled legacy area and consumes the same canonical scaffold assets as the installed generator so the two outputs do not drift.

## User Stories

1. As a researcher, I want to install SMAIRT as one isolated command-line tool, so that I do not need to understand the repository before creating a project.
2. As a macOS, Linux, or WSL user, I want a documented and tested installation path, so that I can start reliably.
3. As a researcher, I want running `smairt` without arguments to open a useful Home screen, so that I do not need to memorize commands.
4. As a first-time user, I want Home to offer project creation prominently, so that the next action is obvious.
5. As a returning user, I want Home to list up to ten recent projects, so that I can reopen work quickly.
6. As a privacy-conscious user, I want recent-project history to remain local, so that project locations are not shared or committed.
7. As a user who moved a project, I want stale recent-project entries removed quietly, so that Home remains useful.
8. As a user with an unlisted project, I want to open it by choosing its folder, so that I can access any valid SMAIRT project.
9. As a new user, I want one question at a time, so that creation does not feel overwhelming.
10. As a new user, I want a progress indicator, so that I know how much setup remains.
11. As a user answering optional questions, I want every wizard screen to advance progress, so that progress behaves predictably.
12. As a user who does not know an optional answer, I want a clear Skip or recommended-default action, so that uncertainty does not block setup.
13. As a user who made a mistake, I want each screen to reassure me that answers can be changed during review, so that I can continue confidently.
14. As a user returning to an earlier screen, I want my answers retained, so that I do not need to restart.
15. As a user ready to create a project, I want an editable review checklist, so that I can correct every answer before files are written.
16. As a user who cancels at review, I want no project files written, so that incomplete setup leaves no clutter.
17. As a user selecting a destination, I want unsafe or non-empty destinations rejected before generation, so that existing work is protected.
18. As a user creating a project, I want the destination exposed only after generation succeeds, so that I never receive a partial workspace.
19. As a researcher, I want a human-readable name and editable slug, so that project identity fits my conventions.
20. As a researcher, I want invalid slugs explained in plain language, so that I can correct them easily.
21. As a researcher, I want to provide a short description, so that collaborators and assistants understand the project.
22. As a researcher whose question is still developing, I want the research question to be optional, so that I do not invent a false commitment.
23. As a researcher with a defined question, I want it included in metadata and generated context, so that framing is preserved.
24. As a researcher, I want to select a broad scientific domain or type my own, so that generated context reflects my work.
25. As an interdisciplinary researcher, I want a Not sure yet domain, so that selection does not block creation.
26. As a primary researcher, I want my name recorded, so that project identity is clear.
27. As a researcher, I want email to be optional and omitted when skipped, so that generated records contain no fake personal data.
28. As a project owner, I want to add collaborators with optional email later, so that collaboration can evolve safely.
29. As a researcher, I want to choose Synthetic, Downloaded/benchmark, or Real data as my starting phase, so that the scaffold reflects my entry point.
30. As a new researcher, I want Synthetic recommended and explained, so that the safest starting point is clear.
31. As a researcher starting later, I want earlier phase directories omitted during creation, so that the initial scaffold is relevant.
32. As a researcher changing phases later, I want current phase metadata updated without deleting directories, so that history remains safe.
33. As a researcher expecting publication, I want to enable Paper support during creation, so that its workspace is ready.
34. As an exploratory researcher, I want to leave Paper support disabled initially, so that the project remains focused.
35. As a researcher whose work becomes publishable, I want to enable Paper support later, so that an early decision does not constrain the project.
36. As a researcher using Paper support, I want paper analyses isolated from exploratory analyses, so that workflows do not collide.
37. As a researcher enabling Paper support later, I want existing work untouched, so that prior analyses are not reinterpreted automatically.
38. As a researcher temporarily not using Paper support, I want to deactivate guidance without deleting files, so that retained work stays safe.
39. As a researcher returning to Paper work, I want safe reactivation, so that retained artifacts remain available.
40. As an HPC user, I want to enable HPC templates during creation or later, so that SLURM guidance is available when needed.
41. As an HPC user, I want generated guidance to reference files that exist, so that onboarding commands are trustworthy.
42. As a researcher not currently using HPC, I want to deactivate guidance without deleting files, so that scripts remain safe.
43. As an HPC user, I want V0.1 not to claim job-management abilities, so that capability boundaries are honest.
44. As a user, I want Paper and HPC choices together on one Optional Capabilities screen, so that setup remains concise.
45. As a researcher, I want to select Zoo Code, Claude Code, OpenCode, Codex, Pi, or Cursor, so that onboarding matches my assistant.
46. As a researcher, I want assistant conventions verified against current official documentation, so that generated instructions are discoverable.
47. As a researcher, I want one canonical AI context document with a thin tool-specific alias, so that guidance does not drift.
48. As a researcher who edits a managed alias, I want SMAIRT to protect my change, so that maintenance does not overwrite it.
49. As a researcher, I want SMAIRT to launch a detected assistant safely or provide exact guidance, so that unavailable tooling does not block access.
50. As a researcher, I want an option to open the project folder, so that I can work without a supported assistant executable.
51. As a project creator, I want plain-language explanations for every license, so that selection is informed.
52. As a project creator, I want MIT recommended but explicitly confirmed, so that defaults do not bypass consent.
53. As a project owner, I want guarded license changes later, so that legitimate evolution is supported.
54. As a project owner changing a license, I want a legal-context warning and preview, so that consequences are visible.
55. As a project owner who edited legal text, I want automatic replacement refused, so that custom terms are protected.
56. As a user with Git, I want initialization recommended but optional, so that project history is convenient without being forced.
57. As a user without Git, I want guidance rather than generation failure, so that I can still create a project.
58. As a Git user, I want files staged but not committed automatically, so that I control project history.
59. As a Git user, I want a suggested first commit command, so that the next step is clear.
60. As a Standard Mode user, I want a comprehensive utility dashboard, so that routine management is approachable.
61. As a Standard Mode user, I want assistant launch, settings, capabilities, Project Check, Help, and Exit, so that common actions are visible.
62. As an Advanced Mode user, I want all Standard actions plus diagnostics and customization, so that added control does not remove convenience.
63. As an Advanced Mode user, I want full metadata and managed-file inspection, so that tool decisions are transparent.
64. As an Advanced Mode user, I want safe regeneration of only unmodified managed assets, so that generated guidance can be restored.
65. As an Advanced Mode user, I want detected Python, Git, and assistant paths, so that environment issues are diagnosable.
66. As a collaborator, I want Standard or Advanced Mode remembered locally per project, so that my preference does not control others.
67. As a user, I want brief animations in interactive terminals and a local motion setting, so that the experience is polished and accessible.
68. As an automation author, I want motion suppressed in redirected and JSON output, so that results remain deterministic.
69. As a researcher, I want Project Check to validate structure without judging science, so that the tool does not overstate authority.
70. As a researcher, I want Project Check to detect metadata, phase, capability, alias, Git, managed-file, and unresolved-token problems, so that structural issues are actionable.
71. As a researcher, I want diagnosis to be read-only before repairs are offered, so that checks never mutate silently.
72. As a researcher, I want selectable, previewed, explicitly confirmed repairs, so that I retain control.
73. As a researcher, I want repairs limited to deterministic tool-owned structure, so that scientific content is never rewritten.
74. As a command-line user, I want stable create, open, check, capability, and version commands, so that common operations are scriptable.
75. As an automation author, I want Project Check JSON and stable exit behavior, so that diagnostics integrate with tooling.
76. As a researcher, I want projects to remain ordinary readable files, so that the installed application is not required to inspect the archive.
77. As a researcher, I want tracked YAML metadata and local hidden bookkeeping, so that shared state is transparent and machine preferences stay private.
78. As a maintainer, I want versioned schemas and managed-file hashes, so that future repairs and migrations can distinguish generated assets from edits.
79. As a maintainer, I want one canonical scaffold asset set, so that installed and legacy generators do not drift.
80. As an existing Cookiecutter user, I want a clearly documented legacy path, so that established automation has a transition route.
81. As a new user, I want `smairt new` recommended, so that legacy complexity is absent from normal onboarding.
82. As a researcher, I want browser-paste artifacts retired and logs canonical, so that guidance reflects file-aware assistants and reproducible records.
83. As a researcher, I want consistent hypothesis and analysis naming, so that scripts and documentation agree.
84. As a user, I want canonical repository links and valid commands, so that onboarding is trustworthy.
85. As a maintainer, I want supported Python and operating-system claims backed by tests, so that release promises are evidence-based.
86. As a contributor, I want focused tests, typing, linting, and formatting during development, so that defects are caught early.
87. As a maintainer, I want full-suite and install smoke tests before release, so that integration failures are caught.
88. As a maintainer, I want work delivered in blocker-ordered tickets and committed frequently, so that progress is auditable.

## Implementation Decisions

- Development occurs on `smairt-lab/smairt-toolkit`, based on `main`, in an isolated worktree.
- The installed package and executable are named `smairt` and target Python 3.11 or later.
- Typer provides stable commands, Prompt Toolkit provides interactive navigation, Rich provides presentation and motion, Pydantic validates models, YAML stores readable metadata, Jinja2 renders canonical scaffold assets, Platformdirs stores user-local state, and Hatchling builds the package.
- V0.1 supports macOS, Linux, and Windows through WSL. Native Windows is deferred.
- The primary installation uses `uv tool install`; `pipx` is the fallback.
- The canonical repository is `PNNL-CompBio/smairt-template`.
- CLI and TUI share project services and durable state; the TUI does not own a separate state machine.
- Project creation uses a temporary sibling directory, validates the result, and exposes it by directory rename.
- Existing non-empty destinations are rejected.
- Every project contains a tracked, versioned `smairt.yaml` contract.
- Project metadata records schema/scaffold versions, identity, immutable slug, description, optional research question, domain, people, assistant, phase, license, Git choice, and Paper/HPC capability state.
- Paper and HPC state distinguishes never enabled, enabled, and inactive after prior enablement.
- Capability deactivation changes configuration and guidance but never deletes generated files.
- Starting phase controls initial directories. Later phase changes never delete project directories.
- Tool-owned files are hashed in a Git-ignored local managed-file manifest. Scientific artifacts are never tool-owned.
- Experience and animation preferences are local per project checkout and Git-ignored.
- Recent Projects is user-local, contains paths and timestamps only, and is capped at ten.
- The wizard is linear, retains answers on Back, counts every screen toward progress, and writes nothing before final confirmation.
- Domain offers broad categories, custom text, and Not sure yet.
- Paper and HPC share one Optional Capabilities screen and default off.
- Supported assistants are Zoo Code, Claude Code, OpenCode, Codex, Pi, and Cursor.
- Assistant instruction and launch conventions must be verified against current official documentation.
- Canonical AI guidance remains tool-neutral; selected assistants receive thin managed pointers, not duplicated instructions or symlinks.
- SMAIRT never installs assistants automatically.
- MIT is recommended but explicitly confirmed; all license choices receive plain-language explanations.
- License changes use a warning, preview, and confirmation and refuse to overwrite modified legal text.
- Git initialization is optional, initializes and stages files, and never commits automatically.
- Standard Mode offers assistant launch/open, Project Settings, Paper support, HPC support, Project Check, Help, and Exit.
- Advanced Mode adds metadata and managed-file inspection, verbose checks, safe managed-asset regeneration, convention customization, and detected tool paths.
- The dashboard never creates research artifacts, infers scientific next steps, executes experiments, or assesses scientific quality.
- Paper support adds a Paper workspace, Paper guidance and helpers, and a separate Paper analysis area without converting exploratory work.
- HPC support adds corrected SLURM templates and guidance only.
- Project Check is read-only until a user selects, previews, and confirms safe deterministic repairs.
- Repairs never delete artifacts, overwrite modified research content, or alter scientific meaning.
- Stable commands cover Home/dashboard, new, open, check with JSON, Paper enable/disable, HPC enable/disable, and version.
- Labels use consistent title capitalization, including Project Check, Standard Mode, and Advanced Mode.
- Interactive TTYs animate by default; redirected, test, CI, dumb-terminal, and JSON output does not.
- Browser-paste/session-log mode is removed from the canonical workflow, logs are canonical, and hypothesis/analysis naming is normalized.
- Stale links, commands, mode claims, Paper assumptions, HPC references, fake email defaults, and the unused example setting are corrected.
- Legacy Cookiecutter is clearly secondary but remains functional and consumes the same canonical scaffold assets.
- Existing projects without `smairt.yaml` are not adopted or migrated in V0.1.
- Delivery uses five blocker-ordered tracer-bullet tickets. Each is implemented in a fresh context, tested and reviewed, and committed before the next ticket.

## Testing Decisions

- Good tests verify externally observable behavior through public interfaces and durable outputs, not private helpers or internal wiring.
- The primary seam is the installed `smairt` command: CLI/TUI input, visible output, exit status, JSON, and resulting project filesystem.
- The compatibility seam is the legacy Cookiecutter entry point, compared against canonical generator behavior for equivalent inputs.
- Package installation is verified in clean-environment smoke tests.
- Interactive tests use real terminal input streams where practical rather than mocking prompt internals.
- Creation coverage includes Back retention, progress, optional skips, validation, review editing, cancellation, confirmation, destination safety, and atomic exposure.
- Generation coverage includes each starting phase and Paper/HPC combinations with independently specified expected outputs.
- Managed-file tests prove researcher edits are protected.
- Capability tests cover initial and later enablement, non-destructive deactivation, retained artifacts, reactivation, and idempotency.
- Paper tests verify the separate Paper analysis area and preservation of exploratory work.
- HPC tests verify templates and guidance without scheduler behavior.
- Assistant tests cover canonical guidance, each verified thin alias, and controlled launch detection.
- License tests cover every license and guarded changes, including modified-file refusal.
- Git tests cover available, missing, declined, initialized, staged, and no-automatic-commit cases.
- Home/dashboard tests cover project detection, recents, stale paths, Standard/Advanced Mode, local preference persistence, and navigation.
- Project Check tests cover human and JSON output, exit behavior, metadata, phase/capability consistency, aliases, unresolved tokens, and managed files.
- Repair tests prove no mutation before selection, preview, and confirmation and no overwrite or deletion of scientific content.
- Motion tests prove interactive defaults and deterministic non-interactive output.
- Legacy tests prove compatibility without a divergent scaffold copy.
- Existing generation-level integration tests are prior art; the new suite retains that high seam and extends it through the installed application.
- CI runs formatting, linting, strict type checking, focused tests, the full suite, builds, and installation smoke tests on Python 3.11-3.13 and Ubuntu/macOS.

## Out of Scope

- The fork's scientific state machine, evidence cards, claims, immutable run bundles, scientific transition enforcement, or approval gates.
- Automatic research planning, scientific next-step recommendations, or dashboard creation of hypotheses, experiments, analyses, or reports.
- Running experiments or judging research validity, novelty, quality, or reproducibility.
- Literature providers, API keys, Zotero, external research services, MCP, full harness adapters, hooks, or permission systems.
- Automatic assistant installation.
- HPC submission, monitoring, cancellation, synchronization, SSH orchestration, or cluster profiles.
- Data classification, compliance, safety, provenance, evidence graph, retrieval, memory, or hosted services.
- Native Windows support.
- Existing-project adoption or migration.
- Automatic conversion of exploratory work into Paper analyses.
- Destructive capability disablement.
- Automatic commits or remote repository creation.
- Slug/folder rename after creation.
- Arbitrary YAML editing or arbitrary shell execution.
- Removing legacy Cookiecutter during V0.1.
- PyPI publication unless separately approved.
- Claims of legal, regulatory, institutional, clinical, security, or scientific certification.

## Further Notes

- The branch and isolated worktree already exist.
- The specification and its generated tickets use the local Markdown tracker and `ready-for-agent` status.
- Implementation should proceed blockers-first, with bounded subagent parallelism only after core interfaces are fixed.
- Repository/package licensing must be resolved before a public package release; generated-project license selection is separate.
