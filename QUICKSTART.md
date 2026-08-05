# SMAIRT Quick Start

SMAIRT creates a local research workspace for a coding assistant. It is
supported on macOS, Linux, and WSL with Python 3.11 or newer. Native Windows is
deferred; use WSL.

## 1. Install From This Repository

This is a repository-local preview, not a PyPI installation. Clone the
canonical PNNL repository and install the checkout as a tool:

```bash
git clone https://github.com/PNNL-CompBio/smairt-template.git
cd smairt-template
uv tool install .
smairt --version
```

If `uv` is unavailable, use `pipx install .` from the checkout instead.

## 2. Create A Project

Launch the guided wizard:

```bash
smairt new
```

For automation, provide all required values:

```bash
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

Choose `--paper` to add a paper workspace and `--hpc` to add editable SLURM
guidance. The latter does not submit or manage jobs. Use `--git` when you want
the generated files staged in a new Git repository; SMAIRT never makes a
commit.

## 3. Start The Research Workflow

Open the project in the selected coding assistant. Ask it to read
`prompts/AI_CONTEXT.md`, then work through a traceable chain:

1. Record the research question and context in `background/`.
2. Write a hypothesis in `hypotheses/`.
3. Create an experiment in the selected `experiments/` phase directory.
4. Record raw command output in `results/logs/`.
5. Interpret the result and record the decision in `analysis/`.
6. Consolidate the completed study in its study report. Create a plan in
   `plans/` before complex work.

SMAIRT does not perform science or validate conclusions. The researcher owns
the question, the evidence, and the interpretation.

## 4. Check And Manage

Run the dashboard from the project root with `smairt`. In a capable terminal,
move with Up/Down or `k`/`j`, scroll long lists with PageUp/PageDown, choose
with Enter, toggle checkboxes with Space, go back with Left or Escape, and
cancel with Ctrl-C. Basic terminals, redirected input, and CI show the same
options as a numbered list, where each row also carries a stable token such as
`[settings]` that selects it.

Optional capabilities are one screen. It previews exactly which files enabling
would create and writes nothing until you accept that preview. Disabling only
marks a capability inactive; your files stay exactly as they are.

Or use stable commands:

```bash
smairt check . --json
smairt paper enable .
smairt hpc enable .
smairt settings . --experience advanced --no-motion
```

Project Check is read-only. If it reports a deterministic structural repair,
review it first with `smairt repair .`, then apply only the chosen repair with
`smairt repair . --select REPAIR --confirm`.

If Project Check reports that the project's scaffold version differs from the
installed SMAIRT, review the difference with `smairt upgrade .` and apply it with
`smairt upgrade . --confirm`. The preview writes nothing, and an upgrade never
rewrites your own work or a starter file you have edited.

## Legacy Automation

Cookiecutter implementations under `legacy/cookiecutter/` are unsupported,
untested historical references. Replace existing automation with `smairt new`.
