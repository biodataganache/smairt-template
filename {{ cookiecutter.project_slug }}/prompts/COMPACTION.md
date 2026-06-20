# Compaction & Memory Protocol

> How to keep the AI on task and the context window small at near-zero token cost.
> This is the cheap, do-this-first layer — it works in any topology and any tool.

The three memory layers (see `PROJECT_STATE.md` and `FINDINGS.md`):

| Layer | File(s) | Job |
|-------|---------|-----|
| 1. Working state | `PROJECT_STATE.md` | "Where we are right now" — tiny, overwritten |
| 2. Findings ledger | `FINDINGS.md` (+ `prompts/KNOWN_PATTERNS.md` for code/errors) | "What we've learned that's still true" — curated |
| 3. Archive | `analysis/`, `results/logs/`, `hypotheses/` | Every result, ever — never deleted, searched on demand |

---

## The compaction loop

When the conversation gets long (the AI starts losing the thread, repeating itself,
or the context window is filling up):

1. **Write state.** Update `PROJECT_STATE.md` so it accurately reflects: current
   hypothesis, last result, next step, open threads. Overwrite — keep it short.
2. **Promote findings.** Move any durable result from this session into `FINDINGS.md`
   (see the promotion checklist below).
3. **Record the detail.** Make sure the full result lives in an `analysis/ANALYSIS_XX.md`
   file and the log is in `results/logs/` (layer 3). Nothing important should exist
   only in the chat.
4. **Restart.** Begin a fresh session. Rehydrate by reading, in order:
   `PROJECT_STATE.md` → `FINDINGS.md` → the most recent `analysis/` file(s).
   Search the archive only for the specific older result you need.

Restarting drops accumulated context bloat for free and is the single biggest
token-cost lever — cheaper than any sub-agent.

> For cross-tool transfer or archival, `scripts/compile_for_ai.py` bundles the full
> state into `prompts/compiled_for_ai.md`. Use it when switching AI tools, not for
> routine restarts (layers 1–2 are enough for those).

---

## The promotion checklist (what makes recall work)

Forgetting happens when a key result never leaves its iteration's analysis file.
Promote a result to `FINDINGS.md` when it graduates from "a number in one run" to "a
fact that should shape future work." Use the entry schema in `FINDINGS.md`:

- [ ] Does it change what we would do next, or what future scripts must include? If so, promote it.
- [ ] Written with a `Claim` and a `Scope` (size, phase, conditions). Never a bare verdict.
- [ ] Carries `Data` (what it ran on) and `Metric` (the headline number).
- [ ] Linked to its `Evidence` (analysis file plus log).
- [ ] Given a `Status` (`established` or `provisional`).
- [ ] If it sets a standing rule, also add it to Requirements / Must-Holds.

## The re-validation rule (when context changes)

When the dataset, scale, or phase changes:

- [ ] Mark prior narrower-context findings `needs-revalidation` — do **not** trust them.
- [ ] Re-test before relying on them.
- [ ] Record the new result with its new scope; link it to the old one (`Supersedes:`).
- [ ] Keep both entries — scale-dependence is itself a finding.

## Before designing any new experiment

- [ ] Read `FINDINGS.md` (don't repeat a dead end; honor must-holds).
- [ ] Search recent `analysis/` files for related prior work.
- [ ] Confirm the current `PROJECT_STATE.md` next-step still matches the goal.

{% if cookiecutter.agent_topology == 'orchestrated' %}---

## Orchestrated topology notes

In orchestrated mode the **Orchestrator** owns this protocol: it maintains
`PROJECT_STATE.md` and `FINDINGS.md`, runs compaction, and validates promoted
findings against the log file. A **Builder** never edits memory files — it returns a
Build Report (`prompts/handoffs/BUILD_REPORT.md`), and the Orchestrator decides what,
if anything, to promote. See `prompts/roles/ORCHESTRATOR.md`.
{% endif %}