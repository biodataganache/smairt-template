# Team update: `smairt-lab/smairt-toolkit` branch

Copy-paste text below.

---

Hi all,

Quick update on the `smairt-lab/smairt-toolkit` branch (repo: PNNL-CompBio/smairt-template).

**Context.** SMAIRT is moving from a cookiecutter template to an installed tool (`pip install smairt`, then `smairt new`). During that move, a lot of the scientific guidance in the generated project got thinned out — the file structure survived, but the actual instructions inside many files were reduced to a heading and a sentence. A new project was technically valid but had very little to teach a researcher or an AI assistant.

**What I did.** I went back to the original template and restored the real content. Guidance in a new project went from about 29% of the original to about 69%. Some examples:

- `KNOWN_PATTERNS.md` — was 179 bytes, now ~12 KB
- `AI_CONTEXT.md` — was 732 bytes, now ~11.5 KB (this is the file an assistant reads first)
- `CODE_CONVENTIONS.md` — was 172 bytes, now ~6.8 KB

**The bigger change: `docs/12_STEPS.md`.** This is the core workflow doc. The old version was mostly about file discipline (numbering, logging, audit trail). The current version is about reasoning order. Both matter, so I merged them. Every step now says four things:

- who owns the decision
- what the researcher does
- what the assistant does
- which file holds the record

Two things worth flagging:

1. **It is written for both readers.** The researcher and the AI assistant both read this file. It no longer addresses only one of them, so an assistant gets direct instructions instead of overhearing advice meant for a person. There's a short vocabulary section at the top so both start from the same terms.

2. **"Steering" is now distinct from "deciding."** A researcher can push an assistant toward a direction, ask for alternatives, or reject a framing — that's steering, and it's where most of the judgment happens. It is not the same as making the call. A few steps are researcher-only on purpose: the decision criterion, and the choice to stop.

There's also a provenance point I want feedback on. When an assistant can write and run the experiments, the order work happened in is no longer proof of the reasoning. So the decision criterion now gets committed *before* the experiment script exists. Git history becomes the evidence that we didn't pick the threshold after seeing the data.

**Retired tooling.** Four old helper scripts are gone: `compile_for_ai.py`, `new_experiment.py`, `new_iteration.py`, and `finalize_iteration.py`. The first is obsolete now that assistants read files directly. The last one deleted and rewrote researcher files, which we no longer allow. Three helpers remain and all of them are documented with commands I actually ran.

**One consolidation.** `SESSION_START.md` and `00_priming_prompts.md` both held "paste this at the start of a session" prompts and were impossible to tell apart. They're now one file organized by situation. Existing projects that still have the old file are unaffected — nothing breaks.

**Verification.** Full test suite passes (99 tests), and every command in the documentation was run against a real generated project rather than assumed. That caught one broken instruction that would have failed for anyone on their first try.

**What I'd like from you.** Mainly the division of labour in `12_STEPS.md`. I've drawn lines on who decides what, and those lines are opinions, not facts. If you think interpretation should be researcher-only, or that I've given the assistant too much or too little, that's the conversation I want to have.

Thanks,
Salvador

---

## Notes for me (not part of the message)

- Branch head: `4af22f8`, pushed to `origin/smairt-lab/smairt-toolkit`
- Three commits in this pass: `2b590e4`, `d139ba8`, `6b74ede`, plus `4af22f8`
- The boundaries most likely to be challenged: step 10 (interpretation, currently shared),
  step 4 (decision criterion, researcher-only), step 11 (stop decision, researcher-only)
