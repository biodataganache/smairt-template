#!/usr/bin/env python3
"""
Script 01: Benjamini-Hochberg Correction Baseline

Hypothesis: hypotheses/H1_bh_correction_baseline.md
Phase: synthetic
Track: None
Iteration: 1

Depends on:
  - None (pure synthetic baseline generation and validation)
"""

import sys
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.stats.multitest as multitest
import matplotlib.pyplot as plt

# === PATH SETUP ===
# The script is in experiments/01_synthetic/
# PROJECT_ROOT should be the proteomics_de directory (three levels up)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

# === CONFIGURATION ===
SCRIPT_NAME = "script_01_bh_correction"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"

# Parameters as specified in background/01_initial_question.md
N_PROTEINS = 2000
N_REPLICATES = 5  # 5 control + 5 treated
N_PLANTED_DE = 100
PLANTED_LOG2_FC = 1.0  # ~2x fold change
MEASUREMENT_NOISE_SD = 0.3
FDR_THRESHOLD = 0.05
RANDOM_SEED = 1024  # Standard from KNOWN_PATTERNS.md consistency rules

def generate_synthetic_data(seed=RANDOM_SEED):
    """
    Generate synthetic proteomics abundance matrix.
    Rows are proteins, columns are samples (5 controls, 5 treated).
    """
    np.random.seed(seed)
    
    # 1. Base log2 intensities
    # Assume base expression is normally distributed around 20.0 with some variation
    base_expression = np.random.normal(loc=20.0, scale=1.5, size=(N_PROTEINS, 1))
    
    # 2. Control samples: base expression + random noise
    control_data = base_expression + np.random.normal(loc=0.0, scale=MEASUREMENT_NOISE_SD, size=(N_PROTEINS, N_REPLICATES))
    
    # 3. Treated samples: base expression + planted DE + random noise
    # Initialize treated data with base expression + noise
    treated_data = base_expression + np.random.normal(loc=0.0, scale=MEASUREMENT_NOISE_SD, size=(N_PROTEINS, N_REPLICATES))
    
    # Plant the DE effects
    # First 50 up-regulated, next 50 down-regulated
    is_planted = np.zeros(N_PROTEINS, dtype=bool)
    planted_direction = np.zeros(N_PROTEINS, dtype=float)
    
    # Plant 50 up-regulated
    treated_data[0:50, :] += PLANTED_LOG2_FC
    is_planted[0:50] = True
    planted_direction[0:50] = PLANTED_LOG2_FC
    
    # Plant 50 down-regulated
    treated_data[50:100, :] -= PLANTED_LOG2_FC
    is_planted[50:100] = True
    planted_direction[50:100] = -PLANTED_LOG2_FC
    
    # Combine into dataframes
    col_names = [f"Ctrl_Rep{i+1}" for i in range(N_REPLICATES)] + [f"Treat_Rep{i+1}" for i in range(N_REPLICATES)]
    data_matrix = np.hstack([control_data, treated_data])
    
    df = pd.DataFrame(data_matrix, columns=col_names)
    df.index = [f"Prot_{i+1:04d}" for i in range(N_PROTEINS)]
    
    # Store ground truth metadata
    metadata = pd.DataFrame({
        "is_planted": is_planted,
        "planted_fc": planted_direction
    }, index=df.index)
    
    return df, metadata

def run_de_analysis(df):
    """
    Run Welch's t-test per protein and calculate log2 fold change.
    """
    ctrl_cols = [col for col in df.columns if "Ctrl" in col]
    treat_cols = [col for col in df.columns if "Treat" in col]
    
    p_values = []
    log2_fcs = []
    t_stats = []
    
    for idx, row in df.iterrows():
        ctrl_vals = row[ctrl_cols].values
        treat_vals = row[treat_cols].values
        
        # Welch's t-test (equal_var=False)
        t_stat, p_val = stats.ttest_ind(treat_vals, ctrl_vals, equal_var=False)
        
        # Log2 fold change (difference since data is on log2 scale)
        log2_fc = np.mean(treat_vals) - np.mean(ctrl_vals)
        
        p_values.append(p_val)
        log2_fcs.append(log2_fc)
        t_stats.append(t_stat)
        
    results = pd.DataFrame({
        "log2_fc": log2_fcs,
        "t_stat": t_stats,
        "p_value": p_values
    }, index=df.index)
    
    return results

