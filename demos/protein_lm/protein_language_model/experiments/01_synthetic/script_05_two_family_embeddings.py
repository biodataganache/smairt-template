#!/usr/bin/env python3
"""
Script 05: Two-family embedding separation (Rung 2 headline).

Hypothesis: HYPOTHESIS_05.md (H_05A AUC, H_05B silhouette, H_05C controls, H_05D MLM)
Phase: synthetic
Iteration: 5

Purpose:
  Plant the SAME motif `GKTYRG` in two families that differ ONLY by motif
  POSITION (Family A at cols 22-27, Family B at cols 10-15) on an identical
  uniform background. Per-sequence composition is therefore identical between
  families, so any separation must be learned positional grammar (not a
  bag-of-residues shortcut; see KNOWN_PATTERNS.md S2.2). Train one nano-MLM with
  the masked-residue objective ONLY (family labels never shown), mean-pool the
  encoder output to a 64-d per-sequence embedding, and test whether a linear
  probe separates the families. Controls: untrained random-init model embeddings
  and raw residue-composition vectors must stay at chance.

Depends on:
  - script_04_conservation_sweep.py (same model/training/eval); ANALYSIS_04.md
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

SCRIPT_NAME = "script_05_two_family_embeddings"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIG_DIR = PROJECT_ROOT / "results" / "figures"

SEED = 1024
ALPHABET = "ACDEFGHIKLMNPQRSTVWY"
N_PER_FAMILY = 1000
N_SEQ = 2 * N_PER_FAMILY
SEQ_LEN = 50
MASK_RATE = 0.15

MOTIF = "GKTYRG"
FAMILY_A_START = 22
FAMILY_B_START = 10
AA_TO_IDX = {aa: i for i, aa in enumerate(ALPHABET)}

A_COLS = list(range(FAMILY_A_START, FAMILY_A_START + len(MOTIF)))
B_COLS = list(range(FAMILY_B_START, FAMILY_B_START + len(MOTIF)))
A_RESIDUES = {FAMILY_A_START + i: AA_TO_IDX[c] for i, c in enumerate(MOTIF)}
B_RESIDUES = {FAMILY_B_START + i: AA_TO_IDX[c] for i, c in enumerate(MOTIF)}

PAD_ID = len(ALPHABET)
MASK_ID = len(ALPHABET) + 1
VOCAB_SIZE = len(ALPHABET) + 2

D_MODEL, N_HEAD, N_LAYERS, FF_DIM = 64, 4, 2, 128
LR, EPOCHS, BATCH_SIZE, VAL_FRAC = 1e-3, 30, 128, 0.2


def generate_two_family_corpus(rng):
    """Half the sequences are Family A (motif at A_COLS), half Family B (motif at
    B_COLS). Background is uniform for all positions; family identity is encoded
    ONLY by where the (identical) motif sits. Returns (corpus, labels)."""
    corpus = rng.integers(0, len(ALPHABET), size=(N_SEQ, SEQ_LEN), dtype=np.int64)
    labels = np.zeros(N_SEQ, dtype=np.int64)
    labels[N_PER_FAMILY:] = 1  # 0 = Family A, 1 = Family B
    for col, res in A_RESIDUES.items():
        corpus[:N_PER_FAMILY, col] = res
    for col, res in B_RESIDUES.items():
        corpus[N_PER_FAMILY:, col] = res
    # shuffle so train/val split mixes families
    order = rng.permutation(N_SEQ)
    return corpus[order], labels[order]


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

    def encode(self, x):
        """Return per-residue contextual embeddings (B, L, D)."""
        h = self.tok_emb(x) + self.pos_emb(self.positions)
        return self.encoder(h)

    def forward(self, x):
        return self.head(self.encode(x))


def apply_masking(batch, gen):
    mask = torch.rand(batch.shape, generator=gen) < MASK_RATE
    inputs = batch.clone()
    inputs[mask] = MASK_ID
    targets = batch.clone()
    targets[~mask] = -100
    return inputs, targets, mask


def mean_pool_embeddings(model, data):
    """Mean-pool the encoder output over positions -> (N, D_MODEL) numpy array.
    No masking applied here: we embed the full (unmasked) sequence."""
    model.eval()
    with torch.no_grad():
        emb = model.encode(data).mean(dim=1)  # (N, D)
    return emb.cpu().numpy()


def composition_vectors(corpus):
    """Per-sequence residue-count vector (N, 20). The strongest composition
    baseline; identical in expectation across families by construction."""
    counts = np.zeros((corpus.shape[0], len(ALPHABET)), dtype=np.float64)
    for a in range(len(ALPHABET)):
        counts[:, a] = (corpus == a).sum(axis=1)
    return counts


def _standardize(x_train, x_val):
    mu = x_train.mean(axis=0, keepdims=True)
    sd = x_train.std(axis=0, keepdims=True) + 1e-8
    return (x_train - mu) / sd, (x_val - mu) / sd


def logistic_regression_auc(x_train, y_train, x_val, y_val, epochs=300, lr=0.1):
    """Train a linear logistic-regression probe by gradient descent (numpy) and
    return val-split AUC. Features standardized on the train split."""
    x_train, x_val = _standardize(x_train, x_val)
    n, d = x_train.shape
    w = np.zeros(d)
    b = 0.0
    for _ in range(epochs):
        z = x_train @ w + b
        p = 1.0 / (1.0 + np.exp(-z))
        grad_w = x_train.T @ (p - y_train) / n + 1e-3 * w
        grad_b = float(np.mean(p - y_train))
        w -= lr * grad_w
        b -= lr * grad_b
    scores = x_val @ w + b
    return roc_auc(y_val, scores)


def roc_auc(y_true, scores):
    """AUC via the Mann-Whitney U statistic (rank-based, handles ties)."""
    y_true = np.asarray(y_true)
    order = np.argsort(scores)
    ranks = np.empty(len(scores), dtype=np.float64)
    ranks[order] = np.arange(1, len(scores) + 1)
    # average ranks for ties
    s_sorted = scores[order]
    i = 0
    while i < len(s_sorted):
        j = i
        while j + 1 < len(s_sorted) and s_sorted[j + 1] == s_sorted[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = (i + 1 + j + 1) / 2.0
        i = j + 1
    n_pos = float(np.sum(y_true == 1))
    n_neg = float(np.sum(y_true == 0))
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    sum_ranks_pos = ranks[y_true == 1].sum()
    return (sum_ranks_pos - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)


def silhouette_score(x, labels):
    """Mean silhouette over points for 2 clusters (euclidean). O(n^2) — fine for
    n=400 val points."""
    labels = np.asarray(labels)
    d = np.sqrt(((x[:, None, :] - x[None, :, :]) ** 2).sum(axis=2))
    sil = np.zeros(len(x))
    for i in range(len(x)):
        same = labels == labels[i]
        same[i] = False
        other = labels != labels[i]
        a = d[i, same].mean() if same.any() else 0.0
        b = d[i, other].mean() if other.any() else 0.0
        sil[i] = (b - a) / max(a, b) if max(a, b) > 0 else 0.0
    return float(sil.mean())


def motif_accuracy_by_family(model, data, labels, gen):
    """Masked-residue accuracy on each family's motif columns and on background."""
    model.eval()
    inputs, targets, mask = apply_masking(data, gen)
    with torch.no_grad():
        preds = model(inputs).argmax(dim=-1)
    correct = (preds == data) & mask
    out = {}
    for fam, cols in [(0, A_COLS), (1, B_COLS)]:
        sel = labels == fam
        cm = mask[sel][:, cols]
        cc = correct[sel][:, cols]
        denom = cm.sum().item()
        out[("motif", fam)] = (cc.sum().item() / denom) if denom else float("nan")
    # background = columns that are NOT a motif column for EITHER family
    bg_cols = [c for c in range(SEQ_LEN) if c not in A_COLS and c not in B_COLS]
    bm = mask[:, bg_cols]
    bc = correct[:, bg_cols]
    denom = bm.sum().item()
    out["background"] = (bc.sum().item() / denom) if denom else float("nan")
    return out


