"""Run canonical SMAIRT generation for the legacy Cookiecutter entry point."""

from pathlib import Path

from smairt.generator import GenerationError, generate_project
from smairt.models import Assistant, License, ProjectIdentity, ProjectOptions, Researcher, StartingPhase


def main() -> None:
    root = Path.cwd()
    options = ProjectOptions(
        project=ProjectIdentity(
            name="{{ cookiecutter.project_name }}",
            slug="{{ cookiecutter.project_slug }}",
            description="{{ cookiecutter.description }}",
            domain="{{ cookiecutter.domain }}",
            research_question="{{ cookiecutter.initial_research_question }}" or None,
        ),
        researcher=Researcher(
            name="{{ cookiecutter.author_name }}",
            email="{{ cookiecutter.author_email }}" or None,
        ),
        assistant=Assistant("{{ cookiecutter.assistant }}"),
        starting_phase=StartingPhase("{{ cookiecutter.starting_phase }}"),
        license=License("{{ cookiecutter.license }}"),
        initialize_git="{{ cookiecutter.create_git_repo }}" == "yes",
        paper="{{ cookiecutter.paper }}" == "yes",
        hpc="{{ cookiecutter.hpc }}" == "yes",
    )
    staging = root.with_name(f".{root.name}.legacy-cookiecutter")
    root.rename(staging)
    try:
        messages = generate_project(root, options)
    except GenerationError as error:
        staging.rename(root)
        raise SystemExit(f"ERROR: {error}") from error
    for message in messages:
        print(message)
    print("Legacy Cookiecutter compatibility path. Prefer `smairt new` for new projects.")
    print(f"Created SMAIRT project at {root}")
    import shutil
    shutil.rmtree(staging)


if __name__ == "__main__":
    main()
