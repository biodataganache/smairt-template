# Upgrading an existing project

A project records the scaffold version that made it, in `smairt.yaml`. When you update SMAIRT,
that recorded version and the installed one disagree, and the project says so.

## Why a mismatch blocks things

```bash
smairt check .
# [scaffold-version-mismatch] Project scaffold 0.4.0 differs from installed SMAIRT 0.5.0.
# Run `smairt upgrade` to review and apply the difference.
```

Package-owned changes — repair, regeneration, capability toggles — wait for an explicit upgrade
rather than acting on a project shaped by a different version of the tool. Guessing what a
half-recognized project should look like is how work gets destroyed. Every refusal names the
command that resolves it.

## Upgrading

```bash
smairt upgrade .            # preview; writes nothing
smairt upgrade . --confirm  # apply
```

The preview lists which tool-owned guidance would be rewritten, which files would be created,
and how many are already current. It is rendered from the same plan the write uses, so it cannot
describe an operation different from the one that runs.

## What an upgrade will not touch

- **Researcher work is never read, rewritten, or judged.** Your hypotheses, analyses, logs,
  data, and scripts are not inputs to an upgrade.
- **A modified starter file is kept as it is.** If you edited a file SMAIRT supplied as a
  starting point, your version stays.
- **A path that resolves outside the project is reported and never written**, including through
  a symbolic link on the file itself or on any parent directory.
- **Each file is replaced atomically**, so a failure partway leaves the previous content intact
  rather than a half-written file.
- **The version moves last.** An interrupted upgrade stays on its old version, and the same
  command can simply be run again.

## Exit codes

Every command uses the same three:

| Code | Meaning |
|---|---|
| `0` | The command did what it said. |
| `1` | The project was found, and the operation failed or reported findings. |
| `2` | The command could not be carried out: no project there, or unusable arguments. |

`smairt check` is read-only: `0` when it finds nothing, `1` when it reports findings.

## Related commands

```bash
smairt repair .       # preview deterministic fixes for tool-owned files
smairt regenerate .   # restore missing or replace unmodified managed assets
smairt inspect .      # the full contract, optionally with --hashes
```

`smairt regenerate` leads with what is missing and therefore actionable, and names anything it
would refuse because you have modified it. `--all` lists everything.

## Settings

```bash
smairt settings . --question "Does X predict Y?"
smairt settings . --experience advanced --no-motion
```

Updates approved metadata, collaborators, current phase, assistant, conventions, or local
dashboard preferences. It cannot change the immutable project slug or folder. A license change
shows a preview, requires `--confirm-license`, and refuses to replace `LICENSE` text you have
modified.

Advanced mode adds one `Advanced ▸` row to the dashboard opening contract inspection, verbose
check, regeneration, convention controls, and detected local tools — rather than lengthening the
everyday menu.

## Version history

[CHANGELOG.md](../CHANGELOG.md) records what changed and what an existing project needs to do
about it. [scaffold-transition.md](scaffold-transition.md) records why each scaffold version
moved.

## Next

- [The research workflow](workflow.md)
- [Paper and HPC capabilities](capabilities.md)
