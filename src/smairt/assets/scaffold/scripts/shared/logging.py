"""Write experiment output to the terminal and a timestamped log file."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import TextIO


class TeeLogger:
    """Redirect standard output to both its original stream and a log file."""

    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self._console: TextIO | None = None
        self._log: TextIO | None = None

    def __enter__(self) -> TeeLogger:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._console = sys.stdout
        self._log = self.log_path.open("w")
        sys.stdout = self
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._console is not None:
            sys.stdout = self._console
        if self._log is not None:
            self._log.close()
        self._console = None
        self._log = None

    def write(self, message: str) -> int:
        written = 0
        if self._console is not None:
            written = self._console.write(message)
        if self._log is not None:
            self._log.write(message)
        return written

    def flush(self) -> None:
        if self._console is not None:
            self._console.flush()
        if self._log is not None:
            self._log.flush()


def setup_logging(script_name: str, logs_dir: Path, timestamp: str | None = None) -> Path:
    """Return a timestamped log path for an experiment script."""
    value = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir / f"{script_name}_{value}.log"
