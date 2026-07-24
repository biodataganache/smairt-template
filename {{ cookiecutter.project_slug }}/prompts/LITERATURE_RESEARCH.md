# Reviewed Literature Research Workflow

Use this workflow to move from the project's research question to a local,
researcher-curated evidence corpus. Brave and Exa are discovery tools configured
by the researcher in Zoo Code; SMAIRT does not configure them or handle keys.

## Security Boundary

- Check whether Brave and Exa tools are available in Zoo before searching.
- If either tool is unavailable, explain how to enable it in Zoo's GUI.
- Never request, display, store, or write an API key.
- Never create `.env`, credential, MCP configuration, or provider configuration files.
- Never place credentials in chat, Markdown, scripts, logs, or project settings.

## Required Workflow

### 1. Read the Question and Existing Evidence

Read:

- `background/01_initial_question.md`
- existing records in `references/searches/`
- existing `references/sources/*/reference.md` files
- relevant recent hypotheses and analyses, if any

If an optional topic or sub-question was supplied, relate it explicitly to the
primary research question.

### 2. Propose a Search Strategy Before Searching

Present a concise strategy containing:

- research concepts and relationships to investigate
- synonyms, abbreviations, and adjacent terminology
- exclusions and scope boundaries
- useful domains, source types, and date ranges
- planned Brave queries for broad web, institutional, standards, and current information
- planned Exa queries for semantic and research-paper-oriented discovery

Wait for researcher approval or correction of the strategy before running a
broad search. A narrow exploratory query is allowed only when needed to refine
the proposed strategy, and must be identified as exploratory.

### 3. Search and Record Provenance

After approval, query the available tools. For every query record:

- provider name
- exact query
- filters, domains, and date limits
- date searched
- candidate title, authors when available, identifier, and canonical URL

Create or update `references/searches/YYYYMMDD_short_topic.md` with this search
provenance and the candidate table.

### 4. Deduplicate and Screen Candidates

Deduplicate in this order where fields are available:

1. DOI, PMID, arXiv ID, or another stable identifier
2. normalized title
3. author and year

Prefer canonical publisher, DOI, PubMed, arXiv, institutional, or repository
records over aggregators. Clearly distinguish discovery snippets from claims
verified in a source. Search rank is never scientific proof.

Present a compact candidate table to the researcher. Include relevance, source
type, apparent version/status, and any reason for caution. Do not create source
folders yet.

### 5. Stop for Human Review

Ask the researcher to mark candidates `APPROVE`, `REJECT`, or `NEEDS REVIEW`.
Record each decision and reason in the search record. Do not infer approval from
silence and do not create one folder per raw result.

### 6. Import Approved References

Only after explicit approval, create:

```text
references/sources/author_year_short_title/
├── reference.md
├── paper/
├── supplemental/
└── data/
```

Copy `references/REFERENCE_TEMPLATE.md` to `reference.md` and fill all metadata
that can be verified. Leave unknown fields explicit rather than guessing.

The researcher may then place a paper, supplements, and data in those folders.
Inventory provided files in `reference.md`; do not download or fabricate missing
artifacts unless the researcher separately requests and approves that action.

### 7. Use Evidence in SMAIRT

Before defining a hypothesis, comparing to prior work, claiming novelty, writing
Related Work, preparing a study report, or drafting paper text:

- read the relevant selected `reference.md` records
- verify important claims against the source and record a precise source location
- cite local source-folder IDs in hypotheses and analyses
- distinguish external literature claims from this project's experimental findings
- record contradictions, uncertainty, and applicability boundaries

If the evidence changes the research direction, ask whether the researcher's
decision or interpretation should be logged in `prompts/intellectual_contribution.md`.

## Completion Point

A literature-search session is complete when its query provenance and screening
decisions are recorded, approved source folders exist, and the next hypothesis or
paper task identifies which reviewed sources provide its evidence basis.
