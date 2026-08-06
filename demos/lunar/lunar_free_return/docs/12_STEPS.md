# The SMAIRT Research Loop

Twelve steps. Each one states who owns the decision, what the researcher does, what
the assistant does, and which file carries the record.

This document is written for two readers, the researcher and the assistant, and it is
the shared reference for both.

## Vocabulary

Both readers use these terms with the same meaning.

**Researcher** — the person accountable for the scientific claims. Owns the question,
the hypothesis, the decision criterion, and the choice to stop.

**Assistant** — the AI collaborator. Reads project files directly rather than being
told their contents. Writes and runs code, surveys prior work, drafts text, and flags
anomalies.

**Decision** — a choice that is acted on and has a consequence. Each step names one
owner. Where a step is owned by the researcher, the assistant may inform the choice
but does not make it.

**Steer** — to shape the options a decision is made from: narrowing scope, requesting
alternatives, rejecting a framing, redirecting an approach. Steering is where most of
the researcher's judgment is applied. It is not the same as deciding. An assistant can
be steered toward a sound criterion and still must not be what selects it.

**Record** — the file that carries a step's provenance. When an assistant can write
and run experiments, the order in which work happened is no longer evidence of the
reasoning behind it. Only committed files are. Each step names its record so the
project can show what was concluded, by whom, and in what order.

**Iteration** — one attempt at bringing the work closer to the goal: one script, the
log it produced, and the interpretation of that log. Iterations are numbered across the
whole project in the order the work happened, so the numbering is a timeline rather than
a filing scheme.

An iteration takes one of two shapes. A **single point** tests one change and answers
one question: does this modification improve performance. A **panel** probes several
directions at once: do any of these candidate changes improve the model. A panel is one
iteration because it is one attempt, even though it returns several answers.

**Probe** — one arm of a panel iteration. Each probe carries its own label and its own
result. A panel of eight probes can come back with three improvements, one regression,
and four null results, and all three groups are findings. Recording a panel as a single
verdict discards most of what it produced, so probe-level results stay separated from
the moment they are written.

**Track** — a direction of inquiry, spanning as many iterations as it takes. A track has
a plan and one or more hypotheses. An iteration is one attempt within a track.

---

## Step 1 - State the research question

The question the project exists to answer, in one or two sentences, in language a
colleague outside the subfield can follow. A vague question produces experiments that
cannot fail.

**Decision: researcher.** This framing is inherited by everything downstream.

- **Researcher:** writes the question. May ask for restatements or sharper drafts, then
  chooses the wording.
- **Assistant:** restate the question back and name what it leaves ambiguous. Offer
  two or three sharper alternatives. Do not substitute a different question for the
  one given.
- **Record:** `smairt.yaml` holds the question as project metadata. Expand on it in
  `background/`.

---

## Step 2 - Record relevant background and constraints

What is already known, what is being assumed, and what limits the work: data
availability, compute, time, licensing. Constraints recorded now are design rationale.
Constraints recalled later are excuses.

**Decision: shared.** The assistant surveys; the researcher judges what is
established, what is contested, and what actually binds this project.

- **Researcher:** decides which prior work is relevant and which constraints are real.
  Verifies any reference that matters to the argument.
- **Assistant:** survey prior work and summarize it. State which claims are least
  certain and mark every reference as unverified. Do not present a citation as
  confirmed. Do not assert that a result is novel; that judgment depends on what the
  field already considers settled.
- **Record:** `background/`.

---

## Step 3 - Form a falsifiable hypothesis

A specific prediction, the reasoning that makes it plausible, and the alternative
explanations that would produce the same observation. If no result could contradict
the statement, it is not yet a hypothesis.

**Decision: researcher.** The prediction is the scientific claim being made.

- **Researcher:** states the prediction and rationale. Decides which objections to
  answer and which to accept as limitations.
- **Assistant:** attack the hypothesis. Name confounds, alternative mechanisms, and
  the objection a skeptical reviewer would raise first. Do not weaken the prediction
  to make it easier to support.
- **Record:** `hypotheses/HYPOTHESIS_XX.md`, from
  `hypotheses/HYPOTHESIS_TEMPLATE.md`. Status begins at `PENDING`.

---

## Step 4 - Define a decision criterion

What result supports the hypothesis and what result refutes it, written before
anything runs. A criterion written after the data is a rationalization.

**Decision: researcher only.** This is the judgment that makes the experiment
falsifiable.

- **Researcher:** sets both criteria. May ask for candidates and reasoning, then
  chooses and can say why.
