# SMAIRT Orchestrated Mode: Keeping the AI On Track Without Blowing the Budget

## Summary

Running a long SMAIRT project through a chat-based LLM causes two failure modes. The
model loses the thread of what it's doing, and per-turn cost grows without bound. This
proposal adds an optional **orchestrated mode** that addresses both, using an
orchestrator-worker agent pattern on top of a file-based memory protocol.

Three findings drive the design:

1. The largest cost reduction is nearly free. Externalize project state to a small
   file and restart the conversation when the active context grows large. This
   "compaction" loop cuts token spend by roughly 3x to 5x and is the main lever for
   keeping the model on task.
2. A disposable worker sub-agent buys context isolation, not token savings. Delegating
   execution-heavy work to a cold-start Builder keeps the orchestrator's context
   window small, but total token spend is roughly unchanged because the Builder
   re-pays context to orient itself.
3. A single overwritten state file is working memory only, and working memory forgets.
   So memory is split into three tiers: a small live-state file, a curated ledger of
   durable findings, and the append-only archive on disk. This preserves and correctly
   scopes results from many iterations back.

The recommendation is to implement the memory and compaction protocol first, since it
carries most of the benefit, and gate the worker tier behind an opt-in flag.

---

## 1. Goals and constraints

| | Definition |
|---|---|
| Goal A: stay on task | The model should not drift, repeat solved work, or violate an established constraint across a long project. |
| Goal B: bound the active context | The orchestrator's context window should stay small. A large window is slower, more error-prone, and more expensive per turn. |
| Constraint 1: budget | Total token spend matters, not just per-turn context size. |
| Constraint 2: sequential | Experiments run one at a time. There is no parallel fan-out to amortize multi-agent overhead against. |
| Constraint 3: tool-agnostic | The mode must run in Roo, Cursor, Windsurf, Claude Code, or a browser chat, so it cannot depend on any one tool's sub-agent API. |

Goals A and B partly conflict with Constraint 1. Offloading work to a sub-agent
reduces the orchestrator's window but increases total tokens, because a cold sub-agent
re-reads context to orient. Section 6 quantifies the tradeoff and shows it nets out
close to neutral for sequential work.

---

## 2. The cost mechanic everything follows from

The Messages API is stateless. The model retains nothing between turns except the
transcript you resend, so every request carries the full message array as input
tokens. Cost per turn scales with the size of the accumulated context, and that
context is billed again on each subsequent turn.

This gives three primitives:

A long conversation is a recurring cost. Suppose a debugging burst adds about 15k
tokens of stack traces and log output to the transcript early in a session. Over the
next 30 turns that 15k is resent on every request, so it is billed on the order of 30
times, not once. The expensive quantity is not the work itself but its residence time
in the active context.

A disposable side-context is a one-time cost. Performing the same debugging in a
throwaway sub-agent that returns a short summary keeps those 15k tokens out of the
orchestrator transcript entirely. They are billed once, inside the sub-agent.

A restart resets the recurring cost. Writing state to disk and starting a fresh
conversation truncates the prompt prefix back to a small, fixed base, dropping the
accumulated transcript from all future requests.

Two mechanisms therefore attack the recurring cost: delegation and restart. Restart is
strictly cheaper, because it does not require any agent to re-pay orientation. The one
caveat is that a restart discards the warm prompt cache (see Section 6), so the first
post-restart request writes the cache cold.

---

## 3. Architecture: a two-tier orchestrator-worker

The original sketch had three standing roles: Manager, Architect, and Builders. Under
"sequential plus budget-constrained," the Architect as a separate persistent thread is
net overhead, so it is fused into the orchestrator. The result is the standard
supervisor pattern with two roles.

