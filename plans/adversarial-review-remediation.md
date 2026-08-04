# Adversarial review of the branch, and the plan to repair what it found

Reviewed `main` at `78f22af` against the branch head, plus the complete generated workspace,
on four axes: repository standards, fidelity to the accepted specs, the scientific process
the scaffold teaches, and the interface that hands a researcher into it.

The branch is sound in its parts. Nearly every finding below is a **seam** — two pieces that
are each correct and that disagree with each other. That is the expected failure mode when a
workflow is added to a scaffold that was restored from an older one, and it is why the
findings cluster so tightly around the iteration record.

## Two decisions that shape everything below

Both were made by the researcher during this review and are treated as settled.

**1. One numbering authority.** Every numbered scientific script is an iteration and appears
in the record. Utilities and exploration get a different name and location, and never consume
an iteration number.

**2. Default solid, rigor configurable.** The default must be a sound, easy basis. Anything
that is a *stance* on how strict the scientific method should be here belongs in per-project
Advanced settings, so a researcher can build on the base without the tool imposing one school
of practice. What never becomes optional is the philosophical grounding: a criterion before a
result, evidence that outlives the session, negative results retained, and the researcher
owning the judgment.

---

## What the review found

### The central defect

The branch built an append-only iteration record, and then the documented path walks around it.

[`docs/12_STEPS.md:180`](src/smairt/assets/scaffold/docs/12_STEPS.md:180) and the project front
door at [`scaffold/README.md:24`](src/smairt/assets/scaffold/README.md:24) both teach
`cp` a template plus [`new_script.py`](src/smairt/assets/scaffold/scripts/new_script.py:17).
Neither mentions [`new_track.py`](src/smairt/assets/scaffold/scripts/new_track.py:24),
[`new_iteration.py`](src/smairt/assets/scaffold/scripts/new_iteration.py:33), or
[`select_result.py`](src/smairt/assets/scaffold/scripts/select_result.py:28). A researcher who
follows the twelve steps exactly produces a project whose
[`ITERATION_LOG.md`](src/smairt/assets/scaffold/analysis/ITERATION_LOG.md) is empty and whose
`SELECTED_NN.md` never exists. The record the branch exists to create is optional on the only
path the documentation teaches.

Worse, the two helpers draw from the same number pool without agreeing.
[`new_script.py:29`](src/smairt/assets/scaffold/scripts/new_script.py:29) reimplements the scan
that [`existing_iterations()`](src/smairt/assets/scaffold/scripts/shared/iterations.py:62) owns,
and writes at [`new_script.py:40`](src/smairt/assets/scaffold/scripts/new_script.py:40) with no
`exists()` guard — so it can overwrite a script `new_iteration.py` created. That is a direct
breach of the `CONTEXT.md` invariant that researcher work is never overwritten, and the guard
test at [`test_scaffold_content.py:158`](tests/test_scaffold_content.py:158) does not catch it
because it greps for `rmtree` and `unlink`, not for an unguarded `write_text`.

### The append-only rule contradicts itself

The accepted rule is that a helper may append and may never modify an existing line. But
[`iterations.py:98`](src/smairt/assets/scaffold/scripts/shared/iterations.py:98) writes
`Outcome` as `[Record after interpreting]`, and then
[`scripts/README.md:90`](src/smairt/assets/scaffold/scripts/README.md:90) instructs the reader
to fill that cell in — editing a line the rule forbids editing, in the same table that says
rows are "appended and never rewritten"
([`ITERATION_LOG.md:9`](src/smairt/assets/scaffold/analysis/ITERATION_LOG.md:9)).

The design error is treating one row as both *the attempt was made* and *this is what it
showed*. Those are two events at two times. One row cannot be append-only and hold both.

### Restored guidance still teaches the superseded model

The copy-and-correct pass fixed the retired directory tree. It did not catch four semantic
contradictions that came back with the prose:

