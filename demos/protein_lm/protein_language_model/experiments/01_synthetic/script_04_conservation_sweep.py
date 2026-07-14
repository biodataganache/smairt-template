#!/usr/bin/env python3
"""
Script 04: Conservation sweep — does motif-recovery accuracy track conservation?

Hypothesis: HYPOTHESIS_04.md (H_04A monotonic, H_04B Bayes-optimal, H_04C bg chance)
Phase: synthetic
Iteration: 4

Purpose:
  Iterations 02-03 used a 100%-conserved motif (trivially learnable). The
  background doc calls out the real science: "how accuracy tracks the conservation
  level you set." Here each motif column is conserved with probability p (else
  drawn from uniform background). We train one nano-MLM per p in {1.0,0.9,0.7,0.5,
  0.25} and check that recovered motif accuracy tracks the Bayes-optimal curve
  p + (1-p)/20, while background stays at chance.

Depends on:
  - script_03_discriminating_motif.py (same model/training/eval); ANALYSIS_03.md
  - torch (CPU), numpy, matplotlib
"""

import sys
from pathlib import Path
from datetime import datetime

import numpy as np
import torch
import torch.nn as nn

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

SCRIPT_NAME = "script_04_conservation_sweep"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIG_DIR = PROJECT_ROOT / "results" / "figures"

SEED = 1024
ALPHABET = "ACDEFGHIKLMNPQRSTVWY"
N_SEQ = 2000
SEQ_LEN = 50
MASK_RATE = 0.15

MOTIF_START = 22
MOTIF = "GKTYRG"
AA_TO_IDX = {aa: i for i, aa in enumerate(ALPHABET)}
MOTIF_COLS = list(range(MOTIF_START, MOTIF_START + len(MOTIF)))
MOTIF_RESIDUES = {MOTIF_START + i: AA_TO_IDX[c] for i, c in enumerate(MOTIF)}
BACKGROUND_COLS = [c for c in range(SEQ_LEN) if c not in MOTIF_COLS]

PAD_ID = len(ALPHABET)
MASK_ID = len(ALPHABET) + 1
VOCAB_SIZE = len(ALPHABET) + 2

D_MODEL, N_HEAD, N_LAYERS, FF_DIM = 64, 4, 2, 128
LR, EPOCHS, BATCH_SIZE, VAL_FRAC = 1e-3, 30, 128, 0.2

CONSERVATION_LEVELS = [1.0, 0.9, 0.7, 0.5, 0.25]


def generate_corpus(rng, p):
    """Uniform background; each motif column = its conserved residue w.p. p, else background."""
    corpus = rng.integers(0, len(ALPHABET), size=(N_SEQ, SEQ_LEN), dtype=np.int64)
    for col, res in MOTIF_RESIDUES.items():
        keep = rng.random(N_SEQ) < p
        corpus[keep, col] = res
        # non-kept rows keep their random background draw (already set)
    return corpus


class NanoMLM(nn.Module):
    def __init__(self):
        super().__init__()
        self.tok_emb = nn.Embedding(VOCAB_SIZE, D_MODEL, padding_idx=PAD_ID)
        self.pos_emb = nn.Embedding(SEQ_LEN, D_MODEL)
        layer = nn.TransformerEncoderLayer(
            d_model=D_MODEL, nhead=N_HEAD, dim_feedforward=FF_DIM,
            batch_first=True, dropout=0.0)
        self.encoder = nn.TransformerEncoder(layer, num_layers=N_LAYERS)
        self.head = nn.Linear(D_MODEL, VOCAB_SIZE)
        self.register_buffer("positions", torch.arange(SEQ_LEN).unsqueeze(0))

    def forward(self, x):
        h = self.tok_emb(x) + self.pos_emb(self.positions)
        h = self.encoder(h)
        return self.head(h)


def apply_masking(batch, gen):
    mask = torch.rand(batch.shape, generator=gen) < MASK_RATE
    inputs = batch.clone()
    inputs[mask] = MASK_ID
    targets = batch.clone()
    targets[~mask] = -100
    return inputs, targets, mask


def evaluate(model, data, gen):
    model.eval()
    inputs, targets, mask = apply_masking(data, gen)
    with torch.no_grad():
        logits = model(inputs)
        preds = logits.argmax(dim=-1)
    correct = (preds == data) & mask
    col_acc = {}
    for col in range(SEQ_LEN):
        m = mask[:, col]
        denom = m.sum().item()
        col_acc[col] = (correct[:, col].sum().item() / denom) if denom > 0 else float("nan")
    return col_acc


def train_one(corpus):
    """Train a fresh nano-MLM on the given corpus; return per-column val accuracy."""
    data = torch.from_numpy(corpus).long()
    n_val = int(N_SEQ * VAL_FRAC)
    perm = torch.randperm(N_SEQ, generator=torch.Generator().manual_seed(SEED))
    val_idx, train_idx = perm[:n_val], perm[n_val:]
    train_data, val_data = data[train_idx], data[val_idx]

    torch.manual_seed(SEED)
    model = NanoMLM()
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    loss_fn = nn.CrossEntropyLoss(ignore_index=-100)
    train_gen = torch.Generator().manual_seed(SEED + 7)
    n_train = train_data.shape[0]

    for _ in range(EPOCHS):
        model.train()
        order = torch.randperm(n_train, generator=train_gen)
        for start in range(0, n_train, BATCH_SIZE):
            batch = train_data[order[start:start + BATCH_SIZE]]
            inputs, targets, _ = apply_masking(batch, train_gen)
            logits = model(inputs)
            loss = loss_fn(logits.reshape(-1, VOCAB_SIZE), targets.reshape(-1))
            opt.zero_grad(); loss.backward(); opt.step()

    return evaluate(model, val_data, torch.Generator().manual_seed(SEED + 99))