```
+-------------------------------------------------------------+
|  ORCHESTRATOR: the single persistent context                |
|    - the only role that talks to the user                   |
|    - owns the research question, the plan, and memory state |
|    - designs experiments and interprets results             |
|    - delegates execution; does not debug inline             |
+---------------+---------------------------------------------+
                |  Build Brief (self-contained handoff)
                v
        +----------------------------------------+
        |  BUILDER: a stateless worker           |
        |    - spawned only for execution-heavy  |
        |      steps; otherwise skipped          |
        |    - writes one script, runs it,       |
        |      iterates on errors                |
        |    - returns a Build Report            |
        |      (key results plus log path)       |
        +----------------------------------------+
```

The Orchestrator is the single persistent context the user interacts with. It holds
the durable state (question, plan, memory) and performs the high-value, low-token
work: experiment design, result interpretation, and the decision about what to run
next.

A Builder is a stateless worker spawned for one execution-heavy step. It starts cold,
with no access to the orchestrator's conversation, so its entire input is the Build
Brief. It performs the high-token, low-residual-value work (running scripts, iterating
on errors, parsing logs) in an isolated context window, returns a compact Build
Report, and is then discarded.

Why fuse the Architect rather than keep it standing? A second persistent thread is a
second context to keep warm and resend on every turn, which doubles the recurring cost
of Section 2 for the planning layer, and it adds an orchestrator-to-architect handoff
round trip with nothing to parallelize against. Experiment design is intermittent
reasoning, not a continuous process that needs its own thread, so the orchestrator
absorbs it. Keeping one authoritative context is also the strongest move for Goal A.

---

## 4. Memory: a three-tier model

A small orchestrator context is only viable if project memory lives in files rather
than in the transcript. A single file cannot serve all roles at once: an overwritten
status file loses long-term findings, and a full log is too large to reload every
session. So memory is tiered by access pattern.

| Tier | File(s) | Role | Mutation | Loaded per session |
|------|---------|------|----------|--------------------|
| 1. Working state | `PROJECT_STATE.md` | Current position of the project | Overwritten | Always |
| 2. Findings ledger | `FINDINGS.md` (plus `KNOWN_PATTERNS.md` for code and errors) | Durable, curated claims that are still true | Append and edit | Always |
| 3. Archive | `analysis/`, `results/logs/`, `hypotheses/` | Full provenance record | Append-only | On demand, retrieved by search |

Nothing is deleted. Tier 1 churns, tier 2 is curated, tier 3 is immutable history.
Tier 1 keeps the model on task, tier 2 provides recall and prevents repeated work,
and tier 3 is the system of record for audit and retrieval.

### 4.1 Working state (`PROJECT_STATE.md`)

A small file the orchestrator keeps current: research question, current hypothesis,
last result, next action, and open threads. It is reloaded at the start of every
session and after every restart. It is overwritten, not appended. Growth in any
section is a signal that the content belongs in the ledger or the archive.

### 4.2 Findings ledger (`FINDINGS.md`): claims are conditional, not absolute

This tier is what gives the model long-term recall. The invariant: a finding is never
an unscoped verdict like "X does not work." It is a claim paired with the context in
which it was observed. Every entry records its scope and status as structured fields,
so two runs of the same intervention are distinguishable and an out-of-scope result is
flagged rather than silently trusted.

```
### F-017: Frequency weighting improves AUPRC
- Claim:      frequency weighting improves the target metric
- Scope:      real dataset (N approx 50k), phase 03_real, iter 17
- Evidence:   analysis/ANALYSIS_17.md, results/logs/script_17*.log
- Status:     established
- Supersedes: F-007 (failed on synthetic data, N approx 500; small-sample artifact)
```

Status is one of `established`, `provisional` (observed only in a narrow scope),
`needs-revalidation` (scope has since changed; not currently trustworthy), or
`superseded-by F-NN`. The `Supersedes` and `superseded-by` links form a small directed
graph, so the history of a claim is reconstructable rather than overwritten.

### 4.3 Re-validation on scope change

This is the case you raised: a result established on a small early dataset may not
transfer to a larger one. The rule:

> When the dataset, scale, or phase changes, demote older narrow-scope findings to
> `needs-revalidation`. Re-test before relying on them, record the new result under
> its new scope, and link it to the prior finding. Retain both entries. "X fails at
> N=500 but holds at N=50k" is a stronger claim than either observation alone, because
> it localizes the boundary.

This formalizes SMAIRT's existing "works within certain boundaries" guidance and its
phase-transition advice ("validate whether results transfer") as machine-checkable
structure rather than prose convention.

### 4.4 Promotion as the recall mechanism

Recall fails when a useful result remains buried in a single iteration's analysis file
and is never lifted into a tier that loads each session. The mechanism that prevents
this is promotion: when a result graduates from "one run's number" to "a fact that
constrains future work," the orchestrator writes it into `FINDINGS.md` with full
scope. Symmetrically, before designing any new experiment, the orchestrator reads the
ledger and searches recent analyses, which is what blocks duplicate work and the use
of stale assumptions. Promotion plus the pre-design read is the load-bearing behavior
of the whole memory model.

### 4.5 Compaction and prompt caching

Compaction is the externalize-and-restart loop. When the orchestrator context grows
large, write current state to `PROJECT_STATE.md`, start a fresh conversation, and
rehydrate from tiers 1 and 2, retrieving from tier 3 only as needed. This bounds the
prompt prefix far more cheaply than any sub-agent. SMAIRT already provides the
primitives: `compile_for_ai.py` to bundle state and `CONTEXT_INDEX.md` to route what
to read.

Prompt caching is prefix-keyed. The provider caches on the exact byte prefix of the
prompt, and any change invalidates everything after the change point, so stable
content (role instructions, conventions, the ledger) belongs at the front of the
prompt and volatile content at the end. A cache read is billed at roughly 0.1x of a
fresh input token, so a well-ordered prefix is the single largest multiplier on every
other saving. Note the interaction with compaction: a restart discards the warm cache,
so compact on a cadence that keeps cache writes amortized rather than restarting every
turn.

---

## 5. Delegation policy

The partition rule: route high-token, low-residual-value work to a Builder, and retain
low-token, high-value reasoning in the orchestrator.

| Route to a Builder | Retain in the Orchestrator |
|--------------------|----------------------------|
| Running and re-running scripts | The research question |
| Iterating on errors and stack traces | Hypotheses and experiment design |
| Parsing large logs | Interpretation and conclusions |
| Exploring unfamiliar files | The next-step decision |

A Builder absorbs the token-heavy execution and returns a compact residue. Two typed
handoffs make this work, both as fill-in templates.

The Build Brief (orchestrator to Builder) specifies the exact script to write, its
inputs, expected outputs, the log destination, the applicable conventions, and the
definition of done. Because the Builder starts cold, the brief must be a complete,
standalone spec.

The Build Report (Builder to orchestrator) returns what ran, the log path, the key
results, and any anomalies. It is kept short, since it is the only artifact that
re-enters the orchestrator context.

The orchestrator validates the Build Report against the log file rather than the
report text, on the principle that a generated success claim is not evidence. This is
the same skepticism SMAIRT already applies to model-sourced literature claims.

---

## 6. Cost model

The figures below are from an explicit parametric model, not measurements. They are
for comparing architectures, not for billing. The derivation is in the Appendix; this
section states the result.

The comparison is over a session of about five iterations:

- A, Naive: one persistent context, no restarts, no worker. Execution noise
  accumulates and is resent every turn.
- B, Compaction: one context with externalized state and a restart between iterations.
- C, Compaction plus worker: B with a Builder for execution-heavy steps.

### Dollar estimate (Claude Opus 4.8 rates)

| Architecture | No caching | With caching |
|--------------|------------|--------------|
| A, Naive | about $8 to $9 per session | about $7 to $8 (accumulated noise is not cacheable) |
| B, Compaction | about $3 to $4 | about $1.50 to $2.50 |
| C, Compaction plus worker | about $3 to $4 | about $1.50 to $2.50 |

Rate card (per 1M tokens):