- **Assistant:** propose candidate thresholds with the reasoning for each, and name
  what result would be uninformative either way. Do not select the criterion. Do not
  begin the experiment script until the criterion is recorded.
- **Record:** the `Success criteria` and `Rejection criteria` sections of the
  hypothesis file, committed before the script exists.

Commit the criteria before the script for the same reason you write them first: the
ordering is what makes the test a test. Be honest about how much that ordering proves.
Local Git history can be rewritten and dates can be set by hand, so a commit is a record
you keep for yourself and offer to a collaborator who trusts it, not a proof against
someone who does not. If you need the stronger claim, timestamp the criteria somewhere you
do not control — a preregistration, a signed tag pushed to a shared remote, or a message to
a colleague. What the commit does reliably give you is the thing that matters most often:
you cannot quietly convince yourself afterwards that this was the criterion all along.

---

## Step 5 - Plan the smallest informative experiment

The cheapest test that could still change the answer. Scope grows without help.

**Decision: shared.** The assistant proposes designs; the researcher judges what is
worth the cost.

- **Researcher:** approves the design and its cost. Writes a plan first when the work
  spans many experiments.
- **Assistant:** propose a design, name any missing control, and state what could be
  cut while keeping the test informative. Do not expand scope beyond what the
  hypothesis requires.
- **Record:** `plans/` for multi-experiment work; the `Experimental Design` section of
  the hypothesis file otherwise.

---

### Questions worth answering before the run

The right structure depends on the field, but four risks are present whether or not this
project enables extra rigor fields in Advanced settings:

- **Multiplicity**: testing many probes or outcomes creates more chances for an accidental
  pass. State how the project will interpret the family of tests rather than presenting
  only the best result.
- **Discovery versus validation**: repeated adaptation against the same data can make a
  discovery look independently confirmed. State which role an iteration and its data play.
- **Unit of inference**: repeated seeds or measurements are not automatically independent
  evidence. Name the independent unit that supports the claim.
- **Per-probe status**: one verdict can hide a mixed panel. Preserve what each probe showed,
  including null and adverse results.

Advanced settings can make helpers add blank declarations for these questions to files
created afterward. The settings never name a method or choose an answer. If enabled, the
researcher records standing policy in `analysis/RIGOR.md`; an assistant may suggest wording,
but the researcher approves, edits, or rejects it.

## Step 6 - Select the data phase

Every project carries all three phases:

```
experiments/01_synthetic/    Fast feedback, controlled conditions, verify the code
experiments/02_downloaded/   Benchmarks, diversity, comparison to known results
experiments/03_real_data/    The target data, the actual question
```

Synthetic data establishes whether the code does what it is believed to do.
Benchmarks establish whether the approach generalizes past one dataset. Real data
answers the question, and is where noise and edge cases appear.

Starting at a later phase is legitimate when the data is already in hand and well
understood. The earlier phases remain available: when a real-data result is ambiguous,
dropping back to a case with a known answer is usually the fastest way to find out why.

**Decision: researcher.**

- **Researcher:** chooses the phase. `starting_phase` never changes; `current_phase`
  advances as the work does.
- **Assistant:** state which phase would most cheaply separate a code defect from a
  genuine finding. Do not claim a phase directory is absent; all three always exist.
- **Record:** `current_phase` in `smairt.yaml`, and the phase directory holding the
  script.

---

## Step 7 - Create a numbered experiment script

One script, one hypothesis, runnable on its own. Create it from the project root:

```bash
python3 scripts/new_iteration.py baseline synthetic --hypothesis HYPOTHESIS_01
```

The hypothesis argument is required. Naming what a script is meant to settle before
writing it is the convention.

This is also what records the attempt: the helper appends a row to
`analysis/ITERATION_LOG.md`, so the sequence of attempts stays readable without opening
every analysis. Every numbered script is an iteration and is recorded. Code that supports
the work without testing anything is a utility, created by `scripts/new_utility.py` into
`scripts/utilities/`, and it takes no number.

Numbering is sequential across the project, so the filenames read as the order the
work happened:

```
experiments/01_synthetic/script_01_baseline.py
experiments/02_downloaded/script_04_benchmark_sweep.py
experiments/03_real_data/script_07_validation.py
```

**Decision: shared.** The assistant can own the implementation.

- **Researcher:** confirms the script tests the stated hypothesis and nothing else.
- **Assistant:** read `prompts/CODE_CONVENTIONS.md` and `prompts/KNOWN_PATTERNS.md`
  before writing, and reuse what is already there. Name the hypothesis file in the
  script docstring. Do not create a script that tests several hypotheses at once.
