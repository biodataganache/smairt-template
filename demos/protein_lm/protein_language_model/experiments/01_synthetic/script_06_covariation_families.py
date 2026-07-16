#!/usr/bin/env python3
"""
Script 06: Covariation families — separation that ONLY learning can achieve.

Hypothesis: HYPOTHESIS_06.md (H_06A trained AUC, H_06B controls at chance, H_06C coupling)
Phase: synthetic
Iteration: 6

Purpose:
  Fix the iteration-05 design flaw (KNOWN_PATTERNS S2.3): there the families
  differed by motif POSITION, which the position embeddings encode for free, so an
  untrained model already separated them. Here the two families have IDENTICAL
  single-column marginals (uniform at every position) and differ ONLY in a pairwise
  COVARIATION between two fixed columns i and j:
    Family A (coupled):     seq[j] = seq[i]
    Family B (independent): seq[i], seq[j] drawn independently
  No composition, position, or single-position statistic can tell them apart; only
  the JOINT (i,j) distribution differs. A trained nano-MLM can route information
  from i to j via self-attention and learn the coupling; an untrained model and a
  composition baseline cannot -> both controls should be at chance, isolating
  LEARNING as the cause of any separation.

Depends on:
  - script_05_two_family_embeddings.py (same model/embedding/probe); ANALYSIS_05.md
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

SCRIPT_NAME = "script_06_covariation_families"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIG_DIR = PROJECT_ROOT / "results" / "figures"

SEED = 1024
ALPHABET = "ACDEFGHIKLMNPQRSTVWY"
N_PER_FAMILY = 1000
N_SEQ = 2 * N_PER_FAMILY
SEQ_LEN = 50
MASK_RATE = 0.15

COUPLE_I = 15
COUPLE_J = 35

PAD_ID = len(ALPHABET)
MASK_ID = len(ALPHABET) + 1
VOCAB_SIZE = len(ALPHABET) + 2

D_MODEL, N_HEAD, N_LAYERS, FF_DIM = 64, 4, 2, 128
LR, EPOCHS, BATCH_SIZE, VAL_FRAC = 1e-3, 30, 128, 0.2


def generate_covariation_corpus(rng):
    """Uniform background everywhere. Family A: seq[j]=seq[i] (coupled).
    Family B: i,j independent. Marginals at i and j are uniform in BOTH families,
    so only the JOINT (i,j) distribution differs. Returns (corpus, labels)."""
    corpus = rng.integers(0, len(ALPHABET), size=(N_SEQ, SEQ_LEN), dtype=np.int64)
    labels = np.zeros(N_SEQ, dtype=np.int64)
    labels[N_PER_FAMILY:] = 1  # 0 = Family A (coupled), 1 = Family B (independent)
    # Family A: overwrite column j with column i's value (both already uniform).
    corpus[:N_PER_FAMILY, COUPLE_J] = corpus[:N_PER_FAMILY, COUPLE_I]
    # Family B: leave i and j as independent uniform draws (already the case).
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


def conditional_j_accuracy(model, corpus, labels):
    """Mask ONLY column j (leave i visible) and measure accuracy at j per family.
    Family A should be high (model can copy i->j); Family B near chance."""
    data = torch.from_numpy(corpus).long()
    inputs = data.clone()
    inputs[:, COUPLE_J] = MASK_ID
    model.eval()
    with torch.no_grad():
        preds = model(inputs).argmax(dim=-1)[:, COUPLE_J]
    truth = data[:, COUPLE_J]
    out = {}
    for fam in (0, 1):
        sel = labels == fam
        out[fam] = float((preds[sel] == truth[sel]).float().mean().item())
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
    corpus, labels = generate_covariation_corpus(rng)
    data = torch.from_numpy(corpus).long()

    # Sanity: marginals at i and j should be ~uniform in BOTH families.
    for fam, name in [(0, "A(coupled)"), (1, "B(indep)")]:
        sel = labels == fam
        pi = np.bincount(corpus[sel, COUPLE_I], minlength=len(ALPHABET)) / sel.sum()
        pj = np.bincount(corpus[sel, COUPLE_J], minlength=len(ALPHABET)) / sel.sum()
        match = float((corpus[sel, COUPLE_I] == corpus[sel, COUPLE_J]).mean())
        print(f"[DATA]   Family {name}: max|marg_i-1/20|={abs(pi-1/20).max():.3f} "
              f"max|marg_j-1/20|={abs(pj-1/20).max():.3f}; P(seq[i]==seq[j])={match:.3f}")
    print(f"[DATA]   (Family A coupling => match~1.0; Family B independent => ~1/20=0.05)\n")

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

    jacc = conditional_j_accuracy(model, corpus[val_idx.numpy()], y_val)

    print(f"\n[EMBED]  linear-probe AUC (Family A vs B), held-out val split:")
    print(f"           trained model : {auc_tr:.4f}")
    print(f"           untrained ctrl: {auc_un:.4f}   (must be ~0.5 now)")
    print(f"           composition   : {auc_co:.4f}   (must be ~0.5)")
    print(f"[MECH]   masked acc at col j with i visible: "
          f"FamA(coupled)={jacc[0]:.4f}  FamB(indep)={jacc[1]:.4f}  "
          f"(chance=1/20={1/len(ALPHABET):.3f})")

    h06a = auc_tr >= 0.90
    h06b = (auc_un <= 0.60 and auc_co <= 0.60)
    h06c = ((jacc[0] - jacc[1]) >= 0.30 and jacc[1] <= 0.15)

    print(f"\n[HYPOTHESIS CHECKS]")
    print(f"  H_06A trained AUC>=0.90        : {'PASS' if h06a else 'FAIL'} (AUC={auc_tr:.4f})")
    print(f"  H_06B controls at chance<=0.60 : {'PASS' if h06b else 'FAIL'} "
          f"(untrained={auc_un:.3f} comp={auc_co:.3f})")
    print(f"  H_06C coupling learned         : {'PASS' if h06c else 'FAIL'} "
          f"(gap={jacc[0]-jacc[1]:.3f}, FamB j-acc={jacc[1]:.3f})")
    all_pass = h06a and h06b and h06c
    print(f"\n{'='*60}")
    print(f"VERDICT: {'ALL CHECKS PASSED' if all_pass else 'CHECKS FAILED'}")
    if all_pass:
        print("  Separation requires LEARNING: both controls are at chance, only the")
        print("  trained model separates, and it does so by learning the i->j coupling.")
    else:
        print("  Separation did NOT isolate learning as predicted; inspect controls.")
    print(f"{'='*60}")

    metrics = {"auc": {"trained": auc_tr, "untrained": auc_un, "composition": auc_co},
               "jacc": jacc}
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
        for fam, color, name in [(0, "tab:red", "Family A (coupled i,j)"),
                                 (1, "tab:blue", "Family B (independent)")]:
            sel = labels == fam
            ax.scatter(pts[sel, 0], pts[sel, 1], s=10, alpha=0.6,
                       color=color, label=name)
        ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
        ax.set_title(title); ax.legend(loc="best", fontsize=8)
    fig.suptitle("Embeddings of covariation families (val); only learning can separate")
    fig.tight_layout()
    f1 = FIG_DIR / "script_06_embedding_pca.png"
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
    f2 = FIG_DIR / "script_06_auc_vs_controls.png"
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
        print("Hypothesis: HYPOTHESIS_06.md (pairwise-covariation families)")
        print(f"Coupling: Family A seq[{COUPLE_J}]=seq[{COUPLE_I}]; Family B independent")
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
# [DATA] Family A(coupled): marg_i,j ~uniform; P(seq[i]==seq[j])=1.000
# [DATA] Family B(indep):   marg_i,j ~uniform; P(seq[i]==seq[j])=0.053
# [EMBED] linear-probe AUC (val): trained=0.4849  untrained=0.4855  composition=0.4765
# [MECH]  masked acc at col j with i visible: FamA=0.0550  FamB=0.0550 (chance 0.050)
#   H_06A trained AUC>=0.90        : FAIL (0.4849)
#   H_06B controls at chance<=0.60 : PASS (untrained=0.486 comp=0.476)
#   H_06C coupling learned         : FAIL (gap=0.000, FamB j-acc=0.055)
#   VERDICT: CHECKS FAILED
#
# INTERPRETATION (see ANALYSIS_06.md):
#   - The DESIGN is now airtight: equal marginals removed the position- and
#     composition-shortcuts, so BOTH controls dropped to chance (H_06B PASS) --
#     this fixes the iteration-05 confound (KNOWN_PATTERNS S2.3).
#   - But the TRAINED model also stayed at chance and the mechanistic probe shows
#     it never learned the coupling (j-acc=0.055=chance for BOTH families). A
#     SINGLE coupled pair among 50 columns barely affects the masked-LM loss
#     (it only helps when j is masked AND i visible, on 1/50 columns), so 30
#     epochs of a nano model learn nothing there. The dependency is in the data
#     (match=1.000) but the objective has no incentive to capture it.
#   => Finding: MLM does not learn a sparse pairwise dependency that does not
#      materially reduce its loss. Iteration 07 strengthens the signal with MANY
#      bijection-coupled position pairs (per-column marginals stay uniform,
#      composition stays ~equal), so learning the rule yields a large loss
#      reduction -> trained model should separate while both controls stay at
#      chance. New anti-pattern logged: KNOWN_PATTERNS S2.4.
# =============================================================================
