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
    "new_iteration.py",
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


def test_the_legacy_content_baseline_is_available_to_re_enrich_from() -> None:
    """Re-enrichment copies from the original scaffold, so its absence is a blocker."""
    assert (LEGACY_TEMPLATE / "prompts" / "AI_CONTEXT.md").is_file()
    assert (LEGACY_TEMPLATE / "prompts" / "KNOWN_PATTERNS.md").is_file()
