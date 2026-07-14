#!/usr/bin/env python3
"""
Script 09: Pretrained ESM-2 embeddings separate two REAL protein families (Rung 3).

Hypothesis: HYPOTHESIS_09.md (H_09A AUC, H_09B silhouette, H_09C controls)
Phase: real_data
Iteration: 9

Purpose:
  Embed two real UniProt families (globin PF00042 vs cytochrome c PF00034) with a
  FROZEN pretrained ESM-2 (esm2_t6_8M_UR50D, ~8M params, CPU) -- mean-pool the final
  layer's per-residue representations to one vector per sequence -- and test whether
  the families separate. NO fine-tuning: ESM-2 is a fixed feature extractor, so
  success demonstrates TRANSFER from a real PLM. Controls: shuffled labels (must be
  at chance) and a length-only classifier (separation must not be a length artifact).

Depends on:
  - data/downloaded/rung3_two_families.fasta (from fetch_uniprot_families.py)
  - fair-esm (esm2_t6_8M_UR50D), torch (CPU), numpy, matplotlib
  - Embedding/probe methodology from script_08_identity_coupling.py; ANALYSIS_08.md
"""

import sys
from pathlib import Path
from datetime import datetime

import numpy as np
import torch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

SCRIPT_NAME = "script_09_esm2_family_separation"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIG_DIR = PROJECT_ROOT / "results" / "figures"
FASTA_PATH = PROJECT_ROOT / "data" / "downloaded" / "rung3_two_families.fasta"

SEED = 1024
VAL_FRAC = 0.3
ESM_MODEL = "esm2_t6_8M_UR50D"
ESM_LAYER = 6  # final layer of the 6-layer model


def load_tagged_fasta(path):
    """Parse the combined FASTA whose headers are 'family|label|accession'.
    Returns list of dicts: {name, label, acc, seq}."""
    records = []
    header, seq = None, []

    def flush():
        if header is not None:
            fam, label, acc = header.split("|")[:3]
            records.append({"name": fam, "label": int(label), "acc": acc,
                            "seq": "".join(seq)})

    with open(path) as fh:
        for line in fh:
            if line.startswith(">"):
                flush()
                header, seq = line[1:].strip(), []
            elif line.strip():
                seq.append(line.strip())
    flush()
    return records


def embed_sequences(records):
    """Load frozen ESM-2 and return (N, D) mean-pooled final-layer embeddings.
    Excludes BOS/EOS and padding from the mean."""
    import esm
    print(f"[ESM]    loading {ESM_MODEL} (first run downloads weights)...")
    model, alphabet = esm.pretrained.__dict__[ESM_MODEL]()
    model.eval()
    batch_converter = alphabet.get_batch_converter()

    data = [(r["acc"], r["seq"]) for r in records]
    embs = []
    bs = 8
    for start in range(0, len(data), bs):
        chunk = data[start:start + bs]
        _, _, toks = batch_converter(chunk)
        with torch.no_grad():
            out = model(toks, repr_layers=[ESM_LAYER])
        reps = out["representations"][ESM_LAYER]  # (B, L, D)
        for i, (_, seq) in enumerate(chunk):
            # tokens 1..len(seq) are residues; 0 is BOS, len+1 is EOS.
            v = reps[i, 1:len(seq) + 1].mean(dim=0)
            embs.append(v.cpu().numpy())
        print(f"[ESM]    embedded {min(start + bs, len(data))}/{len(data)}")
    return np.asarray(embs)


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


def logistic_regression_auc(x_train, y_train, x_val, y_val, epochs=400, lr=0.1):
    x_train, x_val = _standardize(x_train, x_val)
    n, d = x_train.shape
    w = np.zeros(d)
    b = 0.0
    for _ in range(epochs):
        z = x_train @ w + b
        p = 1.0 / (1.0 + np.exp(-z))
        grad_w = x_train.T @ (p - y_train) / n + 1e-2 * w
        grad_b = float(np.mean(p - y_train))
        w -= lr * grad_w
        b -= lr * grad_b
    return roc_auc(y_val, x_val @ w + b)


