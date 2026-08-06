"""The demos must declare what they import, or they do not run for anyone but their author.

A demo is the first thing a researcher tries after the README, so a missing dependency is a
broken front door. These checks read the demo sources rather than executing them: the point is
that the declared environment is complete, which is knowable without running any science.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).parents[1]
DEMOS = REPOSITORY_ROOT / "demos"

# The standard library, taken from the interpreter rather than hand-listed. A hand-list silently
# reports `platform` or `socket` as a missing dependency the first time a demo imports one, which
# sends the reader looking for a package that does not exist.
STANDARD_LIBRARY = set(sys.stdlib_module_names) | {
    # `scripts` is the in-project package every generated iteration imports its helpers from.
    "scripts",
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


@pytest.mark.parametrize("demo", demo_directories(), ids=lambda path: path.name)
def test_a_demo_never_tells_a_reader_to_copy_a_file_that_is_not_there(demo: Path) -> None:
    """Seven of eight demos pointed at a path that does not exist.

    `cp background/01_initial_question.md <project>/background/` reads plausibly, but the
    reference question lives inside the completed project rather than beside `DEMO.md`. A reader
    following the tutorial hit `No such file or directory` on the first command.
    """
    guide = demo / "DEMO.md"
    if not guide.is_file():
        pytest.skip(f"{demo.name} has no DEMO.md")
    missing: list[str] = []
    for number, line in enumerate(guide.read_text().splitlines(), start=1):
        for source in re.findall(r"\bcp\s+([\w/.-]+)\s", line):
            if not (demo / source).exists():
                missing.append(f"{guide.name}:{number} -> {source}")
    assert not missing, f"{demo.name} documents copying files that do not exist:\n" + "\n".join(
        missing
    )


# How current each demo is. A reader has to be able to tell, because two of these levels document
# a workflow that no longer exists. Recorded here so the classification cannot drift from what the
# demos actually contain.
CURRENT_DEMOS = {"enzyme_kinetics"}
IMPORTED_HISTORY_DEMOS = {"lunar", "peptide_digest"}
LEGACY_DEMOS = {
    "epidemic_sird",
    "ppi_network",
    "protein_lm",
    "protein_properties",
    "proteomics_de",
}
CONFORMING_DEMOS = CURRENT_DEMOS | IMPORTED_HISTORY_DEMOS

# Helpers the current scaffold does not create. A conforming demo that still ships one is telling a
# reader to run something that no longer exists.
RETIRED_HELPERS = ("new_script.py", "new_experiment.py", "finalize_iteration.py")


def completed_project(demo: Path) -> Path | None:
    """Return the completed project inside a demo folder, if it has one."""
    candidates = [
        path
        for path in demo.iterdir()
        if path.is_dir() and not path.name.startswith(".") and path.name != "background"
    ]
    return candidates[0] if len(candidates) == 1 else None


def test_the_demo_status_taxonomy_covers_every_demo() -> None:
    """Every demo carries exactly one status, so none is silently unclassified."""
    classified = CONFORMING_DEMOS | LEGACY_DEMOS
    present = {demo.name for demo in demo_directories()} - {"bring_your_own"}
    assert present == classified, (
        f"unclassified demos: {sorted(present - classified)}; "
        f"classified but absent: {sorted(classified - present)}"
    )


@pytest.mark.parametrize("name", sorted(CONFORMING_DEMOS))
def test_a_conforming_demo_is_a_project_the_tool_recognises(name: str) -> None:
    """A demo claiming to be current must carry the contract that makes that true.

    None of the legacy demos had `smairt.yaml`, so `smairt check` refused all eight. Passing that
    check is the minimum for a demo whose guide teaches the current workflow.
    """
    project = completed_project(DEMOS / name)
    assert project is not None, f"{name} has no single completed project directory"
    contract = project / "smairt.yaml"
    assert contract.is_file(), f"{name} claims to be current but has no smairt.yaml"
    for required in ("analysis/ITERATION_LOG.md", "analysis/RUN_HISTORY.md", "LICENSE"):
        assert (project / required).is_file(), f"{name} is missing {required}"


@pytest.mark.parametrize("name", sorted(CONFORMING_DEMOS))
def test_a_conforming_demo_ships_no_retired_helper(name: str) -> None:
    """A stale helper in a current demo is an instruction to run something that is gone."""
    project = completed_project(DEMOS / name)
    assert project is not None
    for helper in RETIRED_HELPERS:
        assert not (project / "scripts" / helper).exists(), (
            f"{name} still ships scripts/{helper}, which the current scaffold does not create"
        )


@pytest.mark.parametrize("name", sorted(CONFORMING_DEMOS))
def test_a_conforming_demo_teaches_the_current_helpers(name: str) -> None:
    """The guide is what a reader follows, so structural conformance alone is not enough.

    Every demo guide once said "There are no solution scripts here" while shipping a complete
    project, and told readers to hand-create numbered scripts. A demo can pass `smairt check` and
    still teach the retired workflow, which is the failure this catches.
    """
    guide = (DEMOS / name / "DEMO.md").read_text()
    for helper in ("new_track.py", "new_iteration.py", "record_outcome.py"):
        assert helper in guide, f"{name}/DEMO.md never mentions {helper}"
    assert "no solution scripts" not in guide.lower(), (
        f"{name}/DEMO.md claims it has no solution scripts while shipping a completed project"
    )


@pytest.mark.parametrize("name", sorted(LEGACY_DEMOS))
def test_a_legacy_demo_says_so_before_its_instructions(name: str) -> None:
    """A reader must learn a demo is legacy before following steps that no longer apply."""
    guide = (DEMOS / name / "DEMO.md").read_text()
    # "Before its instructions" means before the first top-level section, not merely present
    # somewhere in the file. Splitting on any "## " would match the banner's own subheading.
    lines = guide.splitlines()
    first_section = next(
        (index for index, line in enumerate(lines) if line.startswith("## ")), len(lines)
    )
    banner = "\n".join(lines[:first_section])
    assert "Status: legacy" in banner, (
        f"{name}/DEMO.md has no legacy status banner before its first section"
    )
    assert "docs/workflow.md" in guide, (
        f"{name}/DEMO.md marks itself legacy without pointing at the current workflow"
    )


@pytest.mark.parametrize("name", sorted(CONFORMING_DEMOS))
def test_a_conforming_demo_has_no_dangling_local_link(name: str) -> None:
    """A link into the project is a promise it can be followed.

    The migrated demos carried 47 broken links: some to a repository-root-style prefix that
    resolved nowhere, and some to execution logs that were never committed. The second kind
    matters most, because a link to missing evidence looks like evidence.
    """
    project = completed_project(DEMOS / name)
    assert project is not None
    dangling: list[str] = []
    for document in sorted(project.rglob("*.md")):
        for target in re.findall(r"\]\((?!https?://|#|mailto:)([^)#]+)", document.read_text()):
            if not (document.parent / target.strip()).resolve().exists():
                dangling.append(f"{document.relative_to(project)} -> {target.strip()}")
    assert not dangling, f"{name} has dangling local links:\n" + "\n".join(dangling)


# Files that are data payloads rather than code, configuration, or documentation.
DATA_SUFFIXES = {".csv", ".tsv", ".fasta", ".fa", ".json", ".parquet"}


def data_payloads(demo: Path) -> list[Path]:
    """Return every committed data file under a demo's `data/` directory."""
    return sorted(
        path
        for path in (demo).rglob("data/**/*")
        if path.is_file() and path.suffix.lower() in DATA_SUFFIXES
    )


