"""Write complete experiment output to the terminal and a timestamped log file."""

from __future__ import annotations

import sys
import traceback as traceback_module
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import TextIO


class TeeLogger:
    """Duplicate stdout and stderr while retaining uncaught traceback output."""

    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self._stdout: TextIO | None = None
        self._stderr: TextIO | None = None
        self._stdout_tee: _TeeStream | None = None
        self._stderr_tee: _TeeStream | None = None
        self._log: TextIO | None = None

    def __enter__(self) -> TeeLogger:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        self._log = self.log_path.open("w", buffering=1)
        self._stdout_tee = _TeeStream(self._stdout, self._log)
        self._stderr_tee = _TeeStream(self._stderr, self._log)
        sys.stdout = self._stdout_tee
        sys.stderr = self._stderr_tee
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None and exc_value is not None:
            traceback_module.print_exception(exc_type, exc_value, traceback, file=self._stderr_tee)
        if self._stdout is not None:
            sys.stdout = self._stdout
        if self._stderr is not None:
            sys.stderr = self._stderr
        if self._log is not None:
            self._log.close()
        self._stdout = None
        self._stderr = None
        self._stdout_tee = None
        self._stderr_tee = None
        self._log = None

    def write(self, message: str) -> int:
        return self._stdout_tee.write(message) if self._stdout_tee is not None else 0

    def flush(self) -> None:
        if self._stdout_tee is not None:
            self._stdout_tee.flush()
        if self._stderr_tee is not None:
            self._stderr_tee.flush()


def setup_logging(script_name: str, logs_dir: Path, timestamp: str | None = None) -> Path:
    """Return a timestamped log path for an experiment script."""
    value = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir / f"{script_name}_{value}.log"


class _TeeStream:
    def __init__(self, console: TextIO, log: TextIO) -> None:
        self.console = console
        self.log = log

    def write(self, message: str) -> int:
        written = self.console.write(message)
        self.log.write(message)
        return written

    def flush(self) -> None:
        self.console.flush()
        self.log.flush()
