# SMAIRT: Scientific Method with AI Research Toolkit

SMAIRT creates readable, hypothesis-driven scientific research workspaces for
coding assistants. The installed `smairt` command is the recommended project
creation path.

## Install

SMAIRT requires Python 3.11 or newer. Install it as an isolated tool:

```bash
uv tool install smairt
smairt --version
```

`pipx install smairt` is an equivalent alternative.

## Create A Project

`smairt new` is non-interactive so every choice can be scripted and tested:

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
  --no-git
```

The starting phase controls the initial data and experiment directories:

| Phase | Directories created |
| --- | --- |
| `synthetic` | Synthetic, downloaded/benchmark, and real |
| `downloaded` | Downloaded/benchmark and real |
| `real` | Real only |

Use `--paper` to add a paper workspace. Its analyses are under
`paper/analysis/`, separate from exploratory `analysis/`. Use `--hpc` to add
HPC guidance and a SLURM template. The tool does not submit or manage jobs.

Use `--git` to initialize Git and stage the generated files. SMAIRT never
creates a commit. If Git is unavailable, project creation succeeds and reports
the skipped initialization.

## Generated Workspace

Each project is ordinary, readable files:

```text
my_smairt_project/
|-- smairt.yaml            # Tracked, versioned project contract
|-- .smairt/               # Ignored local managed-file hashes
|-- background/
|-- hypotheses/
|-- plans/
|-- analysis/              # Exploratory analyses
|-- experiments/           # Directories selected by starting phase
|-- data/                  # Directories selected by starting phase
|-- results/logs/          # Canonical raw run records
|-- results/figures/
|-- prompts/AI_CONTEXT.md  # Tool-neutral workflow guidance
|-- paper/analysis/        # Present only with --paper
`-- hpc/                   # Present only with --hpc
```

`smairt.yaml` records the schema and scaffold versions, identity, optional
research question and email, domain, researcher, assistant, starting phase,
license, Git state, and Paper/HPC capability state. `.smairt/managed-files.yaml`
contains hashes for generator-managed files and is excluded by the project's
`.gitignore`.

Generation occurs in a temporary sibling directory and is exposed only after
the complete project is rendered. Existing destinations are rejected.

## Legacy Cookiecutter

Cookiecutter remains a clearly secondary compatibility path for existing
automation. Install `smairt` first, then run Cookiecutter from this repository:

```bash
cookiecutter /path/to/smairt-template-smairt-toolkit
```

The Cookiecutter hook delegates generation to the same packaged canonical
assets used by `smairt new`; there is no second scaffold to maintain. New
projects should use `smairt new`.

## Research Workflow

SMAIRT supports a traceable chain from hypothesis to experiment to raw log to
analysis. Start a session by sharing `prompts/AI_CONTEXT.md` with your coding
assistant. Record raw command output in `results/logs/` before interpreting it
in `analysis/`. Researchers retain responsibility for scientific judgment,
validation, and conclusions.

## Development

The package uses Hatchling, Typer, Pydantic, PyYAML, and Jinja2. Run the focused
public-seam suite and strict type checking with:

```bash
uv run --extra dev pytest tests
uv run --extra dev mypy src tests
```
