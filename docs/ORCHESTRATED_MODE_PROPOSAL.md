# SMAIRT Orchestrated Mode Proposal: Lean Two-Tier Agents for Focus & Context Control

## Executive Summary

This document proposes a new SMAIRT workflow mode — **orchestrated mode** — whose
goal is to keep the AI on task and keep the main thread's context window small,
under **strong budget constraints and no parallelization**.

The headline conclusion, derived from a token-cost model in §8:

> **Compaction is the cost lever. Delegation is the focus lever. Layered memory
> is the recall lever.**
> Aggressively externalizing state and restarting the thread ("compaction") cuts
> token spend ~3–5× and is nearly free. Adding a disposable "builder" sub-agent on
> top is roughly **cost-neutral** for sequential work — it buys reliability and a
> clean main thread, *not* token savings. It only becomes a net cost *win* when a
> single iteration is dominated by heavy execution/debugging, or when work
> parallelizes (which we are explicitly not doing). And a lean working-state file
> alone *forgets* — so memory is split into three layers (§6) so old, context-
> scoped findings are never lost or misapplied.

So the recommended design is **two tiers, not three**: a single lean
**Orchestrator** (Manager + Architect fused) plus optional **transient Builders**,
sitting on top of a mandatory **three-layer memory protocol** (working state +
scoped findings ledger + permanent archive).

---

## 1. Goals and Constraints

| | |
|---|---|
| **Goal A** | Keep the LLM on task across a long research project |
| **Goal B** | Keep the main thread's context window small |
| **Constraint 1** | Strong token budget — total spend matters, not just main-thread size |
| **Constraint 2** | No parallelization — work is sequential (one experiment at a time) |
| **Constraint 3** | Stay tool-agnostic (Roo, Cursor, Windsurf, Claude, ChatGPT) |

Goals A and B partly conflict with Constraint 1: offloading work to a sub-agent
shrinks the main thread but raises *total* tokens, because a cold sub-agent
re-reads context to orient itself. The cost model in §8 resolves the tradeoff.

---

## 2. Core Insight: Recurring vs. One-Time Context Cost

Every turn on a conversation thread re-sends that thread's **entire accumulated
context** as input tokens. Therefore:

- **Main-thread context is a recurring tax.** 15k tokens of debugging noise added
  to the main thread early in a session is re-transmitted on *every* subsequent
  turn. Over 30 turns that single mess costs ~450k tokens.
- **A disposable sub-context is a one-time cost.** The same work done in a builder
  that returns a two-line summary costs its tokens once; the main thread never
  carries it.
- **A restart erases the tax entirely.** Writing state to a file and starting a
  fresh thread drops accumulated noise for ~free.

This is why naive single-threading is expensive: noise accumulates and is paid
repeatedly. Both compaction and delegation attack that recurring tax — but
compaction attacks it far more cheaply, because it doesn't re-pay orientation.

---

## 3. Architecture: Two Tiers

```
┌──────────────────────────────────────────────────────────┐
│  ORCHESTRATOR  (stable thread; Manager + Architect fused) │
│  • talks to the user                                      │
│  • owns the research question + north-star state          │
│  • designs experiments, writes hypotheses, reviews results│
│  • delegates execution; never debugs inline               │
└───────────────┬──────────────────────────────────────────┘
                │  Build Brief (self-contained)
                ▼
        ┌───────────────────────┐
        │  BUILDER (transient)  │   ← spawned only when an iteration is
        │  • writes one script  │     execution-heavy; otherwise skipped
        │  • runs & debugs it   │
        │  • returns Build Report (short summary + log path)
        └───────────────────────┘
```

### Why not three tiers (no separate standing Architect)

A separate, *persistent* Architect was the part of the original idea that
parallelization would have justified. Without parallelization it is pure overhead:

- A second standing thread is a second context to keep alive and re-inject every
  turn — it doubles the "recurring tax" of §2 for the planning layer.
- It adds a Manager↔Architect handoff round-trip with nothing to parallelize
  against.
- Experiment design is *intermittent thinking*, not a process that needs its own
  permanent thread. The Orchestrator wears the "architect hat" (or uses a
  plan-mode) when designing, then returns to driving.

Fusing Manager + Architect keeps one authoritative thread holding the north-star
— which is also the best thing for Goal A (staying on task).

---

## 4. Roles Mapped to SMAIRT Artifacts

The artifacts are the shared memory. Agents coordinate by reading/writing files,
not by passing long messages.

