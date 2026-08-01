# Demo: Protein-Protein Interaction Networks

**You are given:** the background and the research question.

**You build:** the synthetic-network generator and the hub/community analysis
using SMAIRT.

There are **no solution scripts here**. The goal is to experience using SMAIRT
to go from a question to an answer with an AI assistant, on a small network
biology problem you can iterate on.

> New to AI assistants? Read [`../USING_ZOO_CODE.md`](../USING_ZOO_CODE.md) first
> (install, sign in, attach files, approve edits).

---

## Background / Why this matters

**The field:** Proteins rarely work alone; they physically bind and cooperate
with other proteins to do their jobs. Map every such interaction and you get a
**protein-protein interaction (PPI) network** - a graph where each protein is a
dot (node) and each interaction is a line (edge). This is a cornerstone of
**systems biology**, used to find disease genes, drug targets, and the machinery
of the cell.

**The core idea:** networks have structure you can measure. Some proteins have
far more partners than others - **hubs** - and are often essential to the cell.
Proteins also cluster into **modules (communities)**: tight-knit groups that talk
mostly among themselves, usually because they share a pathway or form a complex.
Standard graph algorithms claim to find these hubs and modules automatically.

---

## The question

In a protein-protein interaction network, can standard graph methods reliably
**identify the most important proteins (hubs)** and **detect the functional
modules (communities)** that are actually present?

Full context, hypothesis, and metrics are in
[`background/01_initial_question.md`](background/01_initial_question.md).

### Key terms

- **Node / edge:** a protein is a node; an interaction between two proteins is an
  edge. The whole set is the network (graph).
- **Hub:** a protein with an unusually high number of interaction partners (high
  degree). Often biologically important.
- **Module / community:** a group of proteins that interact much more with each
  other than with the rest of the network; usually a shared pathway or complex.
- **Centrality:** measures of how "important" a node is. Degree centrality counts
  partners; betweenness centrality counts how often a node sits on shortest paths.
- **Community detection:** algorithms (e.g. greedy modularity / Louvain in
  networkx) that partition the graph into densely connected groups.
- **Synthetic data with known truth:** you generate the network with planted hubs
  and modules, so you can check whether the methods recover them before using
  real data.

---

## Steps

0. **Set up your environment first** (run from this folder, `ppi_network/`):
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
   cp background/01_initial_question.md ppi_network/background/
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
   - Select a **Model** by difficulty. This is an **intermediate** track, so a
     mid-tier reasoning model is a good default for the graph analysis and
     community-detection steps. Step up to a larger model if the assistant struggles.
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
   with a synthetic example. Create the first numbered script in
   experiments/01_synthetic/ that (a) generates a network with a KNOWN number of
   hubs and modules (e.g. a stochastic block model plus a few high-degree nodes),
   (b) ranks nodes by degree and betweenness centrality, and (c) reports whether
   the planted hubs appear in the top-k, with a drawing of the network.

   Before writing code, briefly state how many hubs/modules you'll plant, what
   "recovering" a hub means (e.g. precision/recall in the top-k), and how later
   scripts will add community detection and a noise-robustness test. Follow the
   project code conventions for logging, figures, and the output comment block.
   ```

   How to handle the AI response:
   - If the plan plants a known structure and checks recovery against it, say:
     `Proceed with building the script.`
   - Before trusting results, check it uses a **fixed random seed**, that the
     planted hubs/modules are recorded as ground truth, and that recovery is
     measured **against that truth** (not just "this node has high degree").
   - If the assistant only reports centrality values with no comparison to the
     plant, redirect it: `Report precision/recall of the planted hubs in the
     top-k; that is the experiment.`
   - **Second iteration:** add community detection (greedy modularity or Louvain)
     and measure agreement with the planted module labels (adjusted Rand index or
     NMI).
   - **Third iteration:** add random noise edges (and/or remove true edges) and
     plot how hub and community recovery degrade as noise increases.

5. **Interpret and log.** In `analysis/ANALYSIS_01.md`, note: did centrality
   recover the planted hubs? did community detection match the planted modules,
   and by how much? at what noise level did recovery break down? Record your key
   judgment call (e.g. which centrality you trust and why) in
   `prompts/intellectual_contribution.md`. That reasoning is the science.

---

## What "done" looks like

On synthetic data: centrality rankings that recover the planted hubs in the
top-k, community detection that matches the planted modules with high agreement,
a noise-robustness curve, and a network drawing, all reproducible from your
installed in Step 0; CPU-only, no network needed.)

> **Going further (optional, later):** load a small published interaction list
> (e.g. a subset of STRING or BioGRID for one organism or complex). Truth is now
> real biology, so discuss which detected hubs/modules make biological sense and
> which look like artifacts in your log.

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---------|--------------------|
| `No such file or directory: .../.venv/bin/...` | The venv was deleted/moved. Recreate it: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`. |
| `ModuleNotFoundError: networkx` | venv not active or Step 0 skipped. Activate the venv and reinstall requirements. |
| Centrality doesn't find the planted hubs | Hubs aren't actually high-degree relative to the background, or you compared against the wrong node IDs. Increase the hubs' degree and track the planted IDs explicitly. |
| Community detection finds one giant community | Modules aren't dense enough vs. between-module edges. Raise within-module edge probability or lower the between-module probability. |
| Adjusted Rand index is near 0 | Detected and planted labels aren't aligned, or modules are too weak. Compare label sets correctly and strengthen the planted structure. |
| Betweenness is very slow | Expected on larger graphs; use a smaller node count for the demo or approximate betweenness. |
| Results change every run | No fixed random seed. Set and log a seed so the synthetic network is reproducible. |
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
