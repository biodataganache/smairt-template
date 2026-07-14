#!/usr/bin/env python3
"""
Script 03: Missingness and Heteroscedasticity Impact

Hypothesis: hypotheses/H3_missingness_heteroscedasticity.md
Phase: synthetic
Track: None
Iteration: 3

Depends on:
  - script_02_parameter_sweep.py (builds on the baseline design envelopes)
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
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

# === CONFIGURATION ===
SCRIPT_NAME = "script_03_missingness_heteroscedasticity"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"

N_PROTEINS = 2000
N_PLANTED_DE = 100
PLANTED_LOG2_FC = 1.0
FDR_THRESHOLD = 0.05
RANDOM_SEED = 1024

# LOD Parameters
LOD_THRESHOLD = 17.5  # 50% detection probability threshold
LOD_SLOPE = 1.5       # Slope of the logistic decay

def generate_heteroscedastic_data(n_replicates, noise_base, seed=RANDOM_SEED):
    """
    Generate synthetic proteomics abundance matrix with heteroscedastic noise.
    """
    np.random.seed(seed)
    
    # 1. Base log2 intensities
    base_expression = np.random.normal(loc=20.0, scale=1.5, size=(N_PROTEINS, 1))
    
    # 2. Compute protein-specific noise SD based on abundance
    # Standard deviation scales inversely with abundance:
    # A = 24.0 -> SD = noise_base
    # A = 14.0 -> SD = 3.0 * noise_base
    noise_sd_vector = noise_base * (1.0 + np.maximum(0.0, (24.0 - base_expression) / 5.0))
    
    # 3. Control samples: base expression + heteroscedastic noise
    control_data = base_expression + np.random.normal(loc=0.0, scale=noise_sd_vector, size=(N_PROTEINS, n_replicates))
    
    # 4. Treated samples: base expression + planted DE + heteroscedastic noise
    treated_data = base_expression + np.random.normal(loc=0.0, scale=noise_sd_vector, size=(N_PROTEINS, n_replicates))
    
    is_planted = np.zeros(N_PROTEINS, dtype=bool)
    planted_direction = np.zeros(N_PROTEINS, dtype=float)
    
    # Up-regulated (0 to 50)
    treated_data[0:50, :] += PLANTED_LOG2_FC
    is_planted[0:50] = True
    planted_direction[0:50] = PLANTED_LOG2_FC
    
    # Down-regulated (50 to 100)
    treated_data[50:100, :] -= PLANTED_LOG2_FC
    is_planted[50:100] = True
    planted_direction[50:100] = -PLANTED_LOG2_FC
    
    col_names = [f"Ctrl_Rep{i+1}" for i in range(n_replicates)] + [f"Treat_Rep{i+1}" for i in range(n_replicates)]
    df = pd.DataFrame(np.hstack([control_data, treated_data]), columns=col_names)
    df.index = [f"Prot_{i+1:04d}" for i in range(N_PROTEINS)]
    
    metadata = pd.DataFrame({
        "is_planted": is_planted,
        "planted_fc": planted_direction,
        "base_expression": base_expression.flatten(),
        "noise_sd": noise_sd_vector.flatten()
    }, index=df.index)
    
    return df, metadata

def apply_limit_of_detection(df, seed=RANDOM_SEED):
    """
    Apply logistic limit of detection (LOD) curve to generate MNAR missingness.
    Values below detection limit are set to NaN.
    """
    np.random.seed(seed)
    df_missing = df.copy()
    
    # Calculate probability of detection logistically
    p_detect = 1.0 / (1.0 + np.exp(-LOD_SLOPE * (df_missing.values - LOD_THRESHOLD)))
    
    # Generate random mask based on detection probability
    random_draws = np.random.uniform(0.0, 1.0, size=df_missing.shape)
    undetected_mask = random_draws > p_detect
    
    # Set undetected values to NaN
    df_missing_vals = df_missing.values
    df_missing_vals[undetected_mask] = np.nan
    df_missing = pd.DataFrame(df_missing_vals, columns=df.columns, index=df.index)
    
    return df_missing

def impute_mindet(df):
    """
    Impute NaN values with simulated local minimum (MinDet).
    Defined as the 1st percentile of detected intensities minus 1.5 * SD of detected intensities.
    """
    df_imputed = df.copy()
    detected_vals = df_imputed.values[~np.isnan(df_imputed.values)]
    
    # Calculate local minimum target
    pct_1 = np.percentile(detected_vals, 1)
    sd_detected = np.std(detected_vals)
    mindet_value = pct_1 - 1.5 * sd_detected
    
    # Fill NaNs
    df_imputed = df_imputed.fillna(mindet_value)
    return df_imputed

def run_de_analysis_with_missingness(df, filter_threshold=None):
    """
    Run Welch's t-test per protein.
    If filter_threshold is set, discard proteins with fewer valid replicates.
    """
    ctrl_cols = [col for col in df.columns if "Ctrl" in col]
    treat_cols = [col for col in df.columns if "Treat" in col]
    
    p_values = []
    log2_fcs = []
    
    for idx, row in df.iterrows():
        ctrl_vals = row[ctrl_cols].values
        treat_vals = row[treat_cols].values
        
        # Remove NaNs for t-test
        ctrl_clean = ctrl_vals[~np.isnan(ctrl_vals)]
        treat_clean = treat_vals[~np.isnan(treat_vals)]
        
        # Apply replica filter if specified
        if filter_threshold is not None:
            if len(ctrl_clean) < filter_threshold or len(treat_clean) < filter_threshold:
                p_values.append(np.nan)
                log2_fcs.append(np.nan)
                continue
                
        # Welch's t-test (only run if we have at least 2 valid values in each group to compute variance)
        if len(ctrl_clean) >= 2 and len(treat_clean) >= 2:
            _, p_val = stats.ttest_ind(treat_clean, ctrl_clean, equal_var=False)
            log2_fc = np.mean(treat_clean) - np.mean(ctrl_clean)
        else:
            p_val = np.nan
            log2_fc = np.nan
            
        p_values.append(p_val)
        log2_fcs.append(log2_fc)
        
    results = pd.DataFrame({
        "log2_fc": log2_fcs,
        "p_value": p_values
    }, index=df.index)
    
    return results

def compute_metrics(results, metadata, alpha=FDR_THRESHOLD):
    """
    Evaluate TP, FP, Recall, and Empirical FDR.
    """
    # Exclude NaNs from BH correction (proteins filtered out)
    valid_mask = ~results["p_value"].isna()
    valid_results = results[valid_mask].copy()
    
    if len(valid_results) == 0:
        return 0, 0, 0, 0.0, 0.0
        
    reject, q_values, _, _ = multitest.multipletests(
        valid_results["p_value"], 
        alpha=alpha, 
        method="fdr_bh"
    )
    
    valid_results["q_value"] = q_values
    
    # Map back to full proteins
    full_q_values = pd.Series(np.nan, index=results.index)
    full_q_values[valid_mask] = q_values
    
    called_sig = full_q_values < alpha
    is_planted = metadata["is_planted"]
    
    tp = np.sum(called_sig & is_planted)
    fp = np.sum(called_sig & ~is_planted)
    fn = np.sum(~called_sig & is_planted)
    
    called_total = tp + fp
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    empirical_fdr = fp / called_total if called_total > 0 else 0.0
    
    # Store q_values in results
    results["q_value"] = full_q_values
    
    return int(tp), int(fp), int(called_total), float(recall), float(empirical_fdr)

def generate_validation_plots(metadata, df_missing):
    """
    Save diagnostics for heteroscedasticity and logistic detection probability curves.
    """
    # 1. Heteroscedasticity plot
    plt.figure(figsize=(8, 6), dpi=300)
    plt.scatter(metadata["base_expression"], metadata["noise_sd"], c='teal', alpha=0.5, s=15)
    plt.xlabel("Base Protein Abundance (log2 scale)")
    plt.ylabel("Measurement Noise SD")
    plt.title("Heteroscedastic Noise Profile (Noise SD vs. Abundance)")
    plt.grid(True, alpha=0.2)
    fig_path1 = FIGURE_DIR / "script_03_heteroscedasticity_noise_vs_abundance.png"
    plt.savefig(fig_path1, bbox_inches='tight', dpi=300)
    plt.close()
    
    # 2. Limit of Detection plot
    plt.figure(figsize=(8, 6), dpi=300)
    # Re-draw the logistic detection curve
    xs = np.linspace(13.0, 24.0, 200)
    ys = 1.0 / (1.0 + np.exp(-LOD_SLOPE * (xs - LOD_THRESHOLD)))
    plt.plot(xs, ys * 100, color='crimson', linewidth=2.5, label='Logistic LOD Probability')
    
    # Calculate actual fraction detected per protein
    nan_fraction = df_missing.isna().mean(axis=1).values
    detected_fraction = (1.0 - nan_fraction) * 100
    plt.scatter(metadata["base_expression"], detected_fraction, color='grey', alpha=0.3, s=10, label='Actual Protein Detection %')
    
    plt.axvline(LOD_THRESHOLD, color='blue', linestyle='--', alpha=0.5, label=f'50% Detection limit (x = {LOD_THRESHOLD})')
    plt.xlabel("True Protein Intensity (log2 scale)")
    plt.ylabel("Detection Probability (%)")
    plt.title("Limit of Detection (LOD) Logistic Curve")
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.2)
    fig_path2 = FIGURE_DIR / "script_03_missingness_p_detection.png"
    plt.savefig(fig_path2, bbox_inches='tight', dpi=300)
    plt.close()

def plot_comparison_volcanos(oracle_res, imputed_res, filtered_res, metadata, title_suffix):
    """
    Plot three-panel volcano plot comparing the methods.
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True, dpi=300)
    methods_data = [
        ("A. Oracle (Heteroscedastic)", oracle_res),
        ("B. MinDet Imputation", imputed_res),
        ("C. Replica Filtering", filtered_res)
    ]
    
    is_planted = metadata["is_planted"].values
    
    for i, (method_name, res) in enumerate(methods_data):
        ax = axes[i]
        
        # Pull values
        log_fc = res["log2_fc"].values
        # Handle cases where p_value is NaN (filtered out)
        p_val = res["p_value"].values
        neg_log_p = -np.log10(p_val)
        neg_log_p[np.isnan(neg_log_p)] = 0.0  # Set NaNs to 0 for plotting
        
        q_val = res["q_value"].values
        
        # Null proteins (Non-significant)
        null_mask = ~is_planted & ((q_val >= FDR_THRESHOLD) | np.isnan(q_val))
        ax.scatter(log_fc[null_mask], neg_log_p[null_mask], c='lightgrey', alpha=0.5, s=15, edgecolors='none', label='Null / Non-Sig')
        
        # False Positives (Null, but q < 0.05)
        fp_mask = ~is_planted & (q_val < FDR_THRESHOLD)
        ax.scatter(log_fc[fp_mask], neg_log_p[fp_mask], c='orange', alpha=0.8, s=40, edgecolors='black', label='False Positives')
        
        # True Positives (Planted, called DE)
        tp_mask = is_planted & (q_val < FDR_THRESHOLD)
        ax.scatter(log_fc[tp_mask], neg_log_p[tp_mask], c='crimson', alpha=0.8, s=50, edgecolors='black', label='True Positives')
        
        # False Negatives (Planted, not called)
        fn_mask = is_planted & ((q_val >= FDR_THRESHOLD) | np.isnan(q_val))
        ax.scatter(log_fc[fn_mask], neg_log_p[fn_mask], c='blue', alpha=0.8, s=50, edgecolors='black', label='False Negatives')
        
        ax.axhline(-np.log10(FDR_THRESHOLD), color='blue', linestyle='--', alpha=0.5)
        ax.axvline(0, color='black', alpha=0.3)
        ax.axvline(PLANTED_LOG2_FC, color='darkgreen', linestyle=':', alpha=0.4)
        ax.axvline(-PLANTED_LOG2_FC, color='darkgreen', linestyle=':', alpha=0.4)
        
        ax.set_title(method_name, fontsize=11, fontweight='bold')
        ax.set_xlabel("log2 Fold Change")
        if i == 0:
            ax.set_ylabel("-log10 p-value")
            ax.legend(loc='upper right', fontsize=8)
            
        ax.grid(True, alpha=0.15)
        ax.set_xlim(-2.5, 2.5)
        
    plt.suptitle(f"Comparison of Missingness Handling Methods ({title_suffix})", fontsize=13, fontweight='bold', y=1.02)
    fig_path = FIGURE_DIR / f"script_03_volcano_comparison_{title_suffix.lower().replace(' ', '_')}.png"
    plt.savefig(fig_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Saved Comparison Volcano plot to {fig_path}")

def run_experiment_for_config(n_rep, noise_base, config_name):
    """
    Run the full analysis comparison for a specific configuration.
    """
    print(f"=== Running Experiment: {config_name} (N={n_rep}, Base Noise={noise_base}) ===")
    
    # 1. Generate heteroscedastic data (Oracle dataset)
    df_oracle, metadata = generate_heteroscedastic_data(n_rep, noise_base)
    oracle_res = run_de_analysis_with_missingness(df_oracle, filter_threshold=None)
    otp, ofp, ocall, orecall, ofdr = compute_metrics(oracle_res, metadata)
    
    # Generate diagnostic plots only for first run to avoid duplication
    if n_rep == 5:
        # Apply missingness
        df_missing_diag = apply_limit_of_detection(df_oracle)
        generate_validation_plots(metadata, df_missing_diag)
        
    # 2. Apply MNAR Limit of Detection
    df_missing = apply_limit_of_detection(df_oracle)
    
    # Count missing values
    missing_count = df_missing.isna().sum().sum()
    total_elements = df_missing.size
    print(f"  Missing values generated: {missing_count} out of {total_elements} cells ({missing_count / total_elements:.2%})")
    
    # Method B: MinDet Imputation
    df_imputed = impute_mindet(df_missing)
    imputed_res = run_de_analysis_with_missingness(df_imputed, filter_threshold=None)
    itp, ifp, icall, irecall, ifdr = compute_metrics(imputed_res, metadata)
    
    # Method C: Replica-Presence Filtering (Dynamic filter threshold)
    # Require N >= 3 for N=5, and N >= 4 for N=8
    filter_val = 3 if n_rep == 5 else 4
    print(f"  Replica filtering threshold: require >= {filter_val} detected values per group")
    
    filtered_res = run_de_analysis_with_missingness(df_missing, filter_threshold=filter_val)
    ftp, ffp, fcall, frecall, ffdr = compute_metrics(filtered_res, metadata)
    
    # Generate Volcano plots
    plot_comparison_volcanos(oracle_res, imputed_res, filtered_res, metadata, config_name)
    
    # Print individual summary
    print(f"  Oracle Baseline:         TP={otp:02d}, FP={ofp:02d} | Recall={orecall:.2%}, Observed FDR={ofdr:.2%}")
    print(f"  MinDet Imputation:       TP={itp:02d}, FP={ifp:02d} | Recall={irecall:.2%}, Observed FDR={ifdr:.2%}")
    print(f"  Replica Filtering:       TP={ftp:02d}, FP={ffp:02d} | Recall={frecall:.2%}, Observed FDR={ffdr:.2%}")
    print()
    
    return {
        "N": n_rep,
        "base_noise": noise_base,
        "oracle_recall": orecall, "oracle_fdr": ofdr,
        "mindet_recall": irecall, "mindet_fdr": ifdr, "mindet_FP": ifp,
        "filtered_recall": frecall, "filtered_fdr": ffdr, "filtered_FP": ffp
    }

def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)

    with TeeLogger(log_path):
        print(f"{'='*60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Hypothesis: hypotheses/H3_missingness_heteroscedasticity.md")
        print(f"{'='*60}")
        print()

        results_records = []
        
        # Config A: N=5, noise_base = 0.2
        res_a = run_experiment_for_config(5, 0.2, "Config A (N=5 Replicates)")
        results_records.append(res_a)
        
        # Config B: N=8, noise_base = 0.3
        res_b = run_experiment_for_config(8, 0.3, "Config B (N=8 Replicates)")
        results_records.append(res_b)
        
        # Save results matrix for tracking
        comp_df = pd.DataFrame(results_records)
        results_dir = PROJECT_ROOT / "results"
        comp_df.to_csv(results_dir / f"{SCRIPT_NAME}_comparison.csv", index=False)
        print(f"Saved comparative results table to {results_dir / f'{SCRIPT_NAME}_comparison.csv'}")
        print()
        
        # Hypothesis Testing Assertions
        print("=== HYPOTHESIS ASSESSMENT ===")
        
        # Assertion 1: MinDet Imputation Catastrophe (FDR exceeds 15% in both configs)
        mindet_fdr_a = res_a["mindet_fdr"]
        mindet_fdr_b = res_b["mindet_fdr"]
        fdr_exploded = (mindet_fdr_a >= 0.15) and (mindet_fdr_b >= 0.15)
        print(f"1. MinDet Imputation FDR exploded (>= 15.0%)?")
        print(f"   - Config A FDR: {mindet_fdr_a:.2%} (FP: {res_a['mindet_FP']})")
        print(f"   - Config B FDR: {mindet_fdr_b:.2%} (FP: {res_b['mindet_FP']})")
        print(f"   - Outcome: {fdr_exploded}")
        
        # Assertion 2: Filtering restores FDR control (FDR <= 5.0%)
        filtered_fdr_a = res_a["filtered_fdr"]
        filtered_fdr_b = res_b["filtered_fdr"]
        fdr_restored = (filtered_fdr_a <= 0.05) and (filtered_fdr_b <= 0.05)
        print(f"2. Replica Filtering restored FDR control (<= 5.0%)?")
        print(f"   - Config A FDR: {filtered_fdr_a:.2%} (FP: {res_a['filtered_FP']})")
        print(f"   - Config B FDR: {filtered_fdr_b:.2%} (FP: {res_b['filtered_FP']})")
        print(f"   - Outcome: {fdr_restored}")
        
        # Assertion 3: Heteroscedasticity Power Penalty (Oracle recall is lower than homoscedastic sweep recall by >= 15%)
        # Sweep recall: Config A (N=5, base=0.2) = 95.0% | Config B (N=8, base=0.3) = 97.0%
        penalty_a = 0.95 - res_a["oracle_recall"]
        penalty_b = 0.97 - res_b["oracle_recall"]
        power_penalized = (penalty_a >= 0.15) and (penalty_b >= 0.15)
        print(f"3. Heteroscedasticity caused overall Recall degradation (>= 15.0%)?")
        print(f"   - Config A: Oracle Recall {res_a['oracle_recall']:.2%} vs. Clean Baseline 95.00% (Loss: {penalty_a:.2%})")
        print(f"   - Config B: Oracle Recall {res_b['oracle_recall']:.2%} vs. Clean Baseline 97.00% (Loss: {penalty_b:.2%})")
        print(f"   - Outcome: {power_penalized}")
        
        # Assertion 4: Discarding low-abundance proteins under filtering adds recall penalty (filtered vs. oracle)
        filtering_recall_loss_a = res_a["oracle_recall"] - res_a["filtered_recall"]
        filtering_recall_loss_b = res_b["oracle_recall"] - res_b["filtered_recall"]
        filtering_loss_heavy = (filtering_recall_loss_a >= 0.10) or (filtering_recall_loss_b >= 0.10)
        print(f"4. Replica-Presence Filtering added additional Recall loss (>= 10.0%)?")
        print(f"   - Config A: Filtered Recall {res_a['filtered_recall']:.2%} vs. Oracle {res_a['oracle_recall']:.2%} (Loss: {filtering_recall_loss_a:.2%})")
        print(f"   - Config B: Filtered Recall {res_b['filtered_recall']:.2%} vs. Oracle {res_b['oracle_recall']:.2%} (Loss: {filtering_recall_loss_b:.2%})")
        print(f"   - Outcome: {filtering_loss_heavy}")
        
        print()
        if fdr_exploded and fdr_restored and power_penalized and filtering_loss_heavy:
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
# Script: script_03_missingness_heteroscedasticity
# Timestamp: 2026-06-30T11:17:24.611726
# Hypothesis: hypotheses/H3_missingness_heteroscedasticity.md
# ============================================================
#
# === Running Experiment: Config A (N=5 Replicates) (N=5, Base Noise=0.2) ===
#   Missing values generated: 2042 out of 20000 cells (10.21%)
#   Replica filtering threshold: require >= 3 detected values per group
# Saved Comparison Volcano plot to ./proteomics_de/proteomics_de/results/figures/script_03_volcano_comparison_config_a_(n=5_replicates).png
#   Oracle Baseline:         TP=23, FP=01 | Recall=23.00%, Observed FDR=4.17%
#   MinDet Imputation:       TP=05, FP=00 | Recall=5.00%, Observed FDR=0.00%
#   Replica Filtering:       TP=10, FP=00 | Recall=10.00%, Observed FDR=0.00%
#
# === Running Experiment: Config B (N=8 Replicates) (N=8, Base Noise=0.3) ===
#   Missing values generated: 3403 out of 32000 cells (10.63%)
#   Replica filtering threshold: require >= 4 detected values per group
# Saved Comparison Volcano plot to ./proteomics_de/proteomics_de/results/figures/script_03_volcano_comparison_config_b_(n=8_replicates).png
#   Oracle Baseline:         TP=50, FP=02 | Recall=50.00%, Observed FDR=3.85%
#   MinDet Imputation:       TP=30, FP=02 | Recall=30.00%, Observed FDR=6.25%
#   Replica Filtering:       TP=45, FP=02 | Recall=45.00%, Observed FDR=4.26%
#
# Saved comparative results table to ./proteomics_de/proteomics_de/results/script_03_missingness_heteroscedasticity_comparison.csv
#
# === HYPOTHESIS ASSESSMENT ===
# 1. MinDet Imputation FDR exploded (>= 15.0%)?
#    - Config A FDR: 0.00% (FP: 0)
#    - Config B FDR: 6.25% (FP: 2)
#    - Outcome: False
# 2. Replica Filtering restored FDR control (<= 5.0%)?
#    - Config A FDR: 0.00% (FP: 0)
#    - Config B FDR: 4.26% (FP: 2)
#    - Outcome: True
# 3. Heteroscedasticity caused overall Recall degradation (>= 15.0%)?
#    - Config A: Oracle Recall 23.00% vs. Clean Baseline 95.00% (Loss: 72.00%)
#    - Config B: Oracle Recall 50.00% vs. Clean Baseline 97.00% (Loss: 47.00%)
#    - Outcome: True
# 4. Replica-Presence Filtering added additional Recall loss (>= 10.0%)?
#    - Config A: Filtered Recall 10.00% vs. Oracle 23.00% (Loss: 13.00%)
#    - Config B: Filtered Recall 45.00% vs. Oracle 50.00% (Loss: 5.00%)
#    - Outcome: True
#
# Status: PARTIALLY SUPPORTED
#
# ============================================================
# === COMPLETE ===
# ============================================================
# </PASTED_OUTPUT>