| Contradiction | Where it survives | Why it bites |
|---|---|---|
| A track is a script-name letter prefix with its own numbering | [`CODE_CONVENTIONS.md:30`](src/smairt/assets/scaffold/prompts/CODE_CONVENTIONS.md:30), [`AI_CONTEXT.md:176`](src/smairt/assets/scaffold/prompts/AI_CONTEXT.md:176) | `script_B01` is invisible to [`existing_iterations()`](src/smairt/assets/scaffold/scripts/shared/iterations.py:66); following the documented convention silently corrupts numbering |
| An iteration produces a hypothesis file | [`AI_CONTEXT.md:60`](src/smairt/assets/scaffold/prompts/AI_CONTEXT.md:60) | Contradicts the PI's definition: an iteration is a unit of work that *references* hypotheses |
| Hypotheses are `H01` | [`scripts/README.md:34`](src/smairt/assets/scaffold/scripts/README.md:34), [`ANALYSIS_PLAN.md:169`](src/smairt/assets/scaffold/analysis/ANALYSIS_PLAN.md:169) | Helpers mint `HYPOTHESIS_01` ([`new_track.py:42`](src/smairt/assets/scaffold/scripts/new_track.py:42)); the log column cannot be joined |
| The assistant writes the contribution record | [`intellectual_contribution.md:104`](src/smairt/assets/scaffold/prompts/intellectual_contribution.md:104), [`AI_CONTEXT.md:216`](src/smairt/assets/scaffold/prompts/AI_CONTEXT.md:216) | [`12_STEPS.md:321`](src/smairt/assets/scaffold/docs/12_STEPS.md:321) says the assistant must not write entries at all |

The fourth needs care, because the contradiction is real but the resolution the researcher wants
is the opposite of what the prohibition implies.

A researcher frequently does not recognize their own contribution in the moment. Expecting them
to notice and record it unprompted means the record is written by whoever happened to feel
self-congratulatory, which is worse than useless as evidence. An assistant is better placed to
notice "you just rejected my approach and proposed a different one" precisely because it has no
stake in the answer.

So the assistant should observe and track objectively, and the researcher retains sole authority
to agree, disagree, edit, or delete. What is wrong today is not that the assistant writes — it is
that [`12_STEPS.md:321`](src/smairt/assets/scaffold/docs/12_STEPS.md:321) flatly forbids writing
while [`AI_CONTEXT.md:216`](src/smairt/assets/scaffold/prompts/AI_CONTEXT.md:216) instructs it, so
an assistant reading both cannot comply with either. The fix is to make `12_STEPS.md` describe the
actual division: the assistant proposes and records observations, the researcher owns the record
and every entry in it, and an unreviewed observation is visibly unreviewed rather than
indistinguishable from a researcher's own words.

### Selection and reporting are advisory where they were meant to be structural

The plan required that a panel iteration name its supporting probes so a panel is never
reported as though all of it worked. [`select_result.py:73`](src/smairt/assets/scaffold/scripts/select_result.py:73)
prints a suggestion and proceeds, and nothing reads the iteration's `Kind` — so a panel can be
reported as a single point by omitting one flag. The `--paper` manifest append was specified
and never built ([`select_result.py:75`](src/smairt/assets/scaffold/scripts/select_result.py:75)
substitutes "by hand"), which reintroduces the forgettable step the append rule exists to
remove.

`select_result.py` also selects anything with a script and a log
([`select_result.py:43`](src/smairt/assets/scaffold/scripts/select_result.py:43)), so today it
will happily select a `new_script.py` output that is in no record at all.

### Evidence is thinner than the claims made about it

The workflow calls `results/logs/` canonical and requires every claimed number to be findable
there. Several gaps make that promise weaker than it reads:

- **Provenance stops at the seed.** The generated script
  ([`new_iteration.py:182`](src/smairt/assets/scaffold/scripts/new_iteration.py:182)) records no
  interpreter version, no dependency versions, no commit, no input hash, no argv, no host or
  device. A log therefore cannot be tied to the environment that produced it.
