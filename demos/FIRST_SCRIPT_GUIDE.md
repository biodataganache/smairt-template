# What a Good First SMAIRT Script Looks Like

This guide is for the moment right after you generate a fresh SMAIRT project and
ask: **what should the first script actually do?**

Short answer: the first script should be **small, checkable, and useful**. It
should prove that the project is pointed in the right direction before you spend
iterations on larger analyses.

---

## The job of the first script

A good first SMAIRT script is **not** the whole project. It is a first scientific
step that helps you answer one of these questions:

1. Did we understand the background question correctly?
2. Did we build or load the data correctly?
3. Can we recover a planted or hand-checkable signal?
4. Are the basic assumptions and units sane?
5. Do we have a reproducible starting point for the next iteration?

If the first script does those things, it is good enough.

---

## The simplest rule

Your first script should usually do **one narrow validation task** before doing
any ambitious modeling.

That often means one of these patterns:

- **Synthetic validation:** generate a small dataset with known truth and show
  the method recovers it.
- **Hand-checkable calculation:** compute values for a few tiny examples whose
  answers you can verify yourself.
- **Load-and-inspect step:** read a file or table and print enough summary
  information to prove it was parsed correctly.
- **Baseline before model:** compute the simplest baseline first, before training
  or fitting anything complex.
- **One figure, one decision:** produce a single plot or summary table that lets
  you decide what the next step should be.

---

## What “good” looks like in practice

A good first script is usually:

- **small** — one script, one purpose
- **fast** — runs in seconds or a few minutes, not an hour
- **deterministic** — uses a fixed random seed if randomness is involved
- **interpretable** — prints the values or summaries a human needs to review
- **grounded** — tied directly to the research question in
  `background/01_initial_question.md`
- **reproducible** — writes logs and follows SMAIRT naming conventions
- **honest** — reports caveats, assumptions, and obvious limitations

A bad first script is usually the opposite: huge, slow, multi-purpose,
unvalidated, and hard to inspect.

---

## What the first script should usually contain

In most demos, a solid first script includes these ingredients:

### 1. A narrow goal

At the top, the script should make clear what it is testing.

Examples:

- “Validate that the synthetic generator plants the intended motif.”
- “Check that MW and GRAVY calculations match hand-computed expectations.”
- “Confirm the digestion rule produces the expected peptides on toy examples.”
- “Measure the no-skill baseline before training a model.”

### 2. Minimal inputs

Use the smallest dataset or examples that can still answer the question.

That could be:

- 3–5 toy examples
- a tiny synthetic cohort
- a subset of rows from a real dataset
- one known reference case plus one counterexample

### 3. Explicit assumptions

If the script depends on units, thresholds, motif positions, pKa tables,
sequence lengths, mask rates, or random seeds, state them clearly in code and in
printed output.

### 4. Human-readable output

The script should print enough information that a scientist can inspect whether
it makes sense.

Examples of useful output:

- summary statistics
- example rows / sequences
- expected vs observed values
- baseline metrics
- a single sanity-check figure

### 5. A next-step implication

A good first script should make the next iteration obvious.

Examples:

- “The synthetic signal is recoverable, so now train the simplest model.”
- “The parser works, so now compute the real metric on the full dataset.”
- “The baseline is weak, so now test whether a simple classifier beats it.”

---

## A simple anatomy for the first script

This is the rough shape many good first scripts follow:

1. **State the purpose** in a short module docstring or header comment.
2. **Load or generate minimal data**.
3. **Run one core calculation**.
4. **Print a compact summary** of what happened.
5. **Save any figure or table** needed for later review.
6. **Preserve the complete tracked log** under `results/logs/` after running it.

You do not need a perfect software package in iteration 1. You need a clean,
reviewable scientific step.

---

## Examples across these demos

### Example pattern: enzyme kinetics

A good first script does **not** jump to a full noisy fitting study.
It starts by generating a tiny synthetic Michaelis-Menten curve with known
parameters and checks whether the fit recovers them reasonably.

### Example pattern: peptide digestion

A good first script does **not** begin with a large proteome.
It starts with short hand-checkable sequences and verifies that cleavage rules
produce exactly the expected peptides.

### Example pattern: protein properties

A good first script does **not** begin with a classifier leaderboard.
It first validates MW, pI, and GRAVY calculations against known or
hand-computable values.

### Example pattern: protein language model

A good first script does **not** begin by training a transformer immediately.
It first proves that the synthetic corpus really contains the planted motif,
correct masking setup, and a baseline the model should beat.

### Example pattern: epidemic modeling (SIRD)

A good first script does **not** start by sweeping every parameter and fitting a
real outbreak curve. It first integrates the SIRD equations for one scenario and
verifies that the population is conserved (S + I + R + D = N) with sensible,
non-negative curves, before varying R0 in later scripts.

---

## Common failure modes

These are the most common “bad first script” mistakes.

### 1. It tries to do the whole project

If the first script loads all data, trains a model, tunes hyperparameters,
generates five figures, and writes conclusions, it is too much.

### 2. It skips validation

If the first script assumes the parser, generator, metrics, or units are
correct without checking them, it is too risky.

### 3. It has no known answer

If nothing in the first script is checkable, you cannot tell whether success is
real or accidental.

### 4. It is too large for review

If the AI generates hundreds of lines across many files in the first step, the
human reviewer loses control.

### 5. It produces output but not interpretation

Raw numbers alone are not enough. The script should make it possible to say what
those numbers mean.

---

## A checklist you can use before approving the first script

Before you approve AI-generated code, ask:

- Does this script test **one** clear idea?
- Is there a known answer, baseline, or sanity check?
- Can I explain why this is the right first step?
- Will it run quickly enough for tight iteration?
- Are the assumptions visible?
- Will the output help me decide the next step?
- Is it writing to the expected SMAIRT locations?
- Is it small enough that I can actually review it?

If most of those answers are “yes,” the first script is probably good.

---

## A starter prompt you can paste into Zoo Code

Use this after the assistant has read `prompts/AI_CONTEXT.md`,
`prompts/CODE_CONVENTIONS.md`, and `background/01_initial_question.md`.

```text
Based on the background question and the SMAIRT code conventions, propose the
smallest useful first script for this project.

The script should do one narrow validation task before any ambitious modeling.
It must be fast to run, easy to review, and scientifically checkable. Before
writing code, explain:
1. what exact question the first script will answer,
2. what known truth / baseline / sanity check it will use,
3. what files it will create,
4. what output I should inspect, and
5. how the result will determine the next iteration.

Keep the scope to a single numbered script in the correct experiments folder.
```

---

## The key mindset

The first script is not meant to impress anyone.
It is meant to **reduce uncertainty**.

In SMAIRT, that is how momentum starts: one small validated step, then one more,
then one more, until the project leaves behind a reviewable scientific trail.
