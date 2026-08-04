from __future__ import annotations

import tempfile
from pathlib import Path

from smairt.generator import generate_project
from smairt.models import (
    Assistant,
    License,
    ProjectIdentity,
    ProjectOptions,
    Researcher,
    StartingPhase,
)
from smairt.project import load_contract
from smairt.scaffold import render_template_assets

LEGACY_TEMPLATE = (
    Path(__file__).resolve().parents[1]
    / "legacy"
    / "cookiecutter"
    / "original-template"
    / "{{ cookiecutter.project_slug }}"
)
"""The byte-identical original scaffold, which is the content baseline for re-enrichment."""


def rendered_assets() -> dict[str, str]:
    """Return every scaffold asset as a researcher would receive it, capabilities included.

    Inactive capabilities are included so Paper and HPC guidance is covered in one
    pass rather than only when a project happens to enable them.
    """
    identity = ProjectIdentity(
        name="Study",
        slug="study",
        description="A study.",
        domain="Computational biology",
    )
    return render_template_assets(
        _contract(identity),
        include_inactive=True,
    )


def _contract(identity: ProjectIdentity) -> object:
    """Return a real contract, built the way generation builds one."""
    with tempfile.TemporaryDirectory() as directory:
        destination = Path(directory) / identity.slug
        generate_project(
            destination,
            ProjectOptions(
                project=identity,
                researcher=Researcher(name="Researcher"),
                assistant=Assistant.OPENCODE,
                starting_phase=StartingPhase.SYNTHETIC,
                license=License.MIT,
                initialize_git=False,
                paper=True,
                hpc=True,
            ),
        )
        return load_contract(destination)


def test_no_generated_asset_carries_a_legacy_template_variable() -> None:
    """A copied legacy asset would crash generation or ship a raw variable to a researcher.

    Markdown assets are rendered, so a surviving variable raises at generation time,
    but Python assets are copied verbatim and are exempt from the unresolved-token
    check, which is exactly where a bad copy would pass silently.
    """
    offenders = sorted(
        relative for relative, content in rendered_assets().items() if "cookiecutter" in content
    )
    assert offenders == []


def test_no_rendered_guidance_asset_carries_an_unrendered_template_construct() -> None:
    """Guidance a researcher reads must be finished prose, not a half-rendered template."""
    offenders = sorted(
        relative
        for relative, content in rendered_assets().items()
        if not relative.endswith(".py") and ("{%" in content or "{{" in content)
    )
    assert offenders == []


RETIRED = (
    "compile_for_ai",
    "new_experiment.py",
    "new_script.py",
    "finalize_iteration",
    "paper_draft/",
    "paper_driven mode",
    "paper-driven mode",
    "workflow mode",
    "BEST_PRACTICE_SINGLE",
)
"""Concepts and helpers the transition record retires, which must stay retired."""


def test_no_generated_guidance_describes_a_retired_helper_or_concept() -> None:
    """Re-enriching from the original must not carry its retired tooling back in.

    The originals were written when a destructive iteration engine and a
    browser-paste compiler existed. Restoring their prose without rewriting these
    passages would hand a researcher instructions for tools that are gone.
    """
    offenders = sorted(
        f"{relative}: {term}"
        for relative, content in rendered_assets().items()
        for term in RETIRED
        if term in content
    )
    assert offenders == []


RETIRED_STRUCTURE = (
    "iter_0",
    "iter_X",
    "iterations/",
    "run_analysis_",
    "lib/core",
    "lib/io",
    "lib/processing",
    "lib/visualization",
    "HNN_",
    "H0X_",
)
"""Paths from the original nested analysis tree, which this scaffold does not create.

An iteration is now a unit of work numbered project-wide rather than a folder inside a
per-analysis tree, and shared code lives in `scripts/shared/` rather than a `lib/`
package. Guidance naming these paths sends a reader to somewhere that does not exist.
"""


def test_no_generated_guidance_directs_a_reader_to_a_path_this_scaffold_never_creates() -> None:
    """Guidance that names a phantom path is worse than absent guidance.

    A reader who follows it either creates a second competing structure or concludes
    the project is broken. This is distinct from a retired helper: the tool is gone in
    that case, whereas here the whole directory layout was replaced.
    """
    offenders = sorted(
        f"{relative}: {term}"
        for relative, content in rendered_assets().items()
        for term in RETIRED_STRUCTURE
        if term in content
    )
    assert offenders == []


DESTRUCTIVE_CALLS = ("shutil.rmtree", "shutil.move", "os.remove", "os.unlink", "Path.unlink")
"""Operations that would destroy researcher work, which no shipped helper may perform."""


def test_no_shipped_helper_can_delete_or_relocate_researcher_work() -> None:
    """The helpers create and append; destroying evidence is never one of their jobs.

    The original iteration workflow deleted prior results when finalizing an iteration.
    The replacement records a pointer to evidence instead, so this asserts the property
    that made the original unsafe cannot return through a later edit.
    """
    offenders = sorted(
        f"{relative}: {call}"
        for relative, content in rendered_assets().items()
        if relative.endswith(".py")
        for call in DESTRUCTIVE_CALLS
        if call in content
    )
    assert offenders == []


def test_a_helper_writing_a_record_opens_it_for_append_rather_than_write() -> None:
    """A record whose earlier lines can be rewritten is not an audit trail.

    Iterations are appended so the sequence of attempts stays intact, including the
    attempts that failed. Opening the log in write mode would silently discard them.
    """
    iterations = rendered_assets()["scripts/shared/iterations.py"]
    assert 'open("a")' in iterations
    assert 'open("w")' not in iterations


def test_exactly_one_shipped_helper_assigns_an_iteration_number() -> None:
    """Two numbering authorities cannot stay consistent, so there must only be one.

    Each would eventually hand out a number the other had already used, and the loser is
    a script silently overwritten by a later attempt whose log and analysis still point
    at it. The scan lives in the shared module; a helper that reimplements it is a second
    authority regardless of how carefully it is written.
    """
    scan = 'glob("*/script_*.py")'
    offenders = sorted(
        relative
        for relative, content in rendered_assets().items()
        if relative.endswith(".py")
        and relative != "scripts/shared/iterations.py"
        and scan in content
    )
    assert offenders == []


def test_no_shipped_helper_writes_a_file_without_first_refusing_an_existing_one() -> None:
    """Overwriting destroys work that other records still reference.

    The destructive-call guard above does not cover this: an unguarded `write_text` names
    no deletion function while still discarding researcher work. A helper must either go
    through the shared script writer, which refuses an existing path, or refuse one
    itself.
    """
    offenders = sorted(
        relative
        for relative, content in rendered_assets().items()
        if relative.endswith(".py")
        and "write_text" in content
        and "write_new_script" not in content
        and "exists()" not in content
    )
    assert offenders == []


def test_selecting_a_result_is_decided_by_the_record_rather_than_the_filesystem() -> None:
    """A script that was never recorded is not a reportable attempt.

    Reading the filesystem would let an unrecorded script be selected as evidence, which
    is exactly the gap that made a second numbering authority dangerous. Selection reads
    the iteration log instead.
    """
    select = rendered_assets()["scripts/select_result.py"]
    assert "recorded_iterations" in select
    assert "existing_iterations" not in select


def test_the_legacy_content_baseline_is_available_to_re_enrich_from() -> None:
    """Re-enrichment copies from the original scaffold, so its absence is a blocker."""
    assert (LEGACY_TEMPLATE / "prompts" / "AI_CONTEXT.md").is_file()
    assert (LEGACY_TEMPLATE / "prompts" / "KNOWN_PATTERNS.md").is_file()
