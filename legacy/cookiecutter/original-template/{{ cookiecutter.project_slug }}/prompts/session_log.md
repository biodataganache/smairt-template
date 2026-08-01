# Session Log

Record prompts and key decisions here. This is primarily for the **browser-paste workflow** (ChatGPT, Claude web) where session history isn't preserved.

---

## How to Use This File

{% if cookiecutter.workflow_mode == 'ide_native' %}
**IDE-Native Note:** With tools like Roo/Zoo, Cursor, or Windsurf, your AI can read project files directly. This session log is less critical for context continuity, but remains valuable for:
- Recording key decisions and their reasoning
- Documenting intellectual contributions
- Creating a searchable history of what was tried

{% endif %}
For each session:
1. Record the date and session number
2. Note the key prompts and what you asked for
3. Summarize key results and outcomes
4. Note which scripts were generated/modified
5. Add your own observations and thoughts

This creates a breadcrumb trail for tracking the research journey.

---

## Session 1 - [DATE]

### Context
- **Iteration:** 1
- **Phase:** Synthetic data
- **Hypothesis being tested:**

### Prompt 1.1
```
[Your prompt here]
```

### Response Summary
[Key points from AI response]

### Scripts Generated
- `experiments/01_synthetic/script_01_xxx.py`

### Results
[Brief summary — refer to `results/logs/` for full output]

### My Observations
[Your thoughts, what you noticed, connections you made, what you want to try next]

### Critical Steps I Made
[Document where YOU provided key insights vs. where AI suggested things]

---

## Session 2 - [DATE]

### Context
- **Iteration:**
- **Phase:**
- **Hypothesis being tested:**

### Prompt 2.1
```
[Your prompt here]
```

### Response Summary


### Scripts Generated
-

### Results


### My Observations


### Critical Steps I Made


---

## Session 3 - [DATE]

### Context
- **Iteration:**
- **Phase:**
- **Hypothesis being tested:**

### Prompt 3.1
```
[Your prompt here]
```

### Response Summary


### Scripts Generated
-

### Results


### My Observations


### Critical Steps I Made


---

## Quick Reference: What to Record

From each session, capture:

1. **The prompts** - What you asked (exact text for browser-paste; summary for IDE-native)
2. **Scripts generated** - Link to the files created or modified
3. **Results** - What happened (reference log files in `results/logs/`)
4. **Your observations** - What you noticed, thought about, connected
5. **Your critical steps** - Where YOU made the key intellectual contributions
6. **Patterns discovered** - New entries for `prompts/KNOWN_PATTERNS.md`

---

## Tips

- **Don't edit your prompts after the fact** - Keep them as you actually wrote them
- **Note what worked within certain boundaries** - Document where approaches work and where they break down
- **Record when things stop working** - Approaches often work within certain boundaries but fail with real data, are not robust to noise, or have other limitations
- **Reference log files** - Full output is in `results/logs/`; just summarize here
- **Update KNOWN_PATTERNS.md** - When you discover a reusable pattern or recurring error, add it there
