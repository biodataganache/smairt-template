#!/usr/bin/env python3
"""
Script 03: Discriminating-motif nano-MLM (fixes the H_02A metric flaw).

Hypothesis: HYPOTHESIS_03.md
Phase: synthetic
Iteration: 3

Purpose:
  ANALYSIS_02 showed the model learned the all-glycine motif perfectly but
  overall masked accuracy tied the unigram baseline, because the motif residue
  WAS the baseline's single guess (glycine) and 47/50 columns are unlearnable
  noise. This script fixes the experiment two ways:
    (1) a multi-residue conserved motif "GKTYRG" (distinct residues, not the
        global mode), so a single-residue unigram baseline can capture at most
        one motif column; and
    (2) reporting TWO baselines — a global-unigram baseline AND a per-column
        most-common-residue baseline — so we can show the model beats the global
        baseline overall and matches the (optimal) per-column baseline.

Depends on:
  - script_02_train_nano_mlm.py (same model/training); ANALYSIS_02.md
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

SCRIPT_NAME = "script_03_discriminating_motif"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIG_DIR = PROJECT_ROOT / "results" / "figures"

SEED = 1024
ALPHABET = "ACDEFGHIKLMNPQRSTVWY"
N_SEQ = 2000
SEQ_LEN = 50
MASK_RATE = 0.15

# Multi-residue fully-conserved motif (distinct residues, NOT all the global mode).
MOTIF_START = 22
MOTIF = "GKTYRG"  # 6 conserved residues at cols 22..27
AA_TO_IDX = {aa: i for i, aa in enumerate(ALPHABET)}
MOTIF_COLS = list(range(MOTIF_START, MOTIF_START + len(MOTIF)))
MOTIF_RESIDUES = {MOTIF_START + i: AA_TO_IDX[c] for i, c in enumerate(MOTIF)}
BACKGROUND_COLS = [c for c in range(SEQ_LEN) if c not in MOTIF_COLS]

PAD_ID = len(ALPHABET)
MASK_ID = len(ALPHABET) + 1
VOCAB_SIZE = len(ALPHABET) + 2

D_MODEL, N_HEAD, N_LAYERS, FF_DIM = 64, 4, 2, 128
LR, EPOCHS, BATCH_SIZE, VAL_FRAC = 1e-3, 30, 128, 0.2


def generate_corpus(rng):
    """Uniform background + multi-residue conserved motif planted at cols 22..27."""
    corpus = rng.integers(0, len(ALPHABET), size=(N_SEQ, SEQ_LEN), dtype=np.int64)
    for col, res in MOTIF_RESIDUES.items():
        corpus[:, col] = res
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


def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    with TeeLogger(log_path):
        print(f"{'='*60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("Hypothesis: HYPOTHESIS_03.md (discriminating motif + dual baselines)")
        print(f"Motif: {MOTIF} at cols {MOTIF_COLS}")
        print(f"{'='*60}\n")

        torch.manual_seed(SEED)
        np.random.seed(SEED)
        rng = np.random.default_rng(SEED)
        corpus = generate_corpus(rng)
        run(corpus)

        print(f"\n{'='*60}")
        print("=== COMPLETE ===")
        print(f"{'='*60}")


def compute_baselines(train_corpus):
    """Return (global_unigram_acc, per_column_optimal_acc) expected on held-out data.

    Both are computed from TRAIN statistics, then their accuracy is the expected
    fraction correct on data drawn from the same distribution.
    """
    # Global unigram: always guess the single most common residue over all positions.
    global_counts = np.bincount(train_corpus.reshape(-1), minlength=len(ALPHABET))
    most_common = int(np.argmax(global_counts))
    # Expected accuracy on a fresh sequence = average over columns of P(residue==most_common).
    # Motif columns are deterministic; background columns are uniform (1/20).
    n_pos = SEQ_LEN
    motif_hits = sum(1 for c in MOTIF_COLS if MOTIF_RESIDUES[c] == most_common)
    bg_hit_rate = 1.0 / len(ALPHABET)
    global_acc = (motif_hits + len(BACKGROUND_COLS) * bg_hit_rate) / n_pos

    # Per-column optimal: for each column guess its own most common residue.
    # Motif columns -> deterministic -> 1.0; background -> 1/20.
    per_col_acc = (len(MOTIF_COLS) * 1.0 + len(BACKGROUND_COLS) * bg_hit_rate) / n_pos
    return most_common, float(global_acc), float(per_col_acc)


def evaluate(model, data, gen):
    model.eval()
    loss_fn = nn.CrossEntropyLoss(ignore_index=-100)
    inputs, targets, mask = apply_masking(data, gen)
    with torch.no_grad():
        logits = model(inputs)
        loss = loss_fn(logits.reshape(-1, VOCAB_SIZE), targets.reshape(-1))
        preds = logits.argmax(dim=-1)
    correct = (preds == data) & mask
    overall = correct.sum().item() / max(mask.sum().item(), 1)
    col_acc = {}
    for col in range(SEQ_LEN):
        m = mask[:, col]
        denom = m.sum().item()
        col_acc[col] = (correct[:, col].sum().item() / denom) if denom > 0 else float("nan")
    return float(loss.item()), overall, col_acc


def run(corpus):
    data = torch.from_numpy(corpus).long()
    n_val = int(N_SEQ * VAL_FRAC)
    perm = torch.randperm(N_SEQ, generator=torch.Generator().manual_seed(SEED))
    val_idx, train_idx = perm[:n_val], perm[n_val:]
    train_data, val_data = data[train_idx], data[val_idx]
    train_corpus = corpus[train_idx.numpy()]
    print(f"[DATA] train={train_data.shape[0]} val={val_data.shape[0]} vocab={VOCAB_SIZE}\n")

    # --- Baselines (computed before training, from train statistics) ---
    mc, global_acc, per_col_acc = compute_baselines(train_corpus)
    print("[BASELINES]")
    print(f"  global-unigram guess = {ALPHABET[mc]} (most common residue)")
    print(f"  global-unigram expected acc = {global_acc:.4f}")
    print(f"  per-column-optimal expected acc = {per_col_acc:.4f}  (the ceiling)\n")

    model = NanoMLM()
    n_params = sum(p.numel() for p in model.parameters())
    print(f"[MODEL] NanoMLM params={n_params:,}\n")

    opt = torch.optim.Adam(model.parameters(), lr=LR)
    loss_fn = nn.CrossEntropyLoss(ignore_index=-100)
    train_gen = torch.Generator().manual_seed(SEED + 7)
    eval_seed = SEED + 99
    n_train = train_data.shape[0]
    history = {"epoch": [], "train_loss": [], "val_loss": [], "val_acc": []}

    print("[TRAIN] epoch | train_loss | val_loss | val_masked_acc")
    for epoch in range(1, EPOCHS + 1):
        model.train()
        order = torch.randperm(n_train, generator=train_gen)
        ep_loss, nb = 0.0, 0
        for start in range(0, n_train, BATCH_SIZE):
            batch = train_data[order[start:start + BATCH_SIZE]]
            inputs, targets, _ = apply_masking(batch, train_gen)
            logits = model(inputs)
            loss = loss_fn(logits.reshape(-1, VOCAB_SIZE), targets.reshape(-1))
            opt.zero_grad(); loss.backward(); opt.step()
            ep_loss += loss.item(); nb += 1
        train_loss = ep_loss / max(nb, 1)
        val_loss, val_acc, _ = evaluate(model, val_data,
                                        torch.Generator().manual_seed(eval_seed))
        history["epoch"].append(epoch)
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)
        if epoch == 1 or epoch % 5 == 0 or epoch == EPOCHS:
            print(f"        {epoch:>5} | {train_loss:>10.4f} | {val_loss:>8.4f} | {val_acc:>13.4f}")

    final_loss, final_acc, col_acc = evaluate(
        model, val_data, torch.Generator().manual_seed(eval_seed))
    motif_accs = [col_acc[c] for c in MOTIF_COLS]
    bg_accs = [col_acc[c] for c in BACKGROUND_COLS if not np.isnan(col_acc[c])]
    motif_mean = float(np.mean(motif_accs))
    bg_mean = float(np.mean(bg_accs))

    print(f"\n[FINAL EVAL on held-out val]")
    print(f"  overall masked accuracy = {final_acc:.4f}")
    print(f"  motif-column accuracy   = {[f'{a:.3f}' for a in motif_accs]} "
          f"(cols {MOTIF_COLS}) mean={motif_mean:.4f}")
    print(f"  background-column mean   = {bg_mean:.4f}\n")

    # --- Hypothesis checks ---
    h03a = final_acc > global_acc + 0.02              # clearly beat global baseline
    h03b = motif_mean >= 0.95 and bg_mean <= 0.15     # reconstruct motif, bg at chance
    h03c = abs(final_acc - per_col_acc) <= 0.03       # match per-column optimum
    h03d = history["val_loss"][-1] < history["val_loss"][0]
    print("[HYPOTHESIS CHECKS]")
    print(f"  H_03A beat GLOBAL baseline (acc>{global_acc:.4f}+0.02): "
          f"{'PASS' if h03a else 'FAIL'} ({final_acc:.4f})")
    print(f"  H_03B reconstruct motif (motif>=0.95, bg<=0.15): "
          f"{'PASS' if h03b else 'FAIL'} (motif={motif_mean:.4f}, bg={bg_mean:.4f})")
    print(f"  H_03C match per-column optimum (|acc-{per_col_acc:.4f}|<=0.03): "
          f"{'PASS' if h03c else 'FAIL'} ({final_acc:.4f})")
    print(f"  H_03D healthy curve (val_loss decreased): "
          f"{'PASS' if h03d else 'FAIL'} "
          f"({history['val_loss'][0]:.3f} -> {history['val_loss'][-1]:.3f})")
    all_pass = h03a and h03b and h03c and h03d
    print(f"\n{'='*60}")
    print(f"VERDICT: {'ALL CHECKS PASSED' if all_pass else 'CHECKS FAILED'}")
    print(f"  Nano-MLM {'learned the grammar AND the metric now discriminates.' if all_pass else 'did NOT meet criteria.'}")
    print(f"  global baseline={global_acc:.4f}  model={final_acc:.4f}  ceiling={per_col_acc:.4f}")
    print(f"{'='*60}")

    save_figures(history, col_acc, global_acc, per_col_acc)


def save_figures(history, col_acc, global_acc, per_col_acc):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(history["epoch"], history["train_loss"], label="train loss")
    ax.plot(history["epoch"], history["val_loss"], label="val loss")
    ax.set_xlabel("epoch"); ax.set_ylabel("masked cross-entropy")
    ax.set_title("Nano-MLM training curve (discriminating motif)")
    ax.legend(); fig.tight_layout()
    f1 = FIG_DIR / "script_03_loss_curve.png"
    fig.savefig(str(f1), dpi=300); plt.close(fig)
    print(f"[FIGURE] saved {f1.relative_to(PROJECT_ROOT)}")

    fig, ax = plt.subplots(figsize=(10, 3.5))
    cols = list(range(SEQ_LEN))
    accs = [col_acc[c] for c in cols]
    colors = ["tab:red" if c in MOTIF_COLS else "tab:blue" for c in cols]
    ax.bar(cols, accs, color=colors)
    ax.axhline(global_acc, color="gray", ls="--", lw=1,
               label=f"global-unigram baseline ({global_acc:.3f})")
    ax.axhline(1.0 / len(ALPHABET), color="green", ls=":", lw=1, label="chance (1/20)")
    ax.set_xlabel("sequence column"); ax.set_ylabel("masked accuracy")
    ax.set_title("Per-column masked accuracy (red = conserved motif GKTYRG)")
    ax.legend(); fig.tight_layout()
    f2 = FIG_DIR / "script_03_per_column_accuracy.png"
    fig.savefig(str(f2), dpi=300); plt.close(fig)
    print(f"[FIGURE] saved {f2.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
