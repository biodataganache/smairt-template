from __future__ import annotations

import re
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
from smairt.scaffold import active_assets, render_template_assets

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


def test_the_outcome_history_is_only_ever_appended_to() -> None:
    """A history whose earlier lines can change is not evidence of what was believed.

    Every recording and revision appends, so a conclusion that changed still shows what it
    changed from. The state table above it is rewritten in place, which is why the two
    records exist separately: one is scannable, the other is permanent.
    """
    iterations = rendered_assets()["scripts/shared/iterations.py"]
    assert 'open("a")' in iterations
    assert 'open("w")' not in iterations


def test_a_helper_fills_only_the_placeholder_it_wrote_itself() -> None:
    """Filling a placeholder is safe; overwriting a researcher's sentence is not.

    The narrowed rule allows a helper to replace text it authored, because the history
    keeps every value and nothing is lost. It never allows editing prose a researcher
    wrote, so the fill is conditional on the placeholder still being present and reports
    back when it is not.
    """
    iterations = rendered_assets()["scripts/shared/iterations.py"]
    assert "OUTCOME_PLACEHOLDER" in iterations
    assert "if line.startswith(prefix) and OUTCOME_PLACEHOLDER in line:" in iterations


def test_recording_an_outcome_requires_an_interpretation_to_exist() -> None:
    """An outcome recorded before the run was read is a guess wearing a record's clothes.

    The helper holds no opinion about what the outcome says, but it does enforce the
    ordering the workflow claims: interpret, then record.
    """
    record = rendered_assets()["scripts/record_outcome.py"]
    assert "ANALYSIS_{number:02d}.md" in record
    assert "interpret the run" in record


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
    assert "iteration_records" in select
    assert "existing_iterations" not in select


TRACK_PREFIXED_SCRIPT = re.compile(r"script_[A-Za-z]\d")
"""A track letter standing where the iteration number belongs, as in `script_B01_...`.

Deliberately narrower than `script_[A-Za-z]`, which also matches the `script_NN_name`
placeholder that guidance legitimately uses to describe the real convention.
"""


def test_no_guidance_encodes_a_track_in_a_script_name() -> None:
    """A letter-prefixed script name is invisible to the numbering scan.

    `script_B01_...` does not match the scan that finds the next number, so a project
    following that convention hands the same number out twice. A track belongs in
    `analysis/ANALYSIS_PLAN.md` and in the hypothesis it tests, never in a filename.
    """
    offenders = sorted(
        f"{relative}: {match.group(0)}"
        for relative, content in rendered_assets().items()
        for match in TRACK_PREFIXED_SCRIPT.finditer(content)
    )
    assert offenders == []


def test_one_hypothesis_identifier_form_is_used_everywhere() -> None:
    """Two spellings of the same identifier break the trail they exist to preserve.

    A researcher told to reference `H01` and a helper that creates
    `hypotheses/HYPOTHESIS_01.md` disagree about the name of the same file, so the link
    from an analysis back to its precommitment is a guess rather than a path.
    """
    offenders = sorted(
        f"{relative}: {match.group(0)}"
        for relative, content in rendered_assets().items()
        for match in re.finditer(r"(?<![A-Z_])H\d{2}\b", content)
    )
    assert offenders == []


def test_no_always_present_guidance_cites_a_capability_only_file() -> None:
    """Citing a file the project does not have sends a reader to a dead path.

    Paper and HPC guidance is added by a capability, so a base project never receives it.
    An unconditional file may mention that such guidance exists once the capability is
    enabled, which is why only a bare path citation counts as a defect here.
    """
    contract = _contract(
        ProjectIdentity(
            name="Study",
            slug="study",
            description="A study.",
            domain="Computational biology",
        )
    )
    conditional = {
        asset.path for asset in active_assets(contract, include_inactive=True) if asset.condition
    }
    unconditional = {asset.path: asset for asset in active_assets(contract, include_inactive=True)}
    rendered = rendered_assets()
    offenders = sorted(
        f"{relative}: {path}"
        for relative, content in rendered.items()
        if not unconditional[relative].condition
        for path in conditional
        if f"`{path}`" in content
    )
    assert offenders == []


def test_an_assistant_observation_is_marked_unreviewed_where_it_is_written() -> None:
    """An unconfirmed observation that looks like a record becomes one by accident.

    The assistant notices contributions because a researcher often will not recognise
    their own, but noticing is not confirming. The marking has to live in the file being
    written, so reading that file alone tells you which entries the researcher accepted.
    """
    contribution = rendered_assets()["prompts/intellectual_contribution.md"]
    assert "Status: unreviewed" in contribution
    assert "**Status:** unreviewed" in contribution


def test_a_helper_fills_a_shipped_template_rather_than_its_own_copy() -> None:
    """A helper carrying its own copy of a template makes the shipped one a lie.

    Guidance tells the researcher that `HYPOTHESIS_TEMPLATE.md` and `PLAN_TEMPLATE.md` are
    the shape of these records, and a researcher may edit either to suit their field. A
    helper with an inlined duplicate ignores those edits and drifts from the template
    silently, so the file a reader is told to follow stops matching what they receive.
    """
    track = rendered_assets()["scripts/new_track.py"]
    assert "HYPOTHESIS_TEMPLATE.md" in track
    assert "PLAN_TEMPLATE.md" in track
    assert "## Hypothesis Statement" not in track
    assert "## Risks and mitigations" not in track


def test_the_legacy_content_baseline_is_available_to_re_enrich_from() -> None:
    """Re-enrichment copies from the original scaffold, so its absence is a blocker."""
    assert (LEGACY_TEMPLATE / "prompts" / "AI_CONTEXT.md").is_file()
    assert (LEGACY_TEMPLATE / "prompts" / "KNOWN_PATTERNS.md").is_file()
