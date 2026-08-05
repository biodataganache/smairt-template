# ADR 0006: Bind Citations to Resolvable Identifiers

Status: Accepted

## Context

The scaffold handled literature with prose caution. Its background guidance warned that an
assistant may report false negatives and false positives about prior work and may be
confident about both, then asked the researcher to verify important claims independently.
Across the entire generated project only two files mentioned citations at all, both
incidentally. There was no registry, no identifier, and nothing mechanical.

This is a documented failure mode rather than a hypothetical one. A generated paper that
passed workshop review carried inaccurate citations and omitted the foundational reference for
the architecture it used. Systems that address it do so mechanically, resolving each reference
through bibliographic services before it can appear in a draft.

A fabricated citation is the same class of error as a fabricated number: plausible text with
no grounding. It deserves the same treatment, and identifier resolution is a lookup rather
than a judgment, so it can be checked without a model.

## Decision

Cited works are recorded in a registry where each entry carries an identifier alongside its
citation. A verifier resolves each entry mechanically, trying DOI resolution, title matching,
arXiv identifier lookup, and a bibliographic fallback in turn, then classifies it verified,
unresolved, or absent and prints a report.

The verifier writes only the verification field. It never edits a citation, never touches an
analysis, and never removes an entry. It does not classify relevance, because whether a paper
bears on the argument is a scientific judgment that belongs to the researcher. Systems that
delete references an inspecting model deems irrelevant would violate the rule that researcher
work is never overwritten.

The verifier runs offline by reporting entries as unresolved rather than failing, so a
project without network access remains workable.

## Consequences

- A citation cannot be simultaneously plausible and absent without the project saying so.
- Verification becomes a repeatable command rather than the researcher's memory against an assistant's confidence.
- Recording an identifier is extra work at the moment a work is cited, and a work without any identifier can only ever be unresolved.
- The verifier depends on external services, so its report reflects availability as well as existence, which is why unresolved and absent are distinct.
- Because relevance is untouched, a resolvable but irrelevant citation still passes, and that limit is stated in guidance.
- Registry and verifier are gated by an opt-in capability, so a project that does not want them is unaffected.
