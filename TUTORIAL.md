# SMAIRT Research Workflow Tutorial

This tutorial uses the installed `smairt` command. It applies on macOS,
Linux, and WSL with Python 3.11 or newer; native Windows is deferred. The
repository preview is installed from a checkout, not from PyPI.

## Create The Workspace

```bash
git clone https://github.com/PNNL-CompBio/smairt-template.git
cd smairt-template
uv tool install .
smairt new ./classification_noise_study \
  --name "Classification Noise Study" \
  --slug classification_noise_study \
  --description "Test classification boundaries under varying noise." \
  --researcher "Your Name" \
  --domain "Computational biology" \
  --phase synthetic \
  --assistant opencode \
  --accept-license \
  --no-git
```

Use `pipx install .` from the checkout when `uv` is unavailable. The guided
alternative is simply `smairt new`.

## Work In A Traceable Loop

Open the generated folder in your selected assistant and direct it to read
`prompts/AI_CONTEXT.md`. Each iteration should connect these ordinary files:

```text
hypotheses/HYPOTHESIS_01.md
  -> experiments/01_synthetic/script_01_baseline.py
  -> results/logs/script_01_baseline.log
  -> analysis/ANALYSIS_01.md
```

Start with a hypothesis, write and run the experiment, retain raw output in
`results/logs/`, and then interpret the evidence in `analysis/`. Put complex
work plans in `plans/`. The coding assistant can read project files directly;
SMAIRT does not require browser-paste workflows or generated context compilers.

The researcher remains responsible for the hypothesis, study design, execution,
validation, and conclusions. SMAIRT records a structure; it does not establish
scientific validity.

## Optional Paper And HPC Guidance

Enable Paper support when publication-focused work needs to be separate from
exploratory analysis:

```bash
smairt paper enable ./classification_noise_study
```

This creates `paper/analysis/`, `paper/outline.md`, and a short README without
changing exploratory `analysis/` work. Deactivation changes capability state
but never deletes files.

Enable HPC guidance when you need a starting SLURM script:

```bash
smairt hpc enable ./classification_noise_study
```

Edit `hpc/slurm_job.sh` for the cluster. SMAIRT does not connect to,
submit to, monitor, or manage a scheduler.

## Check And Repair Structure

```bash
smairt check ./classification_noise_study --json
smairt repair ./classification_noise_study
smairt repair ./classification_noise_study --select REPAIR_ID --confirm
```

Project Check is read-only and reports structure, configuration, managed-file,
and unresolved-template issues. Repairs are opt-in and restricted to
deterministic tool-owned structure; replace `REPAIR_ID` with an identifier from
the repair preview. Modified researcher-owned files are
preserved. Set `smairt settings ./classification_noise_study --experience
advanced` to access Advanced Mode dashboard controls, including inspection and
managed-asset regeneration previews.

## Git And Local Preferences

Pass `--git` to `smairt new` to initialize a repository and stage the generated
files. SMAIRT never creates a commit. Advanced/Standard mode and motion are
local checkout preferences in ignored `.smairt/preferences.yaml`; use
`--no-motion` for a static interactive dashboard. Motion is already suppressed
for JSON, redirected output, tests, and CI.

## Compatibility Note

Cookiecutter implementations are retained under `legacy/cookiecutter/` as
unsupported historical references only. Migrate automation to `smairt new`.
