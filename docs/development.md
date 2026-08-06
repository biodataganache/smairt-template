# Development

## Clone

Clone into an ordinary local directory rather than a cloud-synced folder such as OneDrive,
iCloud Drive, or Dropbox. Generated development files (`.venv`, caches, `dist`, smoke-install
workspaces) are large, disposable, and untracked; syncing them wastes upload capacity and can
corrupt a virtual environment when files are offloaded to the cloud.

```bash
git clone https://github.com/PNNL-CompBio/smairt-template.git ~/Developer/smairt-template
cd ~/Developer/smairt-template
uv sync --all-extras --locked
```

## Release gates

These are exactly what CI runs:

```bash
uv run ruff format --check .
uv run ruff check .
uv run ruff check --config config/ruff-demos.toml demos/
uv run mypy src tests
uv run python scripts/ci_scaffold_diff.py
uv run pytest
uv build
uv run python scripts/smoke_install.py --artifact dist --kind wheel --workspace .smoke/wheel
uv run python scripts/smoke_install.py --artifact dist --kind sdist --workspace .smoke/sdist
```

`demos/` is excluded from the project's own Ruff configuration and linted separately against a
narrow rule set, because five demos are historical scientific records rather than current code.
See `config/ruff-demos.toml` for which rules apply and why.

GitHub Actions runs all of them on Ubuntu and macOS with Python 3.11, 3.12, and 3.13 — six
cells. It also runs on any `verify/**` branch and by manual dispatch, so the matrix is reachable
before opening a pull request.

**Reach for that.** Local runs share your machine's state and cannot see what only a clean
checkout can. An empty declared directory once passed every local gate and failed all six CI
cells, because Git does not track empty directories and the fixture existed only in the working
tree that generated it.

## The scaffold blueprint

`src/smairt/assets/scaffold-blueprint.yaml` is the authoritative declaration of what a generated
project contains: paths, purposes, ownership, and activation conditions. One module interprets it
for generation, checking, inspection, repair, regeneration, and capability activation.

Changing it is a change to the product, so it must be visible:

```bash
uv run python scripts/scaffold_diff.py OLD.yaml src/smairt/assets/scaffold-blueprint.yaml
```

CI prints this diff against the pull request's base branch, separately from ordinary
implementation changes. See [ADR 0001](adr/0001-protect-generated-project-surface.md).

Two rules the blueprint enforces on itself:

- **Nothing may ship as an empty directory.** Git cannot track one, so it would not survive a
  clone.
- **Every file a helper creates must be declared.** Otherwise a project contains files the
  blueprint does not know about, which is a second definition of what a project is.

## Golden projects

`tests/fixtures/golden/` holds three complete normalized generated projects — base, Paper, and
HPC — as an independent record of expected output. Generator and checker agreeing with each other
proves nothing if both are wrong.

```bash
uv run python scripts/update_goldens.py
```

Inspect the resulting diff before committing. A change you did not intend is the point of the
fixtures.

## Ownership vocabulary

Four categories, defined in [CONTEXT.md](../CONTEXT.md):

| Ownership | Meaning |
|---|---|
| `tool-guidance` | Package-maintained. Modifications are reported and preserved. |
| `editable-starter` | Supplied to be edited. Content is not enforced after creation. |
| `researcher-work` | Owned entirely by the researcher. Never regenerated or judged. |
| Historical reference | Archived; not part of active generation or checks. |

Getting this wrong is how a tool destroys work, so an asset's ownership is part of the review of
any blueprint change.

## Version numbers

`pyproject.toml` is the only place a version is written. `__version__` reads installed
distribution metadata, and `scaffold_version` derives from `__version__`. Do not restate a
version as a literal anywhere — a test enforces this.

Bump the minor version when the blueprint's declared surface changes, because existing projects
must then be told they are behind. See [scaffold-transition.md](scaffold-transition.md).

## Testing conventions

- Tests exercise the installed command through public seams rather than importing internals.
- pty-driven tests wait for the pty to fall quiet before writing input. Seeing prompt text is not
  the same as the reader being ready for it, and input written mid-paint is dropped rather than
  queued.
- Prefer a test that asserts a class of defect over one that pins a single line.

## Contributing

See [CONTRIBUTING.md](../.github/CONTRIBUTING.md).
