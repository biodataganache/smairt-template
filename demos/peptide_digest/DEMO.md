# Demo: Tryptic Peptide Digestion

**You are given:** the background and the research question.

**You build:** the in-silico trypsin digester and the MS-observable peptide
filter using SMAIRT.

There are **no solution scripts here**. The goal is to experience using SMAIRT
to go from a question to an answer with an AI assistant, on a small,
exactly-checkable biology problem.

> New to AI assistants? Read [`../USING_ZOO_CODE.md`](../USING_ZOO_CODE.md) first
> (install, sign in, attach files, approve edits).

---

## Background / Why this matters

**The field:** **Proteomics** is the large-scale study of the proteins in a cell,
tissue, or organism. The workhorse instrument is the **mass spectrometer**, which
weighs molecules with extraordinary precision. But a whole protein is usually too
big to measure directly, so scientists first chop it into small pieces called
**peptides** using a protein-cutting enzyme, then weigh those.

**The core idea:** the standard "molecular scissors" is **trypsin**, and it cuts
by a simple, near-deterministic rule: snip the chain right after the amino acids
K (lysine) or R (arginine) - *unless* the next amino acid is P (proline). Knowing
this rule, you can predict, purely on a computer ("in silico"), exactly which
peptides a given protein will produce. Then you can predict each peptide's mass
and ask which ones fall in the range a mass spectrometer can actually detect.

---

## The question

For a given protein sequence, what set of peptides does **trypsin** produce, and
which of those peptides fall in the **mass and length window a mass spectrometer
can actually observe**?

Full context, hypothesis, and metrics are in
[`background/01_initial_question.md`](background/01_initial_question.md).

### Key terms

- **Trypsin:** the standard protease in proteomics. It cuts a protein into
  peptides **after K (lysine) or R (arginine)**, but **not when the next residue
  is P (proline)**.
- **Peptide:** a short stretch of a protein produced by digestion; what the mass
  spectrometer actually measures.
- **Missed cleavage:** a site trypsin should have cut but didn't, leaving an
  internal K/R inside a peptide. Real digests have a few.
- **Monoisotopic mass:** a peptide's mass computed from the lightest isotope of
  each atom; the value an MS reports. = sum of residue masses + one water.
- **MS-observable window:** mass spectrometers only see peptides in a limited
  mass/length range (roughly 500-5000 Da, 6-40 residues).
- **Exact validation:** because the digestion rules are deterministic, you can
  hand-check the answer on tiny sequences. "Correct" is unambiguous.

---

## Steps

