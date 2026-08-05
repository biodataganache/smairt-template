# Contributing To SMAIRT

SMAIRT is an installable research-workspace generator. The supported
development platforms are macOS, Linux, and WSL with Python 3.11 through 3.13.
Native Windows support is deferred.

## Development Setup

```bash
git clone https://github.com/PNNL-CompBio/smairt-template.git
cd smairt-template
uv sync --all-extras --locked
```

Use a feature branch, make focused changes, and open a pull request against the
canonical PNNL repository. Do not claim that the preview is published on PyPI.

## Required Checks

Run the same gates used by CI before opening a pull request:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest tests/test_cli.py
uv run pytest
uv build
uv run python scripts/smoke_install.py --artifact dist --kind wheel --workspace .smoke/wheel
uv run python scripts/smoke_install.py --artifact dist --kind sdist --workspace .smoke/sdist
```

The focused suite exercises the installed command seam.
The artifact smoke tests install the wheel and source distribution into clean
environments, create a representative project, and run Project Check.

## Documentation And Compatibility

- Document `smairt new` as the normal onboarding path.
- Keep `uv tool install .` as the repository-preview installation command;
  document `pipx install .` as the fallback.
- Treat Cookiecutter files as unsupported historical references only. The CLI
  is the sole supported generator.
- Keep generated-project guidance aligned with actual `smairt` commands and
  assets. Do not introduce browser-paste, removed helper-script, or stale
  Cookiecutter repository instructions.