- **Real data has no checksum column** ([`data/real/README.md:13`](src/smairt/assets/scaffold/data/real/README.md:13))
  while downloaded data does ([`data/downloaded/README.md:13`](src/smairt/assets/scaffold/data/downloaded/README.md:13)).
  The phase carrying the actual claim is the one with no data identity.
- **Reruns produce competing evidence with no status.** `select_result.py` globs every matching
  log ([`select_result.py:55`](src/smairt/assets/scaffold/scripts/select_result.py:55)) with no
  exit status and no authoritative run, so three logs with different numbers are all "the
  evidence" and the researcher picks.
- **Same-second collision.** [`TeeLogger`](src/smairt/assets/scaffold/scripts/shared/logging.py:28)
  opens `"w"` against a second-resolution filename, so two fast runs overwrite one log.
- **The log row is dated at creation, not execution** ([`iterations.py:97`](src/smairt/assets/scaffold/scripts/shared/iterations.py:97)),
  so the timeline column dates intent.

### Precommitment rests on something that does not carry it

Three places assert that commit order proves the criterion preceded the result
([`12_STEPS.md:123`](src/smairt/assets/scaffold/docs/12_STEPS.md:123),
[`new_track.py:82`](src/smairt/assets/scaffold/scripts/new_track.py:82),
[`scripts/README.md:49`](src/smairt/assets/scaffold/scripts/README.md:49)). Commit dates are
author-settable and history is rewritable — and the project's own Git guidance endorses rebase
([`BEST_PRACTICE_COLLABORATIVE.md:87`](src/smairt/assets/scaffold/docs/BEST_PRACTICE_COLLABORATIVE.md:87)).

Then `new_track.py` defeats the claim by construction: it writes the hypothesis and
immediately runs the first iteration ([`new_track.py:67`](src/smairt/assets/scaffold/scripts/new_track.py:67)),
so the default path produces an empty-criteria hypothesis and a script in the same instant.

### Rigor safeguards that are absent rather than configurable

These are the domain-dependent ones, and under decision 2 they become Advanced settings rather
than hardcoded policy. Recorded here so the default is an informed choice:

- **Panel multiplicity.** A per-probe criterion applied eight times produces spurious passes,
  and "three of eight helped" is currently presented as three findings
  ([`ANALYSIS_PLAN.md:60`](src/smairt/assets/scaffold/analysis/ANALYSIS_PLAN.md:60)) with no
  adjustment, no pre-specified primary probe, and no confirmation of winners.
- **Exploratory versus confirmatory.** Unlimited `--from-iteration` chains against the same
  data are adaptive overfitting, and iteration 14 tuned on real data reads exactly like
  iteration 1. No held-out split is required anywhere.
- **Unit of inference.** [`HYPOTHESIS_TEMPLATE.md:24`](src/smairt/assets/scaffold/hypotheses/HYPOTHESIS_TEMPLATE.md:24)
  asks for metrics and "repetitions" but never the denominator, and conflates seed reruns with
  independent replicates.
- **Single-valued hypothesis status.** The framework argues at
  [`ITERATION_LOG.md:16`](src/smairt/assets/scaffold/analysis/ITERATION_LOG.md:16) that one
  verdict cannot describe a panel, then leaves exactly one overwritable status on the hypothesis
  ([`HYPOTHESIS_TEMPLATE.md:3`](src/smairt/assets/scaffold/hypotheses/HYPOTHESIS_TEMPLATE.md:3)).
- **Manifest completeness.** Nothing reconciles `FINAL_MANIFEST.md` against `SELECTED_*.md` or
  refuted hypotheses, so a manuscript can be internally consistent while omitting every
  iteration that disagreed.

### The interface hands off into nothing

