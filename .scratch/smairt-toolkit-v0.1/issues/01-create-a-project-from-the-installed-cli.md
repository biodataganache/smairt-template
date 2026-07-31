# 01 - Create a project from the installed CLI

**What to build:** Deliver the first complete `smairt new` path: a packaged command accepts project choices, validates them through a versioned project contract, renders the corrected canonical SMAIRT scaffold atomically, records managed-file ownership, optionally initializes Git without committing, and leaves a readable project that can be checked through the command line. Keep a functional legacy Cookiecutter entry point backed by the same canonical assets.

**Blocked by:** None - can start immediately.

**Status:** done

- [x] The package installs on Python 3.11+ and exposes `smairt --version` and a non-interactive project-creation path suitable for testing.
- [x] A created project contains valid versioned YAML metadata and Git-ignored local managed-file bookkeeping.
- [x] Synthetic, Downloaded/benchmark, and Real starting phases produce the agreed directory sets.
- [x] Paper and HPC assets are independently selectable and Paper analyses use a separate Paper analysis area.
- [x] Generation uses a temporary sibling and never exposes a partial or overwrites a non-empty destination.
- [x] Optional email is omitted, browser-paste/example options are absent, canonical naming and log-first guidance are used, and stale commands/links are corrected.
- [x] Git initialization stages files but never commits and degrades clearly when Git is unavailable.
- [x] Legacy Cookiecutter is clearly labeled and produces equivalent meaningful output from the same canonical assets.
- [x] Focused generation, metadata, safety, managed-file, Git, and compatibility tests pass through public seams.
