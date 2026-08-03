# Scaffold Content Re-enrichment

Status: ready-for-agent

## Problem Statement

The scientific scaffold restoration recreated the original template's file paths but not its content. Path-level accounting in `docs/scaffold-transition.md` is complete and honest about retirements, yet of the 50 assets retained from the original template, 44 shrank — and the transition record describes them as "Restored at same path," true of the path and misleading about the substance.

The generated scientific scaffold now carries 48,179 bytes of guidance where the original carried 194,401 bytes across the same asset set. That is 25 percent retained. The loss is not uniform trimming; several assets were reduced to a placeholder. `prompts/KNOWN_PATTERNS.md` fell from 12,541 bytes to 179 — three sentences. `prompts/CODE_CONVENTIONS.md` fell from 7,805 bytes to 172. `prompts/AI_CONTEXT.md`, the file every assistant session is instructed to read first, fell from 12,241 bytes to 732.

This defeats the restoration's own acceptance criterion. `.scratch/scientific-scaffold-restoration/spec.md` user story 11 requires that "generated Markdown must stand alone, so that the workflow remains understandable before project-local skills are introduced." `CONTEXT.md` states the same as an invariant. A researcher generating a project today receives correct directory structure and section headings, but not the scientific guidance those headings promise. An assistant priming on `prompts/AI_CONTEXT.md` receives 732 bytes where the workflow needs thousands.

No content was destroyed. Every original asset survives byte-for-byte under `legacy/cookiecutter/original-template/{{ cookiecutter.project_slug }}/`, verified by blob-hash equality against `main` at `78f22af`. The recovery source is intact and available; the work of using it has not been done.

## Solution

Re-enrich each retained scaffold asset from its byte-identical legacy original, applying only the compatibility corrections already documented in `docs/scaffold-transition.md`.

The legacy original is the content baseline. Where the original text conflicts with a decision the restoration made deliberately — workflow modes retired, browser-paste compilation retired, all phase directories always present, Paper and HPC as additive capabilities, no scheduler-management claims — the decision wins and the text is rewritten to match. Where no such conflict exists, the original's substance is preserved.

Retirements stay retired. The eight assets `docs/scaffold-transition.md` marks as retired or archived-only are not reintroduced, and `results/.DS_Store` remains excluded as operating-system metadata.

Re-enrichment changes generated content only. The scaffold blueprint's declared paths, ownership types, and activation conditions do not change, so `scripts/scaffold_diff.py` should report no structural change. Because generated output does change, the three golden projects must be regenerated so the content growth is visible as ordinary reviewable text, satisfying the independent-verification requirement in ADR 0001.

`docs/scaffold-transition.md` gains a content-fidelity column so "Restored at same path" can no longer stand in for "restored in substance."

## User Stories

1. As a researcher, I want generated guidance to explain the scientific workflow in full, so that a new project is usable without consulting the repository or an external skill.
2. As a researcher, I want `prompts/AI_CONTEXT.md` to carry complete workflow guidance, so that priming an assistant on the documented first file actually primes it.
3. As a researcher, I want `prompts/CODE_CONVENTIONS.md` to state the real conventions, so that generated code advice is actionable rather than a heading.
4. As a researcher, I want `prompts/KNOWN_PATTERNS.md` to explain what a pattern record contains and show its shape, so that I know what to write.
5. As a researcher, I want `docs/12_STEPS.md` to explain each step, not just name it, so that the loop is teachable to someone new.
6. As a researcher, I want `scripts/README.md` to document each active helper's purpose and usage, so that I can use the helpers without reading their source.
7. As a researcher, I want `analysis/` templates to carry their original prompting structure, so that interpretation is guided rather than blank.
8. As a researcher, I want `hypotheses/` guidance to walk through assumptions, predictions, alternatives, and rejection criteria, so that hypothesis quality is supported.
9. As a researcher, I want phase directory guidance to explain what belongs in each phase, so that phase choice is meaningful.
10. As a researcher, I want `background/README.md` to explain what context to capture, so that the audit trail starts well.
11. As a researcher, I want `plans/README.md` to explain when and how to plan, so that the directory is not an empty gesture.
12. As an HPC user, I want `hpc/` configuration and template guidance restored in detail, so that cluster adaptation is possible without external reference.
13. As an HPC user, I want restored HPC text to continue making no scheduler-management claims, so that capability boundaries stay honest.
14. As a Paper user, I want Paper guidance restored in detail while remaining an additive capability, so that publication work is supported without reintroducing a separate project mode.
15. As an assistant, I want session-start and priming guidance to describe reading project files and logs directly, so that restored text does not resurrect browser-paste workflows.
16. As a researcher, I want retired helpers to stay retired, so that re-enrichment does not reintroduce destructive or obsolete tooling.
17. As a maintainer, I want re-enrichment to change content only, so that the blueprint diff stays empty and review focuses on prose.
18. As a maintainer, I want golden projects regenerated in the same change, so that content growth is independently recorded as reviewable text.
19. As a maintainer, I want the transition record to distinguish path restoration from content fidelity, so that this gap cannot recur undetected.
20. As a reviewer, I want each re-enriched asset traceable to its legacy source, so that I can verify substance rather than trusting a summary.
21. As a maintainer, I want a measurable fidelity floor per asset, so that "restored" is falsifiable rather than a judgement call.
22. As a maintainer, I want all existing release gates to keep passing, so that re-enrichment does not trade content for correctness.

