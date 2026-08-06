# Utilities

Scripts that support the work without testing anything: a downloader, a converter, a figure
regenerator, a data-checking helper you run by hand.

A utility takes no iteration number and appears in no log. That is the whole distinction:

- **An iteration tests a hypothesis.** It gets a number from `new_iteration.py`, and that
  number joins its hypothesis, script, log, and analysis. Every numbered script appears in
  `analysis/ITERATION_LOG.md`.
- **A utility does not.** Numbering it would put a row in the iteration log for something that
  settles no question, and the log is the record of what the project actually tested.

Create one with:

```bash
python3 scripts/new_utility.py fetch_reference_data --purpose "Download the reference set"
```

That wires logging for you and writes the script here. If what you are about to write tests
something, create an iteration instead — `python3 scripts/new_iteration.py`.

Utilities are yours. SMAIRT never regenerates or judges them. Shared code that several
scripts import belongs in `scripts/shared/` rather than here.
