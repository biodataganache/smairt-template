#!/usr/bin/env python3
"""
Script 02: Train a nano masked-language model (MLM) on the synthetic corpus.

Hypothesis: HYPOTHESIS_02.md (H_02A beat baseline, H_02B reconstruct motif, H_02C curve)
Phase: synthetic
Track: (none — sequential numbering)
Iteration: 2

Purpose:
  Train a tiny transformer with 15% masked-residue prediction on the iteration-01
  synthetic corpus (P-loop motif G-x-G-x-x-G at columns 22/24/27). Tests whether
  the model (a) beats the unigram-frequency baseline (0.1076 from ANALYSIS_01),
  (b) reconstructs the conserved-motif G positions at ~1.0 accuracy while scoring
  background positions near chance, and (c) shows a healthy train/val loss curve.

Depends on:
  - experiments/01_synthetic/script_01_validate_generator.py (same generator/params)
  - results/ANALYSIS_01.md baseline target = 0.1076
  - torch (CPU), numpy, matplotlib
"""

import sys
from pathlib import Path
from datetime import datetime

import numpy as np
import torch
import torch.nn as nn

# === PATH SETUP ===
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

# === CONFIGURATION (mirrors HYPOTHESIS_02.md; corpus matches script_01) ===
SCRIPT_NAME = "script_02_train_nano_mlm"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIG_DIR = PROJECT_ROOT / "results" / "figures"

SEED = 1024
ALPHABET = "ACDEFGHIKLMNPQRSTVWY"   # 20 standard amino acids
N_SEQ = 2000
SEQ_LEN = 50
MASK_RATE = 0.15

# Conserved motif: G-x-G-x-x-G at cols 22..27; invariant G cols = {22,24,27}.
MOTIF_START = 22
MOTIF = "GxGxxG"
INVARIANT_COLS = [MOTIF_START + i for i, c in enumerate(MOTIF) if c == "G"]
VARIABLE_MOTIF_COLS = [MOTIF_START + i for i, c in enumerate(MOTIF) if c == "x"]
BACKGROUND_COLS = [c for c in range(SEQ_LEN) if c not in INVARIANT_COLS]

AA_TO_IDX = {aa: i for i, aa in enumerate(ALPHABET)}
GLY_IDX = AA_TO_IDX["G"]

# Vocabulary: 20 AA + special tokens.
PAD_ID = len(ALPHABET)       # 20
MASK_ID = len(ALPHABET) + 1  # 21
VOCAB_SIZE = len(ALPHABET) + 2

# Model / training hyperparameters.
D_MODEL = 64
N_HEAD = 4
N_LAYERS = 2
FF_DIM = 128
LR = 1e-3
EPOCHS = 30
BATCH_SIZE = 128
VAL_FRAC = 0.2
BASELINE_ACC = 0.1076  # from ANALYSIS_01.md (unigram-frequency baseline)


def generate_corpus(rng):
    """Same generator as script_01: uniform background + planted invariant G cols."""
    corpus = rng.integers(0, len(ALPHABET), size=(N_SEQ, SEQ_LEN), dtype=np.int64)
    for col in INVARIANT_COLS:
        corpus[:, col] = GLY_IDX
    return corpus


class NanoMLM(nn.Module):
    """Tiny transformer encoder for masked residue prediction."""

    def __init__(self):
        super().__init__()
        self.tok_emb = nn.Embedding(VOCAB_SIZE, D_MODEL, padding_idx=PAD_ID)
        self.pos_emb = nn.Embedding(SEQ_LEN, D_MODEL)
        layer = nn.TransformerEncoderLayer(
            d_model=D_MODEL, nhead=N_HEAD, dim_feedforward=FF_DIM,
            batch_first=True, dropout=0.0,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=N_LAYERS)
        self.head = nn.Linear(D_MODEL, VOCAB_SIZE)
        self.register_buffer("positions", torch.arange(SEQ_LEN).unsqueeze(0))

    def forward(self, x):
        h = self.tok_emb(x) + self.pos_emb(self.positions)
        h = self.encoder(h)
        return self.head(h)


