# 04 - Bind every citation to a resolvable identifier

**What to build:** Add the `evidence` capability and, within it, a `background/references.yaml`
registry in which each entry carries an identifier alongside its citation, plus
`scripts/verify_references.py` which resolves each entry mechanically through DOI lookup via
CrossRef, title matching via OpenAlex, arXiv identifier lookup, and Semantic Scholar as a
fallback, then classifies it `verified`, `unresolved`, or `absent` and prints a report. The
script writes only the `verified` field, never a citation and never an analysis, and never
judges relevance or removes an entry, because whether a paper is relevant is the researcher's
judgment. It runs offline by reporting entries as unresolved rather than failing. This closes
the failure mode where a generated paper cited works that did not exist while omitting the
foundational reference for its own architecture.

**Blocked by:** 01 - Establish the SMAIRT Lab baseline.

**Status:** ready-for-agent

- [ ] `smairt-lab new --evidence` creates `background/references.yaml` and the verifier.
- [ ] The verifier resolves a real DOI and marks the entry `verified`.
- [ ] The verifier reports a fabricated DOI as `absent` and leaves the entry present.
- [ ] The verifier exits non-zero when a reference cited in a strict section is unresolved.
- [ ] The verifier runs with no network and reports every entry as unresolved.
- [ ] The verifier never writes to a file under `background/` other than the `verified` field.
- [ ] A test asserts an unresolvable entry survives verification byte-identical apart from `verified`.
- [ ] `background/README.md` explains the registry and retains the caution about assistant literature claims.
