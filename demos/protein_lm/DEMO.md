# Demo: Protein Language Model

**You are given:** the background and the research question.

**You build:** a tiny masked-language-model workflow that learns a planted protein
sequence grammar using SMAIRT.

There are **no solution scripts here**. The goal is to experience using SMAIRT
to go from a question to an answer with an AI assistant, on a compact
computational biology / ML problem that stays scientifically checkable.

> New to AI assistants? Read [`../USING_ZOO_CODE.md`](../USING_ZOO_CODE.md) first
> (install, sign in, attach files, approve edits).

---

## Background / Why this matters

**The field:** **Language models** (the technology behind tools like ChatGPT)
learn patterns by predicting missing or next words in text. Biologists have
borrowed the same idea for **proteins**: an amino-acid sequence is treated like a
sentence, and a **protein language model (PLM)** learns which "letters" (amino
acids) tend to occur together. Big PLMs like ESM now help predict protein
structure and function.

**The core idea:** you train the model by hiding some amino acids and asking it to
fill in the blanks (**masked language modeling**). If the model has genuinely
learned the "grammar" of the sequences, it will predict the hidden residues far
better than simply guessing the most common amino acid, and it will be especially
good at **conserved motifs** - short patterns that recur across related proteins.

---

## The question

Can a **nano masked-language model** trained on synthetic protein-like sequences
learn a **planted grammar**, beating a unigram-frequency baseline on masked
residue prediction and reconstructing a conserved motif far above chance?

Full context, hypothesis, and metrics are in
[`background/01_initial_question.md`](background/01_initial_question.md).

### Key terms

- **Protein language model (PLM):** a model that treats an amino-acid sequence
  like text and learns which residues tend to appear together.
- **Masked language modeling (MLM):** hide some residues, then train the model to
  predict the missing ones from context.
- **Conserved motif:** a short pattern that appears repeatedly in related
  sequences and should be easier to reconstruct than variable positions.
- **Synthetic data with known truth:** the motif and family structure are planted
  by you, so the model can be tested against a controlled ground truth.
- **Unigram-frequency baseline:** the trivial baseline that predicts residues
  from frequency alone. A working model must beat it.
- **Embedding:** a vector representation of a sequence; if the model learns the
  grammar, embeddings from different planted families should separate.

---

## Steps

0. **Set up your environment first** (run from this folder,
   `protein_lm/`):
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
   cp background/01_initial_question.md protein_language_model/background/
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
   - Select a **Model** by difficulty. This is an **advanced** track, so prefer a
     larger, stronger reasoning model. Larger models tend to perform better on
     this kind of multi-file, model-training work.
   >
   > **Markdown preview tip:** press `Cmd+Shift+V` on Mac or `Ctrl+Shift+V` on
   > Windows to render this file in VS Code.

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
   Don't write any code yet. First summarize the question, identify the planted
   ground truth, propose a first hypothesis, and suggest the smallest experiment
   that validates the synthetic data generator before training any model.
   ```

   Read its reply. You decide whether the proposed hypothesis/experiment is
   reasonable before moving on.

4. **Start the SMAIRT loop with one focused request.** After the assistant has
   summarized the question and proposed a first hypothesis, paste a prompt like
   this. Treat the reply as a proposal: you may accept, narrow, or redirect it.

   ```text
   Based on background/01_initial_question.md and the SMAIRT conventions, start
   with a validation-first script in experiments/01_synthetic/.

   I want the first numbered script to:
   (a) generate a synthetic protein-like corpus with a planted conserved motif,
   (b) print a few example sequences,
   (c) report the motif positions and residue frequencies,
   (d) compute a unigram-frequency masked prediction baseline, and
   (e) save simple figures or summaries showing the planted structure.

   Before writing code, briefly state the sequence length, motif design, number of
   sequences, masking rate, fixed random seed, and what exact outputs will let me
   verify that the grammar was planted correctly before any training happens.
   Follow the project code conventions for logging, figures, and the output
   comment block.
   ```

   How to handle the AI response:
   - If the plan starts with **data validation before model training**, say:
     `Proceed with building the script.`
   - Check that the script makes the planted motif positions explicit and uses a
     **fixed random seed** so the corpus is reproducible.
   - If the assistant jumps straight into training a transformer without first
     proving the corpus is correct, redirect it: `First validate the synthetic
     generator and baseline; model training comes after that.`
   - **Second iteration:** train a tiny masked-language model (for example 1-2
     layers, small embedding dimension) and show validation masked-token
     accuracy beats the unigram-frequency baseline.
   - **Third iteration:** compare motif-position accuracy vs. variable-position
     accuracy, and if time allows add a harder two-family synthetic corpus and
     test whether mean-pooled embeddings separate the families.

5. **Interpret and log.** In `analysis/ANALYSIS_01.md`, note: did the synthetic
   corpus actually contain the intended motif and residue biases? what baseline
   accuracy did you expect? after training, how much did masked-token accuracy
   improve over baseline, especially at conserved motif positions? Record your key
   judgment call (for example motif design, mask rate, model size, or stopping
   point) in `prompts/intellectual_contribution.md`. That reasoning is the
   science.

---

## What "done" looks like

On synthetic data: a reproducible corpus with a clearly planted motif, a
validated unigram-frequency baseline, a tiny masked-language model that beats the
baseline on held-out masked prediction, and evidence that motif positions are
reconstructed much better than variable positions. A stronger later rung also
+ numpy/torch/matplotlib, installed in Step 0; CPU-only for the synthetic track.)

> **Going further (optional, later):** use a tiny pretrained ESM-2 model on a
> very small real sequence set and ask whether embeddings cluster by family.
> That is a transfer-learning demonstration, not proof that the nano synthetic
> model captures real biology.

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---------|--------------------|
| `No such file or directory: .../.venv/bin/...` | The venv was deleted/moved. Recreate it: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`. |
| PyTorch install is slow | Normal for this demo. It is the heaviest dependency here, but still CPU-only. Let `pip` finish inside the active venv. |
| Baseline and model accuracy are almost identical | The planted motif may be too weak, the mask setup may be wrong, or the model may not be learning. First confirm the synthetic generator really inserts a conserved signal. |
| Motif reconstruction is poor | The motif may be too noisy, shifted unexpectedly, or not actually masked/evaluated correctly. Print motif positions and inspect a few sequences by hand. |
| Validation accuracy looks unrealistically perfect everywhere | Possible leakage between train and validation sets, or evaluation accidentally includes unmasked tokens. Check the split and metric logic. |
| Results change every run | No fixed random seed. Set and log a seed for corpus generation, data splitting, and model initialization. |
| The model overfits immediately | Corpus too small, model too large, or training too long. Reduce capacity, add a validation split, and stop based on held-out loss. |
| Zoo Code edits the wrong file / drifts | Re-attach `AI_CONTEXT.md` + your `background/01_initial_question.md` and restate the current step. |

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
