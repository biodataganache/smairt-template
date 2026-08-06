# Paper and HPC capabilities

Two optional overlays. Both are additive: they add files and guidance to a project that already
works, and neither changes the research loop or introduces a separate mode.

## Enabling and disabling

```bash
smairt paper enable .
smairt hpc enable .
```

Either can also be requested at creation, as long as the command has a destination:

```bash
smairt new ./study --paper --hpc \
  --name "Study" --slug study --description "..." \
  --researcher "Ada Researcher" --domain "Computational biology" --accept-license
```

Guided creation asks which capabilities you want, so it refuses these flags rather than
silently ignoring them.

Enabling shows you exactly which files it would create and writes nothing until you confirm.

```bash
smairt paper disable .
smairt hpc disable .
```

**Disabling never deletes anything.** It changes state in `smairt.yaml` and leaves every file
in place, because a manuscript draft is your work and a tool that removed it on a state change
would be indefensible. Re-enabling later creates only what is missing.

## Paper

For work heading toward publication.

| Path | Holds |
|---|---|
| `paper/outline.md` | The argument you intend to make |
| `paper/drafts/` | Manuscript drafts |
| `paper/analysis/` | Publication-focused interpretation, linked to core analyses |
| `paper/reviewer_feedback/` | Reviewer comments and your responses |
| `FINAL_MANIFEST.md` | The evidence inventory behind reported claims |

Paper does not replace the audit trail — it points at it. A figure in a draft should be
traceable to the analysis that produced it, and that analysis to the log behind it. This is what
makes a reviewer question answerable months later.

The core loop is unchanged: hypotheses, iterations, logs, and analyses stay where they were, and
`select_result.py` is still how you mark an iteration as the evidence for a claim.

## HPC

For work that outgrows a laptop.

| Path | Holds |
|---|---|
| `hpc/config.yaml` | Your cluster's account, partition, and resource defaults |
| `hpc/slurm_job.sh` | A submission script to adapt |
| `hpc/templates/slurm_basic.sh` | A minimal starting template |
| `hpc/logs/` | Scheduler output |

**HPC supplies guidance and templates, not scheduler integration.** SMAIRT does not submit jobs,
poll queues, or manage allocations. Every cluster differs in account names, partitions, module
systems, and filesystem layout, and a tool that guessed at those would produce scripts that fail
in ways you would have to debug anyway.

So `hpc/config.yaml` and `hpc/slurm_job.sh` are yours to edit. They are starting points that
name what a scheduler needs, not working submissions.

## After enabling

```bash
smairt check .
```

Confirms the capability's files are present and the contract records it. To see exactly which
files are tool-owned versus yours:

```bash
smairt inspect . --hashes
```

## Next

- [The research workflow](workflow.md)
- [Upgrading an existing project](upgrading.md)
