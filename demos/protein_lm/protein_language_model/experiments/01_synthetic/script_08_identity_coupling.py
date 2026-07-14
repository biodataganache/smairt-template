#!/usr/bin/env python3
"""
Script 08: Identity-copy coupling — the airtight AND learnable family-separation test.

Hypothesis: HYPOTHESIS_08.md (H_08A trained AUC, H_08B controls at chance, H_08C copy)
Phase: synthetic
Iteration: 8

Purpose:
  iter 05 (position) had a confounded control; iter 06 (single pair) had a signal
  too sparse to affect the loss; iter 07 (K=10 arbitrary permutation) made the
  signal loss-relevant and the model rose above controls, but the permutation was
  too hard to fully learn at nano budget (KNOWN_PATTERNS S2.4, S2.5). This iteration
  keeps the airtight property (every column marginal stays uniform => both controls
  at chance) but uses the simplest learnable mapping, an IDENTITY COPY, plus a
  modest budget bump (40 epochs):
    Family A (copy):        seq[b_k] = seq[a_k] for every pair k
    Family B (independent): all columns independent uniform
  Since seq[a_k] is uniform, seq[b_k] is uniform too -> marginals identical across
  families. A single copy-attention head can implement "copy your partner", so the
  trained model should learn it and separate the families while both controls stay
  at chance.

Depends on:
  - script_07_bijection_coupling.py (same model/embedding/probe); ANALYSIS_07.md
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

SCRIPT_NAME = "script_08_identity_coupling"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIG_DIR = PROJECT_ROOT / "results" / "figures"

SEED = 1024
ALPHABET = "ACDEFGHIKLMNPQRSTVWY"
N_PER_FAMILY = 1000
N_SEQ = 2 * N_PER_FAMILY
SEQ_LEN = 50
MASK_RATE = 0.15
K_PAIRS = 10

PAD_ID = len(ALPHABET)
MASK_ID = len(ALPHABET) + 1
VOCAB_SIZE = len(ALPHABET) + 2

D_MODEL, N_HEAD, N_LAYERS, FF_DIM = 64, 4, 2, 128
LR, EPOCHS, BATCH_SIZE, VAL_FRAC = 1e-3, 40, 128, 0.2

# Fixed coupling layout (seeded once, reused everywhere).
_layout_rng = np.random.default_rng(SEED + 555)
_cols = _layout_rng.permutation(SEQ_LEN)[:2 * K_PAIRS]
PAIRS = [(int(_cols[2 * k]), int(_cols[2 * k + 1])) for k in range(K_PAIRS)]
A_COLS = [a for a, _ in PAIRS]
B_COLS = [b for _, b in PAIRS]


def generate_bijection_corpus(rng):
    """Uniform background. Family A: for each pair (a,b), seq[b]=seq[a] (identity
    copy). Family B: all independent uniform. seq[a] uniform => seq[b] uniform, so
    every column marginal is uniform in BOTH families."""
    corpus = rng.integers(0, len(ALPHABET), size=(N_SEQ, SEQ_LEN), dtype=np.int64)
    labels = np.zeros(N_SEQ, dtype=np.int64)
    labels[N_PER_FAMILY:] = 1  # 0 = Family A (copy), 1 = Family B (independent)
    for a, b in PAIRS:
        corpus[:N_PER_FAMILY, b] = corpus[:N_PER_FAMILY, a]
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
    model.eval()
    with torch.no_grad():
        emb = model.encode(data).mean(dim=1)
    return emb.cpu().numpy()


def composition_vectors(corpus):
    counts = np.zeros((corpus.shape[0], len(ALPHABET)), dtype=np.float64)
    for a in range(len(ALPHABET)):
        counts[:, a] = (corpus == a).sum(axis=1)
    return counts


def _standardize(x_train, x_val):
    mu = x_train.mean(axis=0, keepdims=True)
    sd = x_train.std(axis=0, keepdims=True) + 1e-8
    return (x_train - mu) / sd, (x_val - mu) / sd


def roc_auc(y_true, scores):
    """AUC via the Mann-Whitney U statistic (rank-based, handles ties)."""
    y_true = np.asarray(y_true)
    scores = np.asarray(scores, dtype=np.float64)
    order = np.argsort(scores)
    ranks = np.empty(len(scores), dtype=np.float64)
    ranks[order] = np.arange(1, len(scores) + 1)
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


def logistic_regression_auc(x_train, y_train, x_val, y_val, epochs=300, lr=0.1):
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
    return roc_auc(y_val, x_val @ w + b)


def coupled_col_accuracy(model, corpus, labels):
    """Mask ONLY the b columns (leave a visible) and measure mean accuracy at the
    b columns per family. Family A should be high (model copies a->b); Family B
    near chance."""
    data = torch.from_numpy(corpus).long()
    inputs = data.clone()
    for b in B_COLS:
        inputs[:, b] = MASK_ID
    model.eval()
    with torch.no_grad():
        preds = model(inputs).argmax(dim=-1)
    out = {}
    for fam in (0, 1):
        sel = labels == fam
        acc = [(preds[sel][:, b] == data[sel][:, b]).float().mean().item()
               for b in B_COLS]
        out[fam] = float(np.mean(acc))
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
    corpus, labels = generate_bijection_corpus(rng)
    data = torch.from_numpy(corpus).long()

    # Sanity: every coupled column's marginal should be ~uniform in BOTH families,
    # and Family A must satisfy seq[b]=seq[a] exactly.
    max_marg_dev = 0.0
    for fam in (0, 1):
        sel = labels == fam
        for c in A_COLS + B_COLS:
            p = np.bincount(corpus[sel, c], minlength=len(ALPHABET)) / sel.sum()
            max_marg_dev = max(max_marg_dev, abs(p - 1 / len(ALPHABET)).max())
    selA = labels == 0
    ruleA = np.mean([(corpus[selA, b] == corpus[selA, a]).mean()
                     for a, b in PAIRS])
    selB = labels == 1
    ruleB = np.mean([(corpus[selB, b] == corpus[selB, a]).mean()
                     for a, b in PAIRS])
    print(f"[DATA]   N={N_SEQ} ({N_PER_FAMILY}/family); K={K_PAIRS} pairs; "
          f"max|marginal-1/20| over coupled cols = {max_marg_dev:.3f}")
    print(f"[DATA]   rule satisfaction seq[b]=seq[a]: FamA={ruleA:.3f} "
          f"FamB={ruleB:.3f} (FamB~1/20=0.05 expected)\n")

    n_val = int(N_SEQ * VAL_FRAC)
    perm = torch.randperm(N_SEQ, generator=torch.Generator().manual_seed(SEED))
    val_idx, train_idx = perm[:n_val], perm[n_val:]
    train_data, val_data = data[train_idx], data[val_idx]
    y_train = labels[train_idx.numpy()]
    y_val = labels[val_idx.numpy()]

    print("[TRAIN]  training nano-MLM (masked-residue objective only)...")
    torch.manual_seed(SEED)
    model = train_model(train_data)
    torch.manual_seed(SEED + 1)
    untrained = NanoMLM()

    emb_tr_train = mean_pool_embeddings(model, train_data)
    emb_tr_val = mean_pool_embeddings(model, val_data)
    emb_un_train = mean_pool_embeddings(untrained, train_data)
    emb_un_val = mean_pool_embeddings(untrained, val_data)
    comp_train = composition_vectors(corpus[train_idx.numpy()])
    comp_val = composition_vectors(corpus[val_idx.numpy()])

    auc_tr = logistic_regression_auc(emb_tr_train, y_train, emb_tr_val, y_val)
    auc_un = logistic_regression_auc(emb_un_train, y_train, emb_un_val, y_val)
    auc_co = logistic_regression_auc(comp_train, y_train, comp_val, y_val)

    cacc = coupled_col_accuracy(model, corpus[val_idx.numpy()], y_val)

    print(f"\n[EMBED]  linear-probe AUC (Family A vs B), held-out val split:")
    print(f"           trained model : {auc_tr:.4f}")
    print(f"           untrained ctrl: {auc_un:.4f}   (must be ~0.5)")
    print(f"           composition   : {auc_co:.4f}   (must be ~0.5)")
    print(f"[MECH]   mean masked acc at b-cols (a visible): "
          f"FamA(coupled)={cacc[0]:.4f}  FamB(indep)={cacc[1]:.4f}  "
          f"(chance=1/20={1/len(ALPHABET):.3f})")

    h08a = auc_tr >= 0.90
    h08b = (auc_un <= 0.60 and auc_co <= 0.60)
    h08c = (cacc[0] >= 0.80 and cacc[1] <= 0.15 and (cacc[0] - cacc[1]) >= 0.50)

    print(f"\n[HYPOTHESIS CHECKS]")
    print(f"  H_08A trained AUC>=0.90        : {'PASS' if h08a else 'FAIL'} (AUC={auc_tr:.4f})")
    print(f"  H_08B controls at chance<=0.60 : {'PASS' if h08b else 'FAIL'} "
          f"(untrained={auc_un:.3f} comp={auc_co:.3f})")
    print(f"  H_08C copy rule learned        : {'PASS' if h08c else 'FAIL'} "
          f"(FamA b-acc={cacc[0]:.3f} FamB b-acc={cacc[1]:.3f})")
    all_pass = h08a and h08b and h08c
    print(f"\n{'='*60}")
    print(f"VERDICT: {'ALL CHECKS PASSED' if all_pass else 'CHECKS FAILED'}")
    if all_pass:
        print("  Airtight + learnable: both controls at chance, only the trained")
        print("  model separates, and it does so by LEARNING the copy rule (seq[b]=seq[a]).")
        print("  This closes the synthetic ladder's embedding claim.")
    else:
        print("  Did not fully isolate learned separation; inspect checks above.")
    print(f"{'='*60}")

    metrics = {"auc": {"trained": auc_tr, "untrained": auc_un, "composition": auc_co},
               "cacc": cacc}
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
        for fam, color, name in [(0, "tab:red", "Family A (copy seq[b]=seq[a])"),
                                 (1, "tab:blue", "Family B (independent)")]:
            sel = labels == fam
            ax.scatter(pts[sel, 0], pts[sel, 1], s=10, alpha=0.6,
                       color=color, label=name)
        ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
        ax.set_title(title); ax.legend(loc="best", fontsize=8)
    fig.suptitle("Bijection-coupling families (val): only learning separates them")
    fig.tight_layout()
    f1 = FIG_DIR / "script_08_embedding_pca.png"
    fig.savefig(str(f1), dpi=300)
    plt.close(fig)
    print(f"[FIGURE] saved {f1.relative_to(PROJECT_ROOT)}")

    groups = ["trained", "untrained", "composition"]
    x = np.arange(len(groups))
    fig2, ax = plt.subplots(figsize=(7, 5))
    ax.bar(x, [metrics["auc"][g] for g in groups], 0.55, color="tab:purple")
    ax.axhline(0.5, color="gray", ls="--", lw=1, label="AUC chance (0.5)")
    ax.set_xticks(x); ax.set_xticklabels(groups)
    ax.set_ylim(0, 1.05); ax.set_ylabel("linear-probe AUC")
    ax.set_title("Family separability: only the trained model rises above chance")
    ax.legend()
    fig2.tight_layout()
    f2 = FIG_DIR / "script_08_auc_vs_controls.png"
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
        print("Hypothesis: HYPOTHESIS_08.md (identity-copy coupling)")
        print(f"K={K_PAIRS} pairs; Family A: seq[b]=seq[a]; Family B independent")
        print(f"Pairs (a->b): {PAIRS}")
        print(f"{'='*60}\n")

        run_experiment()

        print(f"\n{'='*60}")
        print("=== COMPLETE ===")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()


# =============================================================================
# PASTED OUTPUT (run 2026-06-29, seed 1024, torch 2.12.1 CPU, EPOCHS=40)
# -----------------------------------------------------------------------------
# Pairs (a->b): [(11,46),(39,42),(31,0),(36,10),(20,41),(37,45),(29,13),(32,16),(22,12),(35,5)]
# [DATA]  K=10 pairs; max|marginal-1/20| over coupled cols=0.022
# [DATA]  rule satisfaction seq[b]=seq[a]: FamA=1.000 FamB=0.051
# [EMBED] linear-probe AUC (val): trained=1.0000  untrained=0.5157  composition=0.5108
# [MECH]  mean masked acc at b-cols (a visible): FamA=1.0000  FamB=0.0495 (chance 0.050)
#   H_08A trained AUC>=0.90        : PASS (1.0000)
#   H_08B controls at chance<=0.60 : PASS (untrained=0.516 comp=0.511)
#   H_08C copy rule learned        : PASS (FamA b-acc=1.000 FamB b-acc=0.049)
#   VERDICT: ALL CHECKS PASSED
#
# INTERPRETATION (see ANALYSIS_08.md):
#   - This is the airtight AND learnable demonstration of the embedding claim.
#   - Both controls at chance (untrained 0.516, composition 0.511): every column's
#     marginal is uniform in both families, so neither position nor composition can
#     separate them. ONLY a model that LEARNED the copy rule can.
#   - Trained AUC=1.000 and FamA coupled-col accuracy=1.000 (FamB at chance 0.049):
#     the model perfectly learned "seq[b]=seq[a]" via attention and its mean-pooled
#     embeddings perfectly separate the families.
#   - Closes the synthetic ladder (Rung 1 + Rung 2). Resolves the iter-05 confound
#     (position free), iter-06 sparsity (signal too small), iter-07 complexity
#     (permutation too hard). Natural launch point for Rung 3 (real ESM-2).
# =============================================================================
