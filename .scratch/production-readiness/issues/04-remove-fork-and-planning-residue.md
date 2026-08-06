# Remove fork and superseded planning residue

Type: task
Status: resolved
Blocked by: 03

## Question

Can the front repository contain only current framework material without losing durable decisions or work that belongs elsewhere?

## Work

- Confirm the answer to “Decide whether Run History is a declared scaffold asset” and any durable outcome unique to `plans/` is represented in current documentation or `CHANGELOG.md`.
- Delete `plans/` and root-level `adversarial_review1.md`; Git history remains the historical record.
- Delete `.scratch/smairt-agentic-fork/` and `docs/adr/0004-0010`. The files were already verified byte-for-byte on `fork/planning/agentic-science-foundation`.
- Delete or move the untracked `docs/experimental/*.pdf` files outside this checkout; do not commit them and do not add a broad PDF ignore that could hide future publication assets.
- Verify references, ADR numbering, repository navigation, package builds, and tests after removal.

## Resolution

Resolve when no active file links to removed residue, ADR 0001-0003 remain intact, the fork still contains the transferred material, and the working tree contains no untracked experimental PDFs.

## Answer

Removed, after re-verifying all 17 fork files were still byte-for-byte identical on
`fork/planning/agentic-science-foundation` at the moment of deletion rather than trusting the
earlier check.

**Returned to the fork's keeping (17 files):** `.scratch/smairt-agentic-fork/` (spec plus nine
issues) and `docs/adr/0004-0010`. Those seven ADRs map one-to-one onto the fork's issue titles
and describe decisions for a project this repository does not contain. Nothing in the shipped
toolkit referenced any of them.

**Deleted as superseded (6 files):** `plans/` (four planning records, 794 lines),
`adversarial_review1.md`, and `docs/MODERNIZATION_PROPOSAL.md`. Each contained claims that are
now false — a "1,909-line `cli.py`", "refuses until an upgrade flow exists", `new_script.py` as
a live helper — and none was labelled historical in a way a newcomer would notice. The durable
outcomes are in `CHANGELOG.md` and `docs/scaffold-transition.md`, which I checked before
deleting rather than after. Git history holds the rest.

**Removed from the working tree:** the three unreferenced `docs/experimental/*.pdf` files
(17 MB of fork source material). No broad `*.pdf` ignore was added, because that would silently
hide future publication assets — exactly the kind of quiet rule that causes the next problem.

### ADR numbering

`docs/adr/` now holds 0001-0003. Numbering resumes at 0004 for the next real toolkit decision.
Renumbering the survivors would have been worse: their numbers are cited in
`docs/scaffold-transition.md` and in `CONTEXT.md`, and a decision record whose identity moves is
not much of a record.

### Verification

- 17 files confirmed identical on the fork immediately before removal.
- No remaining file references anything removed.
- Link check across all root, `docs/`, and `.github/` Markdown found no broken relative links.
  It did surface a stale `project.py:588` pointer to `project_check()`, now at line 660, so the
  line number was dropped rather than left to rot again.
- 187 tests pass. Build clean; sdist contains none of the removed material.
