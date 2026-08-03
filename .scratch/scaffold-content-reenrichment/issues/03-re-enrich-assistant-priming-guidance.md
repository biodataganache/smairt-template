# 03 - Re-enrich assistant priming guidance

Status: ready-for-agent
Type: task
Blocked by: 02

## Question

Can an assistant prime itself correctly from the generated `prompts/` directory alone?

## Context

This is the highest-value group in the backlog and contains the four worst losses in the scaffold. `prompts/AI_CONTEXT.md` is the file that every generated `AGENTS.md`, `CLAUDE.md`, `README.md`, and tutorial instructs an assistant to read first. It carries 732 bytes against a 12,241-byte original. An assistant priming on it today learns almost nothing.

| Asset | Original | Current | Retained |
|---|---|---|---|
| `prompts/KNOWN_PATTERNS.md` | 12541 | 179 | 1% |
| `prompts/CODE_CONVENTIONS.md` | 7805 | 172 | 2% |
| `prompts/AI_CONTEXT.md` | 12241 | 732 | 5% |
| `prompts/intellectual_contribution.md` | 3319 | 190 | 5% |
| `prompts/CONTEXT_INDEX.md` | 4399 | 401 | 9% |
| `prompts/session_log.md` | 3043 | 517 | 16% |
| `prompts/InitialPrompt_paper_driven.md` | 3010 | 616 | 20% |
| `prompts/figure_generation_prompt.md` | 2338 | 622 | 26% |
| `prompts/iteration_review_prompt.md` | 2009 | 589 | 29% |
| `prompts/SESSION_START.md` | 5847 | 1823 | 31% |
| `prompts/README.md` | 2058 | 1048 | 50% |
| `prompts/00_priming_prompts.md` | 1468 | 1189 | 80% |

The legacy originals under `legacy/cookiecutter/original-template/{{ cookiecutter.project_slug }}/prompts/` are byte-identical to `main` and are the content baseline.

Watch for three conflicts between the original text and current behavior. The originals assume selectable workflow modes, which are retired in favor of one workflow with Paper as an additive capability. They assume `compile_for_ai.py` and browser-paste session transfer, which are retired in favor of reading project files and `results/logs/` directly. And `session_log.md` was a pasted transcript, whereas it is now a durable decision index. Rewrite these passages to current behavior; do not copy text that contradicts the tool.

## Acceptance

- Each asset above meets its declared fidelity floor from ticket 02.
- `prompts/AI_CONTEXT.md` alone is sufficient to orient an assistant: the loop, the directory map, where raw output goes, where interpretation goes, and what the researcher owns versus what the assistant may draft.
- `prompts/CODE_CONVENTIONS.md` states actual naming, logging, parameter-recording, and output-path conventions.
- `prompts/KNOWN_PATTERNS.md` explains what a pattern record contains and shows its shape.
- `prompts/CONTEXT_INDEX.md` indexes files that actually exist in a generated project.
- Paper-conditional prompts describe Paper as an additive capability, never as a separate project mode.
- The prohibition test from ticket 02 passes for every file in this group.
- `smairt check` reports clean for base, Paper, and HPC generation.

## Notes

`prompts/session_log.md` is classified as researcher work in `docs/scaffold-transition.md`. Re-enrich it as guidance about what to record, not as invented session content.
