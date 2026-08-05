"""Write complete experiment output, provenance, and run status to one unique log."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import socket
import subprocess
import sys
import traceback as traceback_module
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import Any, TextIO


class TeeLogger:
    """Duplicate stdout and stderr while retaining traceback and final run status.

    A log that ends at a traceback does not state whether the process failed or merely
    printed one. The status line is therefore written by the context manager itself on
    both paths, after all researcher output and before the log closes.
    """

    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self.status = "NOT STARTED"
        self._stdout: TextIO | None = None
        self._stderr: TextIO | None = None
        self._stdout_tee: _TeeStream | None = None
        self._stderr_tee: _TeeStream | None = None
        self._log: TextIO | None = None

    def __enter__(self) -> TeeLogger:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        self._log = self.log_path.open("x", buffering=1)
        self._stdout_tee = _TeeStream(self._stdout, self._log)
        self._stderr_tee = _TeeStream(self._stderr, self._log)
        sys.stdout = self._stdout_tee
        sys.stderr = self._stderr_tee
        self.status = "RUNNING"
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        clean_exit = isinstance(exc_value, SystemExit) and exc_value.code in (None, 0)
        if exc_type is not None and exc_value is not None and not clean_exit:
            traceback_module.print_exception(exc_type, exc_value, traceback, file=self._stderr_tee)
            self.status = f"FAILED ({exc_type.__name__})"
        else:
            self.status = "SUCCEEDED"
        if self._log is not None:
            self._log.write(f"\nRun status: {self.status}\n")
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
    """Reserve and return a unique timestamped log path.

    Microseconds make ordinary collisions unlikely; exclusive creation makes them
    impossible. A deterministic timestamp used by a test or caller receives a numeric
    suffix instead of replacing an earlier run.
    """
    value = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logs_dir.mkdir(parents=True, exist_ok=True)
    candidate = logs_dir / f"{script_name}_{value}.log"
    suffix = 2
    while candidate.exists():
        candidate = logs_dir / f"{script_name}_{value}_{suffix}.log"
        suffix += 1
    return candidate


def write_provenance(
    *,
    project_root: Path,
    config: dict[str, Any] | None = None,
    input_paths: list[Path] | None = None,
) -> None:
    """Print the default run identity into the active TeeLogger.

    Empty arguments are still facts: `Config: {}` says no separate runtime configuration
    was supplied. When callers do not name inputs, every regular data file is inventoried
    so the log does not depend on the current contents of `data/` to explain itself.
    """
    print("=== Run provenance ===")
    print(f"Started: {datetime.now().astimezone().isoformat()}")
    print(f"Python executable: {_private_path(sys.executable)}")
    print(f"Python version: {platform.python_version()}")
    print(f"Dependencies: {_dependency_versions()}")
    print(f"Git commit: {_git_commit(project_root)}")
    print(f"Arguments: {json.dumps([_private_path(value) for value in sys.argv])}")
    print(f"Config: {json.dumps(config or {}, sort_keys=True, default=str)}")
    print(f"Host: {_host_identity()} ({platform.platform()})")
    print(f"Device: {_device_identity()}")
    print("Inputs:")
    paths = input_paths if input_paths is not None else _default_inputs(project_root)
    if not paths:
        print("- none declared or found")
    for path in paths:
        resolved = path if path.is_absolute() else project_root / path
        relative = _relative_or_absolute(resolved, project_root)
        if resolved.is_file():
            print(
                f"- {relative} | bytes={resolved.stat().st_size} | "
                f"sha256={_cached_sha256(resolved, project_root)}"
            )
        else:
            print(f"- {relative} | MISSING")
    print("=== End provenance ===")


def _dependency_versions() -> str:
    """Return installed distribution versions in one stable, readable value."""
    values = sorted(
        f"{distribution.metadata['Name']}=={distribution.version}"
        for distribution in importlib.metadata.distributions()
    )
    return ", ".join(values) if values else "none"


def _git_commit(project_root: Path) -> str:
    """Return the checked-out commit, or an explicit non-repository value."""
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "not available (not a Git repository or Git is unavailable)"


def _host_identity() -> str:
    """Return a stable host identifier without publishing a workstation's name."""
    hostname = socket.gethostname().encode()
    return f"sha256:{hashlib.sha256(hostname).hexdigest()[:12]}"


def _private_path(value: str) -> str:
    """Replace the current home directory so logs do not publish local usernames."""
    home = str(Path.home())
    return value.replace(home, "<HOME>") if home else value


def _device_identity() -> str:
    """Return useful accelerator visibility without importing optional frameworks."""
    visible = {
        name: os.environ[name]
        for name in ("CUDA_VISIBLE_DEVICES", "ROCR_VISIBLE_DEVICES", "MPS_VISIBLE_DEVICES")
        if name in os.environ
    }
    machine = platform.machine() or "unknown architecture"
    return f"{machine}; visible accelerators={json.dumps(visible, sort_keys=True)}"


def _default_inputs(project_root: Path) -> list[Path]:
    """Return regular data files, excluding the provenance guidance itself."""
    data = project_root / "data"
    if not data.exists():
        return []
    return sorted(path for path in data.rglob("*") if path.is_file() and path.name != "README.md")


def _relative_or_absolute(path: Path, project_root: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _cached_sha256(path: Path, project_root: Path) -> str:
    """Return an input checksum, caching by path, size, and modification time.

    Real data can be terabytes. Hashing it on every run makes provenance the dominant
    computation, while trusting a filename is not identity. The cache hashes each file
    fully the first time and again whenever its size or nanosecond modification time
    changes. Cache failure only costs performance; it never prevents or changes a run.
    """
    cache_path = project_root / "results" / "provenance" / "input_checksums.json"
    key = _relative_or_absolute(path, project_root)
    stat = path.stat()
    fingerprint = {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns}
    cache: dict[str, dict[str, int | str]] = {}
    try:
        loaded = json.loads(cache_path.read_text())
        if isinstance(loaded, dict):
            cache = loaded
    except (OSError, json.JSONDecodeError):
        pass
    entry = cache.get(key, {})
    if (
        entry.get("size") == fingerprint["size"]
        and entry.get("mtime_ns") == fingerprint["mtime_ns"]
    ):
        cached = entry.get("sha256")
        if isinstance(cached, str):
            return cached

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    value = digest.hexdigest()
    cache[key] = {**fingerprint, "sha256": value}
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n")
    except OSError:
        pass
    return value


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

    def __getattr__(self, name: str) -> Any:
        """Delegate file-like attributes used by progress and scientific libraries."""
        return getattr(self.console, name)
