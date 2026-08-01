# SMAIRT: Scientific Method with AI Research Toolkit

SMAIRT V0.1 creates readable, hypothesis-driven scientific research workspaces
for coding assistants. The installed `smairt` command is the supported project
creation path. It supports macOS, Linux, and Windows through WSL; native
Windows support is deferred.

## Install The Preview

This repository provides a local/repository preview, not a PyPI release. On
macOS, Linux, or WSL with Python 3.11 through 3.13, clone the repository and
install the current checkout as an isolated tool:

```bash
git clone https://github.com/PNNL-CompBio/smairt-template.git
cd smairt-template
uv tool install .
smairt --version
```

`pipx` is the fallback when `uv` is unavailable:

```bash
pipx install .
smairt --version
```

Use `uv tool install --force .` or `pipx reinstall smairt` after updating your
checkout. Native Windows is not supported in V0.1; use WSL instead.

## Create A Project

Run the guided wizard:

```bash
smairt new
```

Or use the complete noninteractive form for scripts and automation:

```bash
smairt new ./my_smairt_project \
  --name "My SMAIRT Project" \
  --slug my_smairt_project \
  --description "A brief description of the research project." \
  --researcher "Your Name" \
  --domain "Not sure yet" \
  --phase synthetic \
  --assistant opencode \
  --license MIT \
  --accept-license \
  --no-git
```

The starting phase records provenance and initializes the current phase. Every project
contains all three phase workspaces:

| Phase | Meaning |
| --- | --- |
| `synthetic` | Work begins by testing assumptions with controlled data. |
| `downloaded` | Work begins with public or benchmark data. |
| `real` | Work begins directly with target data. |

Add `--paper` for a publication overlay linked to the standard scientific audit trail.
Add `--hpc` for editable cluster configuration, SLURM templates, and HPC guidance.
SMAIRT does not submit or manage cluster jobs.

Add `--git` to initialize Git and stage generated files. SMAIRT never commits;
if Git is unavailable, generation succeeds and reports that initialization was
skipped.

## Manage A Project

Run `smairt` inside a project for the Standard Mode dashboard. Set the local
experience preference to `advanced` with `smairt settings` to expose Advanced
Mode controls. The dashboard manages workspace utilities only; scientific work
stays with the selected coding assistant.

Stable scriptable commands include:

```bash
smairt open /path/to/project
smairt check /path/to/project --json
smairt repair /path/to/project
smairt paper enable /path/to/project
smairt hpc disable /path/to/project
smairt settings /path/to/project --experience advanced --no-motion
```

Project Check is read-only. It exits `0` when no structural or configuration
issues are found and `1` otherwise. `smairt repair` previews only deterministic
tool-owned repairs; pass `--select REPAIR --confirm` to apply a reviewed repair.
Paper and HPC deactivation never deletes project files. Motion is enabled only
for interactive terminals and can be disabled locally with `--no-motion`; it is
suppressed for tests, redirected output, JSON, and CI.

`smairt settings` updates approved metadata, collaborators, current phase,
assistant, project conventions, or local dashboard preferences without
changing the immutable project slug or folder. License changes show a preview,
require `--confirm-license`, and refuse to replace modified `LICENSE` text.

## Generated Workspace

Each project is ordinary, readable files:

```text
my_smairt_project/
|-- smairt.yaml            # Tracked, versioned project contract
|-- .smairt/               # Ignored local dashboard preferences
|-- background/
|-- hypotheses/
|-- plans/
|-- analysis/              # Plans, interpretations, and report template
|-- experiments/           # All synthetic, downloaded, and real phase folders
|-- data/                  # All phase folders; data files ignored by default
|-- results/logs/          # Canonical raw run records
|-- results/figures/
|-- prompts/AI_CONTEXT.md  # Tool-neutral workflow guidance
|-- paper/                 # Publication overlay present only with --paper
`-- hpc/                   # Present only with --hpc
```

Start a coding-assistant session by reading `prompts/AI_CONTEXT.md`. Record raw
command output in `results/logs/` before interpreting it in `analysis/`.
Researchers remain responsible for scientific judgment, validation, and
conclusions.

## Legacy Cookiecutter

Cookiecutter implementations are retained under `legacy/cookiecutter/` only as
unsupported historical references. They are not packaged, tested, or supported
generation paths. Use `smairt new` for every new project and automation flow.

## V0.1 Limits

- Existing folders without `smairt.yaml` are not adopted or migrated.
- Project Check diagnoses structure and configuration; it does not inspect
  scientific correctness or modify researcher-authored content.
- Repairs and regeneration are limited to deterministic, tool-owned assets.
- HPC support supplies guidance and a template, not scheduler integration.
- Native Windows support is deferred.

## Development

Install development dependencies and run all release gates locally:

```bash
uv sync --all-extras --locked
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest tests/test_cli.py
uv run pytest
uv build
uv run python scripts/smoke_install.py --artifact dist/smairt-0.2.0-py3-none-any.whl --workspace .smoke/wheel
uv run python scripts/smoke_install.py --artifact dist/smairt-0.2.0.tar.gz --workspace .smoke/sdist
```

GitHub Actions runs these gates on Ubuntu and macOS with Python 3.11, 3.12, and
3.13.
