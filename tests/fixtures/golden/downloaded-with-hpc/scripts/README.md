# Scripts

Four helpers, all non-destructive. Run each from the project root, and use `--help` on
any of them for the full argument list.

| Helper | What it does |
|---|---|
| `new_script.py` | Creates the next numbered experiment script in a phase |
| `shared/logging.py` | Captures a complete execution record to `results/logs/` |
| `generate_manifest.py` | Prints or writes an inventory of research artifacts |
| `monitor_template.py` | Observes a progress file from a long or remote run |

Nothing here deletes, overwrites, or rewrites researcher work.

## new_script.py

```bash
python scripts/new_script.py synthetic baseline --hypothesis "The baseline exceeds chance"
```

The phase is `synthetic`, `downloaded`, or `real`. `--hypothesis` is required, because
naming what a script should settle before writing it is the convention this project
runs on. `--iteration` records which iteration the script belongs to.

Numbering is sequential across the whole project, not per phase, so filenames read as
the order the work happened:

```
experiments/01_synthetic/script_01_baseline.py
experiments/02_downloaded/script_04_benchmark_sweep.py
experiments/03_real_data/script_07_validation.py
```

The generated script puts the project root on the path, imports `TeeLogger` and
`setup_logging`, records the hypothesis in its docstring, and leaves a `TODO` where the
experiment goes. Implement it, then run it from the project root.

## shared/logging.py

`TeeLogger` writes to the console and to a file at once, capturing stdout, stderr,
warnings, and uncaught tracebacks. A generated script already uses it:

```python
log_path = setup_logging(SCRIPT_NAME, PROJECT_ROOT / "results" / "logs")
with TeeLogger(log_path):
    ...
```

Everything the run produced ends up in one file named after the script. A traceback
that appeared only in a terminal is not part of the evidence; this is what stops that
happening.

## generate_manifest.py

```bash
python scripts/generate_manifest.py
python scripts/generate_manifest.py --output analysis/MANIFEST_2024-01-15.md
```

Prints the inventory it finds. With `--output` it writes to a new file. It never
modifies an existing manifest, so deciding what counts as final evidence stays with the
researcher.

## monitor_template.py

```bash
python scripts/monitor_template.py results/progress.json --log results/logs/script_01_baseline_*.log
python scripts/monitor_template.py results/progress.json --watch --interval 60
```

Reads a JSON progress file an experiment writes, and optionally summarizes the tail of a
log. It observes only: it does not start, stop, or manage a process or a scheduler job.

## Adding helpers

Project-specific utilities belong in `scripts/shared/`, imported as
`from scripts.shared.<module> import ...`. See `scripts/shared/README.md`.
