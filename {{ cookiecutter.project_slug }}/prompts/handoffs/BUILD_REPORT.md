# Build Report (Builder → Orchestrator)

> What the Builder hands back. Keep it SHORT — this is the only thing that re-enters
> the Orchestrator's lean thread. No transcripts, no full logs; point to the log file.
> Copy this template and fill it in.

---

## Result: [SUCCESS / FAILED / BLOCKED]

## What ran

- Script: `experiments/[phase]/script_[XX]_[desc].py`
- Log: `results/logs/[logfile]`
- Command / config used:

## Key numbers

<!-- The handful of results that matter. Not the whole log. -->
-

## Anomalies / things the Orchestrator should know

<!-- Unexpected behavior, warnings, caveats on the result, scope limits observed. -->
-

## Errors hit (if any)

<!-- If FAILED/BLOCKED: the actual error and where you stopped. Don't claim success. -->
-

## New pattern/error worth saving?

<!-- If you solved a reusable error, flag it so the Orchestrator can add it to
     prompts/KNOWN_PATTERNS.md. You do not edit memory files yourself. -->
-
