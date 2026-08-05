# SMAIRT: Scientific Method with AI Research Toolkit

SMAIRT creates readable, hypothesis-driven scientific research workspaces
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
checkout. Native Windows is not supported; use WSL instead.

## Create A Project

Run the guided wizard:

```bash
smairt new
```

The wizard walks fourteen screens. You confirm one folder name and it derives
the immutable project identifier from it, showing both. Optional capabilities
are checkboxes, so answer `Do you expect to write a paper?` and `Do you expect
to use an HPC?` independently, or leave `Default Workspace` checked. Every
answer stays editable on the final review, where `Create project` sits below a
divider so reviewing and committing are never one keystroke apart.

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
Both are independent and additive, and either can be enabled or disabled later.
SMAIRT does not submit or manage cluster jobs.

Add `--git` to initialize Git and stage generated files. SMAIRT never commits;
if Git is unavailable, generation succeeds and reports that initialization was
skipped.

## Manage A Project

Run `smairt` inside a project for the Standard Mode dashboard. Set the local
experience preference to `advanced` with `smairt settings` to expose Advanced
Mode controls. The dashboard manages workspace utilities only; scientific work
stays with the selected coding assistant.

In a capable interactive terminal, Home, the dashboard, Project Settings, and
guided project creation present framed keyboard screens that repaint in place:

| Control | Action |
| --- | --- |
| Up/Down or `k`/`j` | Move the selection, wrapping at both ends |
| PageUp/PageDown | Scroll one visible viewport without wrapping |
| Enter | Choose the highlighted row |
| Space | Check or uncheck the highlighted row, where a screen offers checkboxes |
| Left or Escape | Return to the previous screen |
| Ctrl-C | Cancel |

Where several answers can hold at once, such as optional capabilities, the
screen offers checkboxes with a visible `Next →` row. Space and Enter both
toggle, so advancing is always a deliberate choice of `Next →`. `Default
Workspace` is mutually exclusive with the capabilities by construction, so a
contradictory selection cannot be reached.

Long lists stay inside a bounded viewport with a scrollbar rather than printing
every row, and a screen never exceeds the height of the terminal. Screens never
take over the terminal with an alternate screen, so scrollback and copy stay
yours. Styling uses only your terminal's own sixteen ANSI colors, and color is
never the only signal.

Redirected input, `TERM=dumb`, CI, tests, and `--no-motion` show the same
options as a numbered listing. Every row carries a stable action token in
brackets, and either the token or the number selects it:

```text
1. Launch assistant or open folder [assistant]
2. Project Settings [settings]
```

Tokens are the contract; numbers are a convenience that may be renumbered when
a menu is regrouped, so scripts should prefer tokens.

Every command uses the same three exit codes, so a script can tell the cases
apart without reading messages:

| Code | Meaning |
| --- | --- |
| `0` | The command did what it said. |
| `1` | The project was found, and the operation failed or reported findings. |
| `2` | The command could not be carried out: no project there, or unusable arguments. |

Stable scriptable commands include:

```bash
smairt open /path/to/project
smairt check /path/to/project --json
smairt repair /path/to/project
smairt upgrade /path/to/project
smairt paper enable /path/to/project
smairt hpc disable /path/to/project
smairt settings /path/to/project --experience advanced --no-motion
```

Project Check is read-only. It exits `0` when no structural or configuration
issues are found and `1` otherwise. `smairt repair` previews only deterministic
tool-owned repairs; pass `--select REPAIR --confirm` to apply a reviewed repair.
The dashboard's Optional capabilities screen chooses Paper and HPC together. It
previews exactly which files enabling would create, derived from the same
rendering the write itself uses, and writes nothing until that preview is
accepted. Paper and HPC deactivation never deletes project files. Motion is
enabled only for interactive terminals and can be disabled locally with
`--no-motion`; it is suppressed for tests, redirected output, JSON, and CI.

## Upgrading An Existing Project

A project records the scaffold version that made it. When you update SMAIRT, an
existing project reports `scaffold-version-mismatch` and package-owned changes
wait for an explicit upgrade:

```bash
smairt upgrade /path/to/project            # preview; writes nothing
smairt upgrade /path/to/project --confirm  # apply
```

The preview lists exactly which tool-owned guidance would be rewritten, which
files would be created, and which files are kept untouched. It is rendered from
the same contract the write uses, so it cannot describe a different operation.
Researcher work is never read, rewritten, or judged, and a starter file that
differs from the installed text is kept as it is.

A managed path that resolves outside the project, through a symbolic link on the
file or on one of its parent directories, is reported and never written. Each
file is replaced atomically, so a failure partway leaves the previous content
intact rather than a half-written file, and the project version moves last, so an
interrupted upgrade stays on its old version and the same command can be run
again.

Advanced Mode adds one `Advanced ▸` row that opens contract inspection, verbose
Project Check, managed-asset regeneration, convention controls, and detected
local tools, rather than lengthening the everyday menu.

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

## Current Limits

- Existing folders without `smairt.yaml` are not adopted or migrated.
- Project Check diagnoses structure and configuration; it does not inspect
  scientific correctness or modify researcher-authored content.
- Repairs, regeneration, and upgrades are limited to deterministic, tool-owned
  assets. An upgrade never rewrites researcher work or a modified starter.
- HPC support supplies guidance and a template, not scheduler integration.
- Native Windows support is deferred.
- Demos under `demos/` show a superseded workflow. Their scientific reasoning
  still holds; their commands and directory layouts do not.

## Changes

[CHANGELOG.md](CHANGELOG.md) records what changed in each version and what an
existing project needs to do about it.

## Development

Clone into an ordinary local directory rather than a cloud-synced folder such
as OneDrive, iCloud Drive, or Dropbox. Generated development files (`.venv`,
caches, `dist`, and smoke-install workspaces) are large, disposable, and not
tracked by Git; syncing them wastes upload capacity and can corrupt a virtual
environment when files are offloaded to the cloud:

```bash
git clone https://github.com/PNNL-CompBio/smairt-template.git ~/Developer/smairt-template
cd ~/Developer/smairt-template
```

Install development dependencies and run all release gates locally:

```bash
uv sync --all-extras --locked
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest tests/test_cli.py
uv run pytest
uv build
uv run python scripts/smoke_install.py --artifact dist --kind wheel --workspace .smoke/wheel
uv run python scripts/smoke_install.py --artifact dist --kind sdist --workspace .smoke/sdist
```

GitHub Actions runs these gates on Ubuntu and macOS with Python 3.11, 3.12, and
3.13.
