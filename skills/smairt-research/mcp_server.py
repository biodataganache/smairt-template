"""Local MCP server for testing the SMAIRT research skill with Claude Code."""

from pathlib import Path

from mcp.server.fastmcp import FastMCP


ROOT = Path(__file__).resolve().parent
SKILL_PATH = ROOT / "SKILL.md"
WORKFLOW_PATH = ROOT / "references" / "workflow.md"

mcp = FastMCP(
    "SMAIRT Research",
    instructions=(
        "Expose the SMAIRT research workflow for AI-assisted computational "
        "research. Use this server when a user asks to start or continue a "
        "SMAIRT project, structure experiments with the scientific method, "
        "or preserve a research breadcrumb trail across AI sessions."
    ),
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@mcp.resource("smairt://skill/SKILL.md")
def smairt_skill_resource() -> str:
    """Return the SMAIRT skill entry point."""
    return _read_text(SKILL_PATH)


@mcp.resource("smairt://skill/workflow.md")
def smairt_workflow_resource() -> str:
    """Return the detailed SMAIRT workflow reference."""
    return _read_text(WORKFLOW_PATH)


@mcp.tool()
def get_smairt_skill() -> str:
    """Return the SMAIRT skill instructions and workflow reference."""
    return (
        "# SMAIRT Skill\n\n"
        f"{_read_text(SKILL_PATH)}\n\n"
        "# SMAIRT Workflow Reference\n\n"
        f"{_read_text(WORKFLOW_PATH)}"
    )


@mcp.tool()
def start_smairt_session(
    research_question: str,
    project_name: str = "Untitled SMAIRT project",
    current_phase: str = "synthetic",
    current_hypothesis: str = "Please help define a testable hypothesis.",
) -> str:
    """Create a structured SMAIRT starting prompt for a new research session."""
    return f"""Use the SMAIRT research workflow for this project.

Project:
- Name: {project_name}
- Research question: {research_question}
- Current phase: {current_phase}
- Current hypothesis: {current_hypothesis}

Please help refine the current hypothesis, design the next testable experiment,
generate or outline code that logs to the console and results/logs, and preserve
the breadcrumb trail for future AI sessions.

Follow this structure:
1. Background
2. Hypothesis
3. Methods or code plan
4. Expected results and interpretation plan
5. Future directions
"""


@mcp.tool()
def continue_smairt_session(
    current_hypothesis: str,
    recent_results: str,
    future_directions: str = "",
) -> str:
    """Create a structured SMAIRT continuation prompt for an existing project."""
    future_text = future_directions or "Please infer the next options from the results."
    return f"""Use the SMAIRT research workflow and continue from this project state.

Current hypothesis:
{current_hypothesis}

Recent results:
{recent_results}

Future directions:
{future_text}

Please interpret the latest results through the hypothesis, say whether they
support, refute, or partially support it, identify boundaries and limitations,
and propose the next one or two experiments.
"""


@mcp.prompt()
def start_smairt_project() -> str:
    """Prompt template for starting a SMAIRT project."""
    return """Use the SMAIRT research workflow.

Project:
- Name: [project name]
- Research question: [question]
- Current phase: [synthetic / downloaded / real]
- Current hypothesis: [hypothesis or "please help define it"]

Please help me refine the current hypothesis, design the next testable
experiment, generate code that logs to console and results/logs, and preserve
the breadcrumb trail for future AI sessions.
"""


@mcp.prompt()
def continue_smairt_project() -> str:
    """Prompt template for continuing a SMAIRT project."""
    return """Use the SMAIRT research workflow and continue from this project state.

I will provide the current hypothesis, recent session log, prior experiment
output, and future directions. Interpret the latest results through the
hypothesis, identify boundaries and limitations, then propose the next one or
two experiments.
"""


if __name__ == "__main__":
    mcp.run()