| Token type | Rate |
|------------|------|
| Input (uncached) | $5.00 |
| Output | $25.00 |
| Cache write (5 minute TTL) | $6.25 |
| Cache write (1 hour TTL) | $10.00 |
| Cache read | $0.50 |

The decisive ratio is the cache read rate. A cache read is about 10% of a fresh input
token ($0.50 versus $5.00), which is why a stable, well-ordered prefix dominates the
economics.

### Interpretation

1. Compaction is the dominant lever. A to B is roughly a 3x to 5x reduction and is
   near-free to implement. It should be adopted independent of any other decision.
2. The worker tier is approximately cost-neutral. B and C are within noise of each
   other, because the Builder relocates execution tokens out of the orchestrator
   rather than eliminating them, and pays a re-orientation cost to do so.
3. The worker's value is therefore context isolation, not spend. Its payoff is an
   orchestrator context that never ingests execution noise, which is more stable and
   predictable and is insulated from a single long debugging burst inflating the
   active window.

### Sensitivity

The worker becomes a net token win when, within one iteration, execution noise is
large relative to design work (large E or many debugging turns). In that regime the
Builder caps the orchestrator at its base context B, whereas a single thread resends a
growing E across that iteration's turns. It is a net loss when iterations are short and
clean, since the Builder's priming cost dominates the noise avoided.

> Heuristic: use a Builder for iterations expected to be debugging-heavy; for short,
> clean experiments, stay single-context and rely on compaction plus the memory files.

---

## 7. When not to use a Builder

- Short, clean experiments, where priming the worker costs more than the noise avoided.
- Tightly-coupled reasoning that requires the full evolving context in one place.
- Interactive iteration where the user is in a tight loop with the orchestrator.

The default is single-context plus compaction. A Builder is reached for only when a
step is execution-heavy, and the mode should make Builders opt-in per step rather than
automatic.

---

## 8. Implementation

Because the mode must be tool-agnostic, it is expressed as prompt files, handoff
templates, and a routing index rather than a hardwired sub-agent API. It then degrades
gracefully across tools. In Claude Code the orchestrator can spawn real Task sub-agents
as Builders. In a browser chat the same role files are executed by a human switching
roles. The protocol is identical; only the execution substrate differs.

A cookiecutter flag selects the topology:

```json
{ "agent_topology": ["single", "orchestrated"] }
```

- `single` (default): one context plus the memory and compaction protocol.
- `orchestrated`: adds the orchestrator and Builder roles and the handoff templates.

Files added by the orchestrated topology:

```
PROJECT_STATE.md                 # tier 1: working state
FINDINGS.md                      # tier 2: findings ledger
prompts/COMPACTION.md            # write state, promote findings, restart
prompts/roles/ORCHESTRATOR.md    # design, review, delegate; no inline debugging
prompts/roles/BUILDER.md         # cold-start worker contract
prompts/handoffs/BUILD_BRIEF.md  # orchestrator to Builder template
prompts/handoffs/BUILD_REPORT.md # Builder to orchestrator template
```

The mode also extends `prompts/CONTEXT_INDEX.md` into a per-role read index (which
files each role loads for which task) and reuses `scripts/compile_for_ai.py` as the
rehydration primitive after a restart.

### Rollout order, highest value first

| Priority | Step | Rationale |
|----------|------|-----------|
| P0 | `PROJECT_STATE.md` plus the compaction protocol (`COMPACTION.md`) | The 3x to 5x cost lever; serves both goals; near-free |
| P0 | `FINDINGS.md` plus the promotion and re-validation rules | Long-term recall; blocks duplicate work and stale, out-of-scope claims |
| P0 | Cache-friendly prefix ordering in role and context files | Multiplies every other saving |
| P1 | Orchestrator and Builder role files plus handoff templates, run by hand | Validates the protocol with no infrastructure |
| P2 | Wire the orchestrator to spawn a real Builder in one tool (Claude Code Task) | Reference implementation |
| P3 | The `agent_topology` cookiecutter flag and conditional generation | Productize |

