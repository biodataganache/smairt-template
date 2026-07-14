#!/usr/bin/env python3
"""
Script 01: Validate the synthetic protein-corpus generator (NO model trained).

Hypothesis: HYPOTHESIS_01.md (sub-hypotheses H_01A, H_01B)
Phase: synthetic
Track: (none — early sequential numbering)
Iteration: 1

Purpose:
  SMAIRT discipline — validate the synthetic data generator BEFORE training any
  model. This script generates a synthetic protein-like corpus with a planted
  conserved motif (P-loop G-x-G-x-x-G), then verifies the planted ground truth:
    (a) generate the corpus with a fixed seed,
    (b) print a few example sequences,
    (c) report motif positions and per-column residue frequencies,
    (d) compute a unigram-frequency masked-prediction baseline (the exact bar
        the nano-MLM in script_02 must beat),
    (e) save figures showing the planted structure,
    plus a 15% masking plumbing smoke test and a reproducibility check.

Depends on:
  - scripts/shared (TeeLogger, setup_logging)
  - numpy, matplotlib
"""

import sys
from pathlib import Path
from datetime import datetime

import numpy as np

# === PATH SETUP ===
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

# === CONFIGURATION (fixed for reproducibility; mirrors HYPOTHESIS_01.md) ===
SCRIPT_NAME = "script_01_validate_generator"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIG_DIR = PROJECT_ROOT / "results" / "figures"

SEED = 1024
ALPHABET = "ACDEFGHIKLMNPQRSTVWY"   # 20 standard amino acids
N_SEQ = 2000                        # number of sequences
SEQ_LEN = 50                        # residues per sequence
MASK_RATE = 0.15                    # MLM masking fraction (plumbing test only)

# Conserved motif: P-loop / Walker-A "G-x-G-x-x-G"
MOTIF_START = 22                    # 0-based start column (occupies 22..27)
MOTIF = "GxGxxG"                    # 'G' = invariant glycine, 'x' = background
INVARIANT_COLS = [MOTIF_START + i for i, c in enumerate(MOTIF) if c == "G"]
VARIABLE_MOTIF_COLS = [MOTIF_START + i for i, c in enumerate(MOTIF) if c == "x"]

AA_TO_IDX = {aa: i for i, aa in enumerate(ALPHABET)}
GLY_IDX = AA_TO_IDX["G"]


def generate_corpus(rng):
    """Generate (N_SEQ, SEQ_LEN) int array from uniform background + planted motif."""
    # Uniform background over the 20 amino acids.
    corpus = rng.integers(0, len(ALPHABET), size=(N_SEQ, SEQ_LEN), dtype=np.int64)
    # Overwrite the invariant motif columns with glycine.
    for col in INVARIANT_COLS:
        corpus[:, col] = GLY_IDX
    # Variable 'x' columns stay as background (already random) — left untouched.
    return corpus


def decode(seq_row):
    """Turn an int row into its amino-acid string."""
    return "".join(ALPHABET[i] for i in seq_row)


def column_frequencies(corpus):
    """Return (SEQ_LEN, 20) matrix of per-column residue frequencies."""
    freqs = np.zeros((SEQ_LEN, len(ALPHABET)), dtype=np.float64)
    for col in range(SEQ_LEN):
        counts = np.bincount(corpus[:, col], minlength=len(ALPHABET))
        freqs[col] = counts / corpus.shape[0]
    return freqs


