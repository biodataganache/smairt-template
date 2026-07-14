#!/usr/bin/env python3
"""
Script 02: Multi-Variable Parameter Sweep

Hypothesis: hypotheses/H2_parameter_sweep.md
Phase: synthetic
Track: None
Iteration: 2

Depends on:
  - script_01_bh_correction.py (builds on the baseline generation and testing)
"""

import sys
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.stats.multitest as multitest
import matplotlib.pyplot as plt
import seaborn as sns

# === PATH SETUP ===
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

# === CONFIGURATION ===
SCRIPT_NAME = "script_02_parameter_sweep"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"

# Constant Parameters
N_PROTEINS = 2000
N_PLANTED_DE = 100
PLANTED_LOG2_FC = 1.0  # ~2x fold change
FDR_THRESHOLD = 0.05
RANDOM_SEED = 1024

# Parameter Sweep Grid (As modified per user request)
REPLICATE_SIZES = [3, 4, 5, 6, 8, 12, 15]
NOISE_LEVELS = [0.1, 0.2, 0.3, 0.4, 0.5]

def generate_synthetic_data(n_replicates, noise_sd, seed=RANDOM_SEED):
    """
    Generate synthetic proteomics abundance matrix for a specific N and noise level.
    """
    np.random.seed(seed)
    
    # 1. Base log2 intensities
    base_expression = np.random.normal(loc=20.0, scale=1.5, size=(N_PROTEINS, 1))
    
    # 2. Control samples
    control_data = base_expression + np.random.normal(loc=0.0, scale=noise_sd, size=(N_PROTEINS, n_replicates))
    
    # 3. Treated samples
    treated_data = base_expression + np.random.normal(loc=0.0, scale=noise_sd, size=(N_PROTEINS, n_replicates))
    
    # Plant the DE effects (50 up, 50 down)
    is_planted = np.zeros(N_PROTEINS, dtype=bool)
    
    # Up-regulated
    treated_data[0:50, :] += PLANTED_LOG2_FC
    is_planted[0:50] = True
    
    # Down-regulated
    treated_data[50:100, :] -= PLANTED_LOG2_FC
    is_planted[50:100] = True
    
    # Combine into dataframes
    col_names = [f"Ctrl_Rep{i+1}" for i in range(n_replicates)] + [f"Treat_Rep{i+1}" for i in range(n_replicates)]
    df = pd.DataFrame(np.hstack([control_data, treated_data]), columns=col_names)
    df.index = [f"Prot_{i+1:04d}" for i in range(N_PROTEINS)]
    
    metadata = pd.DataFrame({"is_planted": is_planted}, index=df.index)
    
    return df, metadata

def run_de_analysis(df):
    """
    Run Welch's t-test per protein and calculate log2 fold change.
    """
    ctrl_cols = [col for col in df.columns if "Ctrl" in col]
    treat_cols = [col for col in df.columns if "Treat" in col]
    
    p_values = []
    log2_fcs = []
    
    # Convert to numpy for fast execution
    ctrl_mat = df[ctrl_cols].values
    treat_mat = df[treat_cols].values
    
    # Welch's t-test (equal_var=False) across all rows
    # stats.ttest_ind can operate on matrices (axis=1)
    t_stats, p_vals = stats.ttest_ind(treat_mat, ctrl_mat, axis=1, equal_var=False)
    log2_fcs = np.mean(treat_mat, axis=1) - np.mean(ctrl_mat, axis=1)
    
    results = pd.DataFrame({
        "log2_fc": log2_fcs,
        "p_value": p_vals
    }, index=df.index)
    
    return results

def evaluate_metrics(results, metadata):
    """
    Apply BH correction and evaluate recall and empirical FDR.
    """
    reject, q_values, _, _ = multitest.multipletests(
        results["p_value"], 
        alpha=FDR_THRESHOLD, 
        method="fdr_bh"
    )
    
    called_sig = q_values < FDR_THRESHOLD
    is_planted = metadata["is_planted"].values
    
    tp = np.sum(called_sig & is_planted)
    fp = np.sum(called_sig & ~is_planted)
    fn = np.sum(~called_sig & is_planted)
    
    called_total = tp + fp
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    empirical_fdr = fp / called_total if called_total > 0 else 0.0
    
    return tp, fp, recall, empirical_fdr