## Implementation Decisions

- The legacy original under `legacy/cookiecutter/original-template/{{ cookiecutter.project_slug }}/` is the content baseline for every retained asset.
- Compatibility corrections are limited to those already recorded in `docs/scaffold-transition.md`. No new product decisions are made here.
- Assets are re-enriched in place at their current scaffold paths. No path, ownership, or activation condition changes.
- Jinja placeholders are used only where the current asset already uses them; re-enrichment does not introduce new template variables.
- Text is rewritten, not concatenated. Original prose that references retired modes, the browser compiler, phase-conditional directories, or scheduler management is rewritten to current behavior rather than copied and contradicted.
- Retirements in `docs/scaffold-transition.md` are honored exactly: `scripts/compile_for_ai.py`, `scripts/new_experiment.py`, `scripts/new_iteration.py`, `scripts/finalize_iteration.py`, `paper_draft/README.md`, `docs/BEST_PRACTICE_SINGLE.md`, and `results/.DS_Store` are not reintroduced.
- Python helpers are re-enriched as working code, not as commentary. Restored behavior must execute.
- `docs/scaffold-transition.md` gains a content-fidelity column recording original bytes, current bytes, and disposition of the difference.
- Golden projects are regenerated with `scripts/update_goldens.py` in the same change as the content edits.
- Work proceeds in small commits grouped by directory so each diff is reviewable as prose.
- The mypy failure at `src/smairt/cli.py:373` is fixed first, separately, so re-enrichment starts from a green baseline.

## Testing Decisions

- Good tests observe generated output and command behavior, not prose wording. No test asserts an exact sentence.
- A fidelity test asserts a minimum retained-byte ratio per re-enriched asset against its legacy original, so regression to placeholder content fails the suite.
- A prohibition test asserts generated guidance contains no reference to retired concepts: workflow modes, browser-paste compilation, the retired helper filenames, phase-conditional directory claims, or scheduler submission.
- Golden tests continue to compare full normalized content and must be updated deliberately, not regenerated to mask an unintended change.
- Blueprint diff output must show no added, removed, renamed, ownership-changed, or condition-changed entries.
- Helper tests execute the re-enriched Python helpers from a generated project and assert non-destructive behavior and log capture.
- `smairt check` must report a clean project for base, Paper, and HPC generation after re-enrichment.
- The full gate sequence runs before completion: `ruff format --check`, `ruff check`, `mypy src tests`, `ci_scaffold_diff.py`, `pytest`, `uv build`, and both `smoke_install.py` artifact checks.

## Out of Scope

- Reintroducing any asset marked retired or archived-only in `docs/scaffold-transition.md`.
- Changing the scaffold blueprint's paths, ownership types, or activation conditions.
- Changing the generated-project contract schema or `smairt.yaml` fields.
- Changing CLI or TUI behavior, including the interactive project-location wizard.
- Migrating or upgrading existing generated projects to the enriched scaffold.
- Converting generated guidance into project-local skills.
- Re-enriching the demo projects under `demos/`.
- Restoring the Cookiecutter path as a supported generator.
- PyPI publication.

## Further Notes

