# Demo: Protein Sequence Properties

**You are given:** the background and the research question.

**You build:** the sequence-property calculators (MW, pI, GRAVY) and the
membrane-vs-soluble test using SMAIRT.

There are **no solution scripts here**. The goal is to experience using SMAIRT
to go from a question to an answer with an AI assistant, on a small protein
biochemistry problem you can iterate on.

> New to AI assistants? Read [`../USING_ZOO_CODE.md`](../USING_ZOO_CODE.md) first
> (install, sign in, attach files, approve edits).

---

## Background / Why this matters

**The field:** A protein is a chain of **amino acids**, and that sequence alone
determines many of the protein's basic physical properties. **Protein
biochemistry** lets you predict useful numbers straight from the sequence, with
no experiment: how heavy the protein is (**molecular weight, MW**), the pH at
which it carries no net charge (**isoelectric point, pI**), and how
water-loving or water-fearing it is on average (**GRAVY**, a hydrophobicity
score). Researchers use these constantly when planning experiments and
interpreting data.

**The core idea:** these properties come from simple, well-established formulas -
sum up residue masses, solve a charge-versus-pH curve, average a hydrophobicity
scale. A neat payoff is that hydrophobicity carries biological signal:
**membrane** proteins, which sit in oily cell membranes, are more hydrophobic
than **soluble** proteins that float in water. So a simple threshold or classifier
on GRAVY should be able to tell the two apart.

---

## The question

From an amino-acid sequence alone, can we compute **MW, pI, and GRAVY**
accurately (validated against references), and can a **hydrophobicity threshold
or simple classifier separate membrane proteins from soluble proteins**?

Full context, hypothesis, and metrics are in
[`background/01_initial_question.md`](background/01_initial_question.md).

### Key terms

- **Molecular weight (MW):** sum of residue masses plus one water for the
  terminal groups. Exactly checkable by hand on short sequences.
- **Isoelectric point (pI):** the pH at which the protein carries no net charge,
  found by solving the charge-vs-pH curve with standard pKa values.
- **GRAVY:** grand average of hydropathy, the mean of a per-residue
  hydrophobicity scale (Kyte-Doolittle). Positive = hydrophobic, negative =
  hydrophilic.
- **Membrane vs. soluble:** membrane-spanning proteins are rich in hydrophobic
  residues, so they tend to have higher GRAVY than water-soluble proteins. That
  is the signal the classifier should pick up.
- **Synthetic data with known truth:** you compute properties for sequences you
  can check by hand, and generate two labeled pools, so you can verify the
  calculators and the rule before touching real data.

---

## Steps

0. **Set up your environment first** (run from this folder,
   `protein_properties/`):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate     # Windows PowerShell: .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
   This installs only the scientific Python dependencies for the demo.


   Windows users: if PowerShell blocks activation, run
   `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal,
   then try `.venv\Scripts\Activate.ps1` again. In Command Prompt, use
   `.venv\Scripts\activate.bat`.
1. **Create a fresh SMAIRT project** with the installed CLI:
   ```bash
   smairt new
   ```
   Use the guided prompts to choose the demo name, research question, domain,
   starting phase, and assistant. The installed `smairt` command is the only
   supported generator.


2. **Seed your project with the background:**

   ```bash
   cp background/01_initial_question.md protein_properties/background/
   ```
3. **Configure Zoo Code, then open the project in VS Code and prime it.** New to
   AI assistants? Read [`../USING_ZOO_CODE.md`](../USING_ZOO_CODE.md) first. It
   covers installing Zoo Code, signing in, and how to attach files and approve
   edits.

   Basic Zoo Code configuration for this demo:

   - Install **Zoo Code** from the VS Code Extensions panel.
   - Set **API Provider** to **OpenAI Compatible**. Any OpenAI-compatible
     endpoint works (OpenAI, Anthropic, OpenRouter, Azure OpenAI, a local server
     such as Ollama / LM Studio, or an institutional gateway).
   - Use **API Base URL**: your provider's documented base URL (for example,
     `https://api.openai.com/v1` for OpenAI).
   - Paste an **API Key** from your chosen provider.
   - Select a **Model** by difficulty. This track runs from **beginner to
     intermediate**, so start with a fast, lightweight model and step up to a
     mid-tier model if the later classification steps need stronger reasoning.
   >
   > **Markdown preview tip:** press `Cmd+Shift+V` on Mac or `Ctrl+Shift+V` on
   > Windows to render this file in VS Code.
   >

   Open your new project folder in VS Code (**File > Open Folder...**). In the
   Zoo Code chat, paste this direct prompt:

   ```text
   I'm starting a SMAIRT project to answer the question in
   background/01_initial_question.md. Please read these files before doing any
   work:
   1. prompts/AI_CONTEXT.md
   2. prompts/CODE_CONVENTIONS.md
   3. background/01_initial_question.md

   Follow the SMAIRT workflow described there: numbered scripts, output to console
   + results/logs/; use the tracked raw log as the execution record.
   Don't write any code yet. First summarize the question and propose a first
   hypothesis and an experiment to test it.
   ```

   Read its reply. You decide whether the proposed hypothesis/experiment is
   reasonable before moving on.
