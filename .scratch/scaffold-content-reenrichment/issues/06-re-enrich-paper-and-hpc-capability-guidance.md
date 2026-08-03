# 06 - Re-enrich Paper and HPC capability guidance

Status: ready-for-agent
Type: task
Blocked by: 02

## Question

Do the optional capabilities carry enough guidance to be usable, without overstating what SMAIRT does?

## Context

These assets are conditional: they generate only when the corresponding capability is enabled, and they appear in the `real-with-paper` and `downloaded-with-hpc` golden projects rather than `base-synthetic`.

| Asset | Original | Current | Retained |
|---|---|---|---|
| `hpc/config.yaml` | 992 | 323 | 32% |
| `hpc/templates/slurm_basic.sh` | 1352 | 449 | 33% |
| `paper/drafts/README.md` | 693 | 261 | 37% |
| `paper/reviewer_feedback/README.md` | 964 | 365 | 37% |
| `paper/outline.md` | 1380 | 806 | 58% |
| `hpc/README.md` | 1293 | 694 | 53% |
| `hpc/logs/README.md` | 785 | 507 | 64% |

Two hard constraints apply here, and they pull in opposite directions from a naive restore.

First, HPC guidance must not claim scheduler management. SMAIRT supplies an editable configuration, a SLURM template, and guidance. It does not submit, cancel, monitor, or synchronize jobs. Re-enrichment must add adaptation detail — resource fields, partition and account placeholders, module loading, log paths — without implying the tool will run any of it.

Second, Paper is an additive capability, not a project mode. The original text was written when paper-driven was a separate project type. Rewrite passages that assume a mode. Publication analyses live under `paper/analysis/` so they stay separate from exploratory `analysis/`.

`paper_draft/README.md` stays retired as a duplicate workspace. Note that `paper/README.md`, `paper/analysis/README.md`, `paper/FINAL_MANIFEST.md`, and `hpc/slurm_job.sh` have no legacy counterpart — they were introduced by the restoration and are exempt from the fidelity floor, though they should read consistently with the re-enriched neighbours.

## Acceptance

- Each asset above meets its declared fidelity floor from ticket 02.
- `hpc/config.yaml` documents each field a researcher must adapt for their cluster.
- `hpc/templates/slurm_basic.sh` is a usable starting template with resource, partition, account, and log-path placeholders.
- No HPC asset claims SMAIRT submits, cancels, monitors, or synchronizes jobs.
- `paper/outline.md`, `paper/drafts/README.md`, and `paper/reviewer_feedback/README.md` describe Paper as an additive capability.
- Paper guidance points publication analyses at `paper/analysis/`, distinct from exploratory `analysis/`.
- Enabling, disabling, and re-enabling both capabilities still creates missing starters only and never deletes or overwrites researcher edits.
- Existing capability tests pass unchanged.
- The prohibition test from ticket 02 passes for every file in this group.

## Notes

Capability deactivation changes contract state only. Re-enriched text must not imply that disabling a capability removes files.