Creation ends with "open the Dashboard below to launch your assistant"
([`cli.py:1670`](src/smairt/cli.py:1670)), and the dashboard
([`cli.py:1119`](src/smairt/cli.py:1119)) offers only utilities plus a one-line reply that
science happens elsewhere. Nothing in the tool ever names `docs/12_STEPS.md`,
`prompts/CONTEXT_INDEX.md`, or `new_track.py`. Staying out of scientific decisions is correct
and intended; being silent about where the workflow starts is not the same thing.

Also found, and dangerous in different ways:

- **Creation failures collapse into one line.** [`cli.py:1713`](src/smairt/cli.py:1713) catches
  cancellation, generation failure, validation failure, and `OSError` together, so a deliberate
  Ctrl-C and a disk-full write read identically.
- **A stale scaffold refuses with no route forward.** Project Check offers repairs first
  ([`cli.py:1349`](src/smairt/cli.py:1349)); [`_require_current_scaffold()`](src/smairt/project.py:841)
  then refuses, with no upgrade instruction.
- **A moved recent project ends the session** rather than returning to Home
  ([`cli.py:1733`](src/smairt/cli.py:1733)).
- **Zoo Code has no launch path at all.** [`Assistant.ZOO_CODE`](src/smairt/models.py:17) is
  absent from [`ASSISTANT_COMMANDS`](src/smairt/project.py:84), so
  [`launch_assistant()`](src/smairt/project.py:546) returns "SMAIRT cannot safely verify a Zoo
  Code launch command" and tells the researcher to consult external guidance. Zoo Code is a
  VS Code extension, so opening the workspace *is* launching it.
- **Failures print in the quietest style available.** Generator messages, including "Git
  initialization failed", render as `hint` ([`cli.py:1668`](src/smairt/cli.py:1668)).
- **`NO_COLOR` is not honored.** [`styling_enabled()`](src/smairt/appearance.py:78) exists and is
  called from nowhere, contradicting ADR 0003's explicit no-color requirement.
- **A base project is pointed at a Paper-only file.** [`CONTEXT_INDEX.md:52`](src/smairt/assets/scaffold/prompts/CONTEXT_INDEX.md:52)
  cites `iteration_review_prompt.md`, which is `condition: paper`
  ([`scaffold-blueprint.yaml:92`](src/smairt/assets/scaffold-blueprint.yaml:92)).

### Structural risks worth naming

- `new_track.py` re-invokes its sibling through `subprocess`
  ([`new_track.py:67`](src/smairt/assets/scaffold/scripts/new_track.py:67)), so a track can
  half-succeed: plan and hypothesis written, iteration absent, exit code swallowed.
- `new_track.py` inlines the hypothesis and plan bodies
  ([`new_track.py:97`](src/smairt/assets/scaffold/scripts/new_track.py:97),
  [`:157`](src/smairt/assets/scaffold/scripts/new_track.py:157)) instead of reading the shipped
  templates, so a researcher's edits to those editable starters are ignored.
- The blueprint marks `scripts/shared` as `researcher-work`
  ([`scaffold-blueprint.yaml:74`](src/smairt/assets/scaffold-blueprint.yaml:74)) while all four
  of its contents are `tool-guidance` — container and contents assert opposite policies.
- Phase strings exist in three representations, and iteration identity travels as five loose
  parameters with the kind string re-derived at
  [`new_iteration.py:84`](src/smairt/assets/scaffold/scripts/new_iteration.py:84),
  [`:148`](src/smairt/assets/scaffold/scripts/new_iteration.py:148), and
  [`:186`](src/smairt/assets/scaffold/scripts/new_iteration.py:186).
- [`cli.py`](src/smairt/cli.py:1) is 1,909 lines carrying commands, wizard, dashboard, theming,
  and label switches, with `self.visual` re-branched in every interactive method.

### Out of scope, recorded

`demos/` still ships the retired model in bulk — `iter_01 → final/`,
`finalize_iteration.py`, letter-prefix tracks — and re-enrichment explicitly excluded demos.
Left as a separate effort, noted because a newcomer reading `demos/` learns the superseded
workflow.

---

## What is already strong

