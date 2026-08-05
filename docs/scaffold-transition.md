# Scientific Scaffold Transition Record

## Scaffold version 0.3.0

The re-enrichment and the readopted iteration workflow both changed what a generated
project contains while `scaffold_version` stayed at `0.2.0`. Since
[`project_check()`](../src/smairt/project.py:588) decides whether a project is current by
comparing that string to the installed version, a project generated before those changes
and one generated after were indistinguishable, and the check reported a stale project as
current.

`0.3.0` rather than `0.2.1` because the blueprint gained five declared assets and the
workflow gained a vocabulary. A researcher on `0.2.0` following current documentation would
look for `analysis/ITERATION_LOG.md` and three helpers their project does not contain. That
is a change in what a project is, not a fix.

Consequence, verified rather than assumed: a `0.2.0` project is now told
`scaffold-version-mismatch`, and capability changes, repair, and regeneration refuse. That is
the behavior [ADR 0001](adr/0001-protect-generated-project-surface.md:21) specifies, and the
bump is what makes it reachable.

> **Superseded.** This section originally continued: "A researcher holding a `0.2.0` project
> who wants the current workflow should generate a new project; there is no migration." That
> answer does not survive contact with a study already under way. See
> [Scaffold upgrades](#scaffold-upgrades) below; `smairt upgrade` is now the route, and the
> refusals name it.

The version string used to appear in ten files, three of them load-bearing. That is no longer
true: `pyproject.toml` is the only place a version is written, `__version__` reads the
installed distribution metadata, and `scaffold_version` derives from `__version__`. CI, the
README, and CONTRIBUTING select build artifacts by kind rather than by filename.

This record accounts for the meaningful files recovered from the original Cookiecutter scaffold. `results/.DS_Store` is intentionally excluded as operating-system metadata.

## Scaffold version 0.4.0 and final remediation gate

Stages A through H changed the generated project's workflow contracts after the `0.3.0`
transition: one numbering authority, append-only outcome history, structural result selection,
self-contained provenance, project-level rigor declarations, and a dashboard handoff into the
recorded workflow. The package and scaffold therefore move together to `0.4.0`. This is the
single version bump for that remediation sequence. Migration is now available separately; see
[Scaffold upgrades](#scaffold-upgrades).

Stage I makes the corrected properties falsifiable. The guard suite now includes the write
path that a destructive-call scan alone misses: a shipped helper containing `write_text` must
either use the shared refusing writer or visibly check that its destination does not exist.
The three normalized golden projects were regenerated after the version bump.

The release gate passed on 2026-08-05:

- `ruff format --check`: 61 files already formatted;
- `ruff check`: no findings;
- strict `mypy`: no findings in 27 source files;
- complete `pytest`: 123 tests passed;
- blueprint diff from the pre-remediation scaffold: five intended additions, removal of
  `scripts/new_script.py`, and the intended `scripts/shared` ownership change; no renames or
  condition changes;
- package build: `smairt-0.4.0-py3-none-any.whl` and `smairt-0.4.0.tar.gz` built;
- isolated wheel and source-distribution smoke installs: both passed;
- installed-wheel end to end: created a Paper project, started a track, created and ran an
  iteration, wrote its interpretation, recorded its outcome, selected it into
  `FINAL_MANIFEST.md`, and finished with an empty `smairt check --json` issue list.

## Scaffold upgrades

`smairt upgrade` is the explicit upgrade flow [ADR 0001](adr/0001-protect-generated-project-surface.md:21)
deferred. It closes a defect that shipped: tying a project to its recorded scaffold version is
correct, but with no route forward the tool went read-only the moment it was updated. A project
created by `0.3.0` and opened with `0.4.0` could not change its phase, enable a capability,
repair a missing directory, or regenerate an asset. The only documented answer was to start a
new project, which is not an answer for a study already months in.

The flow previews, then writes only on `--confirm`:

```bash
smairt upgrade /path/to/project            # preview; writes nothing
smairt upgrade /path/to/project --confirm  # apply
```

What it does, and deliberately does not do:

| Asset ownership | On upgrade |
|---|---|
| `tool-guidance`, unmodified | Rewritten to the installed version |
| `tool-guidance`, modified | Rewritten; the package owns this text |
| `editable-starter`, differing | **Kept as it is** |
| `researcher-work` | Never read, rewritten, created, or judged |
| Missing `tool-guidance` asset | Created |
| Any path resolving outside the project | Reported and never touched |

An editable starter that differs from the installed text is kept rather than rewritten, and
the preview says only that it differs. It deliberately does not claim the researcher modified
it: across a real release the newer scaffold may have changed the starter itself, and SMAIRT
cannot distinguish that from an edit. Keeping the file is correct under either reading, so the
wording states the observation and not a conclusion about who made the change.

Verified against a real release rather than a simulated one: a `0.3.0` project was created with
a genuine `0.3.0` install, carried through a track, two iterations, a run, and an
interpretation, then upgraded with the current build. Fifteen tool-guidance files were rewritten
and three created, including the `record_outcome.py` helper `0.3.0` never shipped. Every
researcher artifact — hypothesis, both scripts, the run log, the analysis, the plan, and the
iteration log — was byte-identical afterward, and the project then passed `smairt check` and
accepted the settings and capability changes the mismatch had blocked.

The preview is rendered from the same projected contract the write uses, so it cannot describe
a different operation, and the upgrade writes nothing the preview did not list. An earlier
version finished with a general materialize pass that created every missing active asset,
including the blueprint's `researcher-work` records — so a researcher who had deliberately
deleted `analysis/BREADCRUMB_TRAIL.md` silently got a fresh template back from an operation
whose preview never named the file. A preview that omits a write is not a preview.

Containment is checked per path, not assumed from the blueprint. Blueprint paths are validated
as lexically safe, which says nothing about the filesystem: any managed file or parent directory
can be replaced with a symbolic link, and writing follows both. Pointing `docs/12_STEPS.md` at
an unrelated file and upgrading destroyed that file. Such paths are now reported as resolving
outside the project and never read or written, including dangling links, which could otherwise
be used to create a file elsewhere.

Each asset is written to a temporary neighbour and moved into place, so a full disk or a killed
process cannot leave a truncated guidance file. The contract is saved last, so an interrupted
upgrade stays on its old version and the same command can simply be run again.

Every refusal now names the route. `smairt check` reports the mismatch and says what to run,
and the two commands that previously misreported their state were corrected: `smairt repair`
printed `No safe repairs are available` and exited `0` while every repair was blocked, and
`smairt regenerate` listed all forty-three managed assets as eligible before refusing on
`--confirm`. `tests/test_upgrade.py` holds each of these properties, including that researcher
work and an edited starter survive an upgrade byte for byte.

## Content fidelity

"Restored at same path" describes the path only. For a period it stood in for
"restored in substance" and hid a real gap: the paths existed while the guidance
they promised did not. Across the retained assets, content moved from **29 percent**
of the legacy original to **69 percent**.

Byte ratio is a detection heuristic, not the acceptance criterion. Acceptance is
whether an asset explains its subject well enough to stand alone. Several assets are
deliberately shorter than their originals because the originals documented retired
tooling; those are listed as rewritten rather than restored.

| Disposition | Meaning |
|---|---|
| Restored | Legacy content carried over, with legacy selections resolved to the branch current behavior always takes. |
| Rewritten | Legacy content described retired tooling or a layout that no longer exists, so the passage was rewritten to current behavior. |
| Repaired successor | The current asset is a corrected implementation rather than a thinned copy, and the original is not a recovery source. |

Assets rewritten rather than restored, and why:

| Asset | Reason |
|---|---|
| `paper/FINAL_MANIFEST.md` | Described itself as automatically updated by the retired `finalize_iteration.py`. |
| `analysis/REPOSITORY_PLAN.md` | Listed retired helpers and mapped paper elements to an iteration tree that no longer exists. |
| `hpc/README.md` | Pointed at a `submit_job.py` and a `slurm_gpu.sh` that were never part of this scaffold. |
| `hpc/config.yaml` | Interpolated a researcher email that is optional; the notifications block is kept with an empty value the researcher fills in. |
| `hpc/logs/README.md` | Referenced a per-iteration `NOTES.md` layout that no longer exists. |
| `prompts/session_log.md` | Was a browser-paste transcript store; it is now a durable decision index. |
| `experiments/02_downloaded/README.md`, `experiments/03_real_data/README.md` | Selected prose on `starting_phase`; all three phases are now always present. |
| `scripts/monitor_template.py` | Repaired successor. The original hardcoded placeholder constants instead of accepting arguments. |

The re-enrichment is complete. No generated asset now references a retired helper or
concept, and `tests/test_scaffold_content.py` fails if one reappears.

The eight assets that could not be copied were written rather than restored, because
their originals documented tooling that no longer exists:

| Asset | Why it was written rather than copied |
|---|---|
| `docs/12_STEPS.md` | The original's step 7 was a page on the retired `compile_for_ai.py`, and its ten steps were a filing discipline rather than the reasoning sequence the loop now follows. Rewritten so each step names its decision owner, what each party does, and the file that records it. |
| `prompts/CONTEXT_INDEX.md` | Nine task tables were sound; the cross-tool transfer section instructed a researcher to run the retired compiler. |
| `prompts/00_priming_prompts.md` | Now carries the merged content of `SESSION_START.md` as one prompt per situation. |
| `prompts/README.md` | Listed three prompt files with overlapping descriptions, which is what allowed them to drift. Each file's job is now stated. |
| `scripts/README.md` | The original documented four helpers that are retired. Rewritten for the four that exist, with every command verified against a generated project. |
| `README.md` | The original's file tree and browser-paste section described a layout and workflow that no longer exist. |
| `analysis/README.md` | Labelled three files as belonging to a workflow mode that was retired. |
| `results/logs/README.md` | Described logs as feeding the retired compiler. |

## Merged assets

`prompts/SESSION_START.md` is merged into `prompts/00_priming_prompts.md` and no longer
declared in the blueprint. Both files held ready-made prompts and were not
distinguishable in practice, which is how they drifted apart. `prompts/CONTEXT_INDEX.md`
remains separate because it answers a different question: which files to open for a
given task, rather than what to say.

This is the one structural change in the re-enrichment. Existing projects keep their
copy of the file; an undeclared file does not fail `smairt check`, so nothing breaks.

## Readopted iteration workflow

The original template had three workflow helpers that the first installed version
dropped: `new_experiment.py`, `new_iteration.py`, and `finalize_iteration.py`. Their jobs
were sound; their implementations were welded to a nested
`analysis/<section>/iterations/iter_XX/` tree with a parallel `final/` snapshot, and
`finalize_iteration.py` deleted prior results with `shutil.rmtree`.

Dropping them left a real gap. `new_script.py` covered only script numbering, and nothing
recorded what an iteration was or how attempts related to each other.

The jobs are readopted against the current structure rather than the original one.

| Helper | Job it restores | What changed |
|---|---|---|
| `scripts/new_track.py` | Start a direction of inquiry with its plan and hypothesis in place | Creates `plans/PLAN_*.md`, `hypotheses/HYPOTHESIS_NN.md`, and the first iteration in the existing flat layout; no per-analysis tree |
| `scripts/new_iteration.py` | Create the next attempt and make it comparable to the last | Numbers project-wide, appends to `analysis/ITERATION_LOG.md`, and re-heads a seeded copy so it writes its own log |
| `scripts/select_result.py` | Record which attempt is reportable and why | Writes a pointer to evidence in place; copies and deletes nothing |
| `scripts/shared/iterations.py` | — | New: numbering, lookup, and the append-only writer the three share |

### What an iteration is

Per the project PI: one attempt at bringing the work closer to the goal, being one
script, its log, and its interpretation. Numbered across the whole project so the
numbering is a timeline rather than a filing scheme.

An iteration is either a **single point**, testing one change, or a **panel**, probing
several candidate directions at once. A panel returns a result per probe and can come
back mixed. Records therefore carry a `Kind` column and a prose `Outcome`, because
`SUPPORTED` cannot describe a panel where three of eight candidates helped and one
regressed, and collapsing it would discard the finding.

### The append rule

Every earlier helper only created files that did not exist. Two of these need to add a
row to a running record, so the rule is now explicit:

> A helper may create a file that does not exist, and may append a new entry to a record
> whose format it owns. It may never modify or remove an existing line.

Appending rather than printing a row to paste is deliberate: the paste is the step that
gets skipped, and a log with gaps cannot be trusted. Two tests hold the line:
`test_no_shipped_helper_can_delete_or_relocate_researcher_work` bans destructive calls in
any shipped helper, and
`test_a_helper_writing_a_record_opens_it_for_append_rather_than_write` requires append
mode on the iteration log.

### Defect this surfaced

Seven assets still described the retired tree, including a `lib/` package that never
existed and a styling module `prompts/figure_generation_prompt.md` told readers to import.
The earlier retired-term check covered retired *helpers* but not retired *paths*, so they
survived the copy pass.
`test_no_generated_guidance_directs_a_reader_to_a_path_this_scaffold_never_creates` now
covers the paths. `new_iteration.py` and `ITERATION_LOG` are deliberately absent from the
retired terms, since both names return with non-destructive behavior.

Two further corrections came from running the helpers rather than reading them: a seeded
script inherited the earlier iteration's `SCRIPT_NAME` and would have written its
evidence into that iteration's log, and the documented log filename used a hyphen where
`setup_logging` uses an underscore.

## Template variable mapping

Generation provides exactly two names, `project` and `researcher`, and renders with
`StrictUndefined`. A surviving legacy variable is therefore a generation failure, not
a cosmetic flaw.

| Legacy variable | Current equivalent |
|---|---|
| `cookiecutter.project_name` | `project.name` |
| `cookiecutter.project_slug` | `project.slug` |
| `cookiecutter.description` | `project.description` |
| `cookiecutter.domain` | `project.domain` |
| `cookiecutter.initial_research_question` | `project.research_question`, which may be unset |
| `cookiecutter.author_name` | `researcher.name` |
| `cookiecutter.author_email` | `researcher.email`, which may be unset |
| `cookiecutter.project_mode` | None. Paper is a capability; the asset only ships when it is enabled. |
| `cookiecutter.workflow_mode` | None. There is one workflow. |
| `cookiecutter.starting_phase` | None for guidance purposes. All three phases are always present; the contract records `starting_phase` and `current_phase` as data. |
| `cookiecutter.ai_tool` | None. The assistant pointer is generated from the contract. |
| `cookiecutter.license` | None. License text is a managed asset. |
| `cookiecutter.create_git_repo` | None. Recorded in the contract. |

Python assets are copied verbatim rather than rendered, and are exempt from the
unresolved-token check, so a bad copy there would reach a researcher in silence.
`tests/test_scaffold_content.py` closes that gap and also asserts that no generated
guidance names a retired helper or concept.

| Original path | Active disposition | Condition | Ownership | Compatibility correction |
|---|---|---|---|---|
| `README.md` | Restored at same path | Always | Tool guidance | Installed CLI, one workflow, direct files, all phases |
| `background/README.md` | Restored at same path | Always | Tool guidance | Current project metadata |
| `hypotheses/README.md` | Restored at same path | Always | Tool guidance | Direct audit trail |
| `hypotheses/HYPOTHESIS_TEMPLATE.md` | Restored at same path | Always | Editable starter | Current terminology |
| `plans/README.md` | Restored at same path | Always | Tool guidance | Current workflow |
| `analysis/README.md` | Restored at same path | Always | Tool guidance | Paper mode removed |
| `analysis/ANALYSIS_PLAN.md` | Restored at same path | Always | Editable starter | Paper-only guard removed |
| `analysis/ANALYSIS_TEMPLATE.md` | Restored at same path | Always | Editable starter | Current paths |
| `analysis/BREADCRUMB_TRAIL.md` | Restored at same path | Always | Researcher work | Paper-only guard removed |
| `analysis/REPOSITORY_PLAN.md` | Restored at same path | Always | Editable starter | Mode topology removed |
| `analysis/STUDY_REPORT_TEMPLATE.md` | Restored at same path | Always | Editable starter | Living report created later |
| `analysis/XX_figures/README.md` | Restored at same path | Always | Tool guidance | General evidence guidance |
| `data/synthetic/README.md` | Restored at same path | Always | Editable starter | Tracked provenance and inventory |
| `data/downloaded/README.md` | Restored at same path | Always | Editable starter | Tracked provenance and inventory |
| `data/real/README.md` | Restored at same path | Always | Editable starter | Tracked provenance and inventory |
| `experiments/01_synthetic/README.md` | Restored at same path | Always | Editable starter | Always present |
| `experiments/02_downloaded/README.md` | Restored at same path | Always | Editable starter | Always present |
| `experiments/03_real_data/README.md` | Restored at same path | Always | Editable starter | Always present |
| `results/logs/README.md` | Restored at same path | Always | Tool guidance | Logs tracked; compiler removed |
| `results/figures/README.md` | Restored at same path | Always | Tool guidance | Evidence provenance clarified |
| `docs/README.md` | Restored at same path | Always | Tool guidance | Current index |
| `docs/12_STEPS.md` | Restored at same path | Always | Tool guidance | Direct-file workflow |
| `docs/SMAIRT_PHILOSOPHY.md` | Restored at same path | Always | Tool guidance | Current safety boundary |
| `docs/BEST_PRACTICE_COLLABORATIVE.md` | Restored at same path | Always | Tool guidance | Durable files and logs replace session transfer |
| `docs/BEST_PRACTICE_SINGLE.md` | Retired | Never | Historical reference | Collaborative guide is canonical |
| `prompts/README.md` | Restored at same path | Always | Tool guidance | Compiler entry removed |
| `prompts/00_priming_prompts.md` | Restored at same path | Always | Tool guidance | Direct project-file refresh |
| `prompts/AI_CONTEXT.md` | Restored at same path | Always | Tool guidance | Assistant-neutral, no workflow mode |
| `prompts/CODE_CONVENTIONS.md` | Restored at same path | Always | Tool guidance | All phases and current helpers |
| `prompts/CONTEXT_INDEX.md` | Restored at same path | Always | Tool guidance | Direct file-reading index |
| `prompts/KNOWN_PATTERNS.md` | Restored at same path | Always | Researcher work | Mode conditions removed |
| `prompts/SESSION_START.md` | Restored at same path | Always | Tool guidance | Direct files and logs replace compiler |
| `prompts/session_log.md` | Restored at same path | Always | Researcher work | Durable session decision index, not pasted transcript |
| `prompts/intellectual_contribution.md` | Restored at same path | Always | Researcher work | Current contribution record |
| `scripts/README.md` | Restored at same path | Always | Tool guidance | Lists active safe helper set only |
| `scripts/new_script.py` | Repaired at same path | Always | Tool guidance | All phase directories and complete logging |
| `scripts/monitor_template.py` | Repaired at same path | Always | Tool guidance | Observes project progress only |
| `scripts/generate_manifest.py` | Repaired at same path | Always | Tool guidance | Non-destructive project inventory |
| `scripts/shared/__init__.py` | Repaired at same path | Always | Tool guidance | Current exports |
| `scripts/shared/logging.py` | Repaired at same path | Always | Tool guidance | Captures stdout, stderr, warnings, traceback |
| `scripts/shared/README.md` | Restored at same path | Always | Tool guidance | Current extension guidance |
| `scripts/compile_for_ai.py` | Archived only | Never | Historical reference | Browser compiler retired |
| `scripts/new_experiment.py` | Archived only | Never | Historical reference | Obsolete Paper iteration tree |
| `scripts/new_iteration.py` | Archived only | Never | Historical reference | Obsolete Paper iteration tree |
| `scripts/finalize_iteration.py` | Archived only | Never | Historical reference | Destructive finalization retired |
| `FINAL_MANIFEST.md` | Restored at same path | Paper | Researcher work | Editable claim-to-evidence map |
| `paper/outline.md` | Restored at same path | Paper | Editable starter | Paper capability replaces mode |
| `paper/drafts/README.md` | Restored at same path | Paper | Tool guidance | Paper capability replaces mode |
| `paper/reviewer_feedback/README.md` | Restored at same path | Paper | Tool guidance | Paper capability replaces mode |
| `paper_draft/README.md` | Retired | Never | Historical reference | Duplicate Paper workspace |
| `prompts/InitialPrompt_paper_driven.md` | Restored at same stable path | Paper | Tool guidance | Content describes additive Paper support |
| `prompts/figure_generation_prompt.md` | Restored at same path | Paper | Tool guidance | Current evidence paths |
| `prompts/iteration_review_prompt.md` | Restored at same path | Paper | Tool guidance | Destructive iteration engine removed |
| `hpc/README.md` | Restored at same path | HPC | Tool guidance | No scheduler-management claims |
| `hpc/config.yaml` | Restored at same path | HPC | Editable starter | Optional email and no Paper mode |
| `hpc/logs/README.md` | Restored at same path | HPC | Tool guidance | Durable job logs |
| `hpc/templates/slurm_basic.sh` | Restored at same path | HPC | Editable starter | Correct paths and arguments |
| `hpc/slurm_job.sh` | Repaired active successor | HPC | Editable starter | Safe command wrapper |