| Role | Stable? | Owns (writes) | Reads | Never does |
|------|---------|---------------|-------|------------|
| **Orchestrator** | yes (persistent thread) | `PROJECT_STATE.md`, `background/`, `plans/PLAN_*.md`, `hypotheses/HYPOTHESIS_XX.md`, `analysis/ANALYSIS_XX.md` | prior analyses, `KNOWN_PATTERNS.md` | inline debugging; long log parsing |
| **Builder** | no (disposable) | `experiments/script_XX.py`, `results/logs/` | the Build Brief + conventions + `KNOWN_PATTERNS.md` only | design decisions; user interaction |

---

## 5. Handoff Contracts

Builders start **cold**, so the brief must be self-contained. Templated documents:

- **Build Brief (Orchestrator → Builder):** the exact script to write, inputs,
  expected outputs, where to log, which conventions / `KNOWN_PATTERNS` entries
  apply, and the definition of done. Assume the builder has read nothing else.
- **Build Report (Builder → Orchestrator):** what ran, log path, key numbers,
  anomalies, errors hit. Kept short — this is the only thing that re-enters the
  main thread.

The Orchestrator validates the report **against the log file**, never trusting the
builder's claim of success (same skepticism SMAIRT already applies to LLM
literature claims).

---

## 6. Memory & State Architecture (the cheap, mandatory layer)

A lean main thread only works if memory lives in **files, not the chat**. But a
single overwritten state file is just *working memory* — it forgets long-term
findings. So memory is **three layers**, each with a different job. This is the
part that does most of the work for both goals, at near-zero cost.

| Layer | File(s) | Holds | Size | Overwritten? | Loaded each session? |
|-------|---------|-------|------|--------------|----------------------|
| **1. Working state** | `PROJECT_STATE.md` | "Where we are right now" | tiny | yes | yes |
| **2. Findings ledger** | `FINDINGS.md` (+ `KNOWN_PATTERNS.md` for code/errors) | "What we've learned that's still true" | small, curated | append/edit | yes |
| **3. Archive** | `analysis/`, `results/logs/`, `hypotheses/` | every result, ever | large | never | no — searched on demand |

Nothing is ever deleted: the working state churns, the ledger is curated, the
archive is permanent. Layer 1 keeps the AI on task; layer 2 prevents forgetting and
duplicate work; layer 3 is the searchable system of record.

### 6.1 Working state — `PROJECT_STATE.md`

A single north-star file the Orchestrator keeps current: research question, current
hypothesis, last result, next step, open threads. Re-injected on every fresh start.
This is what keeps the AI on task.

### 6.2 Findings ledger — scoped, conditional, never bare verdicts

A finding is **not** a universal truth ("X doesn't work"); it is a claim bound to
the context it was found in. Every entry carries its **scope**, so the model can
tell runs apart and knows when a result no longer applies. Bare verdicts are
forbidden. Entry template:

```
### F-017: Frequency weighting improves AUPRC
- Claim:      frequency weighting helps the model
- Scope:      real dataset (N≈50k), phase 03_real, iter 17
- Evidence:   analysis/ANALYSIS_17.md, results/logs/script_17*.log
- Status:     established
- Supersedes: F-007 (failed on synthetic N≈500 — small-sample artifact)
```

Status values: `established` · `provisional` (narrow context, untested at scale) ·
`needs-revalidation` · `superseded-by F-NN`.

### 6.3 The re-validation rule (when context changes)

> When the dataset, scale, or phase changes, findings from a narrower context
> become **provisional**. Re-validate before relying on them; record the new result
> with its new scope and link it to the old one. Keep both — *"X fails on small data
> but works at scale"* is a richer, truer finding than either run alone.

This makes SMAIRT's existing "works within certain boundaries" principle and its
phase-transition guidance ("validate whether results transfer") into structured data.

### 6.4 The promotion habit

Forgetting happens when a key result never leaves its iteration's analysis file. So:
when a result graduates from "a number in one iteration" to "a fact that should
shape future work," the Orchestrator **promotes** it into `FINDINGS.md` with full
scope. Before designing any new experiment, it reads `FINDINGS.md` and searches
recent `analysis/` files — this is what stops duplicate work and stale verdicts.
Promotion is the single behavioral rule that makes long-term recall work.

### 6.5 Compaction & caching

- **Compaction** — when the Orchestrator thread grows long, write state to
  `PROJECT_STATE.md`, start a fresh thread, rehydrate from layers 1–2 (and search
  layer 3 as needed). Resets context bloat better than any sub-agent. Reuse the
  existing `compile_for_ai.py` and `CONTEXT_INDEX.md` primitives.
- **Cacheable prefix** — put stable content (role prompt, conventions, ledger) at
  the front of every prompt so prompt caching covers it.

---

## 7. What to Offload vs. Keep

Offload **high-token, low-residual-value** work; keep **low-token, high-value** work.