def train_model(train_data):
    model = NanoMLM()
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    loss_fn = nn.CrossEntropyLoss(ignore_index=-100)
    gen = torch.Generator().manual_seed(SEED + 7)
    n_train = train_data.shape[0]
    for _ in range(EPOCHS):
        model.train()
        order = torch.randperm(n_train, generator=gen)
        for start in range(0, n_train, BATCH_SIZE):
            batch = train_data[order[start:start + BATCH_SIZE]]
            inputs, targets, _ = apply_masking(batch, gen)
            logits = model(inputs)
            loss = loss_fn(logits.reshape(-1, VOCAB_SIZE), targets.reshape(-1))
            opt.zero_grad(); loss.backward(); opt.step()
    return model


def run_experiment():
    rng = np.random.default_rng(SEED)
    corpus, labels = generate_two_family_corpus(rng)
    data = torch.from_numpy(corpus).long()

    # Deterministic train/val split (model never sees labels during training).
    n_val = int(N_SEQ * VAL_FRAC)
    perm = torch.randperm(N_SEQ, generator=torch.Generator().manual_seed(SEED))
    val_idx, train_idx = perm[:n_val], perm[n_val:]
    train_data, val_data = data[train_idx], data[val_idx]
    y_train = labels[train_idx.numpy()]
    y_val = labels[val_idx.numpy()]

    print(f"[DATA]   N={N_SEQ} ({N_PER_FAMILY}/family), L={SEQ_LEN}; "
          f"train={len(train_idx)} val={len(val_idx)}")
    print(f"[DATA]   composition is identical across families by construction "
          f"(same motif residues, uniform background).\n")

    # --- Trained model ---
    print("[TRAIN]  training nano-MLM (masked-residue objective only)...")
    torch.manual_seed(SEED)
    model = train_model(train_data)

    # --- Untrained control (same architecture, random init) ---
    torch.manual_seed(SEED + 1)
    untrained = NanoMLM()

    # --- Embeddings ---
    emb_tr_train = mean_pool_embeddings(model, train_data)
    emb_tr_val = mean_pool_embeddings(model, val_data)
    emb_un_train = mean_pool_embeddings(untrained, train_data)
    emb_un_val = mean_pool_embeddings(untrained, val_data)
    comp_train = composition_vectors(corpus[train_idx.numpy()])
    comp_val = composition_vectors(corpus[val_idx.numpy()])

    # --- Probes (AUC) ---
    auc_tr = logistic_regression_auc(emb_tr_train, y_train, emb_tr_val, y_val)
    auc_un = logistic_regression_auc(emb_un_train, y_train, emb_un_val, y_val)
    auc_co = logistic_regression_auc(comp_train, y_train, comp_val, y_val)

    # --- Silhouettes (val split) ---
    sil_tr = silhouette_score(emb_tr_val, y_val)
    sil_un = silhouette_score(emb_un_val, y_val)
    sil_co = silhouette_score(_standardize(comp_train, comp_val)[1], y_val)

    # --- MLM sanity (H_05D) ---
    macc = motif_accuracy_by_family(
        model, val_data, y_val, torch.Generator().manual_seed(SEED + 99))

    print(f"\n[EMBED]  linear-probe AUC (family A vs B), held-out val split:")
    print(f"           trained model : {auc_tr:.4f}")
    print(f"           untrained ctrl: {auc_un:.4f}")
    print(f"           composition   : {auc_co:.4f}")
    print(f"[EMBED]  silhouette score (val):")
    print(f"           trained model : {sil_tr:.4f}")
    print(f"           untrained ctrl: {sil_un:.4f}")
    print(f"           composition   : {sil_co:.4f}")
    print(f"[MLM]    masked motif accuracy: "
          f"FamA={macc[('motif',0)]:.4f} FamB={macc[('motif',1)]:.4f}; "
          f"background={macc['background']:.4f}")

    # --- Hypothesis checks ---
    h05a = auc_tr >= 0.95
    h05b = sil_tr >= 0.30
    h05c = (auc_un <= 0.65 and auc_co <= 0.65 and sil_un <= 0.10 and sil_co <= 0.10)
    h05d = (macc[("motif", 0)] >= 0.90 and macc[("motif", 1)] >= 0.90
            and macc["background"] <= 0.15)

    print(f"\n[HYPOTHESIS CHECKS]")
    print(f"  H_05A trained AUC>=0.95            : {'PASS' if h05a else 'FAIL'} (AUC={auc_tr:.4f})")
    print(f"  H_05B trained silhouette>=0.30     : {'PASS' if h05b else 'FAIL'} (sil={sil_tr:.4f})")
    print(f"  H_05C controls at chance           : {'PASS' if h05c else 'FAIL'} "
          f"(AUC un={auc_un:.3f} comp={auc_co:.3f}; sil un={sil_un:.3f} comp={sil_co:.3f})")
    print(f"  H_05D both-family motif MLM>=0.90  : {'PASS' if h05d else 'FAIL'} "
          f"(A={macc[('motif',0)]:.3f} B={macc[('motif',1)]:.3f} bg={macc['background']:.3f})")
    all_pass = h05a and h05b and h05c and h05d
    print(f"\n{'='*60}")
    print(f"VERDICT: {'ALL CHECKS PASSED' if all_pass else 'CHECKS FAILED'}")
    print(f"  {'Trained embeddings separate the families by learned POSITION; ' if all_pass else 'Separation did NOT behave as predicted; '}"
          f"{'composition control at chance confirms it is not a bag-of-residues shortcut.' if all_pass else 'inspect controls.'}")
    print(f"{'='*60}")

    metrics = {
        "auc": {"trained": auc_tr, "untrained": auc_un, "composition": auc_co},
        "sil": {"trained": sil_tr, "untrained": sil_un, "composition": sil_co},
    }
    save_figures(emb_tr_val, emb_un_val, y_val, metrics)


