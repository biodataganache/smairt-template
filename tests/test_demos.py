"""The demos must declare what they import, or they do not run for anyone but their author.

A demo is the first thing a researcher tries after the README, so a missing dependency is a
broken front door. These checks read the demo sources rather than executing them: the point is
that the declared environment is complete, which is knowable without running any science.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).parents[1]
DEMOS = REPOSITORY_ROOT / "demos"

# Modules the standard library supplies, plus the in-project package every generated script
# imports its logging helpers from.
STANDARD_LIBRARY = {
    "abc",
    "argparse",
    "collections",
    "copy",
    "csv",
    "dataclasses",
    "datetime",
    "functools",
    "glob",
    "hashlib",
    "io",
    "itertools",
    "json",
    "logging",
    "math",
    "os",
    "pathlib",
    "pickle",
    "random",
    "re",
    "scripts",
    "shutil",
    "statistics",
    "string",
    "subprocess",
    "sys",
    "textwrap",
    "time",
    "typing",
    "urllib",
    "warnings",
}

# Import name to the distribution that provides it, where they differ.
DISTRIBUTION_NAMES = {
    "Bio": "biopython",
    "PIL": "pillow",
    "esm": "fair-esm",
    "sklearn": "scikit-learn",
    "yaml": "PyYAML",
}


def demo_directories() -> list[Path]:
    return sorted(path.parent for path in DEMOS.glob("*/requirements.txt"))


def declared_distributions(requirements: Path) -> set[str]:
    names: set[str] = set()
    for line in requirements.read_text().splitlines():
        entry = line.strip()
        if not entry or entry.startswith("#"):
            continue
        for separator in ("[", "=", ">", "<", "!", ";", " "):
            entry = entry.split(separator)[0]
        if entry:
            names.add(entry.lower())
    return names


def imported_distributions(demo: Path) -> dict[str, set[Path]]:
    """Return each third-party distribution the demo imports, and where.

    Deferred imports inside a function are reported too. An optional dependency is still a
    dependency; whether it belongs in `requirements.txt` or in a documented extra is the
    question, and that cannot be answered by pretending the import is not there.
    """
    found: dict[str, set[Path]] = {}
    for source in sorted(demo.rglob("*.py")):
        try:
            tree = ast.parse(source.read_text())
        except SyntaxError:  # pragma: no cover - a demo that cannot parse is a separate failure
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                modules = [node.module]
            else:
                continue
            for module in modules:
                root = module.split(".")[0]
                if root in STANDARD_LIBRARY:
                    continue
                distribution = DISTRIBUTION_NAMES.get(root, root)
                found.setdefault(distribution, set()).add(source.relative_to(demo))
    return found


@pytest.mark.parametrize("demo", demo_directories(), ids=lambda path: path.name)
def test_every_demo_declares_what_its_scripts_import(demo: Path) -> None:
    """Three demos shipped unable to run: the imports were there, the declarations were not.

    `ppi_network` imported `sklearn.metrics`, `proteomics_de` imported `seaborn`, and neither
    appeared in its `requirements.txt`. A researcher following the demo installed the listed
    dependencies and got an ImportError on the first script.
    """
    declared = declared_distributions(demo / "requirements.txt")
    imported = imported_distributions(demo)
    undeclared = {
        distribution: sources
        for distribution, sources in imported.items()
        if distribution.lower() not in declared
        # An optional dependency may be documented in a comment instead, but only if the import
        # that needs it explains itself when missing rather than raising a bare ImportError.
        and not _documented_as_optional(demo, distribution)
    }
    assert not undeclared, "\n".join(
        f"{demo.name}: {distribution} imported by "
        + ", ".join(str(source) for source in sorted(sources))
        + " but not declared in requirements.txt"
        for distribution, sources in sorted(undeclared.items())
    )


def _documented_as_optional(demo: Path, distribution: str) -> bool:
    """Return whether requirements.txt names the distribution in a comment as optional."""
    lines = (demo / "requirements.txt").read_text().splitlines()
    commented = [line for line in lines if line.strip().startswith("#")]
    return any(distribution.lower() in line.lower() for line in commented)


@pytest.mark.parametrize("demo", demo_directories(), ids=lambda path: path.name)
def test_an_optional_demo_dependency_explains_itself_when_absent(demo: Path) -> None:
    """A bare ImportError on an optional dependency reads as a broken demo.

    `fair-esm` is genuinely optional: it is needed by one real-data rung and downloads
    pretrained weights on first use. That is a reason to defer the import, not a reason to let
    it fail without saying what to install.
    """
    declared = declared_distributions(demo / "requirements.txt")
    optional = {
        distribution: sources
        for distribution, sources in imported_distributions(demo).items()
        if distribution.lower() not in declared
    }
    for distribution, sources in sorted(optional.items()):
        for source in sorted(sources):
            text = (demo / source).read_text()
            assert "ImportError" in text, (
                f"{demo.name}/{source} imports optional {distribution} without handling its "
                "absence, so a researcher sees a traceback instead of the install command"
            )
            assert distribution in text, (
                f"{demo.name}/{source} handles a missing import without naming {distribution}"
            )