def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    with TeeLogger(log_path):
        print(f"{'='*60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("Hypothesis: HYPOTHESIS_02.md (H_02A beat baseline, H_02B motif, H_02C curve)")
        print(f"Baseline to beat (unigram): {BASELINE_ACC}")
        print(f"{'='*60}\n")

        torch.manual_seed(SEED)
        np.random.seed(SEED)
        rng = np.random.default_rng(SEED)

        # --- Data ---
        corpus = generate_corpus(rng)
        data = torch.from_numpy(corpus).long()
        n_val = int(N_SEQ * VAL_FRAC)
        perm = torch.randperm(N_SEQ, generator=torch.Generator().manual_seed(SEED))
        val_idx, train_idx = perm[:n_val], perm[n_val:]
        train_data, val_data = data[train_idx], data[val_idx]
        print(f"[DATA] train={train_data.shape[0]} val={val_data.shape[0]} "
              f"seq_len={SEQ_LEN} vocab={VOCAB_SIZE}\n")

        model = NanoMLM()
        n_params = sum(p.numel() for p in model.parameters())
        print(f"[MODEL] NanoMLM params={n_params:,} "
              f"(d_model={D_MODEL}, heads={N_HEAD}, layers={N_LAYERS}, ff={FF_DIM})\n")

        train_and_evaluate(model, train_data, val_data)

        print(f"\n{'='*60}")
        print("=== COMPLETE ===")
        print(f"{'='*60}")


def apply_masking(batch, gen):
    """Dynamic 15% masking. Returns (inputs, targets, mask) where unmasked targets = -100."""
    mask = torch.rand(batch.shape, generator=gen) < MASK_RATE
    inputs = batch.clone()
    inputs[mask] = MASK_ID
    targets = batch.clone()
    targets[~mask] = -100  # ignore_index for cross-entropy
    return inputs, targets, mask


def evaluate(model, data, gen):
    """Return (mean masked loss, overall masked acc, per-column acc dict)."""
    model.eval()
    loss_fn = nn.CrossEntropyLoss(ignore_index=-100)
    inputs, targets, mask = apply_masking(data, gen)
    with torch.no_grad():
        logits = model(inputs)
        loss = loss_fn(logits.reshape(-1, VOCAB_SIZE), targets.reshape(-1))
        preds = logits.argmax(dim=-1)
    correct = (preds == data) & mask
    overall_acc = correct.sum().item() / max(mask.sum().item(), 1)
    # Per-column accuracy over masked positions only.
    col_acc = {}
    for col in range(SEQ_LEN):
        m = mask[:, col]
        denom = m.sum().item()
        col_acc[col] = (correct[:, col].sum().item() / denom) if denom > 0 else float("nan")
    return float(loss.item()), overall_acc, col_acc


def train_and_evaluate(model, train_data, val_data):
    """Train the nano-MLM, evaluate against baseline and motif targets, plot curves."""
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    loss_fn = nn.CrossEntropyLoss(ignore_index=-100)
    train_gen = torch.Generator().manual_seed(SEED + 7)
    eval_gen_seed = SEED + 99

    n_train = train_data.shape[0]
    history = {"epoch": [], "train_loss": [], "val_loss": [], "val_acc": []}

    print("[TRAIN] epoch | train_loss | val_loss | val_masked_acc")
    for epoch in range(1, EPOCHS + 1):
        model.train()
        order = torch.randperm(n_train, generator=train_gen)
        epoch_loss, n_batches = 0.0, 0
        for start in range(0, n_train, BATCH_SIZE):
            batch = train_data[order[start:start + BATCH_SIZE]]
            inputs, targets, _ = apply_masking(batch, train_gen)
            logits = model(inputs)
            loss = loss_fn(logits.reshape(-1, VOCAB_SIZE), targets.reshape(-1))
            opt.zero_grad()
            loss.backward()
            opt.step()
            epoch_loss += loss.item()
            n_batches += 1
        train_loss = epoch_loss / max(n_batches, 1)

        # Fixed-seed eval masking so val numbers are comparable across epochs.
        val_loss, val_acc, _ = evaluate(model, val_data,
                                        torch.Generator().manual_seed(eval_gen_seed))
        history["epoch"].append(epoch)
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)
        if epoch == 1 or epoch % 5 == 0 or epoch == EPOCHS:
            print(f"        {epoch:>5} | {train_loss:>10.4f} | {val_loss:>8.4f} | {val_acc:>13.4f}")

    # --- Final detailed evaluation ---
    final_loss, final_acc, col_acc = evaluate(
        model, val_data, torch.Generator().manual_seed(eval_gen_seed))
    motif_accs = [col_acc[c] for c in INVARIANT_COLS]
    bg_accs = [col_acc[c] for c in BACKGROUND_COLS if not np.isnan(col_acc[c])]
    motif_mean = float(np.mean(motif_accs))
    bg_mean = float(np.mean(bg_accs))

    print(f"\n[FINAL EVAL on held-out val]")
    print(f"  overall masked accuracy = {final_acc:.4f}  (baseline {BASELINE_ACC})")
    print(f"  motif G-column accuracy : {[f'{a:.3f}' for a in motif_accs]} "
          f"(cols {INVARIANT_COLS}) mean={motif_mean:.4f}")
    print(f"  background-column mean   = {bg_mean:.4f}")
    print(f"  variable x-cols {VARIABLE_MOTIF_COLS}: "
          f"{[f'{col_acc[c]:.3f}' for c in VARIABLE_MOTIF_COLS]}\n")

    # --- Hypothesis checks ---
    h02a = final_acc > BASELINE_ACC and final_acc >= 0.15
    h02b = motif_mean >= 0.95 and bg_mean <= 0.15
    h02c = history["val_loss"][-1] < history["val_loss"][0]
    print("[HYPOTHESIS CHECKS]")
    print(f"  H_02A beat baseline (acc>{BASELINE_ACC} and >=0.15): "
          f"{'PASS' if h02a else 'FAIL'} ({final_acc:.4f})")
    print(f"  H_02B reconstruct motif (motif>=0.95, bg<=0.15): "
          f"{'PASS' if h02b else 'FAIL'} (motif={motif_mean:.4f}, bg={bg_mean:.4f})")
    print(f"  H_02C healthy curve (val_loss decreased): "
          f"{'PASS' if h02c else 'FAIL'} "
          f"({history['val_loss'][0]:.3f} -> {history['val_loss'][-1]:.3f})")
    all_pass = h02a and h02b and h02c
    print(f"\n{'='*60}")
    print(f"VERDICT: {'ALL CHECKS PASSED' if all_pass else 'CHECKS FAILED'}")
    print(f"  Nano-MLM {'learned the planted grammar.' if all_pass else 'did NOT meet criteria.'}")
    print(f"{'='*60}")

    save_figures(history, col_acc)