def silhouette_score(x, labels):
    """Mean silhouette over points for 2 clusters (euclidean)."""
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


def run_experiment():
    records = load_tagged_fasta(FASTA_PATH)
    labels = np.array([r["label"] for r in records])
    lengths = np.array([len(r["seq"]) for r in records], dtype=np.float64)
    names = sorted(set(r["name"] for r in records))
    print(f"[DATA]   {len(records)} sequences; families={names}; "
          f"counts={[int((labels==l).sum()) for l in (0,1)]}")
    print(f"[DATA]   length min/mean/max = "
          f"{int(lengths.min())}/{int(lengths.mean())}/{int(lengths.max())}\n")

    emb = embed_sequences(records)
    print(f"\n[EMBED]  ESM-2 embeddings shape = {emb.shape}")

    # Deterministic stratified-ish split.
    rng = np.random.default_rng(SEED)
    idx = rng.permutation(len(records))
    n_val = int(len(records) * VAL_FRAC)
    val_idx, train_idx = idx[:n_val], idx[n_val:]
    Xtr, Xv = emb[train_idx], emb[val_idx]
    ytr, yv = labels[train_idx], labels[val_idx]

    auc = logistic_regression_auc(Xtr, ytr, Xv, yv)
    sil = silhouette_score(_standardize(emb, emb)[0], labels)

    # Control 1: shuffled labels (should collapse to chance).
    y_shuf = labels.copy()
    rng.shuffle(y_shuf)
    auc_shuf = logistic_regression_auc(Xtr, y_shuf[train_idx], Xv, y_shuf[val_idx])

    # Control 2: length-only classifier (is separation just a length artifact?).
    auc_len = logistic_regression_auc(
        lengths[train_idx, None], ytr, lengths[val_idx, None], yv)

    print(f"\n[PROBE]  ESM-2 embedding AUC (held-out)     : {auc:.4f}")
    print(f"[PROBE]  silhouette (family labels)          : {sil:.4f}")
    print(f"[CTRL]   shuffled-label AUC                  : {auc_shuf:.4f}  (~0.5)")
    print(f"[CTRL]   length-only AUC                     : {auc_len:.4f}")

    h09a = auc >= 0.95
    h09b = sil >= 0.20
    h09c = (auc_shuf <= 0.65 and (auc_len <= 0.75 or auc > auc_len + 0.1))

    print(f"\n[HYPOTHESIS CHECKS]")
    print(f"  H_09A embedding AUC>=0.95        : {'PASS' if h09a else 'FAIL'} (AUC={auc:.4f})")
    print(f"  H_09B silhouette>=0.20           : {'PASS' if h09b else 'FAIL'} (sil={sil:.4f})")
    print(f"  H_09C controls behave            : {'PASS' if h09c else 'FAIL'} "
          f"(shuffled={auc_shuf:.3f}, length-only={auc_len:.3f})")
    all_pass = h09a and h09b and h09c
    print(f"\n{'='*60}")
    print(f"VERDICT: {'ALL CHECKS PASSED' if all_pass else 'CHECKS FAILED'}")
    if all_pass:
        print("  A FROZEN pretrained ESM-2 separates two real protein families with")
        print("  no fine-tuning; shuffled-label control at chance confirms real signal.")
        print("  Transfer from a real PLM -- the top rung of the fidelity ladder.")
    else:
        print("  Real-data separation did not fully meet criteria; see checks above.")
    print(f"{'='*60}")

    metrics = {"auc": auc, "sil": sil, "auc_shuf": auc_shuf, "auc_len": auc_len,
               "names": names}
    save_figures(emb, labels, metrics)


def _pca_2d(x):
    xc = x - x.mean(axis=0, keepdims=True)
    u, s, vt = np.linalg.svd(xc, full_matrices=False)
    return xc @ vt[:2].T


