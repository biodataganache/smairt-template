# Experiment Scripts

Create a numbered experiment scaffold from the project root:

```bash
python scripts/new_script.py synthetic baseline --hypothesis "The baseline exceeds chance"
```

Implement the generated script and run it from the project root. It writes raw
terminal output to `results/logs/`; interpret that output in `analysis/`.