- Total scaffold content: 194,401 bytes original, 48,179 bytes current, 25 percent retained across 50 retained assets.
- The superseded parallel attempt is preserved at tag `superseded/scaffold-restoration-c88cfd6`. It was the thinner of the two implementations at 37,824 bytes and is not a recovery source.
- Legacy blob equality against `main` at `78f22af` was verified by hash for a sample including `prompts/AI_CONTEXT.md`, `prompts/KNOWN_PATTERNS.md`, `docs/12_STEPS.md`, `scripts/README.md`, and `docs/BEST_PRACTICE_SINGLE.md`.
- Five current assets have no original counterpart and need no re-enrichment: `.gitignore`, `hpc/slurm_job.sh`, `paper/analysis/README.md`, `paper/FINAL_MANIFEST.md`, and `paper/README.md`.
- Six assets grew or held steady and are excluded from the fidelity backlog: `analysis/ANALYSIS_TEMPLATE.md`, `data/downloaded/README.md`, `data/real/README.md`, `data/synthetic/README.md`, `hypotheses/HYPOTHESIS_TEMPLATE.md`, and `scripts/shared/logging.py`.

## Fidelity Backlog

Retained bytes as a percentage of the legacy original, ascending. This is the work queue.

| Asset | Original | Current | Retained |
|---|---|---|---|
| `prompts/KNOWN_PATTERNS.md` | 12541 | 179 | 1% |
| `prompts/CODE_CONVENTIONS.md` | 7805 | 172 | 2% |
| `docs/12_STEPS.md` | 9619 | 567 | 5% |
| `plans/README.md` | 1696 | 100 | 5% |
| `prompts/AI_CONTEXT.md` | 12241 | 732 | 5% |
| `prompts/intellectual_contribution.md` | 3319 | 190 | 5% |
| `docs/SMAIRT_PHILOSOPHY.md` | 3080 | 250 | 8% |
| `scripts/README.md` | 11585 | 973 | 8% |
| `background/README.md` | 1045 | 97 | 9% |
| `prompts/CONTEXT_INDEX.md` | 4399 | 401 | 9% |
| `README.md` | 5680 | 522 | 9% |
| `docs/README.md` | 681 | 93 | 13% |
| `prompts/session_log.md` | 3043 | 517 | 16% |
| `scripts/shared/__init__.py` | 877 | 141 | 16% |
| `prompts/InitialPrompt_paper_driven.md` | 3010 | 616 | 20% |
| `prompts/figure_generation_prompt.md` | 2338 | 622 | 26% |
| `prompts/iteration_review_prompt.md` | 2009 | 589 | 29% |
| `docs/BEST_PRACTICE_COLLABORATIVE.md` | 4819 | 1452 | 30% |
| `prompts/SESSION_START.md` | 5847 | 1823 | 31% |
| `analysis/REPOSITORY_PLAN.md` | 4808 | 1555 | 32% |
| `hpc/config.yaml` | 992 | 323 | 32% |
| `analysis/ANALYSIS_PLAN.md` | 4210 | 1430 | 33% |
| `hpc/templates/slurm_basic.sh` | 1352 | 449 | 33% |
| `paper/drafts/README.md` | 693 | 261 | 37% |
| `paper/reviewer_feedback/README.md` | 964 | 365 | 37% |
| `scripts/new_script.py` | 6039 | 2311 | 38% |
| `analysis/BREADCRUMB_TRAIL.md` | 1839 | 752 | 40% |
| `analysis/README.md` | 2892 | 1170 | 40% |
| `scripts/generate_manifest.py` | 3689 | 1644 | 44% |
| `experiments/02_downloaded/README.md` | 1358 | 633 | 46% |
| `scripts/monitor_template.py` | 3496 | 1743 | 49% |
| `prompts/README.md` | 2058 | 1048 | 50% |
| `experiments/03_real_data/README.md` | 1312 | 673 | 51% |
| `hpc/README.md` | 1293 | 694 | 53% |
| `analysis/STUDY_REPORT_TEMPLATE.md` | 9248 | 5246 | 56% |
| `scripts/shared/README.md` | 1132 | 636 | 56% |
| `paper/outline.md` | 1380 | 806 | 58% |
| `analysis/XX_figures/README.md` | 1274 | 787 | 61% |
| `hpc/logs/README.md` | 785 | 507 | 64% |
| `hypotheses/README.md` | 1249 | 844 | 67% |
| `experiments/01_synthetic/README.md` | 864 | 645 | 74% |
| `results/logs/README.md` | 1004 | 763 | 75% |
| `prompts/00_priming_prompts.md` | 1468 | 1189 | 80% |
| `results/figures/README.md` | 644 | 611 | 94% |

Byte ratio is a detection heuristic, not the acceptance criterion. Acceptance is whether the asset explains its subject well enough to stand alone. A shorter asset that fully covers current behavior can pass; a padded one cannot.
