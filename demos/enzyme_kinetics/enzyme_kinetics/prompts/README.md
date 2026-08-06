# Prompts

Files an assistant reads to work on this project, and the record of what the
researcher contributed.

| File | Job | Read it |
|---|---|---|
| `AI_CONTEXT.md` | The assistant's role and how this project works | First, always |
| `CONTEXT_INDEX.md` | Which files to open for a given task | When starting any task |
| `CODE_CONVENTIONS.md` | How code in this project is written | Before writing a script |
| `KNOWN_PATTERNS.md` | What already works here, and what has already failed | Before writing a script |
| `00_priming_prompts.md` | Copy-pasteable prompts, one per situation | When starting or resuming a session |
| `session_log.md` | Decisions and their reasoning, in order | When the reason behind a choice matters |
| `intellectual_contribution.md` | What the researcher determined, as opposed to what was drafted | Continuously, by the researcher |

`AI_CONTEXT.md` and `CONTEXT_INDEX.md` answer different questions. The first explains
the workflow; the second routes to files by task. An assistant beginning work reads
both.

`KNOWN_PATTERNS.md` and `session_log.md` grow as the project runs. A pattern that
proves reusable belongs in the first; the reasoning behind a decision belongs in the
second. Neither is a place for raw output, which stays in `results/logs/`.

`intellectual_contribution.md` belongs to the researcher, who is the only one who
accepts, rewrites, or deletes what it says. An assistant may add observations under
`## AI-Detected Contributions`, each marked `Status: unreviewed` until the researcher
confirms it. A researcher frequently does not recognise their own contribution in the
moment, so an assistant noticing it is worth more than self-reporting; the researcher
still decides whether the observation is true.

## Paper capability

When Paper is enabled, three further prompts appear here:
`InitialPrompt_paper_driven.md`, `figure_generation_prompt.md`, and
`iteration_review_prompt.md`.