def _pca_2d(x):
    xc = x - x.mean(axis=0, keepdims=True)
    u, s, vt = np.linalg.svd(xc, full_matrices=False)
    return xc @ vt[:2].T


def save_figures(emb_tr, emb_un, labels, metrics):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = np.asarray(labels)
    pca_tr = _pca_2d(emb_tr)
    pca_un = _pca_2d(emb_un)

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    for ax, pts, title in [(axes[0], pca_tr, "Trained model embeddings"),
                           (axes[1], pca_un, "Untrained (random-init) control")]:
        for fam, color, name in [(0, "tab:red", "Family A (cols 22-27)"),
                                 (1, "tab:blue", "Family B (cols 10-15)")]:
            sel = labels == fam
            ax.scatter(pts[sel, 0], pts[sel, 1], s=10, alpha=0.6,
                       color=color, label=name)
        ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
        ax.set_title(title); ax.legend(loc="best", fontsize=8)
    fig.suptitle("Mean-pooled per-sequence embeddings, PCA (val split)")
    fig.tight_layout()
    f1 = FIG_DIR / "script_05_embedding_pca.png"
    fig.savefig(str(f1), dpi=300)
    plt.close(fig)
    print(f"[FIGURE] saved {f1.relative_to(PROJECT_ROOT)}")

    groups = ["trained", "untrained", "composition"]
    x = np.arange(len(groups))
    fig2, ax = plt.subplots(figsize=(7, 5))
    ax.bar(x - 0.18, [metrics["auc"][g] for g in groups], 0.36, label="probe AUC", color="tab:purple")
    ax.bar(x + 0.18, [metrics["sil"][g] for g in groups], 0.36, label="silhouette", color="tab:orange")
    ax.axhline(0.5, color="gray", ls="--", lw=1, label="AUC chance (0.5)")
    ax.axhline(0.0, color="black", lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels(groups)
    ax.set_ylabel("score")
    ax.set_title("Family separability: trained vs controls")
    ax.legend()
    fig2.tight_layout()
    f2 = FIG_DIR / "script_05_separability_metrics.png"
    fig2.savefig(str(f2), dpi=300)
    plt.close(fig2)
    print(f"[FIGURE] saved {f2.relative_to(PROJECT_ROOT)}")


def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    with TeeLogger(log_path):
        print(f"{'='*60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("Hypothesis: HYPOTHESIS_05.md (two-family embedding separation)")
        print(f"Motif: {MOTIF}; Family A cols {A_COLS}; Family B cols {B_COLS}")
        print(f"{'='*60}\n")

        run_experiment()

        print(f"\n{'='*60}")
        print("=== COMPLETE ===")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()


# =============================================================================
# PASTED OUTPUT (run 2026-06-29, seed 1024, torch 2.12.1 CPU)
# -----------------------------------------------------------------------------
# [DATA]   N=2000 (1000/family), L=50; train=1600 val=400
# [DATA]   composition is identical across families by construction.
# [TRAIN]  training nano-MLM (masked-residue objective only)...
# [EMBED]  linear-probe AUC (family A vs B), held-out val split:
#            trained model : 0.9998
#            untrained ctrl: 0.9785
#            composition   : 0.4864
# [EMBED]  silhouette score (val):
#            trained model : 0.0575
#            untrained ctrl: 0.0040
#            composition   : -0.0010
# [MLM]    masked motif accuracy: FamA=1.0000 FamB=1.0000; background=0.0558
#
# [HYPOTHESIS CHECKS]
#   H_05A trained AUC>=0.95            : PASS (AUC=0.9998)
#   H_05B trained silhouette>=0.30     : FAIL (sil=0.0575)
#   H_05C controls at chance           : FAIL (untrained AUC=0.978; comp AUC=0.486)
#   H_05D both-family motif MLM>=0.90  : PASS (A=1.000 B=1.000 bg=0.056)
#   VERDICT: CHECKS FAILED
#
# INTERPRETATION (see ANALYSIS_05.md):
#   - Composition control AUC=0.486 -> separation is NOT a bag-of-residues
#     shortcut (the intended control worked perfectly).
#   - But the UNTRAINED random-init model also separates (0.978): motif POSITION
#     is trivially encoded by the fixed sinusoidal-like position embeddings, so a
#     position-only family difference does not require LEARNING. H_05C correctly
#     flagged that this design cannot isolate "learned grammar".
#   - silhouette<<AUC is the high-dim signature: classes are linearly separable
#     along one axis but Euclidean silhouette over 64 noisy dims understates it
#     (wrong metric for the claim).
#   => Iteration 06 must use a discriminator that is invisible to position
#      embeddings AND to composition: a PAIRWISE COVARIATION rule (two positions
#      correlated in Family A, independent/anti-correlated in Family B). Then the
#      untrained control should drop to chance and only the trained model can
#      capture the dependency via attention.
# =============================================================================
