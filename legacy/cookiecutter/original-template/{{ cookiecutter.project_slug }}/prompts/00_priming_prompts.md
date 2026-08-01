# Priming Prompts for {{ cookiecutter.project_slug }}

## IDE-Native Quick Start

When your AI first encounters this project:

```
Please read prompts/AI_CONTEXT.md and prompts/CONTEXT_INDEX.md
to understand this SMAIRT project.
```

## Context Refresh

After a gap or context window reset:

```
SMAIRT project "{{ cookiecutter.project_name }}".
Read prompts/AI_CONTEXT.md, then check the most recent files in
analysis/ and hypotheses/ to see current state.
```

## Task-Specific Priming

### Before Writing Code
```
Read prompts/CODE_CONVENTIONS.md and prompts/KNOWN_PATTERNS.md
before generating any scripts.
```

### Before Interpreting Results
```
Read the hypothesis file and the log output, then write analysis
following the template in analysis/ANALYSIS_TEMPLATE.md.
```

### Before Planning
```
Read existing plans in plans/ and recent analysis files.
Then create a plan following plans/README.md template.
```

## Mid-Session Reminder

If the AI loses track of conventions:

```
SMAIRT reminder:
- Scripts: script_XX_description.py (or track-based: script_A01_...)
- Use TeeLogger from scripts/shared/logging
- Check KNOWN_PATTERNS.md before writing code
- Write hypothesis files BEFORE experiments
- Write analysis files AFTER results
- Note boundaries: where it works, where it breaks
```

## Cross-Tool Transfer

When switching to a different AI tool:

```bash
python scripts/compile_for_ai.py
# Then provide prompts/compiled_for_ai.md to the new tool
```
