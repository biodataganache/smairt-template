# SMAIRT Orchestrated Mode: Keeping the AI On Track Without Blowing the Budget

## Summary

Running a long SMAIRT project through a chat-based AI causes two problems. The AI
slowly loses track of what it's doing, and the conversation gets expensive. This
proposal adds an optional **orchestrated mode** that addresses both at low cost.

Three findings drive the design:

1. The biggest cost saving is nearly free. Have the AI keep a short "where we are
   now" file and start a fresh chat whenever the current one gets bloated. This one
   habit cuts cost by roughly 3x to 5x and keeps the AI focused. We call it
   compaction.
2. A second "helper" AI improves focus, not cost. Handing messy execution work to a
   throwaway sub-agent keeps the main chat clean, but it costs about the same in
   total. Use it for reliability, not savings.
3. A short status file forgets things. So memory is split into three layers: a tiny
   live status, a curated list of lasting findings, and the full archive on disk.
   That way a result from ten iterations ago is never lost or misapplied.

The recommendation is to build the cheap memory habits first, since they are the
real win, and make the helper-AI part opt-in for later.

---

## 1. What this is trying to do

There are two goals and three constraints.

| | What it means |
|---|---|
| Goal A: stay on track | The AI shouldn't drift, repeat itself, or forget a decision made 20 steps back. |
| Goal B: keep the chat small | A bloated conversation is slow, forgetful, and costly. The active chat should stay lean. |
| Constraint 1: tight budget | Total spend matters, not just chat size. |
| Constraint 2: one thing at a time | We are not running experiments in parallel. |
| Constraint 3: tool-agnostic | It has to work in Roo, Cursor, Windsurf, Claude, or a plain browser chat. |

One tension is worth naming up front. Goal B (small chat) can work against
Constraint 1 (low cost). Moving work into a helper AI shrinks the main chat, but the
helper has to re-read context to get oriented, so it can raise total spend. Section 6
settles that tradeoff with numbers.

---

## 2. The idea everything rests on

Every message you send re-sends the whole conversation so far. The AI has no memory
between turns except the transcript you hand it, so each new turn pays for all the
text that came before it, again.

That single fact explains the design.

A long chat is a recurring cost. Say a messy debugging session dumps 15,000 tokens of
errors and logs into the chat early on. If you then take 30 more turns, you re-send
that mess about 30 times. It is not paid once. It is paid on every turn that follows.

A throwaway side-chat is a one-time cost. Do that same debugging in a disposable
helper that hands back a two-line summary, and the main chat never carries the 15,000
tokens at all.

Starting fresh erases the cost. Write down where you are, open a new chat, and the
accumulated junk is gone.

So there are two ways to stop paying: delegate the mess to a helper, or restart the
chat from a short summary. Restarting is far cheaper, because nobody has to re-read
context to get oriented.

---

## 3. The design: two roles, not three

The original sketch had three roles: a Manager, an Architect, and Builders. Under "no
parallelism plus tight budget," the middle role isn't worth its keep, so we fold it
in. That leaves two roles.

```
+-------------------------------------------------------------+
|  ORCHESTRATOR: the one steady chat you work in              |
|    - talks to you                                           |
|    - owns the question, the plan, and the memory files      |
|    - designs each experiment and interprets the results     |
|    - hands messy execution down; never debugs inline        |
+---------------+---------------------------------------------+
                |  a self-contained "Build Brief"
                v
        +----------------------------------------+
        |  BUILDER: a throwaway helper           |
        |    - spawned only for execution-heavy  |
        |      steps; skipped otherwise          |
        |    - writes one script, runs it,       |
        |      fights the bugs                   |
        |    - hands back a short "Build Report" |
        |      (key numbers and the log path)    |
        +----------------------------------------+
```

The Orchestrator is the single chat you actually talk to. It holds the question, the
plan, and the memory, and it does the thinking: designing experiments, reading
results, deciding what comes next.

A Builder is a disposable worker. When a step is going to be messy, with lots of
debugging or big logs, the Orchestrator writes it a self-contained brief and lets it
do the dirty work in its own throwaway context. The Builder returns a clean summary
and is then discarded.

Why drop the standalone Architect? A separate, always-running designer AI would be a
second long chat to keep alive and re-send every turn. That doubles the recurring
cost from Section 2, with nothing to parallelize against. Experiment design is
occasional thinking, not a job that needs its own permanent chat. So the Orchestrator
just does the design work when it's time, then goes back to driving. One
authoritative chat is also the best thing for staying on track (Goal A).