def save_figures(history, col_acc):
    """Loss curve + per-column masked accuracy bar chart (300 DPI)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Figure 1: train/val loss curve.
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(history["epoch"], history["train_loss"], label="train loss")
    ax.plot(history["epoch"], history["val_loss"], label="val loss")
    ax.set_xlabel("epoch")
    ax.set_ylabel("masked cross-entropy")
    ax.set_title("Nano-MLM training curve")
    ax.legend()
    fig.tight_layout()
    f1 = FIG_DIR / "script_02_loss_curve.png"
    fig.savefig(str(f1), dpi=300)
    plt.close(fig)
    print(f"[FIGURE] saved {f1.relative_to(PROJECT_ROOT)}")

    # Figure 2: per-column masked accuracy (motif cols highlighted).
    fig, ax = plt.subplots(figsize=(10, 3.5))
    cols = list(range(SEQ_LEN))
    accs = [col_acc[c] for c in cols]
    colors = ["tab:red" if c in INVARIANT_COLS else
              ("tab:orange" if c in VARIABLE_MOTIF_COLS else "tab:blue")
              for c in cols]
    ax.bar(cols, accs, color=colors)
    ax.axhline(BASELINE_ACC, color="gray", ls="--", lw=1,
               label=f"unigram baseline ({BASELINE_ACC})")
    ax.axhline(1.0 / len(ALPHABET), color="green", ls=":", lw=1,
               label="chance (1/20)")
    ax.set_xlabel("sequence column")
    ax.set_ylabel("masked accuracy")
    ax.set_title("Per-column masked accuracy "
                 "(red = invariant motif G, orange = variable x)")
    ax.legend()
    fig.tight_layout()
    f2 = FIG_DIR / "script_02_per_column_accuracy.png"
    fig.savefig(str(f2), dpi=300)
    plt.close(fig)
    print(f"[FIGURE] saved {f2.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
