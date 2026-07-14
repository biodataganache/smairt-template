# Git History Remediation Before Public Release

This note documents the executed data-exposure cleanup and Git history rewrite performed to ensure this repository is safe for public release under a completely de-identified identity with no personal identifiable data (PII) or internal machine context.

---

## What was exposed and cleaned

### 1. Personal identity & email in commit metadata
Every commit in the legacy repository was authored by `Salvador Rodarte <sarodarte2@miners.utep.edu>`.
* **Remediation**: The repository history was rewritten using a fresh orphan commit containing only the de-identified working-tree state, authored by `SMAIRT Demos <demos@example.com>`.

### 2. Absolute local filesystem paths in tracked logs and scripts
Paths pointing to `OneDrive - PNNL` or `/Users/salvador.rodarte` were embedded in several tracked logs, script comments, and provenance files.
* **Remediation**: Tracked files were scrubbed in place to replace absolute machine paths with generic relative path placeholders (e.g. `./` or generic subdirectories).

### 3. Absolute local path leaks on log regeneration
The shared `TeeLogger` logging code historically logged messages in place as-written, which would leak the running user's local directory path structure whenever a script was executed or regenerated on their machine.
* **Remediation**: Updated all `scripts/shared/logging.py` modules to automatically intercept and substitute absolute repository or project root prefixes with relative `.` indicators in the generated `.log` outputs, preventing future leakage during local execution.

### 4. High-Volume Viriological (HVP) Large Dataset
The `hvp/` viromics database loader contained over 140 binary `.fsa` and heavy `.xlsx` spreadsheets under `build/resource/HiC_Wu/`.
* **Remediation**: In accordance with publishing guidelines, the `hvp/` demo has been removed entirely from this general demos collection to be distributed alongside its own target publication independently.

---

## Post-Cleanup Verification Checklist

- [x] Removed all nested `.git` and untracked `.DS_Store` files repo-wide.
- [x] Configured a persistent neutral identity locally:
  ```bash
  git config user.name  "SMAIRT Demos"
  git config user.email "demos@example.com"
  ```
- [x] Created a fresh de-identified main history branch with `git checkout --orphan`.
- [x] Removed old `upstream` and `origin` git remotes.
- [x] Purged legacy commit reflogs and forcefully ran aggressive garbage collection:
  ```bash
  git reflog expire --expire=now --all
  git gc --prune=now --aggressive
  ```
- [x] Confirmed zero sensitive email or host matching strings remain in any active files.
