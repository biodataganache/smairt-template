"""
TeeLogger — dual console + file logging for SMAIRT experiment scripts.

Usage:
    from scripts.shared import TeeLogger, setup_logging

    # Context manager (recommended):
    log_path = setup_logging("script_01_description", Path("results/logs"))
    with TeeLogger(log_path):
        print("This goes to both console and log file")

    # Manual open/close:
    tee = TeeLogger(log_path)
    tee.open()
    print("Logged to both outputs")
    tee.close()
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


class TeeLogger:
    """
    Redirect stdout to both console and a log file simultaneously.

    Supports use as a context manager for clean resource management.
    """

    def __init__(self, log_path: Path):
        self.log_path = Path(log_path)
        self._original_stdout = None
        self._log_file = None

    def open(self) -> 'TeeLogger':
        """Start tee-logging."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._original_stdout = sys.stdout
        self._log_file = open(self.log_path, "w")
        sys.stdout = self
        return self

    def close(self) -> None:
        """Stop tee-logging and restore stdout."""
        if self._original_stdout is not None:
            sys.stdout = self._original_stdout
        if self._log_file is not None:
            self._log_file.close()
            self._log_file = None

    def __enter__(self) -> 'TeeLogger':
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def write(self, message: str) -> None:
        """Write to both console and log file."""
        if self._original_stdout is not None:
            self._original_stdout.write(message)
        if self._log_file is not None:
            self._log_file.write(message)

    def flush(self) -> None:
        """Flush both outputs."""
        if self._original_stdout is not None:
            self._original_stdout.flush()
        if self._log_file is not None:
            self._log_file.flush()


def setup_logging(script_name: str, logs_dir: Path, timestamp: Optional[str] = None) -> Path:
    """
    Create log directory and return the log file path.

    Args:
        script_name: Name of the script (e.g., "script_01_smoke_test")
        logs_dir: Directory for log files (e.g., Path("results/logs"))
        timestamp: Optional timestamp string. If None, uses current time.

    Returns:
        Path to the log file
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir / f"{script_name}_{timestamp}.log"