- **Record:** the script, with its hypothesis file named in the docstring.

---

## Step 8 - Run it and retain the raw output

Run from the project root. Generated scripts use `TeeLogger`, which captures stdout,
stderr, warnings, and uncaught tracebacks in one file. A traceback that appeared only
on a terminal is not part of the record.

Logs are named after the script that produced them, so evidence traces back to code:

```
results/logs/script_01_baseline_20240115_143022.log
results/logs/script_07_validation_20240220_091544.log
```

Before the script's own output, the log records the Python executable and dependencies,
Git commit when available, arguments and configuration, host and device, and the SHA-256
identity of input files. It ends with `Run status: SUCCEEDED` or `Run status: FAILED
(<exception>)`. The same status and exact log path are appended to
`analysis/RUN_HISTORY.md`, so a crash does not disappear when the iteration is rerun.
Immediate reruns receive distinct microsecond-resolution names rather than competing for
one file.

Four files form the audit trail, and the assistant reads them directly:

| Artifact | File | Question it answers |
|---|---|---|
| Hypothesis | `hypotheses/HYPOTHESIS_XX.md` | What was predicted, and what would refute it? |
| Code | `experiments/XX_phase/script_XX_*.py` | What was actually run? |
| Output | `results/logs/script_XX_*.log` | What happened? |
| Interpretation | `analysis/ANALYSIS_XX.md` | What was learned, and where does it hold? |

**Decision: none.** The assistant can own this.

- **Researcher:** confirms the run completed and a log exists.
- **Assistant:** run the script and retain the complete log. Use
  `scripts/monitor_template.py` to observe a long or remote run through its progress
  file. Never edit or truncate a log; its value depends on being untouched.
- **Record:** `results/logs/`.

---

## Step 9 - Inspect failures and unexpected behavior

Read the output before interpreting it. Warnings, silent fallbacks, and suspiciously
clean numbers are findings. A result that matches the prediction exactly on the first
attempt warrants more suspicion than one that does not.

**Decision: shared.** The assistant spots anomalies; the researcher judges which
threaten the result.

- **Researcher:** decides which anomalies are fatal, which are noise, and which change
  the interpretation.
- **Assistant:** report what in the log is surprising, and what would look identical
  if the code were subtly wrong. Do not omit a warning because the headline result
  looks correct.
- **Record:** `prompts/KNOWN_PATTERNS.md` when the cause generalizes past this run.

---

## Step 10 - Interpret the evidence

Write what the evidence supports, using `analysis/ANALYSIS_TEMPLATE.md`. State the
assessment plainly: `SUPPORTED`, `REFUTED`, `PARTIALLY SUPPORTED`, or `INCONCLUSIVE`.
Say where the result holds and where it breaks; boundaries transfer to the next
problem more usefully than headline numbers.

Negative results stay. An approach that failed, recorded with its reason, saves the
next person the same week.

**Decision: shared.** Drafting and computation can be delegated. What the result means
for the field cannot.

- **Researcher:** writes the assessment and the significance in their own words. A
  conclusion that cannot be restated without the draft in front of them has not yet
  been reached.
- **Assistant:** draft against the template and compute honestly, including
  uncertainty. Report where the result fails as prominently as where it holds. Do not
  characterize a statistically detectable difference as important, and do not remove a
  negative result.
- **Record:** `analysis/ANALYSIS_XX.md`. Interpretation goes here; the raw record in
  `results/logs/` stays unchanged.

Once the analysis exists, record in one line what the iteration showed:

```bash
python3 scripts/record_outcome.py 7 --outcome "Criterion met, 0.71 against a 0.65 target"
```

This refuses until `analysis/ANALYSIS_07.md` exists, because an outcome recorded before the
run was read is a guess wearing a record's clothes. The wording is yours; the helper holds
no opinion about what the outcome says. It appends to the `Outcome history` table every
time, so a conclusion you later revise still shows what it was revised from, and it fills
the state row's outcome cell only while that cell still holds the placeholder it wrote.
Revise the row yourself afterwards — `smairt check` reports any row that has drifted from
the history.

---

## Step 11 - Decide whether to revise, advance, or stop

Compare the result to the criterion from step 4, then choose: revise and iterate,
advance to the next phase or question, or stop.

**Decision: researcher only.** Refinements are always available, so an assistant will
keep proposing them. Recognizing that a direction is exhausted is a scientific
judgment, and abandoning it is frequently the correct one.

- **Researcher:** makes the call and records why. A documented stop is a result; an
  undocumented one is a gap.