Start at P0. For a sequential, budget-constrained project, almost all the benefit is
realized by the memory and compaction layer, before any agent hierarchy exists.

---

## 9. Risks and open questions

Builder result fabrication. A worker can claim a run succeeded without it running
clean. Mitigation: the orchestrator validates against the log file, not the report
text.

Context loss on restart. Compaction can drop state that was not externalized.
Mitigation: keep `PROJECT_STATE.md` disciplined, use `compile_for_ai.py`, and define a
checklist of what must survive a restart.

Ledger drift. Unscoped verdicts can reappear, or scale-dependent results can be logged
without scope. Mitigation: require a `Scope:` field per entry and demote out-of-scope
entries to `needs-revalidation` rather than trusting or deleting them.

Human-in-the-loop placement. The human stays at the orchestrator tier, where
`intellectual_contribution.md` and novel-direction detection already live.

Validate the cost model. The Section 6 figures are modeled, not measured. Instrument
one real project to confirm the B-approximately-C result before committing to the
worker tier.

---

## 10. Next steps

1. Ship P0: working-state file, compaction protocol, and cache-friendly ordering.
2. Trial the orchestrator and Builder roles by hand on one debugging-heavy iteration.
3. Instrument token usage on a real project to validate the cost model.
4. If validated, add the `agent_topology` cookiecutter flag.

---

## Appendix: cost derivation

The dollar figures in Section 6 follow from this parametric model. It is intentionally
coarse, and every assumption is listed so it can be re-run with measured values.

### Parameters

| Symbol | Meaning | Value |
|--------|---------|-------|
| `B` | Orchestrator base context (role, state, conventions) | 8k tokens |
| `E` | Execution and debugging noise generated per iteration | 15k tokens |
| `T` | Turns per iteration | 6 |
| `N` | Iterations per session | 5 |
| | Builder priming (brief plus conventions reread) | 6k tokens |
| | Cost is approximated as total input tokens resent across turns; output is omitted for clarity |

### Architectures (no caching)

A, Naive single context. Noise accumulates across iterations and is resent every turn:

```
input ~ T * sum[ B + (i-1)*E + E/2 ]  for i = 1..5
      = 6 * [5*8k + 15k*10 + 5*7.5k] = 6 * 227.5k ~ 1.37M tokens
```

B, Restart between iterations. Each iteration starts fresh, so noise only accumulates
within an iteration:

```
input ~ N * T * (B + E/2) = 5 * 6 * 15.5k ~ 465k tokens   (plus about 10k for compaction) ~ 0.47M
```

C, Restart plus Builder. Execution noise lives in the Builder, not the orchestrator,
which runs about 3 lean turns per iteration:

```
orchestrator ~ N * 3 * (B + 1k report)   = 5 * 3 * 9k   ~ 135k
builder      ~ N * (prime + T * E/2)     = 5 * (6k+45k) ~ 255k
total                                                     ~ 0.39M to 0.56M
```

### Summary

| Architecture | Input tokens per session | vs. naive | Orchestrator context |
|--------------|--------------------------|-----------|----------------------|
| A, Naive | about 1.37M | 1.0x | grows without bound |
| B, Compaction | about 0.47M | about 2.9x cheaper | small, resets each iteration |
| C, Compaction plus Builder | about 0.39M to 0.56M | about 2.4x to 3.5x cheaper | smallest, clean within an iteration |

### With caching

Caching serves repeated prefix tokens at about 0.1x of full price. It benefits B and C
far more than A, because their context is mostly a stable, reusable prefix, while A is
dominated by non-cacheable accumulating noise.

| Architecture | Input tokens per session, cached |
|--------------|----------------------------------|
| A | about 1.2M (caching barely helps) |
| B | about 0.25M |
| C | about 0.27M |

Multiplying by the Section 6 rate card yields the dollar figures. The conclusion is
invariant across the no-cache and cached views: compaction is the cost lever, and the
Builder buys context isolation rather than token savings.
