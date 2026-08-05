# ADR 0008: Store Lessons as Cards That Cite Their Evidence

Status: Accepted

## Context

Accumulated lessons lived in one file that had already reached several hundred lines and grew
without bound. It had no retrieval, no ordering, and no notion of a lesson being superseded,
so an assistant either read all of it or none of it, and a reversal was invisible.

Systems that carry lessons across runs retrieve a small relevant subset per stage rather than
loading everything, and weight or expire what has gone stale. Retrieval, not accumulation, is
what makes a lesson store useful.

An external memory service was considered and rejected. Most require an embedding provider
and a database, independently reported retrieval accuracy on long-horizon benchmarks is well
short of what a provenance substrate demands, and the common consolidation step has a model
rewrite episodes into insights. That last property is disqualifying here: a card asserting
that something was learned, with no traceable path to the run that showed it, is exactly the
ungrounded claim the registries exist to prevent. One vendor's self-hosting path also requires
operating a graph database, and another gates the graph layer behind a paid tier, neither of
which suits a tool installed as a single command.

## Decision

Lessons are markdown cards, one per lesson, typed by kind and carrying a stage, a confidence,
retrieval hints, and an updated timestamp. Every card must cite non-empty evidence paths. A
card without evidence is not a lesson but an assertion, and is rejected.

An index declares which kinds each stage loads first, so an assistant retrieves a few relevant
cards rather than reading every prompt file in the project. A superseded card is marked rather
than deleted, so a reversal stays visible.

Markdown on disk is the substrate. It is diffable, reviewable, survives the tool, and travels
with the repository. No external memory service is a dependency. Should an optional index
prove worthwhile later, it indexes these cards and never becomes the source of truth.

## Consequences

- An assistant can load a handful of relevant cards instead of a large undifferentiated file, which is the main context saving in the fork.
- Mandatory evidence paths make a lesson re-examinable rather than merely trusted, and reject the ungrounded card outright.
- Writing a lesson costs more than appending a line, and that friction is accepted as the price of grounding.
- Retrieval is textual rather than semantic, so a poorly hinted card is harder to find, and hints are therefore required.
- The existing file is retained and reduced rather than migrated, so no researcher content is rewritten.
- Because cards are plain files, an optional external index remains possible without changing where truth lives.
