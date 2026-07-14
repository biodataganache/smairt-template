#!/usr/bin/env python3
"""
Script 07: Many-pair bijection coupling — learnable, confound-free family separation.

Hypothesis: HYPOTHESIS_07.md (H_07A trained AUC, H_07B controls at chance, H_07C coupling)
Phase: synthetic
Iteration: 7

Purpose:
  Iteration 06 proved the DESIGN was confound-free (both controls at chance) but a
  SINGLE coupled pair did not move the masked-LM loss, so the trained model learned
  nothing (KNOWN_PATTERNS S2.4). Here we keep the airtight property (every column's
  marginal stays uniform => composition & untrained controls at chance) but make the
  rule materially loss-reducing by coupling K=10 disjoint column pairs through a
  fixed alphabet permutation PERM:
    Family A (coupled):     seq[b_k] = PERM[seq[a_k]] for every pair k
    Family B (independent): all columns independent uniform
  Because PERM is a bijection and seq[a_k] is uniform, seq[b_k] is uniform too, so
  marginals are identical across families. Learning PERM lets the model predict ~20
  of 50 columns from their partners -> strong, trainable signal. Only a model that
  LEARNED the rule can separate the families; both controls must stay at chance.

Depends on:
  - script_06_covariation_families.py (same model/embedding/probe); ANALYSIS_06.md
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

SCRIPT_NAME = "script_07_bijection_coupling"
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
LR, EPOCHS, BATCH_SIZE, VAL_FRAC = 1e-3, 30, 128, 0.2

# Fixed coupling layout + permutation (seeded once, reused everywhere).
_layout_rng = np.random.default_rng(SEED + 555)
_cols = _layout_rng.permutation(SEQ_LEN)[:2 * K_PAIRS]
PAIRS = [(int(_cols[2 * k]), int(_cols[2 * k + 1])) for k in range(K_PAIRS)]
A_COLS = [a for a, _ in PAIRS]
B_COLS = [b for _, b in PAIRS]
# Derangement permutation of the alphabet (no fixed points) for a clean rule.
_perm = _layout_rng.permutation(len(ALPHABET))
while np.any(_perm == np.arange(len(ALPHABET))):
    _perm = _layout_rng.permutation(len(ALPHABET))
PERM = _perm.astype(np.int64)


def generate_bijection_corpus(rng):
    """Uniform background. Family A: for each pair (a,b), seq[b]=PERM[seq[a]].
    Family B: all independent uniform. PERM bijection + uniform seq[a] => seq[b]
    uniform, so every column marginal is uniform in BOTH families."""
    corpus = rng.integers(0, len(ALPHABET), size=(N_SEQ, SEQ_LEN), dtype=np.int64)
    labels = np.zeros(N_SEQ, dtype=np.int64)
    labels[N_PER_FAMILY:] = 1  # 0 = Family A (coupled), 1 = Family B (independent)
    for a, b in PAIRS:
        corpus[:N_PER_FAMILY, b] = PERM[corpus[:N_PER_FAMILY, a]]
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
    b columns per family. Family A should be high (model applies PERM); Family B
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
    # and Family A must satisfy seq[b]=PERM[seq[a]] exactly.
    max_marg_dev = 0.0
    for fam in (0, 1):
        sel = labels == fam
        for c in A_COLS + B_COLS:
            p = np.bincount(corpus[sel, c], minlength=len(ALPHABET)) / sel.sum()
            max_marg_dev = max(max_marg_dev, abs(p - 1 / len(ALPHABET)).max())
    selA = labels == 0
    ruleA = np.mean([(corpus[selA, b] == PERM[corpus[selA, a]]).mean()
                     for a, b in PAIRS])
    selB = labels == 1
    ruleB = np.mean([(corpus[selB, b] == PERM[corpus[selB, a]]).mean()
                     for a, b in PAIRS])
    print(f"[DATA]   N={N_SEQ} ({N_PER_FAMILY}/family); K={K_PAIRS} pairs; "
          f"max|marginal-1/20| over coupled cols = {max_marg_dev:.3f}")
    print(f"[DATA]   rule satisfaction seq[b]=PERM[seq[a]]: FamA={ruleA:.3f} "
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

    h07a = auc_tr >= 0.90
    h07b = (auc_un <= 0.60 and auc_co <= 0.60)
    h07c = (cacc[0] >= 0.80 and cacc[1] <= 0.15 and (cacc[0] - cacc[1]) >= 0.50)

    print(f"\n[HYPOTHESIS CHECKS]")
    print(f"  H_07A trained AUC>=0.90        : {'PASS' if h07a else 'FAIL'} (AUC={auc_tr:.4f})")
    print(f"  H_07B controls at chance<=0.60 : {'PASS' if h07b else 'FAIL'} "
          f"(untrained={auc_un:.3f} comp={auc_co:.3f})")
    print(f"  H_07C coupling learned         : {'PASS' if h07c else 'FAIL'} "
          f"(FamA b-acc={cacc[0]:.3f} FamB b-acc={cacc[1]:.3f})")
    all_pass = h07a and h07b and h07c
    print(f"\n{'='*60}")
    print(f"VERDICT: {'ALL CHECKS PASSED' if all_pass else 'CHECKS FAILED'}")
    if all_pass:
        print("  Airtight + learnable: both controls at chance, only the trained")
        print("  model separates, and it does so by LEARNING the PERM coupling rule.")
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
        for fam, color, name in [(0, "tab:red", "Family A (coupled, PERM rule)"),
                                 (1, "tab:blue", "Family B (independent)")]:
            sel = labels == fam
            ax.scatter(pts[sel, 0], pts[sel, 1], s=10, alpha=0.6,
                       color=color, label=name)
        ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
        ax.set_title(title); ax.legend(loc="best", fontsize=8)
    fig.suptitle("Bijection-coupling families (val): only learning separates them")
    fig.tight_layout()
    f1 = FIG_DIR / "script_07_embedding_pca.png"
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
    f2 = FIG_DIR / "script_07_auc_vs_controls.png"
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
        print("Hypothesis: HYPOTHESIS_07.md (many-pair bijection coupling)")
        print(f"K={K_PAIRS} pairs; Family A: seq[b]=PERM[seq[a]]; Family B independent")
        print(f"Pairs (a->b): {PAIRS}")
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
# Pairs (a->b): [(11,46),(39,42),(31,0),(36,10),(20,41),(37,45),(29,13),(32,16),(22,12),(35,5)]
# [DATA]  K=10 pairs; max|marginal-1/20| over coupled cols=0.022
# [DATA]  rule satisfaction seq[b]=PERM[seq[a]]: FamA=1.000 FamB=0.054
# [EMBED] linear-probe AUC (val): trained=0.6044  untrained=0.5204  composition=0.5103
# [MECH]  mean masked acc at b-cols (a visible): FamA=0.1830  FamB=0.0535 (chance 0.050)
#   H_07A trained AUC>=0.90        : FAIL (0.6044)
#   H_07B controls at chance<=0.60 : PASS (untrained=0.520 comp=0.510)
#   H_07C coupling learned         : FAIL (FamA b-acc=0.183 FamB b-acc=0.054)
#   VERDICT: CHECKS FAILED
#
# INTERPRETATION (see ANALYSIS_07.md):
#   - PROGRESS over iter 06: the trained model is now ABOVE chance and ABOVE both
#     controls (FamA b-acc 0.183 vs chance 0.054; AUC 0.604 vs controls ~0.51).
#     The K=10 signal is loss-relevant, so the model STARTED learning the rule.
#   - But it did not finish: learning an ARBITRARY 20-symbol permutation routed
#     across 10 random column pairs is hard for a 2-layer/64-dim model in 30
#     epochs. The rule, not the design, is the bottleneck (controls still clean).
#   => Iteration 08: keep the airtight design (uniform marginals) but make the rule
#      easy to ROUTE and easy to MAP -- use an IDENTITY copy seq[b]=seq[a] (still
#      uniform marginals) so a single copy-attention head suffices, and give a bit
#      more budget (epochs/heads). Expect trained AUC high, controls at chance,
#      FamA b-acc near 1.0. New anti-pattern logged: KNOWN_PATTERNS S2.5.
# =============================================================================
