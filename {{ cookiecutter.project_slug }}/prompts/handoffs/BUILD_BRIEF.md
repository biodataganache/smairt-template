# Build Brief (Orchestrator → Builder)

> The handoff that sends an execution task to a disposable Builder. It MUST be
> self-contained: the Builder starts cold and reads nothing but this brief and the
> files it names. If the Builder would need to ask "what about...?", the brief is
> incomplete. Copy this template and fill every field.

---

## Task

<!-- One sentence: what script to produce and what it must do. -->
-

## Context the Builder needs (and ONLY this)

- Hypothesis being tested:
- Relevant prior script(s) to build on:
- Files to read: `prompts/CODE_CONVENTIONS.md`, `prompts/KNOWN_PATTERNS.md`, [others]
- Relevant findings / must-holds (copy them in — don't make the Builder hunt):
  - <!-- e.g. "Must apply frequency weighting (F-002). Seed = 42." -->

## Inputs

- Data location / files:
- Parameters / config:

## Expected outputs

- Script path: `experiments/[phase]/script_[XX]_[desc].py`
- Log path: `results/logs/` (use TeeLogger from `scripts/shared/logging`)
- What the output should contain:

## Definition of done

<!-- Concrete, checkable. The Builder is done when ALL are true. -->
- [ ] Script runs clean to completion
- [ ] Output logged to `results/logs/`
- [ ] [metric / artifact produced]
- [ ]

## Guardrails

- Follow `prompts/CODE_CONVENTIONS.md` naming and logging conventions.
- If a decision would change the experiment's meaning, STOP and report — don't guess.
- Do not edit `PROJECT_STATE.md`, `FINDINGS.md`, or `analysis/` files.

## Return

Reply with a Build Report in the `prompts/handoffs/BUILD_REPORT.md` format.
