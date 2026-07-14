# Plans

Planning documents for this SMAIRT project.

## Purpose

Plans are created **before** embarking on multi-step work. They serve as:
- A contract between you and the AI about what will be built
- A reference to prevent scope creep during implementation
- A record of architectural decisions and their rationale

## When to Create a Plan

Create a plan document when:
- Starting a new experimental track (e.g., `PLAN_TRACK_B_FITNESS_DATA.md`)
- Designing a complex multi-script experiment
- Proposing an architecture change
- Coordinating work across team members
- Pivoting to a new approach after a dead end

## Plan Template

```markdown
# Plan: [Brief Title]

## Status: DRAFT | ACTIVE | COMPLETED | ABANDONED

## Problem Statement
[What problem does this plan address?]

## Approach
[High-level description of the approach]

## Success Criteria
[How will we know this worked?]

## Dependencies
[What must exist before this can start?]
- [ ] Data: [specific data needed]
- [ ] Code: [specific modules/scripts needed]
- [ ] Results: [prior experiments that must complete]

## Steps
1. [ ] [First concrete step]
2. [ ] [Second concrete step]
3. [ ] [Third concrete step]

## Expected Outputs
- [Script(s) to produce]
- [Analysis document(s)]
- [Figures or results]

## Risks & Mitigations
| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| [Risk 1] | High/Med/Low | [How to handle] |

## Notes
[Any additional context, links to related work, etc.]
```

## Naming Convention

```
PLAN_[TRACK]_[BRIEF_DESCRIPTION].md
```

Examples:
- `PLAN_D05_RAY_TUNE_STRATEGY.md`
- `PLAN_MULTIMODAL_INTEGRATION.md`
- `PLAN_X3_FITNESS_EMBEDDING_DYNAMICS.md`
- `COLLABORATION_GUIDE.md`