4. **Start the SMAIRT loop with one focused request.** After the assistant has
   summarized the question and proposed a first hypothesis, paste a prompt like
   this. Treat the reply as a proposal: you may accept, narrow, or redirect it.

   ```text
   Based on background/01_initial_question.md and the SMAIRT conventions, start
   with a validation example. Create the first numbered script in
   experiments/01_synthetic/ that (a) computes MW and GRAVY for a few SHORT
   sequences whose values I can check by hand, (b) computes pI for one or two
   reference proteins, and (c) reports the computed values next to the expected
   ones so I can confirm the calculators are correct.

   Before writing code, briefly state which short sequences you'll use, the
   hand-computed MW you expect, what tolerance counts as "matching", and how later
   scripts will use these calculators as features to separate membrane from
   soluble proteins. Follow the project code conventions for logging, figures, and
   the output comment block.
   ```

   How to handle the AI response:

   - If the plan validates the calculators against hand-checkable / reference
     values first, say: `Proceed with building the script.`
   - Before trusting results, check that MW uses the right residue masses **plus
     one water**, that pI solves net-charge = 0 with standard pKa values, and that
     GRAVY uses the Kyte-Doolittle scale. Confirm the computed values match the
     references within tolerance.
   - If the assistant jumps straight to classification without validating the
     calculators, redirect it: `First validate MW/pI/GRAVY against known values; that is the foundation of the experiment.`
   - **Second iteration:** generate two labeled pools (hydrophobic "membrane-like"
     vs. charged/polar "soluble-like"), show GRAVY separates them, and recover the
     planted labels with a one-feature threshold or classifier (report
     accuracy/AUC).
   - **Third iteration:** compare features (GRAVY vs. pI vs. MW) and show GRAVY is
     the best separator; plot the GRAVY histograms for the two classes.
5. **Interpret and log.** In `analysis/ANALYSIS_01.md`, note: did the
   calculators match references within tolerance? how well did GRAVY separate the
   two classes? which feature mattered most, and where did the simple rule
   misclassify? Record your key judgment call (e.g. the GRAVY threshold you chose
   and why) in `prompts/intellectual_contribution.md`. That reasoning is the
   science.

---

## What "done" looks like

On synthetic data: MW/pI/GRAVY calculators that match reference values within a
small tolerance, a demonstration that GRAVY separates membrane-like from
soluble-like sequences well above chance, and the GRAVY histograms / feature
comparison, all reproducible from your breadcrumb trail. (Requirements:
CPU-only, no network needed.)

> **Going further (optional, later):** download a small labeled set from UniProt
> (a handful of known transmembrane vs. soluble proteins) and test whether the
> GRAVY rule still separates them. Truth is now real biology, not planted, so
> discuss misclassifications honestly in your log.

---

## Troubleshooting

| Symptom                                          | Likely cause / fix                                                                                                                                                |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `No such file or directory: .../.venv/bin/...` | The venv was deleted/moved. Recreate it:`python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.                                |
| Computed MW is off by ~18 Da                     | Forgot to add (or double-counted) the terminal water. Add exactly one water to the summed residue masses.                                                         |
| Computed MW is off by a lot                      | Mixed up monoisotopic vs. average masses, or used peptide-bond-subtracted residue masses inconsistently. Pick one scheme and check against a reference tool.      |
| pI is wildly wrong                               | Wrong pKa set or missing the N-/C-terminus charges. Include termini plus D, E, C, Y, H, K, R.                                                                     |
| GRAVY sign looks inverted                        | Scale applied backwards. Kyte-Doolittle: positive = hydrophobic.                                                                                                  |
| Classifier accuracy is ~50%                      | The two pools aren't actually biased, or labels are shuffled. Check the generator plants a real hydrophobicity difference and that labels line up with sequences. |
| Results change every run                         | No fixed random seed. Set and log a seed so the synthetic pools are reproducible.                                                                                 |
| Zoo Code edits the wrong file / drifts           | Re-attach`AI_CONTEXT.md` + your `background/01_initial_question.md` and restate the current step.                                                             |

### Zoo Code is stuck (an error a retry won't fix)

If the assistant gets into a broken state, don't keep retrying. **Start a fresh
task/chat** (in Zoo Code, open a new task with the `+` button) and re-prime it
from your breadcrumb trail. SMAIRT is designed for exactly this: your project
files hold the context.

1. Save your work (your scripts/logs are already on disk).
2. Open the new task with your project folder still open.
3. Attach `prompts/AI_CONTEXT.md`, `prompts/CODE_CONVENTIONS.md`, and
   `background/01_initial_question.md`, then paste:

   ```text
   I'm resuming a SMAIRT project (the question is in
   background/01_initial_question.md) after my previous AI session got stuck.
   Please read AI_CONTEXT.md and CODE_CONVENTIONS.md and follow the SMAIRT
   workflow. To get back up to speed, read my existing files:
   - experiments/ (my numbered scripts so far)
   - results/logs/ (run outputs)
   - analysis/ANALYSIS_01.md (what I concluded so far)
   Summarize where the project stands and what the next step is. Don't rewrite
   working code. Continue from here.
   ```
   to hand over the whole trail at once.
