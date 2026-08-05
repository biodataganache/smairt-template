"""Failures a researcher can act on, rather than library output or tracebacks.

SMAIRT's users are researchers who may not read Python tracebacks, and three kinds of
message were reaching them unchanged: pydantic's structured validation output, bare
tracebacks from anything unanticipated, and diagnoses that were correct but addressed to the
wrong reader. These tests hold the translated wording and the exit-code contract that lets a
script tell "this is not a project" from "this project has problems".
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from smairt.messages import (
    describe_slug_rejection,
    describe_unexpected_error,
    describe_validation_error,
    suggest_slug,
)
from smairt.models import ProjectIdentity

CANNOT_PROCEED = 2
OPERATION_FAILED = 1


def installed_smairt() -> Path:
    return Path(sys.executable).with_name("smairt")


def run(*arguments: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(installed_smairt()), *arguments],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def create_project(destination: Path, *, slug: str = "study_project") -> None:
    created = run(
        "new",
        str(destination),
        "--name",
        "Study",
        "--slug",
        slug,
        "--description",
        "A project for message and exit-code checks.",
        "--researcher",
        "Ada Researcher",
        "--domain",
        "Computational biology",
        "--accept-license",
        "--no-git",
    )
    assert created.returncode == 0, created.stderr


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("My Bad Slug!", "my_bad_slug"),
        ("Protein Study 2", "protein_study_2"),
        ("2024 results", "project_2024_results"),
        ("---", ""),
    ],
)
def test_a_slug_suggestion_is_derived_from_what_was_typed(given: str, expected: str) -> None:
    assert suggest_slug(given) == expected


def test_a_suggested_slug_is_actually_valid() -> None:
    """A suggestion that the contract would reject is worse than no suggestion."""
    for given in ("My Bad Slug!", "Protein Study 2", "2024 results", "A--B__c"):
        suggestion = suggest_slug(given)
        assert suggestion
        identity = ProjectIdentity(
            name="Name", slug=suggestion, description="d", domain="Computational biology"
        )
        assert identity.slug == suggestion


def test_a_rejected_slug_is_answered_with_the_rule_and_a_usable_alternative() -> None:
    message = describe_slug_rejection("My Bad Slug!")

    assert "My Bad Slug!" in message
    assert "lowercase letter" in message
    assert "Try: my_bad_slug" in message
    assert "pydantic" not in message
    assert "[type=" not in message


def test_creating_a_project_with_a_bad_slug_says_what_to_do(tmp_path: Path) -> None:
    result = run(
        "new",
        str(tmp_path / "study"),
        "--name",
        "Study",
        "--slug",
        "My Bad Slug!",
        "--description",
        "d",
        "--researcher",
        "R",
        "--domain",
        "b",
        "--accept-license",
        "--no-git",
    )

    assert result.returncode == CANNOT_PROCEED
    assert "my_bad_slug" in result.stderr
    assert "lowercase letter" in result.stderr
    assert "pydantic" not in result.stderr
    assert "[type=" not in result.stderr
    assert "validation error" not in result.stderr


def test_an_unreadable_contract_is_explained_without_library_output(tmp_path: Path) -> None:
    destination = tmp_path / "unreadable_project"
    create_project(destination)
    (destination / "smairt.yaml").write_text("foo: bar\n")

    result = run("check", str(destination))

    assert result.returncode == OPERATION_FAILED
    assert "smairt.yaml could not be read" in result.stdout
    assert "is required but was not provided" in result.stdout
    assert "is not a setting SMAIRT recognizes" in result.stdout
    assert "pydantic" not in result.stdout
    assert "[type=" not in result.stdout


def test_every_reported_contract_problem_is_named_in_words() -> None:
    """No field may report itself by its raw contract key when a label exists."""
    with pytest.raises(Exception) as caught:
        ProjectIdentity(name="", slug="Bad Slug", description="", domain="")
    message = describe_validation_error(caught.value, source="smairt.yaml")  # type: ignore[arg-type]

    assert "smairt.yaml could not be read" in message
    assert "project name" in message
    assert "project slug" in message
    assert "project description" in message
    assert "research domain" in message
    assert "errors.pydantic.dev" not in message


def test_a_nested_contract_field_is_still_named_in_words(tmp_path: Path) -> None:
    """A contract reports a bad researcher name as `people.researcher.name`.

    Only the exact location and a model-qualified guess were consulted, so nested paths fell
    through to the raw YAML key — exactly the library-shaped output this translation exists to
    remove.
    """
    destination = tmp_path / "nested_project"
    create_project(destination)
    contract = destination / "smairt.yaml"
    contract.write_text(contract.read_text().replace("name: Ada Researcher", "name: ''"))

    result = run("check", str(destination))

    assert result.returncode == OPERATION_FAILED
    assert "researcher name: cannot be empty" in result.stdout
    assert "people.researcher.name" not in result.stdout


def test_a_rejected_slug_does_not_hide_the_other_problems(tmp_path: Path) -> None:
    """Answering only the slug forced a correct-one-thing-and-retry loop.

    Every failure is reported, and the slug suggestion is added rather than substituted.
    """
    result = run(
        "new",
        str(tmp_path / "several"),
        "--name",
        "Study {{ x }}",
        "--slug",
        "Bad Slug",
        "--description",
        "d",
        "--researcher",
        "R",
        "--domain",
        "b",
        "--accept-license",
        "--no-git",
    )

    assert result.returncode == CANNOT_PROCEED
    assert "project slug" in result.stderr
    assert "project name" in result.stderr
    assert "For the slug, try: bad_slug" in result.stderr


def test_malformed_yaml_names_the_file_rather_than_the_parser(tmp_path: Path) -> None:
    destination = tmp_path / "malformed_project"
    create_project(destination)
    (destination / "smairt.yaml").write_text("this: is: not: valid: [\n")

    result = run("check", str(destination))

    assert result.returncode == OPERATION_FAILED
    assert "smairt.yaml is not valid YAML" in result.stdout


def test_an_unexpected_failure_says_what_it_means_for_the_project() -> None:
    message = describe_unexpected_error(RuntimeError("something gave way"))

    assert "unexpected error" in message
    assert "RuntimeError: something gave way" in message
    assert "smairt check" in message
    assert "SMAIRT_DEBUG=1" in message
    # No promise about the files: the boundary cannot know how far an operation got, so a
    # reassurance here would be a guess presented to a non-expert as a guarantee.
    assert "were not deleted" not in message
    assert "may be incomplete" in message


def test_a_file_where_a_directory_must_go_is_reported_not_raised(tmp_path: Path) -> None:
    """A researcher's own file blocking a capability directory used to be a traceback.

    The diagnosis was already precise; it was simply delivered as a `ValueError` with a stack
    trace instead of a sentence naming the file and what to do with it.
    """
    destination = tmp_path / "blocked_project"
    create_project(destination)
    (destination / "hpc").write_text("my own notes\n")

    result = run("hpc", "enable", str(destination))

    assert result.returncode == OPERATION_FAILED
    assert "hpc/ to be a directory" in result.stderr
    assert "Move or rename that file" in result.stderr
    assert "Traceback" not in result.stderr
    assert (destination / "hpc").read_text() == "my own notes\n"


def test_an_unexpected_exception_is_translated_but_debug_shows_the_traceback(
    tmp_path: Path,
) -> None:
    """The boundary must not make a real bug harder to report.

    Driven through a genuinely unanticipated failure — a corrupt recents file that makes
    `record_recent` raise — rather than an error the domain already translates, so this
    actually reaches the handler in `main()`.
    """
    destination = tmp_path / "boundary_project"
    create_project(destination)
    data_home = tmp_path / "data"
    recents = data_home / "smairt"
    recents.mkdir(parents=True)
    # A directory where a file is expected: reading tolerates it, writing does not.
    (recents / "recent-projects.json").mkdir()
    environment = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(tmp_path),
        "XDG_DATA_HOME": str(data_home),
    }

    translated = subprocess.run(
        [str(installed_smairt()), "open", str(destination)],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert translated.returncode == OPERATION_FAILED, translated.stdout
    assert "unexpected error" in translated.stderr
    assert "Traceback" not in translated.stderr
    assert "SMAIRT_DEBUG=1" in translated.stderr

    detailed = subprocess.run(
        [str(installed_smairt()), "open", str(destination)],
        check=False,
        capture_output=True,
        text=True,
        env={**environment, "SMAIRT_DEBUG": "1"},
    )

    assert detailed.returncode != 0
    assert "unexpected error" not in detailed.stderr
    assert "IsADirectoryError" in detailed.stderr or "Traceback" in detailed.stderr


def test_creating_a_project_in_an_existing_empty_directory_succeeds(tmp_path: Path) -> None:
    """`smairt new .` from inside a freshly made folder is how researchers actually arrive.

    It used to be refused with "Destination already exists", which restated what the
    researcher already knew and offered nothing to do about it.
    """
    destination = tmp_path / "prepared"
    destination.mkdir()

    result = run(
        "new",
        ".",
        "--name",
        "Prepared Study",
        "--slug",
        "prepared_study",
        "--description",
        "Created in a folder the researcher had already made.",
        "--researcher",
        "Ada Researcher",
        "--domain",
        "Computational biology",
        "--accept-license",
        "--no-git",
        cwd=destination,
    )

    assert result.returncode == 0, result.stderr
    assert "Created SMAIRT project at" in result.stdout
    assert (destination / "smairt.yaml").is_file()
    assert run("check", str(destination)).returncode == 0


def test_a_destination_holding_files_is_still_refused(tmp_path: Path) -> None:
    """Allowing an empty directory must not weaken the protection for a used one."""
    destination = tmp_path / "occupied"
    destination.mkdir()
    preserved = destination / "results.csv"
    preserved.write_text("do not touch\n")

    result = run(
        "new",
        str(destination),
        "--name",
        "Occupied",
        "--slug",
        "occupied_study",
        "--description",
        "d",
        "--researcher",
        "R",
        "--domain",
        "b",
        "--accept-license",
        "--no-git",
    )

    assert result.returncode == OPERATION_FAILED
    assert "already contains files" in result.stderr
    assert preserved.read_text() == "do not touch\n"
    assert not (destination / "smairt.yaml").exists()


def test_cannot_proceed_and_operation_failed_are_distinguishable(tmp_path: Path) -> None:
    """The exit-code contract, stated once for every command that resolves a project.

    A script has to tell "there is no project here" from "this project has problems", and
    only `check` used to make that distinction.
    """
    missing = tmp_path / "not_a_project"
    missing.mkdir()

    for arguments in (
        ("check", str(missing)),
        ("settings", str(missing)),
        ("open", str(missing)),
        ("inspect", str(missing)),
        ("repair", str(missing)),
        ("regenerate", str(missing)),
        ("upgrade", str(missing)),
        ("paper", "enable", str(missing)),
    ):
        result = run(*arguments)
        assert result.returncode == CANNOT_PROCEED, f"{arguments}: {result.returncode}"
        assert "Not a SMAIRT project" in result.stderr

    findings = tmp_path / "project_with_findings"
    create_project(findings)
    (findings / "hypotheses" / "README.md").unlink()

    checked = run("check", str(findings))
    assert checked.returncode == OPERATION_FAILED