def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    with TeeLogger(log_path):
        print(f"{'='*60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Hypothesis: hypotheses/H2_parameter_sweep.md")
        print(f"{'='*60}")
        print()

        print("Starting Multi-Variable Parameter Sweep...")
        print(f"Sweep Grid: Replicates N in {REPLICATE_SIZES}")
        print(f"Sweep Grid: Measurement noise SD in {NOISE_LEVELS}")
        print(f"Planted DE proteins: {N_PLANTED_DE} | Planted fold change: ±{PLANTED_LOG2_FC}")
        print(f"Total proteins: {N_PROTEINS} | BH Target FDR: {FDR_THRESHOLD}")
        print()

        sweep_records = []
        
        # Run parameter sweep grid search
        for n_rep in REPLICATE_SIZES:
            for noise in NOISE_LEVELS:
                # Generate synthetic data
                df, metadata = generate_synthetic_data(n_rep, noise)
                
                # Perform differential expression analysis (Welch's t-test)
                results = run_de_analysis(df)
                
                # Compute recall and empirical FDR
                tp, fp, recall, empirical_fdr = evaluate_metrics(results, metadata)
                
                record = {
                    "replicates_N": n_rep,
                    "noise_SD": noise,
                    "TP": tp,
                    "FP": fp,
                    "recall": recall,
                    "empirical_fdr": empirical_fdr
                }
                sweep_records.append(record)
                
                print(f"N={n_rep:02d}, Noise={noise:.1f} | TP={tp:03d}, FP={fp:02d} | Recall={recall:.2%}, Observed FDR={empirical_fdr:.2%}")
        
        print()
        print("Grid search complete. Processing results for visualization...")
        
        # Process results into DataFrames
        sweep_df = pd.DataFrame(sweep_records)
        results_dir = PROJECT_ROOT / "results"
        sweep_df.to_csv(results_dir / f"{SCRIPT_NAME}_results.csv", index=False)
        print(f"Saved sweep results table to {results_dir / f'{SCRIPT_NAME}_results.csv'}")
        
        # 1. Pivot for heatmaps
        recall_pivot = sweep_df.pivot(index="noise_SD", columns="replicates_N", values="recall")
        fdr_pivot = sweep_df.pivot(index="noise_SD", columns="replicates_N", values="empirical_fdr")
        
        # Plot Heatmaps
        sns.set_theme(style="white")
        
        # Recall Heatmap
        plt.figure(figsize=(10, 8), dpi=300)
        ax = sns.heatmap(
            recall_pivot * 100, 
            annot=True, 
            fmt=".1f", 
            cmap="YlGnBu", 
            cbar_kws={'label': 'Recall (%)'},
            linewidths=0.5
        )
        # Highlight regions of high power (>= 70%) with a red line or standard labels
        plt.title(f"Statistical Power (Recall %) Sweep\n(Planted DE: {N_PLANTED_DE}, FC = ±1.0, Target FDR = 0.05)", fontsize=12, fontweight='bold')
        plt.xlabel("Replicates per Group (N)")
        plt.ylabel("Measurement Noise SD (log2 scale)")
        ax.invert_yaxis() # Invert y-axis so noise goes from low to high
        
        fig_recall_path = FIGURE_DIR / f"{SCRIPT_NAME}_recall_heatmap.png"
        plt.savefig(fig_recall_path, bbox_inches='tight', dpi=300)
        plt.close()
        print(f"Saved Recall Heatmap to {fig_recall_path}")
        
        # FDR Heatmap
        plt.figure(figsize=(10, 8), dpi=300)
        ax = sns.heatmap(
            fdr_pivot * 100, 
            annot=True, 
            fmt=".2f", 
            cmap="OrRd", 
            cbar_kws={'label': 'Observed FDR (%)'},
            linewidths=0.5,
            vmax=5.0  # Anchor max at 5% target to easily identify any escape
        )
        plt.title(f"Empirical False Discovery Rate (FDR %) Sweep\n(Planted DE: {N_PLANTED_DE}, Target FDR = 5.0%)", fontsize=12, fontweight='bold')
        plt.xlabel("Replicates per Group (N)")
        plt.ylabel("Measurement Noise SD (log2 scale)")
        ax.invert_yaxis()
        
        fig_fdr_path = FIGURE_DIR / f"{SCRIPT_NAME}_fdr_heatmap.png"
        plt.savefig(fig_fdr_path, bbox_inches='tight', dpi=300)
        plt.close()
        print(f"Saved FDR Heatmap to {fig_fdr_path}")
        print()

        # Check hypothesis expectations
        print("=== EVALUATION OF DESIGN ENVELOPES ===")
        # Check FDR Control across all cells
        max_observed_fdr = sweep_df["empirical_fdr"].max()
        fdr_under_control = max_observed_fdr <= FDR_THRESHOLD
        print(f"1. FDR Controlled globally (<= 5.0%)? {fdr_under_control} (Max Observed: {max_observed_fdr:.2%})")
        
        # Check Recall for N >= 8 and SD = 0.3
        recall_at_n8_sd03 = sweep_df[(sweep_df["replicates_N"] == 8) & (sweep_df["noise_SD"] == 0.3)]["recall"].values[0]
        recall_n8_ok = recall_at_n8_sd03 >= 0.70
        print(f"2. Recall High (>= 70%) at N=8, SD=0.3? {recall_n8_ok} (Observed: {recall_at_n8_sd03:.2%})")
        
        # Check Recall for N = 5, SD = 0.2
        recall_at_n5_sd02 = sweep_df[(sweep_df["replicates_N"] == 5) & (sweep_df["noise_SD"] == 0.2)]["recall"].values[0]
        recall_n5_ok = recall_at_n5_sd02 >= 0.70
        print(f"3. Recall High (>= 70%) at N=5, SD=0.2? {recall_n5_ok} (Observed: {recall_at_n5_sd02:.2%})")
        
        # Check Recall for N = 6, SD = 0.2
        recall_at_n6_sd02 = sweep_df[(sweep_df["replicates_N"] == 6) & (sweep_df["noise_SD"] == 0.2)]["recall"].values[0]
        recall_n6_ok = recall_at_n6_sd02 >= 0.70
        print(f"4. Recall High (>= 70%) at N=6, SD=0.2? {recall_n6_ok} (Observed: {recall_at_n6_sd02:.2%})")

        # Check Recall for N = 3, SD = 0.2
        recall_at_n3_sd02 = sweep_df[(sweep_df["replicates_N"] == 3) & (sweep_df["noise_SD"] == 0.2)]["recall"].values[0]
        recall_n3_low = recall_at_n3_sd02 < 0.70
        print(f"5. Recall Low (< 70%) at N=3, SD=0.2? {recall_n3_low} (Observed: {recall_at_n3_sd02:.2%})")
        
        # Overall hypothesis assessment
        all_hypotheses_met = fdr_under_control and recall_n8_ok and recall_n5_ok and recall_n6_ok and recall_n3_low
        print()
        print("=== HYPOTHESIS ASSESSMENT ===")
        if all_hypotheses_met:
            print("Status: SUPPORTED")
        else:
            print("Status: PARTIALLY SUPPORTED or REFUTED (Check parameters)")
            
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
# Script: script_02_parameter_sweep
# Timestamp: 2026-06-30T11:10:10.309504
# Hypothesis: hypotheses/H2_parameter_sweep.md
# ============================================================
#
# Starting Multi-Variable Parameter Sweep...
# Sweep Grid: Replicates N in [3, 4, 5, 6, 8, 12, 15]
# Sweep Grid: Measurement noise SD in [0.1, 0.2, 0.3, 0.4, 0.5]
# Planted DE proteins: 100 | Planted fold change: ±1.0
# Total proteins: 2000 | BH Target FDR: 0.05
#
# N=03, Noise=0.1 | TP=081, FP=02 | Recall=81.00%, Observed FDR=2.41%
# N=03, Noise=0.2 | TP=000, FP=00 | Recall=0.00%, Observed FDR=0.00%
# N=03, Noise=0.3 | TP=000, FP=00 | Recall=0.00%, Observed FDR=0.00%
# N=03, Noise=0.4 | TP=000, FP=00 | Recall=0.00%, Observed FDR=0.00%
# N=03, Noise=0.5 | TP=000, FP=00 | Recall=0.00%, Observed FDR=0.00%
# N=04, Noise=0.1 | TP=100, FP=02 | Recall=100.00%, Observed FDR=1.96%
# N=04, Noise=0.2 | TP=069, FP=02 | Recall=69.00%, Observed FDR=2.82%
# N=04, Noise=0.3 | TP=011, FP=01 | Recall=11.00%, Observed FDR=8.33%
# N=04, Noise=0.4 | TP=002, FP=00 | Recall=2.00%, Observed FDR=0.00%
# N=04, Noise=0.5 | TP=002, FP=00 | Recall=2.00%, Observed FDR=0.00%
# N=05, Noise=0.1 | TP=100, FP=03 | Recall=100.00%, Observed FDR=2.91%
# N=05, Noise=0.2 | TP=095, FP=03 | Recall=95.00%, Observed FDR=3.06%
# N=05, Noise=0.3 | TP=036, FP=01 | Recall=36.00%, Observed FDR=2.70%
# N=05, Noise=0.4 | TP=004, FP=00 | Recall=4.00%, Observed FDR=0.00%
# N=05, Noise=0.5 | TP=000, FP=00 | Recall=0.00%, Observed FDR=0.00%
# N=06, Noise=0.1 | TP=100, FP=02 | Recall=100.00%, Observed FDR=1.96%
# N=06, Noise=0.2 | TP=100, FP=02 | Recall=100.00%, Observed FDR=1.96%
# N=06, Noise=0.3 | TP=087, FP=01 | Recall=87.00%, Observed FDR=1.14%
# N=06, Noise=0.4 | TP=038, FP=00 | Recall=38.00%, Observed FDR=0.00%
# N=06, Noise=0.5 | TP=000, FP=00 | Recall=0.00%, Observed FDR=0.00%
# N=08, Noise=0.1 | TP=100, FP=07 | Recall=100.00%, Observed FDR=6.54%
# N=08, Noise=0.2 | TP=100, FP=07 | Recall=100.00%, Observed FDR=6.54%
# N=08, Noise=0.3 | TP=097, FP=07 | Recall=97.00%, Observed FDR=6.73%
# N=08, Noise=0.4 | TP=082, FP=04 | Recall=82.00%, Observed FDR=4.65%
# N=08, Noise=0.5 | TP=057, FP=03 | Recall=57.00%, Observed FDR=5.00%
# N=12, Noise=0.1 | TP=100, FP=03 | Recall=100.00%, Observed FDR=2.91%
# N=12, Noise=0.2 | TP=100, FP=03 | Recall=100.00%, Observed FDR=2.91%
# N=12, Noise=0.3 | TP=100, FP=03 | Recall=100.00%, Observed FDR=2.91%
# N=12, Noise=0.4 | TP=100, FP=03 | Recall=100.00%, Observed FDR=2.91%
# N=12, Noise=0.5 | TP=089, FP=03 | Recall=89.00%, Observed FDR=3.26%
# N=15, Noise=0.1 | TP=100, FP=02 | Recall=100.00%, Observed FDR=1.96%
# N=15, Noise=0.2 | TP=100, FP=02 | Recall=100.00%, Observed FDR=1.96%
# N=15, Noise=0.3 | TP=100, FP=02 | Recall=100.00%, Observed FDR=1.96%
# N=15, Noise=0.4 | TP=100, FP=02 | Recall=100.00%, Observed FDR=1.96%
# N=15, Noise=0.5 | TP=098, FP=02 | Recall=98.00%, Observed FDR=2.00%
#
# Grid search complete. Processing results for visualization...
# Saved sweep results table to ./proteomics_de/proteomics_de/results/script_02_parameter_sweep_results.csv
# Saved Recall Heatmap to ./proteomics_de/proteomics_de/results/figures/script_02_parameter_sweep_recall_heatmap.png
# Saved FDR Heatmap to ./proteomics_de/proteomics_de/results/figures/script_02_parameter_sweep_fdr_heatmap.png
#
# === EVALUATION OF DESIGN ENVELOPES ===
# 1. FDR Controlled globally (<= 5.0%)? False (Max Observed: 8.33%)
# 2. Recall High (>= 70%) at N=8, SD=0.3? True (Observed: 97.00%)
# 3. Recall High (>= 70%) at N=5, SD=0.2? True (Observed: 95.00%)
# 4. Recall High (>= 70%) at N=6, SD=0.2? True (Observed: 100.00%)
# 5. Recall Low (< 70%) at N=3, SD=0.2? True (Observed: 0.00%)
#
# === HYPOTHESIS ASSESSMENT ===
# Status: PARTIALLY SUPPORTED or REFUTED (Check parameters)
#
# ============================================================
# === COMPLETE ===
# ============================================================
# </PASTED_OUTPUT>
