# {{ project.name }}

{{ project.description }}

## Start Here

Read `prompts/AI_CONTEXT.md` with your coding assistant, then record each run
and its output under `results/logs/`. Keep hypotheses, scripts, logs, and
analysis linked so the work remains reproducible.

{% if project.research_question %}## Research Question

{{ project.research_question }}
{% endif %}