0. **Set up your environment first** (run from this folder,
   `peptide_digest/`):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate     # Windows PowerShell: .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

   This installs `cookiecutter` (used in the next step) plus matplotlib (optional
   plots). The digestion itself is pure-Python standard library. If you see
   `command not found: cookiecutter`, this step was skipped or your venv isn't
   active.

   Windows users: if PowerShell blocks activation, run
   `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal,
   then try `.venv\Scripts\Activate.ps1` again. In Command Prompt, use
   `.venv\Scripts\activate.bat`.
1. **Generate a fresh SMAIRT project** (run from this folder, venv active):

   ```bash
   cookiecutter https://github.com/biodataganache/smairt-template.git
   ```

   Cookiecutter then asks you a series of questions. If you've run it before you
   may first see `Is it okay to delete and re-download it? [y/n] (y):`. Press
   **Enter**. Then answer the prompts. Press **Enter** to accept a default,
   or type the value/number shown. For the **Select** prompts, type the
   **number** (not the word). **Suggested answers for this demo:**

   | Prompt                    | Suggested answer                                                               |
   | ------------------------- | ------------------------------------------------------------------------------ |
   | project_name              | `Peptide Digest`                                                             |
   | project_slug              | press Enter (auto)                                                             |
   | author_name               | your name                                                                      |
   | author_email              | your email (or Enter)                                                          |
   | description               | `In-silico tryptic digestion and MS-observable peptides`                     |
   | project_mode              | `1` (standard)                                                               |
   | workflow_mode             | `1` (ide_native)                                                             |
   | initial_research_question | `What tryptic peptides does a protein produce, and which are MS-observable?` |
   | domain                    | `3` (computational_biology)                                                  |
   | ai_tool                   | `1` (roo_zoo / Zoo Code)                                                     |
   | include_example_project   | `1` (no)                                                                     |
   | starting_phase            | `1` (synthetic)                                                              |
   | license                   | `1` (MIT)                                                                    |
   | create_git_repo           | `1` (yes)                                                                    |

   This creates a folder named after your project_slug (e.g. `peptide_digest/`).
2. **Seed your project with the background:**

   ```bash
   cp background/01_initial_question.md peptide_digest/background/
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
   - Select a **Model** by difficulty. This is a **beginner** track, so a fast,
     lightweight reasoning model is usually plenty. Step up to a larger model
     only if the assistant struggles.
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
   + results/logs/, and a pasted-output comment block at the end of each script.
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
   with a small, exactly-checkable example. Create the first numbered script in
   experiments/01_synthetic/ that digests a few short test sequences with trypsin
   (cleave after K/R, NOT before P) and asserts the peptide list matches a
   hand-written expected list. Treat these assertions as the validation.

   Before writing code, briefly state the test sequences and their expected
   peptides, what would make the implementation credible, and how later scripts
   will add missed cleavages and peptide-mass calculation. Follow the project code
   conventions for logging and the output comment block.
   ```

   How to handle the AI response:

   - If the test cases are explicit and the script is focused, say:
     `Proceed with building the script.`
   - Before trusting results, check the **"not before P"** exception is handled
     (no peptide boundary at K-P or R-P) and that the N- and C-terminal peptides
     are produced correctly.
   - If the assistant skips validation and just prints peptides, redirect it:
     `Add explicit assertions against hand-checked expected peptides first; that is the experiment.`
   - **Second iteration:** add missed cleavages (0 -> 1 -> 2) and show how peptide
     count and average length change.
   - **Third iteration:** add monoisotopic peptide mass and filter to the
     MS-observable window (mass 500-5000 Da, length 6-40); report the observable
     fraction and plot the distribution.
5. **Interpret and log.** In `analysis/ANALYSIS_01.md`, note: did the digest
   pass every hand-checked case? how did missed cleavages change the peptide set?
   what fraction was MS-observable? Record any key judgment call (e.g. the exact
   mass table or window you chose, and why) in
   `prompts/intellectual_contribution.md`. That reasoning is the science.

---

## What "done" looks like

A trypsin digester that passes your hand-checked test cases, computes peptide
masses that match reference values, honors the "not before P" rule, and reports
how many peptides are MS-observable, all reproducible from your breadcrumb trail.
(Requirements: cookiecutter + matplotlib, installed in Step 0; pure Python,
CPU-only, no network needed.)

> **Going further (optional, later):** paste a real protein sequence (e.g. BSA or
> human serum albumin from a FASTA) and compare your peptide list and masses
> against a public tool such as ExPASy PeptideMass as an external check.

---

## Troubleshooting

| Symptom                                          | Likely cause / fix                                                                                                                 |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| `command not found: cookiecutter`              | venv not active or Step 0 skipped. Run`source .venv/bin/activate` then `pip install -r requirements.txt`.                      |
| `No such file or directory: .../.venv/bin/...` | The venv was deleted/moved. Recreate it:`python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`. |
| cookiecutter asks to re-download the template    | Normal if you've run it before. Press**Enter** (y).                                                                          |
| Peptide split at K-P or R-P                      | The "not before P" exception isn't implemented. Ask the AI to skip cleavage when the next residue is proline.                      |
| Off-by-one peptides (missing first/last)         | Boundary handling at the protein N-/C-terminus. Check the last peptide is emitted even without a trailing K/R.                     |
| Peptide masses look wrong (~18 Da off)           | Forgot to add one water for the terminal groups, or used average instead of monoisotopic masses.                                   |
| Too few/too many peptides "observable"           | Wrong mass/length window. Re-check the 500-5000 Da, 6-40 residue thresholds.                                                       |
| Missed cleavages explode peptide count           | Expected: count grows with allowed missed cleavages. Keep it at 1-2 like real searches.                                            |
| Zoo Code edits the wrong file / drifts           | Re-attach`AI_CONTEXT.md` + your `background/01_initial_question.md` and restate the current step.                              |

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
   - experiments/ (my numbered scripts so far, with output pasted at the bottom)
   - results/logs/ (run outputs)
   - analysis/ANALYSIS_01.md (what I concluded so far)
   Summarize where the project stands and what the next step is. Don't rewrite
   working code. Continue from here.
   ```
   Tip: if it exists, run `python scripts/compile_for_ai.py` and paste its output
   to hand over the whole trail at once.
