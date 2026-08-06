# SMAIRT

**Scientific Method with AI Research Toolkit**

SMAIRT creates research workspaces that keep an honest record. Every result traces back to the
hypothesis it tested, the script that produced it, and the raw log it came from — so a question
asked six months later has an answer.

It is built for working alongside a coding assistant, but nothing in a SMAIRT project depends on
one. A project is ordinary readable files: Markdown, Python, YAML.

## Install

Python 3.11–3.13 on macOS, Linux, or Windows via WSL. Native Windows is not supported.

```bash
git clone https://github.com/PNNL-CompBio/smairt-template.git
cd smairt-template
uv tool install .
smairt --version
```

Use `pipx install .` if `uv` is unavailable. After updating your checkout, reinstall with
`uv tool install --force .` or `pipx reinstall smairt`.

This is a repository install, not a PyPI release.

## Create a project

```bash
smairt new
```

Guided creation walks fourteen screens, every answer editable until the last. You name a folder;
it derives the immutable project identifier and shows you both before writing anything.

Or give it everything at once:

```bash
smairt new ./classification_noise_study \
  --name "Classification Noise Study" \
  --slug classification_noise_study \
  --description "How label noise affects classifier calibration" \
  --researcher "Ada Researcher" \
  --domain "Computational biology" \
  --accept-license
```

Add `--paper`, `--hpc`, or `--git` as needed. Creation is atomic: it writes into a temporary
sibling and moves it into place, so a failure never leaves a half-built project.

## The loop

```bash
python3 scripts/new_track.py "Label noise degrades calibration" synthetic
# write the prediction and both criteria in hypotheses/HYPOTHESIS_01.md, and commit them
python3 scripts/new_iteration.py baseline synthetic --hypothesis HYPOTHESIS_01
python3 experiments/01_synthetic/script_01_baseline.py
cp analysis/ANALYSIS_TEMPLATE.md analysis/ANALYSIS_01.md
python3 scripts/record_outcome.py 1 --outcome "Criterion met, 0.71 against a 0.65 target"
```

The number `01` joins the hypothesis, the script, its log, and the analysis. Only
`new_iteration.py` assigns it, which is what keeps the chain joinable — a script you create by
hand belongs to nothing.

Committing the criteria *before* the experiment exists is what keeps the test a test.

Lost the thread?

```bash
smairt open .
```

That reports where the work stands and the command that moves it forward, derived from the
records rather than from a fixed script.

**[Full workflow →](docs/workflow.md)**

## Managing a project

```bash
smairt check .        # read-only structural and configuration diagnostics
smairt repair .       # preview deterministic fixes to tool-owned files
smairt upgrade .      # preview moving onto a newer scaffold
smairt settings .     # metadata, phase, assistant, conventions, preferences
smairt paper enable . # additive publication workspace
smairt hpc enable .   # additive cluster guidance
```

Running `smairt` inside a project opens a dashboard; running it elsewhere opens Home.

Anything that would change files previews first and writes only on `--confirm`. Researcher work
is never read, rewritten, or judged.

## What SMAIRT will not do

It does not perform science. It does not validate a conclusion, judge a hypothesis, or decide
whether a result is good. The question, the evidence, and the interpretation are yours.

Other current limits:

- Existing folders without `smairt.yaml` are not adopted or migrated.
- Repairs, regeneration, and upgrades touch only deterministic tool-owned assets.
- HPC support supplies guidance and templates, not scheduler integration.
- Native Windows support is deferred; use WSL.

## Documentation

| Document | For |
|---|---|
| [docs/workflow.md](docs/workflow.md) | The research loop, phases, utilities, checks |
| [docs/capabilities.md](docs/capabilities.md) | Paper and HPC overlays |
| [docs/upgrading.md](docs/upgrading.md) | Scaffold versions, upgrades, exit codes |
| [docs/development.md](docs/development.md) | Contributing, gates, blueprint, goldens |
| [CHANGELOG.md](CHANGELOG.md) | What changed, and what a project must do about it |
| [CONTEXT.md](CONTEXT.md) | Domain vocabulary and invariants |

## Examples

[`demos/`](demos/) holds worked studies across enzyme kinetics, orbital mechanics, proteomics,
network biology, epidemiology, and protein language models.

> **Note:** the completed demo projects predate the current CLI. Their scientific reasoning
> holds; their commands and directory layouts do not. They are being rewritten against the
> current toolkit.

## Legacy

SMAIRT began as a Cookiecutter template, retained under [`legacy/`](legacy/) as a historical
reference only. It is unsupported and receives no fixes. Use the installed `smairt` command.

## License

[MIT](LICENSE). Generated projects choose MIT or BSD-3-Clause and receive the complete license
text.
