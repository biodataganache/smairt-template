# Remove fork and superseded planning residue

Type: task
Status: unclaimed
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