def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    with TeeLogger(log_path):
        print(f"{'='*60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("Hypothesis: HYPOTHESIS_04.md (accuracy tracks conservation level)")
        print(f"Motif: {MOTIF} at cols {MOTIF_COLS}; levels p={CONSERVATION_LEVELS}")
        print(f"{'='*60}\n")

        run_sweep()

        print(f"\n{'='*60}")
        print("=== COMPLETE ===")
        print(f"{'='*60}")


def run_sweep():
    results = []  # (p, motif_mean, bg_mean, bayes_opt)
    base_rng_seed = SEED

    print("[SWEEP]  p   | motif_acc | bayes_opt | bg_acc | per-col motif accs")
    for p in CONSERVATION_LEVELS:
        # Each level gets its own corpus (deterministic seed per level).
        rng = np.random.default_rng(base_rng_seed + int(round(p * 100)))
        corpus = generate_corpus(rng, p)
        col_acc = train_one(corpus)

        motif_accs = [col_acc[c] for c in MOTIF_COLS]
        bg_accs = [col_acc[c] for c in BACKGROUND_COLS if not np.isnan(col_acc[c])]
        motif_mean = float(np.mean(motif_accs))
        bg_mean = float(np.mean(bg_accs))
        bayes_opt = p + (1 - p) / len(ALPHABET)
        results.append((p, motif_mean, bg_mean, bayes_opt))

        print(f"        {p:>4.2f} | {motif_mean:>9.4f} | {bayes_opt:>9.4f} | "
              f"{bg_mean:>6.4f} | {[f'{a:.2f}' for a in motif_accs]}")

    # --- Hypothesis checks ---
    ps = [r[0] for r in results]
    motif_means = [r[1] for r in results]
    bg_means = [r[2] for r in results]
    bayes = [r[3] for r in results]

    # H_04A monotonic in p (results are in descending p; check ascending order).
    asc = sorted(zip(ps, motif_means))  # by p ascending
    asc_acc = [a for _, a in asc]
    monotone = all(asc_acc[i] <= asc_acc[i + 1] + 0.05 for i in range(len(asc_acc) - 1))
    endpoints = asc_acc[-1] > asc_acc[0]  # p=1.0 clearly > p=0.25
    h04a = monotone and endpoints

    # H_04B near Bayes-optimal (within 0.10 each level).
    devs = [abs(m - b) for m, b in zip(motif_means, bayes)]
    h04b = all(d <= 0.10 for d in devs)

    # H_04C background at chance for all levels.
    h04c = all(b <= 0.15 for b in bg_means)

    print(f"\n[HYPOTHESIS CHECKS]")
    print(f"  H_04A monotonic & p=1.0>p=0.25: {'PASS' if h04a else 'FAIL'} "
          f"(asc accs={[f'{a:.3f}' for a in asc_acc]})")
    print(f"  H_04B near Bayes-optimal (|dev|<=0.10): {'PASS' if h04b else 'FAIL'} "
          f"(max dev={max(devs):.4f})")
    print(f"  H_04C background<=0.15 all levels: {'PASS' if h04c else 'FAIL'} "
          f"(max bg={max(bg_means):.4f})")
    all_pass = h04a and h04b and h04c
    print(f"\n{'='*60}")
    print(f"VERDICT: {'ALL CHECKS PASSED' if all_pass else 'CHECKS FAILED'}")
    print(f"  Motif accuracy {'tracks the planted conservation level.' if all_pass else 'did NOT track as predicted.'}")
    print(f"{'='*60}")

    save_figure(results)


def save_figure(results):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ps = [r[0] for r in results]
    motif_means = [r[1] for r in results]
    bg_means = [r[2] for r in results]
    bayes = [r[3] for r in results]
    order = np.argsort(ps)
    ps = np.array(ps)[order]
    motif_means = np.array(motif_means)[order]
    bg_means = np.array(bg_means)[order]
    bayes = np.array(bayes)[order]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(ps, bayes, "k--", label="Bayes-optimal p+(1-p)/20")
    ax.plot(ps, motif_means, "o-", color="tab:red", label="model motif-column acc")
    ax.plot(ps, bg_means, "s-", color="tab:blue", label="model background acc")
    ax.axhline(1.0 / len(ALPHABET), color="green", ls=":", lw=1, label="chance (1/20)")
    ax.set_xlabel("planted conservation level p")
    ax.set_ylabel("masked accuracy")
    ax.set_title("Motif recovery vs planted conservation level")
    ax.set_ylim(0, 1.05)
    ax.legend()
    fig.tight_layout()
    f1 = FIG_DIR / "script_04_accuracy_vs_conservation.png"
    fig.savefig(str(f1), dpi=300)
    plt.close(fig)
    print(f"[FIGURE] saved {f1.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