Worth stating plainly, because the plan below should not disturb any of it.

- Criterion-before-code is a named step with a named owner, not a footnote.
- Decision ownership is explicit per step, and the assistant is barred from choosing criteria,
  judging novelty, or deciding to stop.
- Panel disaggregation is enforced structurally at production time, not merely advised.
- Negative results, dead ends, and documented stops are treated as results.
- Every helper is non-destructive, and the `rmtree` finalizer was deliberately not restored.
- Evidence is pointed at, never copied, so a claim cannot drift from its log.
- Output capture includes warnings and uncaught tracebacks, and editing a log is prohibited.
- Seeded scripts get their own `SCRIPT_NAME`, so two attempts cannot claim one log.
- Preview-before-write is consistent across capabilities, repairs, regeneration, and license.
- The action-token contract makes visual and fallback presentations addressable identically.
- Generation is atomic, so a failed create leaves no half-project.
- "A result that matches the prediction exactly on the first attempt warrants more suspicion."

---

## The plan

Ordered by dependency. Each stage ends with the gates green and is committable on its own.

### Stage A — One numbering authority

Fold script creation into the iteration workflow. `new_script.py` stops being a second
numbering authority: either it becomes a thin front for the shared module and records its
iteration, or it is retired and its documented uses move to `new_iteration.py`. Utilities and
exploration move off the iteration namespace entirely — a different name, a location outside
`experiments/`, and no `script_NN_` number.

Add the `exists()` guard wherever a script is written. Delete the duplicated `PHASES` map and
number scan so [`iterations.py`](src/smairt/assets/scaffold/scripts/shared/iterations.py:18) is
the only definition. Update the blueprint purposes so every helper's declared safety matches
its behavior.

*Verify:* creating N scripts by any documented route yields N contiguous iterations and N rows;
a utility script creates no row and consumes no number; no helper can overwrite an existing
script; `select_result.py` refuses a number that is not an iteration.

### Stage B — The append-only rule stops contradicting itself

**Settled by grilling.** The log must be scannable for current state *and* leave a visible trace
when an outcome is revised. A single append-only table cannot do both: iterations are created and
interpreted interleaved, so appending an outcome row per interpretation produces
create-03, create-04, outcome-03, create-05, outcome-04, and answering "what came of 03" means
scanning the whole file. My original wording inherited that defect.

**Two tables in one file.**

- **Current state** — one row per iteration, the scannable view. `new_iteration.py` appends the
  row with an outcome placeholder it owns.
- **Outcome history** — append-only beneath it, gaining a dated line each time an outcome is
  first recorded or revised. Never edited.

**A new helper, `record_outcome.py`**, refuses unless `analysis/ANALYSIS_NN.md` exists, so an
outcome cannot be recorded before it has been interpreted. That enforces the ordering the
workflow already claims without the helper holding any opinion about what the outcome says, and
gives an assistant one unambiguous command to run after drafting an analysis — which is exactly
where the record gets dropped today.

**The safety rule narrows rather than the behavior.** It becomes:

> A helper may create a file that does not exist, append to a record whose format it owns, and
> replace a placeholder it wrote itself. It may never alter researcher-authored text.

So on first recording the helper appends the history line *and* fills the placeholder, and no
information is lost because the history holds every value. On a **revision** the state row holds
the researcher's own prose, so the helper appends only and stops — the tool writes that row
exactly once, and every later change to a conclusion is the researcher's. The asymmetry is the
rule working, not a gap.

`smairt check` gains a drift diagnostic: a state row whose outcome disagrees with the latest
history line. Structural detection, no scientific judgment, and it is what tells the researcher a
row needs updating after a revision.

Date the row by execution rather than creation, or carry both.

*Verify:* recording an outcome appends a history line and fills only a helper-written
placeholder; revising appends and leaves researcher prose untouched; `smairt check` reports a
stale state row and stays silent when they agree; recording is refused when no analysis file
exists; the guard test asserts no shipped guidance instructs editing researcher-authored text and
no helper writes to a row it did not create.