| Send to Builder | Keep in Orchestrator |
|-----------------|----------------------|
| running / re-running scripts | the research question |
| error & stack-trace iteration | hypotheses and design decisions |
| big log parsing | conclusions drawn from analysis |
| file / codebase exploration | the next-step decision |

The builder's job is to absorb the token-heavy mess and hand back a clean residue.

---

## 8. Cost Model and Estimates

> **These are illustrative estimates from an explicit model, not measurements.**
> They are for *relative* comparison of architectures. Assumptions are stated so
> you can re-run them with your own numbers.

### Assumptions

| Symbol | Meaning | Value |
|--------|---------|-------|
| `B` | Orchestrator base context (role + state + conventions) | 8k tokens |
| `E` | Execution/debugging noise generated per iteration | 15k tokens |
| `T` | Turns per iteration | 6 |
| `N` | Iterations in the session | 5 |
| — | Builder priming (brief + conventions re-read) | 6k tokens |
| — | Cost ≈ cumulative **input** tokens (context re-sent each turn); output ignored for clarity |

### Three architectures, no caching

**A — Single thread, naive** (no compaction, no builder). Noise accumulates across
iterations and is re-sent every turn:

```
input ≈ T · Σ[ B + (i-1)·E + E/2 ]  for i=1..5
      = 6 · [5·8k + 15k·10 + 5·7.5k] = 6 · 227.5k ≈ 1.37M tokens
```

**B — Single thread + compaction** (restart between iterations; no builder). Each
iteration starts fresh; noise only builds *within* an iteration:

```
input ≈ N · T · (B + E/2) = 5 · 6 · 15.5k ≈ 465k tokens   (+~10k compaction) ≈ 0.47M
```

**C — Orchestrator + Builder + compaction**. Execution noise lives in the builder,
not the main thread; orchestrator runs ~3 lean turns/iteration:

```
orchestrator ≈ N · 3 · (B + 1k report)          = 5 · 3 · 9k   ≈ 135k
builder      ≈ N · (prime + T · (E/2))           = 5 · (6k+45k) ≈ 255k
total                                                            ≈ 0.39M–0.56M
```
(≈0.56M with builder priming re-paid each iteration; ≈0.39M if the builder prime
is small/stable.)

### Summary (no caching)

| Architecture | Est. session input | vs. naive | Main-thread context |
|--------------|--------------------|-----------|---------------------|
| **A** Naive single thread | ~1.37M | 1.0× | grows unbounded |
| **B** Single + compaction | ~0.47M | **~2.9× cheaper** | small, resets each iteration |
| **C** Orchestrator + builder | ~0.39M–0.56M | ~2.4–3.5× cheaper | smallest, stays clean *within* an iteration |

### With prompt caching

Caching (~0.1× on cached prefix tokens) helps B and C far more than A, because
their stable-prefix fraction is large while A is dominated by non-cacheable
accumulating noise:

| Architecture | Est. session input, cached |
|--------------|----------------------------|
| **A** | ~1.2M (caching barely helps; noise isn't cacheable) |
| **B** | ~0.25M |
| **C** | ~0.27M |

### In dollars (Claude Opus 4.8 rates)

Rate card (per 1M tokens):

| Token type | Rate |
|------------|------|
| Input (uncached) | $5.00 |
| Output | $25.00 |
| Cache write — 5-min TTL (1.25×) | $6.25 |
| Cache write — 1-hour TTL (2×) | $10.00 |
| Cache read (~0.1×) | $0.50 |

The decisive ratio: a **cache read is ~10% of a fresh input token** ($0.50 vs $5.00)
— the reason the cacheable-prefix + compaction layer is so cheap. Applying these
rates to the per-session token estimates above (input-dominated; ~$1–2 of output
added per session):

| Architecture | No caching | With caching |
|--------------|-----------|--------------|
| **A** Naive single thread | **~$8–9** | **~$7–8** (noise isn't cacheable) |
| **B** Single + compaction | **~$3–4** | **~$1.5–2.5** |
| **C** Orchestrator + builder | **~$3–4** | **~$1.5–2.5** |

The dollar view confirms the token view: the **~$8 → ~$3** drop is almost entirely
the **compaction + memory protocol** (P0), not the builder tier (B ≈ C). Under a
tight budget, the P0 layer is where the savings live; builders are a focus/
reliability choice, roughly cost-neutral.

### What the model says

1. **Compaction is the dominant lever** — ~3–5× cheaper than naive, essentially
   free to implement. Do this regardless of anything else.
2. **The builder is ~cost-neutral vs. compaction alone** for sequential work
   (B ≈ C). It moves the execution noise out of the main thread rather than
   eliminating it, and re-pays orientation — so total tokens are a wash, sometimes
   slightly worse.
3. **The builder's payoff is non-cost:** a main thread that never sees execution
   noise stays more focused (Goal A) and more predictable, and avoids a single
   long debugging slog bloating the active context mid-iteration.

### Sensitivity — when the builder *does* save tokens

The builder becomes a net cost **win** when, within one iteration, execution noise
is large relative to design work — i.e. `E` is big or debugging takes many turns.
In the limit of heavy debugging, the builder caps the orchestrator at `B` while a
single thread would re-send a growing `E` across that iteration's turns. It is a
net **loss** when iterations are short and clean (the 6k priming dominates).

> **Rule of thumb:** use a builder for iterations you expect to be debugging-heavy;
> for short, clean experiments, skip it and stay single-thread + compaction.

---

## 9. When NOT to Use a Builder

- Short, clean experiments (priming cost > noise avoided).
- Tightly-coupled reasoning that needs the full evolving context in one place.
- Anything where the human is iterating conversationally with the Orchestrator.

Default to **single thread + compaction**; reach for a builder only on heavy
execution. The mode should make builders *opt-in per iteration*, not automatic.

---

## 10. Implementation as a SMAIRT Mode

Tool-agnostic: express the mode as **role prompt files + handoff templates + a
router**, not a hardwired sub-agent API. It then degrades gracefully — in Claude
Code the Orchestrator can spawn real Task sub-agents as builders; in a plain web
chat the same files are driven by the human switching hats.

### New cookiecutter variable

```json
{ "agent_topology": ["single", "orchestrated"] }
```

- `single` (default): one thread + state/compaction protocol.
- `orchestrated`: adds Orchestrator/Builder roles and handoff templates.

### Files to add

```
PROJECT_STATE.md                    # layer 1: working state (both topologies)
FINDINGS.md                         # layer 2: scoped findings ledger (both topologies)
prompts/roles/ORCHESTRATOR.md       # role: design + review + delegate, never debug inline
prompts/roles/BUILDER.md            # cold-start contract; self-contained
prompts/handoffs/BUILD_BRIEF.md     # Orchestrator → Builder template
prompts/handoffs/BUILD_REPORT.md    # Builder → Orchestrator template
prompts/COMPACTION.md               # when/how to write state, promote findings, and restart
```

Extend the existing `prompts/CONTEXT_INDEX.md` into a per-role router (which files
each role reads). Reuse `scripts/compile_for_ai.py` as the rehydration primitive.

---

## 11. Priority & Phased Rollout

| Priority | Step | Why |
|----------|------|-----|
| **P0** | `PROJECT_STATE.md` + `prompts/COMPACTION.md` | The ~3–5× cost lever; helps both goals; near-free |
| **P0** | `FINDINGS.md` ledger + promotion habit + re-validation rule | Long-term recall; prevents duplicate work & stale, out-of-scope verdicts |
| **P0** | Cacheable-prefix ordering in role/context files | Multiplies every other saving |
| **P1** | Orchestrator + Builder role files + handoff templates (manual, one human switching hats) | Validates the protocol with zero infra |
| **P2** | Wire Orchestrator → real Builder sub-agent in one tool (Claude Code Task) | Reference implementation |
| **P3** | `agent_topology` cookiecutter variable + conditional generation | Productize the mode |

Start at P0. Most of the benefit for a budget-constrained, sequential workflow is
there before any agent hierarchy exists.

---

## 12. Open Questions & Risks

- **Builder result hallucination** — mitigated by Orchestrator validating against
  the log file, not the report text.
- **Compaction losing context** — mitigated by `PROJECT_STATE.md` discipline and
  `compile_for_ai.py`; needs a checklist of what must survive a restart.
- **Findings ledger drift** — bare verdicts creep back in, or scale-dependent
  results get recorded without scope. Mitigated by forbidding bare verdicts in the
  entry template and requiring a `Scope:` field; an out-of-scope finding should be
  marked `needs-revalidation`, never silently trusted or deleted.
- **Human-in-the-loop placement** — the human stays at the Orchestrator tier,
  where `intellectual_contribution.md` and novel-direction detection already live.
- **Measure before productizing** — the §8 numbers are a model; instrument a real
  project to confirm the B≈C result before committing to the builder tier.

---

## Next Steps

1. Implement P0 (`PROJECT_STATE.md` + compaction protocol + cacheable ordering).
2. Trial the Orchestrator/Builder roles manually on one debugging-heavy iteration.
3. Instrument token usage on a real project to validate the cost model.
4. If validated, add the `agent_topology` cookiecutter variable.