---

## 4. Memory: think of it as a lab notebook

A lean main chat only works if the project's memory lives in files, not in the chat
history. But you can't put everything in one file. A short status note forgets
long-term findings, and a giant log is too big to reread every session.

So memory has three layers, like a good lab notebook.

| Layer | File(s) | What it's for | Stays small? | Reread every session? |
|-------|---------|---------------|--------------|----------------------|
| 1. Live status | `PROJECT_STATE.md` | Where are we right now? | Yes, overwritten | Yes |
| 2. Findings ledger | `FINDINGS.md` (plus `KNOWN_PATTERNS.md` for code and errors) | What have we learned that's still true? | Yes, curated | Yes |
| 3. Archive | `analysis/`, `results/logs/`, `hypotheses/` | Every result, ever | No | No, searched when needed |

Nothing is ever thrown away. The status note churns, the ledger is hand-curated, and
the archive is permanent. Layer 1 keeps the AI on task, layer 2 stops it forgetting
or repeating work, and layer 3 is the permanent record you can always dig into.

### 4.1 The live status note (`PROJECT_STATE.md`)

One short file the Orchestrator keeps current: the question, the current hypothesis,
the last result, the next step, and any loose ends. It is reread at the start of
every session. Keep it short. If a section is growing, that content belongs in the
ledger or the archive instead.

### 4.2 The findings ledger (`FINDINGS.md`): never write a bare verdict

This is what stops the AI forgetting what it learned. The rule: a finding is never a
flat statement like "X doesn't work." It is always a claim plus the context it was
found in. Every entry records its scope, so the AI can tell two runs apart and knows
when an old result no longer applies.

```
### F-017: Frequency weighting improves AUPRC
- Claim:      frequency weighting helps the model
- Scope:      real dataset (N approx 50k), phase 03_real, iter 17
- Evidence:   analysis/ANALYSIS_17.md, results/logs/script_17*.log
- Status:     established
- Supersedes: F-007 (it failed on synthetic data, N approx 500, a small-sample artifact)
```