- **Assistant:** state the strongest case for continuing and the strongest case for
  stopping. Do not decide, and do not keep proposing refinements once the researcher
  has stopped.
- **Record:** the hypothesis file status, and the `Next Steps` section of the analysis,
  which seeds the following hypothesis:

```
ANALYSIS_XX.md -> Next Steps -> HYPOTHESIS_YY.md -> script_YY.py -> ANALYSIS_YY.md
```

When you advance or stop, say which iteration you would stand behind and what it is
evidence for:

```bash
python3 scripts/select_result.py 7 --claim "The wider layer exceeds the 0.65 target"
```

For a panel, name the probes that support the claim; the helper reads the recorded kind and
refuses to collapse a panel into a single success:

```bash
python3 scripts/select_result.py 7 --claim "Three probes exceed the target" \
  --probes "probe_01,probe_03,probe_07"
```

With the Paper capability, add `--paper` to append the same decision, including its exact
log path, to `FINAL_MANIFEST.md`.

Several attempts at the same question produce competing evidence, and without this the
question of which one you would report is settled by whoever reads the folder last.
Selection reads `analysis/ITERATION_LOG.md` rather than the filesystem, so an iteration
that was never recorded cannot be presented as a result. Selecting again is a revision and
is recorded as one, not a silent replacement.

---

## Step 12 - Update the study report and contribution record

At synthesis points, update `analysis/STUDY_REPORT.md` from
`analysis/STUDY_REPORT_TEMPLATE.md`. The `Report Status` field tracks progress, so the
filename stays stable whether the project is ongoing or finished.

Checkpoints: a coherent finding has emerged, a phase transition is near, the project is
being handed over, a paper is being drafted, or the work is complete.

The report synthesizes and does not replace the numbered analyses. It is written as a
research report, not as an account of how the code was produced.

**Decision: shared for the report. Every entry in
`prompts/intellectual_contribution.md` is the researcher's to accept, rewrite, or
delete.**

- **Researcher:** writes the conclusions. Owns the contribution record: confirm an
  observation, reword it, or remove it. An entry you did not agree to is not a
  contribution you made.
- **Assistant:** assemble the audit trail and results matrix from the project files.
  Notice contributions as they happen and record them as observations, marked as
  unreviewed until the researcher confirms them. Do not present an unreviewed observation
  as the researcher's own account, and do not describe the report as a demonstration or a
  template exercise.
- **Record:** `analysis/STUDY_REPORT.md` and `prompts/intellectual_contribution.md`.

The assistant observes here for a reason. A researcher frequently does not recognise their
own contribution in the moment — rejecting a proposed approach and naming a better one
feels like ordinary conversation, not a recorded decision. Leaving the record to
self-reporting means it is written by whoever happens to feel like taking credit, which is
useless as evidence. An assistant is better placed to notice precisely because it has no
stake in the answer.

What that does *not* mean is that the assistant decides. It notices and writes down; the
researcher confirms, corrects, or deletes. An observation that has not been reviewed stays
visibly unreviewed, so nobody later mistakes an assistant's wording for the researcher's.

The record is not a step-12 chore. Every step above names a decision owner, so it
accumulates from following the loop rather than being reconstructed at the end. What
belongs in it: the framing of the question, choices made between presented options,
directions the researcher proposed, interpretations that went beyond what was drafted, and
decisions to pivot or stop.

---

## The loop

```
Question -> Hypothesis -> Criterion -> Script -> Run -> Log -> Analysis -> Decision
                ^                                                            |
                +------------------ Next Steps ------------------------------+
```

Each pass tests one prediction, produces evidence that outlives the session, records an
interpretation, and updates what the project knows.

---

## Division of labour, summarized

| Owned by the researcher | Shared | The assistant can own |
|---|---|---|
| The research question | Background and constraints | Writing the script |
| The hypothesis | Experiment design | Running it and retaining the log |
| The decision criterion | Inspecting anomalies | Drafting analysis text |
| Revise, advance, or stop | Interpretation | Assembling the audit trail |
| What counts as novel | The study report | Flagging failures |
| The contribution record | | Surveying prior work |

Assistants are effective at reaching the current state of a field quickly, writing and
running code, comparing approaches systematically, holding conventions steady across
many experiments, and spotting anomalies in output.

Assistants are not to be relied on for citation accuracy, for deciding what would
refute a hypothesis, for recognizing when to abandon an approach, or for judging
whether a result matters. The first is a factual limitation. The others are the
decisions that make the work the researcher's own.