def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    with TeeLogger(log_path):
        print(f"{'='*60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("Hypothesis: HYPOTHESIS_01.md (H_01A generator, H_01B plumbing)")
        print("Goal: validate planted grammar BEFORE training any model")
        print(f"{'='*60}\n")

        # --- Config echo (metadata for the audit trail) ---
        print("[CONFIG]")
        print(f"  seed            = {SEED}")
        print(f"  n_sequences     = {N_SEQ}")
        print(f"  seq_len         = {SEQ_LEN}")
        print(f"  alphabet (20)   = {ALPHABET}")
        print(f"  background      = uniform over 20 AAs")
        print(f"  motif           = {MOTIF}  (P-loop / Walker-A)")
        print(f"  motif start col = {MOTIF_START}  (0-based, occupies {MOTIF_START}..{MOTIF_START+len(MOTIF)-1})")
        print(f"  invariant cols  = {INVARIANT_COLS}  (must be ~100% glycine)")
        print(f"  variable cols   = {VARIABLE_MOTIF_COLS}  (background)")
        print(f"  mask_rate       = {MASK_RATE}\n")

        rng = np.random.default_rng(SEED)
        corpus = generate_corpus(rng)
        assert corpus.shape == (N_SEQ, SEQ_LEN), "corpus shape mismatch"
        print(f"[GENERATE] corpus shape = {corpus.shape}\n")

        # ========================================
        # (b) Print a few example sequences
        # ========================================
        print("[EXAMPLES] first 5 sequences (motif region in [brackets]):")
        for r in range(5):
            s = decode(corpus[r])
            lo, hi = MOTIF_START, MOTIF_START + len(MOTIF)
            bracketed = f"{s[:lo]}[{s[lo:hi]}]{s[hi:]}"
            print(f"  seq{r}: {bracketed}")
        print()

        # placeholder for remaining sections (filled below)
        run_checks(corpus)

        print(f"\n{'='*60}")
        print("=== COMPLETE ===")
        print(f"{'='*60}")


def run_checks(corpus):
    """Frequency report (c), unigram baseline (d), masking test, reproducibility, figures (e)."""
    freqs = column_frequencies(corpus)

    # ========================================
    # (c) Motif positions & per-column residue frequencies
    # ========================================
    print("[MOTIF REPORT] per motif column: expected vs observed top residue")
    print(f"  {'col':>4} {'role':>9} {'top_aa':>6} {'top_freq':>9} {'gly_freq':>9}")
    for i, c in enumerate(MOTIF):
        col = MOTIF_START + i
        top_idx = int(np.argmax(freqs[col]))
        role = "INVARIANT" if c == "G" else "variable"
        print(f"  {col:>4} {role:>9} {ALPHABET[top_idx]:>6} "
              f"{freqs[col][top_idx]:>9.4f} {freqs[col][GLY_IDX]:>9.4f}")
    print()

    # --- H_01A assertions: planted signal exists ONLY where designed ---
    p = 1.0 / len(ALPHABET)
    print(f"[CHECKS] background p=1/20={p:.4f}")

    checks_passed = True

    # 1. Invariant columns are 100% glycine.
    for col in INVARIANT_COLS:
        gly = freqs[col][GLY_IDX]
        ok = np.isclose(gly, 1.0)
        checks_passed &= ok
        print(f"  invariant col {col}: glycine freq = {gly:.4f}  -> "
              f"{'PASS' if ok else 'FAIL'} (expect 1.0)")

    # 2. Non-invariant columns follow the uniform background.
    #    Per-column chi-square goodness-of-fit vs uniform (df=19). A per-estimate
    #    3-sigma band would flag ~2.5 of 47x20 frequencies by chance alone
    #    (multiple comparisons), so we test each COLUMN's full distribution and
    #    count rejections, comparing to the expected false-positive rate.
    n = corpus.shape[0]
    expected_count = n * p
    df = len(ALPHABET) - 1                 # 19
    alpha = 0.001
    chi2_crit = 43.820                      # chi-square critical, df=19, alpha=0.001
    rejections = []
    max_chi2 = 0.0
    for col in range(SEQ_LEN):
        if col in INVARIANT_COLS:
            continue
        counts = freqs[col] * n
        chi2 = float(np.sum((counts - expected_count) ** 2 / expected_count))
        max_chi2 = max(max_chi2, chi2)
        if chi2 > chi2_crit:
            rejections.append((col, round(chi2, 2)))
    n_nonmotif = SEQ_LEN - len(INVARIANT_COLS)
    expected_fp = alpha * n_nonmotif
    # Pass if observed rejections are consistent with chance (<= ceil of expected
    # false positives + small slack). With alpha=0.001 over 47 cols, expect ~0.
    nonmotif_ok = len(rejections) <= max(1, int(np.ceil(expected_fp)))
    checks_passed &= nonmotif_ok
    print(f"  non-invariant cols: chi-square GOF vs uniform (df={df}, "
          f"alpha={alpha}, crit={chi2_crit})")
    print(f"    max chi2 = {max_chi2:.2f}; rejections = {rejections} "
          f"(expected ~{expected_fp:.2f} by chance)")
    print(f"    {n_nonmotif} non-invariant cols consistent with uniform background: "
          f"{'PASS' if nonmotif_ok else 'FAIL'}")

    # Confirm no non-invariant column is glycine-dominated (glycine clearly the
    # top residue AND well above the uniform background rate).
    stray = [c for c in range(SEQ_LEN)
             if c not in INVARIANT_COLS and int(np.argmax(freqs[c])) == GLY_IDX
             and freqs[c][GLY_IDX] > 2 * p]
    stray_ok = (len(stray) == 0)
    checks_passed &= stray_ok
    print(f"  no stray glycine-dominated cols outside motif: "
          f"{'PASS' if stray_ok else 'FAIL'} (found {stray})\n")

    # ========================================
    # (d) Unigram-frequency masked-prediction baseline
    # ========================================
    # The trivial predictor: always guess the single globally most-common residue.
    # This is the EXACT bar the nano-MLM (script_02) must beat.
    global_counts = np.bincount(corpus.reshape(-1), minlength=len(ALPHABET))
    global_freq = global_counts / corpus.size
    most_common_idx = int(np.argmax(global_freq))
    baseline_acc = float(global_freq[most_common_idx])

    # Expected analytically: 3 invariant G cols are all G; in the other 47 cols G
    # appears at ~1/20. Over all positions the most common residue is glycine.
    n_pos = SEQ_LEN
    expected_gly = (len(INVARIANT_COLS) + (n_pos - len(INVARIANT_COLS)) * p) / n_pos
    print("[BASELINE] unigram-frequency masked-prediction baseline")
    print(f"  most common residue = {ALPHABET[most_common_idx]} "
          f"(freq {baseline_acc:.4f})")
    print(f"  analytic glycine fraction over all positions = {expected_gly:.4f}")
    print(f"  >>> BASELINE ACCURACY TO BEAT = {baseline_acc:.4f} <<<\n")

    # ========================================
    # Masking plumbing smoke test (H_01B)
    # ========================================
    rng_mask = np.random.default_rng(SEED + 1)
    mask = rng_mask.random(corpus.shape) < MASK_RATE
    masked_targets = corpus[mask].copy()       # store true residues before masking
    corrupted = corpus.copy()
    corrupted[mask] = -1                        # sentinel "masked" token
    observed_rate = mask.mean()
    leak_ok = bool(np.all(corrupted[mask] == -1))           # all masked are hidden
    recover_ok = bool(np.array_equal(masked_targets, corpus[mask]))  # targets intact
    rate_ok = abs(observed_rate - MASK_RATE) < 0.01
    checks_passed &= (leak_ok and recover_ok and rate_ok)
    print("[MASKING TEST] 15% MLM plumbing")
    print(f"  observed mask rate = {observed_rate:.4f} (target {MASK_RATE}) -> "
          f"{'PASS' if rate_ok else 'FAIL'}")
    print(f"  no label leakage (masked positions hidden): {'PASS' if leak_ok else 'FAIL'}")
    print(f"  targets recover pre-mask residues: {'PASS' if recover_ok else 'FAIL'}\n")

    # ========================================
    # Reproducibility check (pre-flight #10)
    # ========================================
    corpus2 = generate_corpus(np.random.default_rng(SEED))
    repro_ok = bool(np.array_equal(corpus, corpus2))
    checks_passed &= repro_ok
    print(f"[REPRODUCIBILITY] regenerate with seed {SEED} identical: "
          f"{'PASS' if repro_ok else 'FAIL'}\n")

    # ========================================
    # (e) Figures showing the planted structure
    # ========================================
    save_figures(freqs)

    # ========================================
    # Verdict
    # ========================================
    print(f"{'='*60}")
    print(f"VERDICT: {'ALL CHECKS PASSED' if checks_passed else 'CHECKS FAILED'}")
    print(f"  Generator {'is trustworthy — proceed to script_02 (train nano-MLM).' if checks_passed else 'is NOT trustworthy — fix before training.'}")
    print(f"  Baseline accuracy for script_02 to beat: {baseline_acc:.4f}")
    print(f"{'='*60}")


def save_figures(freqs):
    """Per-column glycine-frequency bar chart + column x residue heatmap (300 DPI)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Figure 1: per-column glycine frequency (spikes at invariant cols).
    fig, ax = plt.subplots(figsize=(10, 3.5))
    cols = np.arange(SEQ_LEN)
    colors = ["tab:red" if c in INVARIANT_COLS else "tab:blue" for c in cols]
    ax.bar(cols, freqs[:, GLY_IDX], color=colors)
    ax.axhline(1.0 / len(ALPHABET), color="gray", ls="--", lw=1,
               label="uniform background (1/20)")
    ax.set_xlabel("sequence column")
    ax.set_ylabel("glycine frequency")
    ax.set_title("Per-column glycine frequency (red = planted invariant motif G)")
    ax.legend()
    fig.tight_layout()
    f1 = FIG_DIR / "script_01_glycine_by_column.png"
    fig.savefig(f1, dpi=300)
    plt.close(fig)
    print(f"[FIGURE] saved {f1.relative_to(PROJECT_ROOT)}")

    # Figure 2: column x residue frequency heatmap.
    fig, ax = plt.subplots(figsize=(10, 5))
    im = ax.imshow(freqs.T, aspect="auto", origin="lower", cmap="viridis",
                   vmin=0.0, vmax=1.0)
    ax.set_yticks(range(len(ALPHABET)))
    ax.set_yticklabels(list(ALPHABET))
    ax.set_xlabel("sequence column")
    ax.set_ylabel("amino acid")
    ax.set_title("Per-column residue frequency (bright row at G in motif columns)")
    fig.colorbar(im, ax=ax, label="frequency")
    fig.tight_layout()
    f2 = FIG_DIR / "script_01_column_residue_heatmap.png"
    fig.savefig(f2, dpi=300)
    plt.close(fig)
    print(f"[FIGURE] saved {f2.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()


# ============================================================================
# PASTED OUTPUT (run 2026-06-29, seed=1024) — see results/logs/ for full log
# ============================================================================
# [GENERATE] corpus shape = (2000, 50)
#
# [MOTIF REPORT] per motif column: expected vs observed top residue
#    col      role top_aa  top_freq  gly_freq
#     22 INVARIANT      G    1.0000    1.0000
#     23  variable      R    0.0590    0.0425
#     24 INVARIANT      G    1.0000    1.0000
#     25  variable      C    0.0550    0.0435
#     26  variable      C    0.0580    0.0425
#     27 INVARIANT      G    1.0000    1.0000
#
# [CHECKS] background p=1/20=0.0500
#   invariant col 22: glycine freq = 1.0000  -> PASS (expect 1.0)
#   invariant col 24: glycine freq = 1.0000  -> PASS (expect 1.0)
#   invariant col 27: glycine freq = 1.0000  -> PASS (expect 1.0)
#   non-invariant cols: chi-square GOF vs uniform (df=19, alpha=0.001, crit=43.82)
#     max chi2 = 33.06; rejections = []  (expected ~0.05 by chance)
#     47 non-invariant cols consistent with uniform background: PASS
#   no stray glycine-dominated cols outside motif: PASS (found [])
#
# [BASELINE] unigram-frequency masked-prediction baseline
#   most common residue = G (freq 0.1076)
#   >>> BASELINE ACCURACY TO BEAT = 0.1076 <<<
#
# [MASKING TEST] 15% MLM plumbing
#   observed mask rate = 0.1496 (target 0.15) -> PASS
#   no label leakage (masked positions hidden): PASS
#   targets recover pre-mask residues: PASS
#
# [REPRODUCIBILITY] regenerate with seed 1024 identical: PASS
#
# VERDICT: ALL CHECKS PASSED
#   Generator is trustworthy — proceed to script_02 (train nano-MLM).
#   Baseline accuracy for script_02 to beat: 0.1076
# ============================================================================
