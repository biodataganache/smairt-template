# ADR 0007: Write the Metrics Registry Mechanically

Status: Accepted

## Context

The audit trail already retained raw logs untouched, which is a real guarantee. But a number
in an analysis and a number in a log were connected only by prose, so a measured value and an
invented one were indistinguishable to any reader who did not re-derive the number from the
log by hand.

Removing an equivalent registry from a comparable system raised apparent acceptance while
manual inspection found that three of five accepted papers contained values present in no
measurement record. The registry was the component that separated genuine results from
fabricated ones, and its cost to apparent quality was the price of that separation.

An analysis passing such a check is not thereby correct. In one reported case every condition
collapsed to identical zero values that were genuinely logged; the numbers were real and the
experiment answered nothing. Grounding is necessary and not sufficient, and the design must
not imply otherwise.

## Decision

Metrics are recorded by instrumented experiment code as it runs. A helper writes each
measurement with its condition, seed, and the exact log path that produced it, so a row is
bound to a run rather than asserted about one. The registry is machine-written, so an
assistant may compose an analysis but cannot introduce a number into the evidence.

A verifier extracts numerics from an analysis and matches each against the registry scoped
per condition, so a value correct for one condition is not accepted for another. It reports
what it cannot match and leaves the analysis byte-identical.

The verifier is not invoked by Project Check and blocks nothing. An earlier decision rejected
turning rigor settings into enforcement, and refusing to operate because a number is
unmatched would both contradict that and assess researcher work semantically.

## Consequences

- Every reported number can be traced to the run that produced it without re-deriving it by hand.
- Grounding becomes structural rather than instructed, because the write path excludes the assistant.
- An experiment must call the helper to be covered, so an uninstrumented script yields an empty registry and every claim reports as unmatched.
- Because the verifier only reports, a project may proceed with unmatched claims, which is deliberate.
- Condition scoping prevents a plausible cross-condition match from passing, at the cost of requiring conditions to be named consistently.
- A grounded result may still be scientifically empty, and guidance says so rather than implying the check confers validity.
