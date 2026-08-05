# ADR 0009: Name the Decisions the Researcher Owns

Status: Accepted

## Context

The twelve steps assign each decision an owner and reserve five for the researcher, but they
do so in prose. An assistant could be asked to respect them and a reader could verify them by
reading the document, yet nothing could be addressed. There was no way to instruct an
assistant to stop at a specific decision, and no way for a project to record that it had.

Published evidence makes the value of naming them concrete. Across seven intervention
regimes, targeted intervention at a small set of high-leverage points reached the best quality
and acceptance, while approving every step scored substantially worse than that and only
marginally better than full autonomy. Dense approval added interaction without information.
The same work found structured adversarial critique to be the single largest contributor to
quality, ahead of failure recovery and cross-run learning.

SMAIRT already places judgment at the right points and already requires choosing between
revising, advancing, and stopping. What is missing is a token to address and an artifact to
record.

## Decision

The five researcher-owned decisions receive stable gate tokens, so an assistant can be
directed to stop at a named gate and present options rather than proceeding, and a project can
record that the gate was reached.

Adversarial critique becomes a durable artifact rather than an instruction. It records the
objections raised, which were answered, and which were accepted as limitations, with roles
supplied by the project's domain pack so critique is phrased in the field's terms.

Each iteration records whether the project proceeded, refined, or pivoted. This names a choice
the loop already requires rather than adding one.

No component decides a gate. Nothing scores a hypothesis, ranks a direction, or selects an
outcome. Full automation of these decisions produces measurably worse work, and they are the
decisions that make the research the researcher's own.

## Consequences

- A gate can be named in an instruction and verified in the record, which prose could not support.
- An objection raised and set aside survives, so a limitation cannot quietly disappear between critique and write-up.
- Critique is another artifact to maintain, and a project that treats it as a formality gains nothing.
- Domain-supplied roles mean critique quality depends on pack quality, which is why packs ship rather than being left empty.
- Recording the decision per iteration makes the shape of the work legible without reading every analysis.
- Because tokens are stable, later tooling can address a gate without re-reading the guidance document.