def compute_metrics(results, metadata, p_col, threshold, is_corrected=False):
    """
    Calculate Sensitivity (Recall) and Empirical FDR.
    """
    called_significant = results[p_col] < threshold
    is_planted = metadata["is_planted"]
    
    tp = np.sum(called_significant & is_planted)
    fp = np.sum(called_significant & ~is_planted)
    fn = np.sum(~called_significant & is_planted)
    tn = np.sum(~called_significant & ~is_planted)
    
    called_total = tp + fp
    
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    empirical_fdr = fp / called_total if called_total > 0 else 0.0
    
    return {
        "called_total": int(called_total),
        "TP": int(tp),
        "FP": int(fp),
        "FN": int(fn),
        "TN": int(tn),
        "recall": float(recall),
        "empirical_fdr": float(empirical_fdr)
    }

def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    with TeeLogger(log_path):
        print(f"{'='*60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Hypothesis: hypotheses/H1_bh_correction_baseline.md")
        print(f"{'='*60}")
        print()

        # 1. Generate Synthetic Data
        print(f"Generating synthetic data: {N_PROTEINS} proteins, {N_REPLICATES} control & {N_REPLICATES} treated replicates.")
        print(f"Planted DE proteins: {N_PLANTED_DE} (50 up-regulated, 50 down-regulated by log2 FC = ±{PLANTED_LOG2_FC}).")
        print(f"Measurement noise SD: {MEASUREMENT_NOISE_SD} on log2 scale.")
        print(f"Random seed set to: {RANDOM_SEED}")
        print()
        
        df, metadata = generate_synthetic_data(RANDOM_SEED)
        
        # Save synthetic data for traceability
        data_dir = PROJECT_ROOT / "data" / "synthetic"
        data_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(data_dir / "synthetic_abundance.csv")
        metadata.to_csv(data_dir / "synthetic_metadata.csv")
        print(f"Saved synthetic abundance to {data_dir / 'synthetic_abundance.csv'}")
        print()

        # 2. Perform Differential Abundance Analysis
        print("Running Welch's t-test per protein...")
        results = run_de_analysis(df)
        print("Completed t-tests.")
        print()
        
        # 3. Apply Benjamini-Hochberg Correction
        print("Applying Benjamini-Hochberg FDR correction...")
        reject, q_values, _, _ = multitest.multipletests(
            results["p_value"], 
            alpha=FDR_THRESHOLD, 
            method="fdr_bh"
        )
        results["q_value"] = q_values
        print(f"Completed BH correction (target FDR threshold: {FDR_THRESHOLD}).")
        print()

        # 4. Compute Metrics
        print("=== EVALUATION METRICS ===")
        
        # Case A: Uncorrected p-value threshold < 0.05
        uncorrected_metrics = compute_metrics(results, metadata, "p_value", FDR_THRESHOLD, is_corrected=False)
        print("Uncorrected p-value < 0.05:")
        print(f"  Called Significant: {uncorrected_metrics['called_total']}")
        print(f"  True Positives (TP): {uncorrected_metrics['TP']}")
        print(f"  False Positives (FP): {uncorrected_metrics['FP']}  <-- Multiple testing problem visible here!")
        print(f"  Recall (Sensitivity): {uncorrected_metrics['recall']:.2%}")
        print(f"  Observed FDR: {uncorrected_metrics['empirical_fdr']:.2%}")
        print()

        # Case B: BH-corrected q-value threshold < 0.05
        corrected_metrics = compute_metrics(results, metadata, "q_value", FDR_THRESHOLD, is_corrected=True)
        print("BH-corrected q-value < 0.05:")
        print(f"  Called Significant: {corrected_metrics['called_total']}")
        print(f"  True Positives (TP): {corrected_metrics['TP']}")
        print(f"  False Positives (FP): {corrected_metrics['FP']}")
        print(f"  Recall (Sensitivity): {corrected_metrics['recall']:.2%}")
        print(f"  Observed FDR: {corrected_metrics['empirical_fdr']:.2%}")
        print()

        # 5. Volcano Plot Visualization
        print("Generating Volcano Plot...")
        plt.figure(figsize=(10, 8), dpi=300)
        
        log_fc = results["log2_fc"].values
        neg_log_p = -np.log10(results["p_value"].values)
        is_planted_arr = metadata["is_planted"].values
        q_vals = results["q_value"].values
        
        # Plot points:
        # Non-DE background
        plt.scatter(log_fc[~is_planted_arr & (q_vals >= FDR_THRESHOLD)], 
                    neg_log_p[~is_planted_arr & (q_vals >= FDR_THRESHOLD)], 
                    c='lightgrey', alpha=0.6, edgecolors='none', label='Null / Non-Significant', s=15)
        
        # False Positives (Null, but called significant by q-value < 0.05)
        plt.scatter(log_fc[~is_planted_arr & (q_vals < FDR_THRESHOLD)], 
                    neg_log_p[~is_planted_arr & (q_vals < FDR_THRESHOLD)], 
                    c='orange', alpha=0.8, edgecolors='black', label='False Positives (BH < 0.05)', s=40)
        
        # True Positives (Planted, called significant)
        plt.scatter(log_fc[is_planted_arr & (q_vals < FDR_THRESHOLD)], 
                    neg_log_p[is_planted_arr & (q_vals < FDR_THRESHOLD)], 
                    c='crimson', alpha=0.8, edgecolors='black', label='Planted True Positives (Called DE)', s=60)
        
        # Planted, but NOT called significant (False Negatives)
        plt.scatter(log_fc[is_planted_arr & (q_vals >= FDR_THRESHOLD)], 
                    neg_log_p[is_planted_arr & (q_vals >= FDR_THRESHOLD)], 
                    c='blue', alpha=0.8, edgecolors='black', label='Planted True Positives (Not Called)', s=60)
        
        # Formatting
        plt.axhline(-np.log10(FDR_THRESHOLD), color='blue', linestyle='--', alpha=0.5, label='p = 0.05')
        
        # Find the actual p-value cutoff for BH q < 0.05
        sig_results = results[results["q_value"] < FDR_THRESHOLD]
        if len(sig_results) > 0:
            max_p_at_q = sig_results["p_value"].max()
            plt.axhline(-np.log10(max_p_at_q), color='red', linestyle='--', alpha=0.7, 
                        label=f'BH FDR q = 0.05 (p ≈ {max_p_at_q:.4f})')
        
        plt.axvline(0, color='black', alpha=0.3)
        plt.axvline(PLANTED_LOG2_FC, color='darkgreen', linestyle=':', alpha=0.5, label='Planted FC threshold')
        plt.axvline(-PLANTED_LOG2_FC, color='darkgreen', linestyle=':', alpha=0.5)
        
        plt.xlabel("log2 Fold Change (Treated - Control)")
        plt.ylabel("-log10 p-value")
        plt.title(f"Volcano Plot: {N_PROTEINS} Proteins (Planted DE: {N_PLANTED_DE})")
        plt.legend(loc='upper right', bbox_to_anchor=(1.0, 1.0), fontsize=9)
        plt.grid(True, alpha=0.2)
        
        fig_path = FIGURE_DIR / f"{SCRIPT_NAME}_volcano.png"
        plt.savefig(fig_path, bbox_inches='tight', dpi=300)
        plt.close()
        
        print(f"Saved Volcano Plot to {fig_path}")
        print()

        # Save results matrix for tracking
        results_df = results.join(metadata)
        results_dir = PROJECT_ROOT / "results"
        results_df.to_csv(results_dir / f"{SCRIPT_NAME}_results.csv")
        print(f"Saved DE results matrix to {results_dir / f'{SCRIPT_NAME}_results.csv'}")
        print()

        # Verify Hypothesis Support Status
        print("=== HYPOTHESIS ASSESSMENT ===")
        fdr_ok = (corrected_metrics['empirical_fdr'] <= FDR_THRESHOLD)
        recall_ok = (corrected_metrics['recall'] >= 0.70)
        uncorrected_fdr_bad = (uncorrected_metrics['empirical_fdr'] > 0.40)
        
        print(f"FDR Controlled (<= 0.05)? {fdr_ok} (Observed: {corrected_metrics['empirical_fdr']:.2%})")
        print(f"Recall High (>= 70%)? {recall_ok} (Observed: {corrected_metrics['recall']:.2%})")
        print(f"Uncorrected FDR High (> 40%)? {uncorrected_fdr_bad} (Observed: {uncorrected_metrics['empirical_fdr']:.2%})")
        
        if fdr_ok and recall_ok and uncorrected_fdr_bad:
            print("Status: SUPPORTED")
        else:
            print("Status: PARTIALLY SUPPORTED")
        
        print()
        print(f"{'='*60}")
        print("=== COMPLETE ===")
        print(f"{'='*60}")

