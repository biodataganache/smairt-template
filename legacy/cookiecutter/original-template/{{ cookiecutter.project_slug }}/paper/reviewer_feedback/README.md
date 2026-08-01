# Reviewer Feedback

{% if cookiecutter.project_mode == 'paper_driven' %}
This directory stores reviewer feedback and response documents.

## Structure

```
reviewer_feedback/
├── round_1/
│   ├── reviewer_1_comments.md
│   ├── reviewer_2_comments.md
│   ├── reviewer_3_comments.md
│   └── response_to_reviewers.md
├── round_2/
│   └── ...
└── README.md
```

## Response Template

When responding to reviewers, use this format:

```markdown
## Reviewer 1

### Comment 1.1
> [Quote the reviewer's comment]

**Response**: [Your response]

**Changes made**: [List specific changes, with line numbers if applicable]

### Comment 1.2
...
```

## Tips

- Be respectful and thorough in responses
- Reference specific sections/figures/tables
- Track which analyses need to be re-run
- Document any new analyses added in response to feedback
{% else %}
This directory is only used in paper-driven mode.
{% endif %}
