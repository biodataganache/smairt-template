# Local Reference Corpus

This directory is the local, researcher-curated evidence corpus for the project.
It is intentionally ignored by Git. Zoo Code and researchers can read it in the
workspace, but its papers, supplements, data, notes, and search records are not
included in commits or `prompts/compiled_for_ai.md`.

## Workflow

1. Start from `background/01_initial_question.md`.
2. Follow `prompts/LITERATURE_RESEARCH.md` to search with Brave and Exa in Zoo.
3. Record candidate results in `searches/`.
4. Present candidates to the researcher and wait for a selection decision.
5. Create source folders only for approved references.
6. Copy `REFERENCE_TEMPLATE.md` to each approved source as `reference.md`.
7. The researcher may place source files in `paper/`, `supplemental/`, and `data/`.
8. Link reviewed sources from hypotheses, analyses, study reports, and paper text.

Search rank is discovery evidence, not scientific proof. Verify important claims
against the source itself and record the page, section, figure, table, or data
location that supports each claim.

## Approved Source Layout

```text
sources/smith_2024_short_title/
├── reference.md
├── paper/
├── supplemental/
└── data/
```

Use lowercase `author_year_short_title` names. If two sources collide, append a
short stable identifier such as a DOI suffix or arXiv number.

## Credential Boundary

Configure Brave and Exa only through Zoo's GUI. Never place API keys in this
directory, project Markdown, scripts, logs, chat messages, or environment files.
