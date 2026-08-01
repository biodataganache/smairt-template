#!/usr/bin/env python3
"""Observe project-controlled progress files without managing a process or scheduler job."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path


def report(progress_path: Path, log_path: Path | None) -> None:
    print(f"Progress check: {datetime.now().isoformat(timespec='seconds')}")
    if progress_path.is_file():
        try:
            progress = json.loads(progress_path.read_text())
        except json.JSONDecodeError as error:
            print(f"Progress file is not valid JSON: {error}")
        else:
            print(json.dumps(progress, indent=2, sort_keys=True))
    else:
        print(f"Progress file not found: {progress_path}")
    if log_path is not None and log_path.is_file():
        lines = log_path.read_text(errors="replace").splitlines()
        print(f"Latest log lines ({log_path}):")
        for line in lines[-10:]:
            print(f"  {line}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("progress", type=Path, help="JSON progress file written by an experiment.")
    parser.add_argument("--log", type=Path, help="Optional experiment log to summarize.")
    parser.add_argument("--watch", action="store_true", help="Repeat until interrupted.")
    parser.add_argument("--interval", type=int, default=30, help="Watch interval in seconds.")
    arguments = parser.parse_args()
    while True:
        report(arguments.progress, arguments.log)
        if not arguments.watch:
            return
        try:
            time.sleep(arguments.interval)
        except KeyboardInterrupt:
            return


if __name__ == "__main__":
    main()