### Stage C — Remove the surviving contradictions

Four targeted rewrites: letter-prefix tracks give way to the track/iteration vocabulary; the
iteration-produces-a-hypothesis passage is corrected to reference; `H01` becomes
`HYPOTHESIS_01` everywhere or the helper changes — one identifier, stated once.

For the contribution record, `12_STEPS.md` changes rather than the prompts. The assistant keeps
its observing role, because a researcher often will not recognize their own contribution and an
assistant has no stake in the judgment. The record states plainly that observations are the
assistant's notes and every entry is the researcher's to accept, rewrite, or delete — and an
unreviewed observation stays visibly unreviewed, so no one later mistakes an assistant's note for
the researcher's own account. The step-12 ownership line becomes an accurate description of that
division instead of a prohibition the prompts already break.

Fix the base-project citation of the Paper-only review prompt, either by making it
unconditional or by citing it only under Paper.

*Verify:* a guard test bans the letter-prefix script pattern and the retired identifier forms; no
always-generated guidance cites a capability-conditional file; no shipped guidance both forbids
and instructs the same assistant action; an assistant observation is distinguishable from a
researcher-authored entry by reading the file alone.

### Stage D — The documented lifecycle teaches the recorded path

`12_STEPS.md` and the project README become one story: track, hypothesis with criteria
committed, iteration, run, interpret, record the outcome, select what you would report. Step 7
teaches `new_iteration.py`; step 11's record names the log; selection appears as a step rather
than only in `scripts/README.md`.

Split `new_track.py` so the criteria are written before a script exists, rather than in the
same instant — the default path must be able to demonstrate precommitment. Soften the
commit-order claim to what Git actually supports, and say what would strengthen it.

Replace the `subprocess` re-invocation with a shared call so a track cannot half-succeed, and
read the shipped hypothesis and plan templates instead of inlining them.

*Verify:* following `12_STEPS.md` verbatim from a fresh project produces a populated iteration
log and a selected result; `new_track.py --no-script` is the documented default shape; an
edited hypothesis template is reflected in what `new_track.py` writes.

### Stage E — Selection and reporting become structural

`select_result.py` reads the iteration's kind and *requires* the supporting probes for a panel
rather than suggesting them. Implement the specified `--paper` manifest append under the append
rule. Refuse selection of a non-iteration.

*Verify:* selecting a panel without probes is refused with a message naming the kind; a Paper
project gains a manifest entry from the same command; the manifest entry names the exact log.

### Stage F — Default provenance and run status

No policy, only better defaults. The generated script records interpreter and dependency
versions, the commit if the project is a repository, input identity, argv or config, and host
and device. Exit status reaches the log and the record, so a failed run is visibly failed.
Real-data provenance gains the checksum column its sibling already has. Log filenames stop
colliding within a second.

*Verify:* a generated script's log answers "what produced this" without external knowledge; a
crashed run is distinguishable from a clean one in both log and record; two immediate runs
produce two logs.

### Stage G — Rigor as per-project Advanced settings

**Settled by grilling.** Five decisions bound this stage, and together they make it much smaller
than the original sketch.

**1. Prompting is default; structure is the setting.** Explaining *why* multiplicity matters costs
nothing and teaches the method, so it ships in the default guidance. A setting governs only what
*structure* appears — the fields and sections a helper writes. Refusals are out of scope
entirely: a tool that blocks scientific work based on a preference is a tool taking a position on
the science.

**2. Shipped templates are never modified.** A setting changes what the helpers write, not the
package-owned templates, so there is no modified-file reconciliation to build and a researcher's
edited template is never touched. This follows the ownership rule
[`managed_asset_contents()`](src/smairt/project.py:822) already enforces.

