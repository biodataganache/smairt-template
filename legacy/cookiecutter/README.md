# Legacy Cookiecutter Compatibility

Cookiecutter is retained in SMAIRT V0.1 only for existing local automation. It
is not the recommended onboarding path. New projects should install this
repository as a tool and run `smairt new`.

## Requirements

- macOS, Linux, or WSL with Python 3.11 through 3.13. Native Windows is
  deferred.
- An installed copy of this checkout: `uv tool install .` is preferred;
  `pipx install .` is the fallback.
- Cookiecutter available to the invoking environment, for example
  `uv tool install cookiecutter`.

## Repository-Local Command

From the repository root, run:

```bash
cookiecutter .
```

For automation, use the same checkout path explicitly:

```bash
cookiecutter /path/to/smairt-template --no-input \
  project_name="My SMAIRT Project" \
  project_slug=my_smairt_project \
  author_name="Your Name"
```

Do not use a `gh:` shorthand, an old Cookiecutter repository name, or a
browser-paste workflow. The post-generation hook runs the installed `smairt`
package, which is the sole owner of scaffold assets. The resulting project is
equivalent to `smairt new` for the same answers, including Paper, HPC, Git,
assistant pointers, and Project Check behavior.
