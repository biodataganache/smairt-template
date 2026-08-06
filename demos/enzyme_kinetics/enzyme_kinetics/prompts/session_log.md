# Session Decision Index

This is a concise living index, not a pasted conversation transcript. Your assistant
reads project files directly, so copying conversations here duplicates what the files
already say and ages badly. What no file captures on its own is *why* the work turned
the way it did, and that is what belongs here.

Record meaningful decisions and link the durable files that hold the scientific detail.

## Entry Template

### [YYYY-MM-DD] - [Researcher or Assistant]

- **Task**: [What was addressed]
- **Decision**: [What changed and why]
- **Evidence read**: [Paths]
- **Artifacts updated**: [Paths]
- **Open questions**: [Unresolved items]
- **Next action**: [Concrete follow-up]

Do not duplicate raw logs, analyses, or plans here.

---

## What Is Worth Recording

1. **Decisions and their reasoning.** A choice you can no longer justify is a
   choice you will make again by accident.
2. **Where you contributed the insight.** Distinguish what you determined from
   what an assistant proposed. That distinction is the record of your intellectual
   contribution, and `prompts/intellectual_contribution.md` is where it accumulates.
3. **What you tried that did not work.** Dead ends are results. Recording them
   stops the same path being explored twice.
4. **Where an approach stops working.** Methods that hold on synthetic data often
   fail on real data, or under noise, or past some scale. The boundary is the
   finding.
5. **Patterns worth reusing.** When a technique or a recurring error proves
   general, promote it to `prompts/KNOWN_PATTERNS.md` rather than leaving it here.

## Practices

- **Link, do not copy.** Full experiment output lives in `results/logs/`;
  interpretation lives in `analysis/`. Reference them.
- **Do not revise history.** Correct a decision with a new entry that supersedes
  the old one. Editing the old entry destroys the reasoning trail.
- **Write the entry when the decision is made.** Reconstructed reasoning is a
  guess about your own thinking.
- **Keep entries short.** If an entry needs paragraphs of scientific detail, that
  detail belongs in `analysis/` and this entry should point at it.