Status can be `established`, `provisional` (seen only in a narrow setting),
`needs-revalidation` (the situation changed, so don't trust it yet), or
`superseded-by F-NN`.

### 4.3 What to do when the situation changes

This is the case you raised. A result from a small early dataset may not hold on a
bigger one later. The rule:

> When the dataset, scale, or phase changes, treat older narrow-context findings as
> provisional. Re-test before relying on them, record the new result with its new
> scope, and link the two. Keep both. "X fails on small data but works at scale" is a
> richer, truer finding than either run alone.

This is SMAIRT's existing "works within certain boundaries" idea, written down as
structured data instead of left implicit.

### 4.4 The habit that makes memory work: promotion

Forgetting happens when a useful result stays buried in one iteration's analysis file
and is never lifted up. So the rule is: when a result graduates from "a number from
one run" to "a fact that should shape what we do next," the Orchestrator promotes it
into `FINDINGS.md`, with full scope. And before designing any new experiment, it
reads the ledger and skims recent analyses first. That is what stops duplicate work
and stale assumptions. Promotion is the single behavior that makes long-term recall
actually work.

### 4.5 Compaction and caching

Compaction means save and restart. When the chat gets long, update
`PROJECT_STATE.md`, start a fresh chat, and reload from layers 1 and 2, digging into
the archive only when you need a specific old result. This clears accumulated junk
better than any helper AI. SMAIRT already has the plumbing for it in
`compile_for_ai.py` and `CONTEXT_INDEX.md`.

Caching means put the stable stuff first. Keep unchanging content (role instructions,
conventions, the ledger) at the top of every prompt, so the AI's prompt cache can
serve it at a fraction of the price. Section 6 has the numbers.

---

## 5. What goes to a Builder, and what stays put

The rule is simple. Send the high-volume, low-value work down, and keep the small,
valuable thinking up top.

| Send to a Builder | Keep in the Orchestrator |
|-------------------|--------------------------|
| Running and re-running scripts | The research question |
| Fighting errors and stack traces | Hypotheses and design decisions |
| Wading through big logs | The conclusions drawn from results |
| Exploring unfamiliar files | Deciding the next step |

A Builder absorbs the token-heavy mess and hands back a clean, short residue. Two
contracts make that work, and both are just fill-in templates.

The Build Brief (Orchestrator to Builder) gives the exact script to write, its
inputs, expected outputs, where to log, which conventions apply, and what "done"
means. The Builder starts cold and reads nothing else, so the brief has to stand on
its own.

The Build Report (Builder to Orchestrator) gives what ran, where the log is, the key
numbers, and any surprises. It is kept short, because it is the only thing that
re-enters the main chat.

One discipline matters: the Orchestrator checks the Build Report against the actual
log file, never taking the Builder's "it worked" on faith. This is the same
skepticism SMAIRT already applies to anything an LLM claims.

---

## 6. What it costs

The numbers below come from a simple, explicit model, not from measuring a real
project. They are meant for comparing the options, not for billing. The full
arithmetic is in the Appendix; this section gives the result.

We compare three ways of working over a session of about five iterations.

- A, Naive: one long chat, no restarts, no helper. Junk piles up and gets re-sent
  every turn.
- B, Restart habit: one chat, but you compact and restart between iterations.
- C, Helper too: the restart habit plus a Builder for execution.

### The bottom line, in dollars (Claude Opus 4.8 rates)

| Way of working | Without caching | With caching |
|----------------|-----------------|--------------|
| A, Naive | about $8 to $9 per session | about $7 to $8 (caching can't help the junk) |
| B, Restart habit | about $3 to $4 | about $1.50 to $2.50 |
| C, Helper too | about $3 to $4 | about $1.50 to $2.50 |

Those figures use this rate card (per 1M tokens):

| Token type | Rate |
|------------|------|
| Input (uncached) | $5.00 |
| Output | $25.00 |
| Cache write (5 minute) | $6.25 |
| Cache write (1 hour) | $10.00 |
| Cache read | $0.50 |

The number that makes everything cheap is the cache read rate. A cached token costs
about 10% of a fresh one ($0.50 versus $5.00). That is why putting stable content
first and reusing it pays off so much.

### Three things to take away

1. The restart habit is the big lever. Going from A to B is roughly a 3x to 5x drop
   in cost, and it is nearly free to adopt. Do this no matter what else you decide.
2. The helper AI is roughly cost-neutral. B and C cost about the same. The helper
   moves the mess out of the main chat rather than removing it, and pays a small
   re-orientation cost, so total spend is a wash or slightly worse.
3. So the helper is a focus tool, not a savings tool. Its real payoff is a main chat
   that never sees debugging noise: steadier, more predictable, and protected from one
   ugly debugging session bloating everything.

### When the helper does save money

Only when a single iteration is dominated by heavy execution, with lots of debugging
or big outputs. In that case the helper caps the main chat's size, while a single
chat would re-send a growing mess across that iteration's turns. For short, clean
experiments it is a small loss, because you pay to orient the helper for little gain.

> Rule of thumb: use a Builder for iterations you expect to be debugging-heavy. For
> quick, clean experiments, skip it and rely on restart plus the memory files.

---

## 7. When not to use a Builder

- Short, clean experiments, where orienting the helper costs more than the mess it
  avoids.
- Tightly-coupled reasoning that needs the whole evolving picture in one place.
- Anything where you are iterating conversationally with the Orchestrator yourself.

The default is one chat plus the restart habit. Reach for a Builder only when a step
is going to be messy. Builders should be opt-in per step, never automatic.

---

## 8. How we would build it

Because SMAIRT has to run anywhere, the mode is just prompt files, handoff templates,
and a small index, not a hardwired sub-agent API. It then degrades gracefully. In
Claude Code the Orchestrator can spawn real sub-agents as Builders. In a plain
browser chat, the same files are driven by a human doing each role in turn.

A cookiecutter option turns it on:

```json
{ "agent_topology": ["single", "orchestrated"] }
```

- `single` (default): one chat plus the memory and restart protocol.
- `orchestrated`: adds the Orchestrator and Builder roles and the handoff templates.

Files the orchestrated option adds:

```
PROJECT_STATE.md                 # layer 1: live status
FINDINGS.md                      # layer 2: findings ledger
prompts/COMPACTION.md            # how to save state, promote findings, and restart
prompts/roles/ORCHESTRATOR.md    # the steady-chat role: design, review, delegate
prompts/roles/BUILDER.md         # the cold-start helper contract
prompts/handoffs/BUILD_BRIEF.md  # Orchestrator to Builder template
prompts/handoffs/BUILD_REPORT.md # Builder to Orchestrator template
```

It also extends `prompts/CONTEXT_INDEX.md` into an index of which files each role
reads, and reuses `scripts/compile_for_ai.py` for reloading a fresh chat.

### Suggested order, most value first

| Priority | Do this | Why |
|----------|---------|-----|
| P0 | `PROJECT_STATE.md` plus the restart protocol (`COMPACTION.md`) | The 3x to 5x cost win; helps both goals; nearly free |
| P0 | `FINDINGS.md` plus the promotion and re-validation rules | Long-term recall; stops duplicate work and stale findings |
| P0 | Put stable content first so it caches | Multiplies every other saving |
| P1 | The Orchestrator and Builder roles plus handoff templates, run by hand | Proves the workflow with no infrastructure |
| P2 | Wire the Orchestrator to spawn a real Builder in one tool (Claude Code) | A working reference implementation |
| P3 | The `agent_topology` cookiecutter option | Package it up |

Start at P0. For a budget-conscious, one-experiment-at-a-time project, almost all the
benefit is there before any helper AI exists.

---

## 9. Risks and open questions

The Builder could claim success it didn't earn. The fix is to check its report
against the actual log file, not its words.

Restarting could lose context. The fix is to keep `PROJECT_STATE.md` disciplined and
use `compile_for_ai.py`. We should write a checklist of what must survive a restart.

The ledger could rot. Bare verdicts could creep back in, or results could get logged
without scope. The fix is to require a `Scope:` line in every entry and to mark
anything out of scope as `needs-revalidation` rather than trusting or deleting it.

Where does the human sit? At the Orchestrator level, the same place
`intellectual_contribution.md` and novel-direction spotting already live.

Measure before committing to Builders. The Section 6 numbers are a model. We should
instrument one real project to confirm that B and C cost about the same before
investing in the helper-AI tier.

---

## 10. Next steps

1. Ship P0: the live status file, the restart protocol, and cache-friendly ordering.
2. Try the Orchestrator and Builder roles by hand on one debugging-heavy iteration.
3. Instrument token usage on a real project to check the cost model.
4. If it holds up, add the `agent_topology` cookiecutter option.

---

## Appendix: the cost arithmetic

The dollar figures in Section 6 come from this model. It is deliberately simple, and
every assumption is listed so you can re-run it with your own numbers.

### Assumptions

| Symbol | Meaning | Value |
|--------|---------|-------|
| `B` | Orchestrator's base context (role, status, conventions) | 8k tokens |
| `E` | Execution and debugging noise generated per iteration | 15k tokens |
| `T` | Turns per iteration | 6 |
| `N` | Iterations in the session | 5 |
| | Builder priming (re-reading the brief and conventions) | 6k tokens |
| | "Cost" approximates total input tokens re-sent across all turns; output is ignored for simplicity |

### The three architectures (no caching)

A, Naive single chat. Junk accumulates across iterations and is re-sent every turn:

```
input ~ T * sum[ B + (i-1)*E + E/2 ]  for i = 1..5
      = 6 * [5*8k + 15k*10 + 5*7.5k] = 6 * 227.5k ~ 1.37M tokens
```

B, Restart between iterations. Each iteration starts fresh, so junk only builds up
within one iteration:

```
input ~ N * T * (B + E/2) = 5 * 6 * 15.5k ~ 465k tokens   (plus about 10k for compaction) ~ 0.47M
```

C, Restart plus Builder. The execution noise lives in the Builder, not the main chat,
and the Orchestrator runs about 3 lean turns per iteration:

```
orchestrator ~ N * 3 * (B + 1k report)   = 5 * 3 * 9k   ~ 135k
builder      ~ N * (prime + T * E/2)     = 5 * (6k+45k) ~ 255k
total                                                     ~ 0.39M to 0.56M
```

### Summary

| Architecture | Input tokens per session | vs. naive | Main-chat size |
|--------------|--------------------------|-----------|----------------|
| A, Naive | about 1.37M | 1.0x | grows without bound |
| B, Restart | about 0.47M | about 2.9x cheaper | small, resets each iteration |
| C, Restart plus Builder | about 0.39M to 0.56M | about 2.4x to 3.5x cheaper | smallest, stays clean within an iteration |

### With caching

Caching serves repeated prefix tokens at about 10% of full price. It helps B and C
far more than A, because most of their context is stable and reusable, while A is
dominated by ever-changing junk that can't be cached.

| Architecture | Input tokens per session, cached |
|--------------|----------------------------------|
| A | about 1.2M (caching barely helps) |
| B | about 0.25M |
| C | about 0.27M |

Multiply these by the rate card in Section 6 to get the dollar figures. The takeaway
is the same at every step. The restart habit is the lever. The Builder buys focus,
not savings.