@pytest.mark.parametrize("demo", demo_directories(), ids=lambda path: path.name)
def test_every_committed_payload_has_recorded_provenance(demo: Path) -> None:
    """A reviewer must be able to tell where a datum came from without reading experiment code.

    Four demos shipped real data behind the scaffold's empty inventory template: STRING
    interactions, UniProt sequences, and two synthetic matrices whose planted truth is what makes
    their analyses meaningful. The template lists a `| | | |` table, so the file looked documented
    while recording nothing.
    """
    payloads = data_payloads(demo)
    if not payloads:
        pytest.skip(f"{demo.name} commits no data payload")

    undocumented: list[str] = []
    for payload in payloads:
        readme = payload.parent / "README.md"
        if not readme.is_file():
            undocumented.append(f"{payload.relative_to(demo)}: no README.md beside it")
            continue
        text = readme.read_text()
        if payload.name not in text:
            undocumented.append(f"{payload.relative_to(demo)}: not named in {readme.name}")
    assert not undocumented, f"{demo.name} has undocumented payloads:\n" + "\n".join(undocumented)


@pytest.mark.parametrize("demo", demo_directories(), ids=lambda path: path.name)
def test_a_documented_payload_records_a_checksum(demo: Path) -> None:
    """Provenance without a checksum cannot be verified, only believed.

    A source and a URL say where a file was meant to come from. A checksum is what lets a reader
    confirm the committed bytes are those bytes, which matters most for the live-service sources
    whose queries are not expected to reproduce the file.
    """
    payloads = data_payloads(demo)
    if not payloads:
        pytest.skip(f"{demo.name} commits no data payload")

    for readme in {payload.parent / "README.md" for payload in payloads}:
        text = readme.read_text().lower()
        assert "sha-256" in text or "sha256" in text, (
            f"{readme.relative_to(demo)} documents a payload without recording a checksum"
        )


def test_the_epidemic_demo_does_not_commit_the_global_snapshot() -> None:
    """The 3.9 MB JHU snapshot must stay fetched-and-verified rather than stored.

    It was committed for three rows the script actually reads, and fetched from a mutable `master`
    URL with no checksum, so what the demo fitted depended on when it ran.
    """
    demo = DEMOS / "epidemic_sird"
    for name in (
        "time_series_covid19_confirmed_global.csv",
        "time_series_covid19_deaths_global.csv",
        "time_series_covid19_recovered_global.csv",
    ):
        found = list(demo.rglob(name))
        assert not found, f"the global JHU snapshot is committed again: {found}"

    script = next(demo.rglob("script_04_fit_published_outbreak.py")).read_text()
    assert "/master/" not in script, "the JHU URL tracks a mutable branch again"
    assert "JHU_COMMIT" in script and "JHU_CHECKSUMS" in script, (
        "the JHU fetch no longer pins a commit and verifies checksums"
    )
    assert "--offline" in script, "the offline fixture path was removed"