if __name__ == "__main__":
    main()

# ==============================================================================
# PASTED SCRIPT OUTPUT (To be populated after execution)
# ==============================================================================
# <PASTED_OUTPUT>
# ============================================================
# Script: script_01_bh_correction
# Timestamp: 2026-06-30T11:00:58.152432
# Hypothesis: hypotheses/H1_bh_correction_baseline.md
# ============================================================
#
# Generating synthetic data: 2000 proteins, 5 control & 5 treated replicates.
# Planted DE proteins: 100 (50 up-regulated, 50 down-regulated by log2 FC = ±1.0).
# Measurement noise SD: 0.3 on log2 scale.
# Random seed set to: 1024
#
# Saved synthetic abundance to ./proteomics_de/proteomics_de/data/synthetic/synthetic_abundance.csv
#
# Running Welch's t-test per protein...
# Completed t-tests.
#
# Applying Benjamini-Hochberg FDR correction...
# Completed BH correction (target FDR threshold: 0.05).
#
# === EVALUATION METRICS ===
# Uncorrected p-value < 0.05:
#   Called Significant: 186
#   True Positives (TP): 98
#   False Positives (FP): 88  <-- Multiple testing problem visible here!
#   Recall (Sensitivity): 98.00%
#   Observed FDR: 47.31%
#
# BH-corrected q-value < 0.05:
#   Called Significant: 37
#   True Positives (TP): 36
#   False Positives (FP): 1
#   Recall (Sensitivity): 36.00%
#   Observed FDR: 2.70%
#
# Generating Volcano Plot...
# Saved Volcano Plot to ./proteomics_de/proteomics_de/results/figures/script_01_bh_correction_volcano.png
#
# Saved DE results matrix to ./proteomics_de/proteomics_de/results/script_01_bh_correction_results.csv
#
# === HYPOTHESIS ASSESSMENT ===
# FDR Controlled (<= 0.05)? True (Observed: 2.70%)
# Recall High (>= 70%)? False (Observed: 36.00%)
# Uncorrected FDR High (> 40%)? True (Observed: 47.31%)
# Status: PARTIALLY SUPPORTED
#
# ============================================================
# === COMPLETE ===
# ============================================================
# </PASTED_OUTPUT>
