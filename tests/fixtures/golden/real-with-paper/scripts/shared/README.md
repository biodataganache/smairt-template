# Shared Experiment Code

Move code into `scripts/shared/` when it is reused, complex enough to test independently, or
needs one fix to propagate across experiments.

| Module | Purpose | Key Exports |
|---|---|---|
| `logging.py` | Complete terminal and file logging | `TeeLogger`, `setup_logging` |

Experiment scripts add the project root to `sys.path`, then import from `scripts.shared`.
Document new modules here and record broadly useful patterns in `prompts/KNOWN_PATTERNS.md`.

Shared code does not replace numbered experiment scripts. Each scientific test still needs a
readable script, hypothesis link, raw log, and analysis.
