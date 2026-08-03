# 04 - Re-enrich the scientific audit trail

Status: ready-for-agent
Type: task
Blocked by: 02

## Question

Does the generated audit trail teach the scientific loop, or only label its directories?

## Context

These assets are the researcher-facing spine of a SMAIRT project: where the question is captured, where the hypothesis is stated, where the experiment lives, where evidence lands, and where interpretation happens. Several are now near-empty. `plans/README.md` is 100 bytes and `background/README.md` is 97 — the directories exist but explain nothing.

| Asset | Original | Current | Retained |
|---|---|---|---|
| `plans/README.md` | 1696 | 100 | 5% |
| `background/README.md` | 1045 | 97 | 9% |
| `analysis/REPOSITORY_PLAN.md` | 4808 | 1555 | 32% |
| `analysis/ANALYSIS_PLAN.md` | 4210 | 1430 | 33% |
| `analysis/BREADCRUMB_TRAIL.md` | 1839 | 752 | 40% |
| `analysis/README.md` | 2892 | 1170 | 40% |
| `experiments/02_downloaded/README.md` | 1358 | 633 | 46% |
| `experiments/03_real_data/README.md` | 1312 | 673 | 51% |
| `analysis/STUDY_REPORT_TEMPLATE.md` | 9248 | 5246 | 56% |
| `analysis/XX_figures/README.md` | 1274 | 787 | 61% |
| `hypotheses/README.md` | 1249 | 844 | 67% |
| `experiments/01_synthetic/README.md` | 864 | 645 | 74% |
| `results/logs/README.md` | 1004 | 763 | 75% |
| `results/figures/README.md` | 644 | 611 | 94% |

Two conflicts to rewrite rather than copy. The originals treat phase directories as conditional on the selected mode, whereas every generated project now contains all three phases — starting phase is immutable provenance and current phase is mutable status, neither controls which directories exist. And `analysis/ANALYSIS_PLAN.md` plus `analysis/BREADCRUMB_TRAIL.md` originally sat behind a Paper-only guard that has been removed; they are now always generated.

Respect ownership from `docs/scaffold-transition.md`: `analysis/BREADCRUMB_TRAIL.md` is researcher work, and the analysis plan, repository plan, and study report template are editable starters. Re-enrich them as prompting structure the researcher fills in, not as invented findings.

## Acceptance

- Each asset above meets its declared fidelity floor from ticket 02.
- `background/README.md` explains what context, constraints, and prior work to capture.
- `hypotheses/README.md` walks through assumptions, predictions, alternatives, and rejection criteria.
- `plans/README.md` explains when planning is warranted and what a plan contains.
- Each `experiments/` phase README explains what belongs in that phase and how it differs from the others, with no claim that the directory is conditional.
- `results/logs/README.md` establishes logs as the canonical raw record, with no reference to browser-paste compilation.
- `analysis/README.md` connects results, limitations, decisions, and follow-up work.
- `analysis/STUDY_REPORT_TEMPLATE.md` remains a template, not a pre-filled report.
- No asset in this group invents scientific content on the researcher's behalf.
- The prohibition test from ticket 02 passes for every file in this group.

## Notes

`analysis/ANALYSIS_TEMPLATE.md` and `hypotheses/HYPOTHESIS_TEMPLATE.md` already exceed their originals and are out of scope here. Leave them alone.
