# Output Logs

Script output is automatically captured here by **TeeLogger**.

## How It Works

When scripts use TeeLogger from `scripts/shared/logging.py`, all `print()` output is simultaneously:
1. Displayed in the terminal (for real-time monitoring)
2. Saved to a timestamped log file in this directory

## Naming Convention

Log files are auto-named to match their scripts:
```
script_01_initial_test_YYYYMMDD_HHMMSS.log
script_02_add_noise_YYYYMMDD_HHMMSS.log
```

## Purpose

These logs serve as:
1. **The audit trail** - Connect hypothesis → script → log → interpretation
2. **AI context** - AI can read these directly (IDE-native) or they feed into `compile_for_ai.py` (browser-paste)
3. **Reproducibility record** - Full output preserved for each experiment run

## The Audit Trail Connection

```
hypotheses/H1_*.md → experiments/script_XX_*.py → results/logs/script_XX_*.log → analysis/
```

Each log file is the "results" piece that connects the experiment to its interpretation.
