# Prompts

AI context files for this SMAIRT project. These files tell the AI how to behave, what conventions to follow, and what knowledge has been accumulated.

---

## Files

| File | Purpose | When to Read |
|------|---------|--------------|
| `AI_CONTEXT.md` | AI role, workflow, project structure | First encounter with project |
| `CODE_CONVENTIONS.md` | Script naming, templates, logging | Before writing any code |
| `KNOWN_PATTERNS.md` | Reusable code, known errors, standards | Before writing code |
| `CONTEXT_INDEX.md` | What files to read for different tasks | When starting a new task |
| `SESSION_START.md` | Context-setting prompts | When context needs refreshing |
| `00_priming_prompts.md` | Quick priming snippets | Mid-session reminders |
| `intellectual_contribution.md` | Human contribution tracking | After making key decisions |
| `compiled_for_ai.md` | Generated project snapshot | Cross-tool transfer only |

---

## Purpose

These files serve as persistent project memory. They accumulate knowledge across sessions so that:
- Each new session starts with the right context
- Patterns are reused instead of reinvented
- Errors aren't repeated
- Human intellectual contributions are tracked

---

## For IDE-Native Workflow (Roo/Zoo, Cursor, Windsurf)

The AI reads these files directly. Point it to `AI_CONTEXT.md` on first encounter, then it knows to check `CONTEXT_INDEX.md` for task-specific guidance.

## For Browser-Paste Workflow (ChatGPT, Claude web)

Paste the contents of key files at the start of each session, or use `compiled_for_ai.md` for full context.

---

## Known Patterns & Error Prevention

`KNOWN_PATTERNS.md` is the project's accumulated knowledge base:
- **Reusable code patterns** — Working snippets to copy
- **Recurring errors** — Mistakes and their fixes
- **Standards** — Seeds, DPI, formats, conventions
- **Pre-flight checklist** — Things to verify before experiments
- **Anti-patterns** — Things that were tried and failed

Update this file after every resolved error or discovered pattern.
