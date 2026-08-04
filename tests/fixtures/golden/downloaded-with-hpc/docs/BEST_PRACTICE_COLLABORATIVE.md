# SMAIRT Git Best Practices

## Collaborative Use Case

### Branch Strategy

```
main
├── user-alice/iteration-XX      # Alice's current work
├── user-bob/iteration-YY        # Bob's current work
└── experiments/[topic-branch]   # Shared experimental branches
```

**Workflow:**
1. Each user works on their own branch
2. Merge to `main` only when an iteration is **complete** (hypothesis tested, results interpreted)
3. Pull from `main` before starting new iterations to get others' findings

### File Ownership & Conventions

**Shared Files (merge carefully):**
- `hypotheses/` - Each user creates their own H*_*.md files; avoid numbering conflicts
- `prompts/KNOWN_PATTERNS.md` - Append only, attribute entries with name/date
- `background/` files - Additions welcome, edits need discussion

**User-Specific Files:**
```
prompts/
├── session_log.md                    # SHARED - append with user attribution
├── session_log_alice.md              # Alice's detailed logs
├── session_log_bob.md                # Bob's detailed logs
├── intellectual_contribution.md       # SHARED - append with user attribution
└── intellectual_contribution_alice.md # Alice's detailed contributions
```

**Script Numbering Convention:**
```
# Option 1: Global numbering with user prefix
script_01_alice_initial_test.py
script_02_bob_alternative_approach.py

# Option 2: User-specific numbering ranges
# Alice: 01-49, Bob: 50-99, Carol: 100-149
script_01_initial_test.py      # Alice
script_50_different_approach.py # Bob
```

### Merge Conflict Prevention

**Structure entries for easy merging:**

```markdown
<!-- In hypotheses/ directory, use separate files per hypothesis -->
hypotheses/H1_alice_noise_threshold.md
hypotheses/H2_bob_alternative_algorithm.md
```

**Use append-only pattern for shared logs:**
```markdown
<!-- In session_log.md -->
# Session Log

---
## Alice - Session 2024-01-15
[content]

---
## Bob - Session 2024-01-16
[content]
```

### Collaborative Git Workflow

```bash
# Starting new work
git checkout main
git pull origin main
git checkout -b user-alice/iteration-05

# Do your iteration work...
# Create scripts, run experiments, update logs

# Before merging
git checkout main
git pull origin main
git checkout user-alice/iteration-05
git rebase main  # or merge main into your branch

# Merge completed iteration
git checkout main
git merge user-alice/iteration-05
git push origin main

# Tag collaborative milestones
git tag -a "collab-v1.0" -m "Team consensus: [finding]. Contributors: Alice, Bob"
```

### Communication Protocol

**Required Updates for Each Merge to Main:**

1. **Hypothesis file** with your name and date in `hypotheses/`
2. **Results log** auto-captured in `results/logs/` by TeeLogger
3. **KNOWN_PATTERNS.md update** if you discovered patterns or errors
4. **Brief summary in commit message** so others can scan git log

**Async Communication File (optional):**
```markdown
<!-- coordination/COLLABORATION_LOG.md -->
## Active Work

| User | Current Iteration | Hypothesis | ETA |
|------|------------------|------------|-----|
| Alice | 05 | Testing noise robustness | 2024-01-17 |
| Bob | 06 | Alternative algorithm | 2024-01-18 |

## Decisions Needed
- [ ] Should we pivot to downloaded data? (raised by Alice, 2024-01-15)

## Recent Findings to Note
- Bob's iteration 04 found the approach breaks above 30% noise - important constraint
```

### Intellectual Contribution Tracking (Collaborative)

This becomes especially important with multiple contributors:

```markdown
<!-- intellectual_contribution.md -->
## Iteration 5 (Alice)
### My Contributions
- Suggested testing with correlated noise (not just i.i.d.)
- Identified that Bob's result from Iter 04 implied we need regularization

### AI Contributions
- Generated the test harness code
- Suggested three approaches (I chose option 2)

### Collaborative Contributions
- Built on Bob's noise threshold finding from Iteration 04
```

---

## Summary Comparison

| Aspect | Single User | Collaborative |
|--------|-------------|---------------|
| Branch strategy | Main only (+ optional exploration branches) | User branches, merge completed iterations |
| Commit frequency | Per iteration | Per iteration, coordinate merges |
| Session logs | Single file | Per-user files + shared summary |
| Script numbering | Sequential | Prefixed or range-based |
| Hypotheses | Sequential H*_*.md files | Attributed, user-prefixed files |
| Intellectual contribution | Track yours vs AI | Track yours vs AI vs collaborators |
| Tags | Phase milestones | Phase + team consensus points |

The key principle for both cases: **the audit trail should be clear enough that anyone (including a new AI session) can reconstruct the full thought process and continue from where you left off.**