**3. One project-level addendum, plus per-file fields.** A new `analysis/RIGOR.md` holds the
project's *standing commitments*, declared once, so a reader learns the rigor stance in one
place. For what genuinely varies per iteration — which probes were pre-specified, whether this run
used held-out data — `new_track.py` and `new_iteration.py` include the matching fields in files
they create from that point forward. The addendum gives those fields something to point at
instead of restating policy in every hypothesis.

**4. Four settings.** Multiplicity policy, discovery/validation separation, unit of inference, and
per-probe hypothesis status. The other two candidates from the review are delivered by better
mechanisms and are deliberately *not* settings: run provenance is unconditional in Stage F, and
manifest reconciliation is a `smairt check` diagnostic like the Stage B drift check. Per-probe
status is affordable here only because of decision 2 — helpers write the block, so the hypothesis
template's shape never changes.

**5. Every setting is a boolean; the content is the researcher's words.** A setting means only
*this project commits to declaring a policy here*. SMAIRT never names a statistical method, so it
cannot be wrong about which corrections exist and a project can express its own field's practice.
The assistant may *suggest* a policy — that is what it is good at — and the researcher approves,
edits, or rejects it. The tool's position is that the question must be answered, never what the
answer is.

The addendum also carries a free-text section for stances no setting covers, so the mechanism
never becomes a ceiling on how rigorous a project can be.

*Verify:* a project with defaults is byte-identical to today; enabling a setting changes only what
helpers write afterward and no shipped template; existing files are untouched when a setting
changes mid-project; settings round-trip through the contract and the Advanced screen; the
contract stores no method name; guidance explains each risk whether or not its setting is on;
disabling a setting never removes work.

### Stage H — The interface hands off into the workflow

The dashboard gains one orientation row that names where the workflow starts and what the
contract says is missing — no question recorded, no hypothesis yet, iterations without
outcomes. Derived from contract and file state, and never a scientific recommendation.

Launching gains a real path for an editor-hosted assistant: `code .` opens the project in
VS Code, which is what launching Zoo Code actually means. It becomes the launch command for
Zoo Code, and the sensible fallback when a configured assistant's own executable is missing but
`code` is present. The row names the assistant and whether it is available before it is chosen,
using what [`detected_tools()`](src/smairt/project.py:809) already knows.

Separate cancellation from failure in creation, and say whether files exist. Give a stale
scaffold a stated route rather than a refusal, and stop offering repairs that will be refused.
Keep a bad recent project inside the Home loop. Print failures in a failure style. Wire
`styling_enabled()` so `NO_COLOR` is honored as ADR 0003 requires.

*Verify:* a fresh project's dashboard names the first scientific action; launching with Zoo Code
selected opens the project in VS Code rather than reporting that no command is known; a missing
executable falls back to `code .` when available and says so; cancelling and failing read
differently; a stale project reports the same thing from every entry point; `NO_COLOR=1` produces
unstyled output with identical wording.

### Stage I — Make every corrected property falsifiable

Extend the guard tests so each fix above has a test that fails if it regresses, including the
unguarded-write case the current destructive-call test misses. Then regenerate the three golden
projects, run the full gate sequence, and record the pass in `docs/scaffold-transition.md`.

Bump the scaffold version once, at the end, since the generated project changes.

*Verify:* format, lint, mypy, full suite, blueprint diff showing only intended changes, build,
and both smoke installs; then a real end-to-end run from the installed binary.

---

## Sequencing notes

A through D are the integrity repairs and are strictly ordered: the numbering authority must be
single before the record can be trusted, the record must be coherent before the documentation
can teach it, and the documentation must be correct before selection is worth enforcing.

E and F are independent of each other and both depend on A–D. G no longer depends on F, because
provenance became an unconditional default rather than a setting; it depends only on the helpers
being settled in A–D. H is independent and can move earlier if the test run needs it. I closes.

Two `smairt check` diagnostics accumulate across stages and can be built together: the Stage B
outcome-drift check and the Stage G manifest reconciliation check. Both are structural detection
with no scientific judgment, which is what keeps them out of the settings surface.

The demo re-enrichment stays out of scope and should become its own spec.