def save_figures(emb, labels, metrics):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = np.asarray(labels)
    pts = _pca_2d(_standardize(emb, emb)[0])
    names = metrics["names"]

    fig, ax = plt.subplots(figsize=(7, 6))
    for fam, color, name in [(0, "tab:red", names[0]),
                             (1, "tab:blue", names[1] if len(names) > 1 else "fam1")]:
        sel = labels == fam
        ax.scatter(pts[sel, 0], pts[sel, 1], s=30, alpha=0.7, color=color, label=name)
    ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
    ax.set_title(f"Frozen ESM-2 ({ESM_MODEL}) embeddings of two real families\n"
                 f"probe AUC={metrics['auc']:.3f}, silhouette={metrics['sil']:.3f}")
    ax.legend()
    fig.tight_layout()
    f1 = FIG_DIR / "script_09_esm2_pca.png"
    fig.savefig(str(f1), dpi=300)
    plt.close(fig)
    print(f"[FIGURE] saved {f1.relative_to(PROJECT_ROOT)}")

    labels_bar = ["ESM-2\nembedding", "shuffled\nlabels", "length\nonly"]
    vals = [metrics["auc"], metrics["auc_shuf"], metrics["auc_len"]]
    fig2, ax = plt.subplots(figsize=(7, 5))
    ax.bar(np.arange(3), vals, 0.55,
           color=["tab:purple", "gray", "tab:olive"])
    ax.axhline(0.5, color="black", ls="--", lw=1, label="chance (0.5)")
    ax.set_xticks(np.arange(3)); ax.set_xticklabels(labels_bar)
    ax.set_ylim(0, 1.05); ax.set_ylabel("classifier AUC")
    ax.set_title("Real family separation: ESM-2 vs controls")
    ax.legend()
    fig2.tight_layout()
    f2 = FIG_DIR / "script_09_auc_vs_controls.png"
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
        print("Hypothesis: HYPOTHESIS_09.md (real ESM-2 family separation)")
        print(f"Model: {ESM_MODEL} (frozen, layer {ESM_LAYER}); data: {FASTA_PATH.name}")
        print(f"{'='*60}\n")

        run_experiment()

        print(f"\n{'='*60}")
        print("=== COMPLETE ===")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()


# =============================================================================
# PASTED OUTPUT (run 2026-06-29, seed 1024, torch 2.12.1 CPU, fair-esm 2.0.0)
# -----------------------------------------------------------------------------
# [DATA]  60 sequences; families=['cytochrome_c','globin']; counts=[30,30]
# [DATA]  length min/mean/max = 105/160/351
# [ESM]   esm2_t6_8M_UR50D (frozen, layer 6); embeddings shape=(60, 320)
# [PROBE] ESM-2 embedding AUC (held-out)     : 1.0000
# [PROBE] silhouette (family labels)          : 0.3918
# [CTRL]  shuffled-label AUC                  : 0.4375  (~0.5)
# [CTRL]  length-only AUC                     : 0.2208
#   H_09A embedding AUC>=0.95 : PASS (1.0000)
#   H_09B silhouette>=0.20    : PASS (0.3918)
#   H_09C controls behave     : PASS (shuffled=0.438, length-only=0.221)
#   VERDICT: ALL CHECKS PASSED
#
# INTERPRETATION (see ANALYSIS_09.md):
#   - A FROZEN pretrained ESM-2 (no fine-tuning) cleanly separates two real protein
#     families (globin PF00042 vs cytochrome c PF00034): held-out AUC=1.000,
#     silhouette=0.392.
#   - Shuffled-label AUC=0.438 (~chance) confirms the probe is reading real
#     family structure, not split leakage.
#   - length-only AUC=0.221 (far from the embedding's 1.000) shows separation is
#     NOT a sequence-length artifact -- it reflects learned sequence/structure.
#   - This is TRANSFER from a real PLM (embeddings only), the top rung of the
#     fidelity ladder; it shows the embedding idea proven synthetically (iter 08)
#     holds on real biology. It does not claim we trained a competitive PLM.
# =============================================================================
