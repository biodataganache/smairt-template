# Iteration Review Prompt

Use this when an iteration has produced a log and the question is what to do next.

An iteration is one attempt: one script, its log, its interpretation. Reviewing it means
deciding whether the attempt settled anything, and what follows from that.

---

## The prompt

```text
Review iteration [NN].

Read the script, its log in results/logs/, and the hypothesis it tests. Do not ask me to
paste them.

Report:
1. What the log actually shows, including anything that ran but was not asked for
2. Whether the result meets the criterion recorded in the hypothesis file
3. Anything in the log that looks wrong, surprising, or silently skipped
4. For a panel iteration, the result for every probe, not just the ones that worked

Then state the strongest case for continuing this direction and the strongest case for
abandoning it. Do not choose. I will decide.
```

---

## What the assistant should check

**The evidence**
- Does the log support the numbers being claimed
- Did anything fail, warn, or get skipped without being noticed
- Is the result reproducible, or does it depend on one seed
- Was the criterion set before the run, or is it being written now to fit the result

**The code**
- Does the script do what its docstring says
- Are parameters recorded, so the run can be repeated
- Is randomness seeded

**The record**
- Is there an `analysis/ANALYSIS_NN.md` interpretation
- Is there a row in `analysis/ITERATION_LOG.md`
- For a panel, is each probe recorded separately

---

## Reviewing a panel iteration

A panel probes several directions at once and returns a result per probe. Reviewing it
is not the same as reviewing a single point.

Report the whole distribution: which probes moved the metric, which did not, and which
made things worse. Then look for the pattern across them. A panel where one of eight
candidates helped has said something about the other seven, and that pattern is usually
more transferable than the winner.

Do not summarize a panel as a single verdict. "Three of eight above criterion, one
regression" is the finding.

Do not quietly drop the probes that failed. A panel reported as its best arm is a panel
reported dishonestly.

---

## The decision

**Decision: researcher only.** The assistant lays out the case both ways; the researcher
chooses.

| Choice | When | What it produces |
|---|---|---|
| Advance | The criterion was met and the result is stable | Next hypothesis, or the next phase |
| Revise | The direction looks sound but the attempt was not decisive | A new iteration stating what changed |
| Stop | The direction is exhausted or the approach is flawed | A recorded reason, which is a result |

A stop is not a failure to be hidden. An abandoned direction, recorded with why, is what
stops the next person spending the same week on it.

---

## After the decision

- **Advance or revise**: record the outcome in `analysis/ITERATION_LOG.md`, update the
  hypothesis status, and write what changed in `analysis/BREADCRUMB_TRAIL.md`
- **Stop**: record the reason in the analysis and the breadcrumb trail, and mark the
  track abandoned in `analysis/ANALYSIS_PLAN.md`
- **Reporting a result**: record it in `FINAL_MANIFEST.md` with the script and log behind
  it. Nothing is copied into a separate final directory; the evidence stays in
  `results/logs/` where it was produced, and the manifest points at it.
