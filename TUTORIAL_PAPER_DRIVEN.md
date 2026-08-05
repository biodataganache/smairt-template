# SMAIRT Paper Workspace Tutorial

Paper support is an additive capability, not a separate project mode. It
keeps publication-focused analysis in `paper/analysis/` while exploratory work
remains in `analysis/`.

## Create Or Enable Paper Support

Create a project with Paper guidance from the start:

```bash
smairt new ./my_study \
  --name "My Study" \
  --slug my_study \
  --description "A publication-focused research workspace." \
  --researcher "Your Name" \
  --domain "Not sure yet" \
  --phase real \
  --assistant opencode \
  --accept-license \
  --paper \
  --no-git
```

Or enable it for an existing SMAIRT project:

```bash
smairt paper enable ./my_study
```

The capability adds `paper/README.md`, `paper/outline.md`, and
`paper/analysis/`. Fill the outline and create paper-specific analysis plans as
your research requires. SMAIRT does not generate manuscripts, revise papers, or
validate publication claims.

## Preserve The Audit Trail

For each paper-focused result, retain the question and background, hypothesis,
phase experiment, raw log, analysis and decision, and study report. Relate that
existing evidence chain to the paper outline. The assistant should read
`prompts/AI_CONTEXT.md` and work from project files directly.

## Validate The Workspace

```bash
smairt check ./my_study
smairt inspect ./my_study --hashes
```

Project Check is read-only. If a tool-owned structural asset is missing,
`smairt repair` previews the available deterministic repair and requires
`--select` plus `--confirm` to apply it. Paper deactivation never deletes paper
files, so researchers retain their work.
