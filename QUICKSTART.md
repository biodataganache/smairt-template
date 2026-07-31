# SMAIRT Quick Start

SMAIRT V0.1 creates a local research workspace for a coding assistant. It is
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
  --no-git
```

Choose `--paper` to add a paper workspace and `--hpc` to add editable SLURM
guidance. The latter does not submit or manage jobs. Use `--git` when you want
the generated files staged in a new Git repository; SMAIRT never makes a
commit.

## 3. Start The Research Workflow

Open the project in the selected coding assistant. Ask it to read
`prompts/AI_CONTEXT.md`, then work through a traceable chain:

1. Write a hypothesis in `hypotheses/`.
2. Create an experiment in the selected `experiments/` phase directory.
3. Record raw command output in `results/logs/`.
4. Interpret the result in `analysis/`.
5. Create a plan in `plans/` before complex work.

SMAIRT does not perform science or validate conclusions. The researcher owns
the question, the evidence, and the interpretation.

## 4. Check And Manage

Run the dashboard from the project root with `smairt`, or use stable commands:

```bash
smairt check . --json
smairt paper enable .
smairt hpc enable .
smairt settings . --experience advanced --no-motion
```

Project Check is read-only. If it reports a deterministic structural repair,
review it first with `smairt repair .`, then apply only the chosen repair with
`smairt repair . --select REPAIR --confirm`.

## Legacy Automation

Cookiecutter remains available only for existing automation. It generates the
same canonical workspace through the installed package; see
[`legacy/cookiecutter/README.md`](legacy/cookiecutter/README.md). Do not use a
GitHub shorthand, browser-paste workflow, or an old Cookiecutter repository
name for new projects.
