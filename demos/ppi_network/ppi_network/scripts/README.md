# Scripts

The active helper set is deliberately small and non-destructive.

| Helper | Purpose |
|---|---|
| `new_script.py` | Create the next numbered experiment script in any phase. |
| `shared/logging.py` | Capture stdout, stderr, warnings, and uncaught tracebacks in a tracked log. |
| `monitor_template.py` | Observe a JSON progress file and optional log without managing a job. |
| `generate_manifest.py` | Print or create a new inventory of evidence without rewriting it. |

Create a numbered experiment scaffold from the project root:

```bash
python scripts/new_script.py synthetic baseline --hypothesis "The baseline exceeds chance"
```

Implement the generated script and run it from the project root. It writes a complete
execution record to `results/logs/`; interpret that evidence in `analysis/`.

Run each helper with `--help`. Browser compilers and destructive Paper iteration helpers are
historical reference material and are not part of active projects.
