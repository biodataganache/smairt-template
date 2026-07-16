#!/usr/bin/env python
"""
Monitor template for long-running experiments.

Create a copy of this script for each long-running job:
    scripts/monitor_XX_progress.py

This script periodically checks results directories for partial output
and reports progress. Useful for HPC jobs that run for hours/days.

Usage:
    python scripts/monitor_XX_progress.py
    python scripts/monitor_XX_progress.py --watch  # continuous monitoring
"""

import argparse
import json
import time
from pathlib import Path
from datetime import datetime


# === CONFIGURATION ===
# Update these for your specific experiment
EXPERIMENT_NAME = "script_XX_description"
RESULTS_DIR = Path("results") / EXPERIMENT_NAME
LOG_DIR = Path("results") / "logs"
EXPECTED_CONDITIONS = 1  # Number of conditions/trials expected
EXPECTED_SEEDS = 3       # Number of seeds per condition


def check_progress():
    """Check and report experiment progress."""
    print(f"\n{'='*60}")
    print(f"Progress Monitor: {EXPERIMENT_NAME}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")

    # Check if results directory exists
    if not RESULTS_DIR.exists():
        print(f"⏳ Results directory not yet created: {RESULTS_DIR}")
        return

    # Count completed results
    result_files = list(RESULTS_DIR.glob("*.json"))
    print(f"📁 Result files found: {len(result_files)}")

    # Check for summary file
    summary_path = RESULTS_DIR / "summary.json"
    if summary_path.exists():
        with open(summary_path) as f:
            summary = json.load(f)
        print(f"✅ Summary file exists!")
        print(f"   Completed: {summary.get('completed', '?')}/{summary.get('total', '?')}")
    else:
        print(f"⏳ No summary file yet")

    # Check log files
    log_files = sorted(LOG_DIR.glob(f"{EXPERIMENT_NAME}*.log"))
    if log_files:
        latest_log = log_files[-1]
        size_kb = latest_log.stat().st_size / 1024
        mtime = datetime.fromtimestamp(latest_log.stat().st_mtime)
        print(f"\n📄 Latest log: {latest_log.name}")
        print(f"   Size: {size_kb:.1f} KB")
        print(f"   Last modified: {mtime.isoformat()}")

        # Read last few lines
        with open(latest_log) as f:
            lines = f.readlines()
        if lines:
            print(f"   Last output:")
            for line in lines[-5:]:
                print(f"     {line.rstrip()}")
    else:
        print(f"\n⏳ No log files found for {EXPERIMENT_NAME}")

    # Check for errors
    error_files = list(RESULTS_DIR.glob("*error*"))
    if error_files:
        print(f"\n❌ ERROR files detected: {len(error_files)}")
        for ef in error_files[:5]:
            print(f"   - {ef.name}")

    print(f"\n{'='*60}")


def watch_progress(interval: int = 30):
    """Continuously monitor progress."""
    print(f"Watching {EXPERIMENT_NAME} (Ctrl+C to stop, interval={interval}s)")
    try:
        while True:
            check_progress()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")


def main():
    parser = argparse.ArgumentParser(description=f"Monitor {EXPERIMENT_NAME} progress")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring")
    parser.add_argument("--interval", type=int, default=30, help="Watch interval (seconds)")
    args = parser.parse_args()

    if args.watch:
        watch_progress(args.interval)
    else:
        check_progress()


if __name__ == "__main__":
    main()
