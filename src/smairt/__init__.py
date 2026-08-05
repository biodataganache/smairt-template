"""SMAIRT project creation tools."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("smairt")
except PackageNotFoundError:  # pragma: no cover - only when running from an uninstalled tree
    # Reading the installed distribution's metadata makes `pyproject.toml` the single place
    # a version is written. Every other version reference in the package derives from this
    # one, so a release cannot leave `__version__`, `scaffold_version`, and the packaged
    # version disagreeing with each other.
    __version__ = "0.0.0+unknown"
