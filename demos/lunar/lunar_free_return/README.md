# Lunar Free Return

Artemis II free-return trajectory

**Author:** Your Name (you@example.com)
**Domain:** physics  
**AI Tool:** roo_zoo

---

## Research Question

Can we find a TLI burn that yeilds a free-return?

---

## About This Project

This project uses the **SMAIRT** (Scientific Method with AI Research Template) framework.

### Core Philosophy

AI excels at regression toward the mean—it can get you quickly to the frontier of what's already known. The human contribution remains essential for:
- Making innovative connections
- Identifying truly novel questions
- Recognizing where AI suggestions fall short

### The Loop

```
Background → Hypothesis → Methods/Code → Results → Analysis → Next Steps → (repeat)
```

### The 4-Part Structure

The template records **4 pieces of information in separate files**:

1. **Background** - The question that went into prompting it, what has been done on that area, what's known about that question from the literature, and a summary of the previous results that have come up to this point
2. **Hypothesis** - Documented in `hypotheses/` using `HYPOTHESIS_TEMPLATE.md`
3. **Methods** - The actual code and data required to test the hypothesis
4. **Results + Interpretation** - Output logs (auto-captured by TeeLogger to `results/logs/`) plus analysis through the lens of the hypothesis

The **next steps** from your analysis feed right back into the background for the next iteration.

### Data Progression

1. **Synthetic data** (`experiments/01_synthetic/`) - Fast iteration, no dependencies
2. **Downloaded data** (`experiments/02_downloaded/`) - Benchmark datasets for validation
3. **Real data** (`experiments/03_real_data/`) - Your actual target data

---

## Quick Start

1. Review the philosophy: `docs/SMAIRT_PHILOSOPHY.md`
2. Review the 10 steps: `docs/12_STEPS.md`
3. Define your question: `background/01_initial_question.md`
4. Set up your AI session: `prompts/00_priming_prompts.md`
5. Start experimenting: `experiments/01_synthetic/`
6. Track your contributions: `prompts/intellectual_contribution.md`

---

## Project Structure

```
├── docs/              # SMAIRT philosophy and 10-step guide
├── prompts/           # AI context, known patterns, code conventions
├── plans/             # AI-generated plans (git-tracked for review)
├── background/        # Research question, literature, prior results
├── hypotheses/        # Hypothesis tracking (HYPOTHESIS_TEMPLATE.md)
├── experiments/       # Scripts organized by data phase
│   ├── 01_synthetic/
│   ├── 02_downloaded/
│   └── 03_real_data/
├── results/           # Auto-captured logs and figures
│   ├── logs/          # TeeLogger output (named to match scripts)
│   └── figures/       # Generated visualizations
├── analysis/          # Interpretation and analysis documentation
├── data/              # Data files by phase
├── scripts/           # Helper scripts (new_script.py, compile_for_ai.py)
│   └── shared/        # TeeLogger and shared utilities
└── paper_draft/       # Parallel narrative and figure generation
```

---

## Key Conventions

### Script Naming
```
script_01_description.py
script_02_another_test.py
script_03_noise_robustness.py
```

### The Audit Trail

Every experiment connects through the audit trail:
```
hypotheses/H1_*.md → experiments/script_XX_*.py → results/logs/script_XX_*.log → analysis/
```

TeeLogger automatically captures all script output to `results/logs/`, creating the permanent record without manual copy-paste.

### Known Patterns & Error Prevention

Track reusable patterns and recurring errors in `prompts/KNOWN_PATTERNS.md`. This prevents repeating the same mistakes and preserves working solutions across sessions.

### Feeding Back to AI

For **IDE-native** workflows (Roo/Zoo, Cursor, Windsurf): AI reads project files directly—use `prompts/AI_CONTEXT.md` and `prompts/KNOWN_PATTERNS.md` as context.

For **browser-paste** workflows (ChatGPT, Claude web): Use `scripts/compile_for_ai.py` to generate a summary of the entire project state that you can paste into a new session.

---

## Parallel Story Generation

As a parallel output to the 4-part structure:
- A **paragraph** for each section
- A **figure** for the results section
- A **schematic diagram** for the methods showing the workflow

The final scientific product won't have all experiments together—it will be based on selected results. Use `paper_draft/` to build this narrative alongside your experiments.

---

## Caveats

- **Literature limitations:** LLMs can't do a deep dive on the literature. Be suspicious about what they bring from the literature—verify important claims independently.
- **Regression toward the mean:** AI is good at known approaches but less good at truly innovative connections. That's your job.

---

## License

MIT
