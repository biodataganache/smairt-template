#!/usr/bin/env python3
"""
Script 04: Comparative classification of real human proteins using whole-sequence vs. sliding-window hydropathy

Hypothesis: hypotheses/HYPOTHESIS_03.md
Phase: downloaded (Phase 2)
Track: Track A
Iteration: 3

Depends on:
  - data/downloaded/uniprot_benchmark.csv
  - hypotheses/HYPOTHESIS_03.md
  - scripts/shared/calculators.py
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# ML Imports
from sklearn.model_selection import LeaveOneOut
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# === PATH SETUP ===
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import (
    TeeLogger,
    setup_logging,
    calculate_molecular_weight,
    calculate_gravy,
    calculate_pi,
    KYTE_DOOLITTLE
)

# === SLIDING WINDOW CALCULATOR ===

def calculate_max_window_gravy(sequence: str, window_size: int = 19) -> float:
    """
    Calculate the maximum average hydropathy over a sliding window of a specified size.
    Allows localized hydrophobic segments (e.g. TM alpha-helices) to be captured
    without being diluted by surrounding hydrophilic soluble domains.
    """
    seq = sequence.strip().upper()
    if len(seq) < window_size:
        # If sequence is shorter than window, fall back to whole-sequence gravy
        return sum(KYTE_DOOLITTLE.get(aa, 0.0) for aa in seq) / len(seq) if seq else 0.0
        
    max_gravy = -999.0
    for i in range(len(seq) - window_size + 1):
        window = seq[i:i + window_size]
        window_gravy = sum(KYTE_DOOLITTLE.get(aa, 0.0) for aa in window) / window_size
        if window_gravy > max_gravy:
            max_gravy = window_gravy
            
    return max_gravy

# === MAIN COMPARISON PIPELINE ===

def main():
    script_name = "script_04_benchmark_classification"
    log_dir = PROJECT_ROOT / "results" / "logs"
    log_path = setup_logging(script_name, log_dir)

    with TeeLogger(log_path):
        print("=" * 70)
        print(f"Script: {script_name}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("Hypothesis: hypotheses/HYPOTHESIS_03.md")
        print("=" * 70)
        print()

        # === 1. LOAD BENCHMARK DATA ===
        csv_path = PROJECT_ROOT / "data" / "downloaded" / "uniprot_benchmark.csv"
        if not csv_path.exists():
            print(f"Error: Benchmark CSV not found at {csv_path}")
            sys.exit(1)
            
        df = pd.read_csv(csv_path)
        print(f"Loaded benchmark dataset with {len(df)} Human reviewed proteins.")
        print()

        # === 2. EXTRACT PROPERTIES ===
        print("--- Extracting Whole-Sequence & Sliding-Window Properties ---")
        df['molecular_weight'] = df['sequence'].apply(calculate_molecular_weight)
        df['pi'] = df['sequence'].apply(calculate_pi)
        df['whole_gravy'] = df['sequence'].apply(calculate_gravy)
        
        # Calculate maximum sliding-window hydropathy (window size 19)
        df['max_window_gravy'] = df['sequence'].apply(lambda s: calculate_max_window_gravy(s, window_size=19))
        
        # Print summary table of computed features
        print("Extracted Protein Sequence Features:")
        features_df = df[['accession', 'name', 'class_name', 'molecular_weight', 'pi', 'whole_gravy', 'max_window_gravy']]
        print(features_df.to_string(index=False))
        print()
        
        # Mean comparisons
        summary = df.groupby('class_name')[['whole_gravy', 'max_window_gravy']].mean()
        print("Property Averages by Biological Class:")
        print(summary.to_string())
        print()

        # === 3. EVALUATE CLASSIFIERS (Leave-One-Out CV) ===
        # Because we are working on a smaller reviewed benchmark set of 12 proteins,
        # Leave-One-Out Cross-Validation (LOOCV) is the rigorous scientific standard
        # to ensure that accuracy estimates are completely unbiased and stable.
        print("--- Running Leave-One-Out Cross-Validation ---")
        
        y = df['label'].values
        loo = LeaveOneOut()
        
        def run_loocv(feature_name: str) -> float:
            X_feat = df[[feature_name]].values
            y_preds = []
            
            for train_idx, test_idx in loo.split(X_feat):
                X_train, X_test = X_feat[train_idx], X_feat[test_idx]
                y_train, y_test = y[train_idx], y[test_idx]
                
                model = LogisticRegression()
                model.fit(X_train, y_train)
                
                y_preds.append(model.predict(X_test)[0])
                
            return accuracy_score(y, y_preds)
            
        acc_whole = run_loocv('whole_gravy')
        acc_window = run_loocv('max_window_gravy')
        acc_pi = run_loocv('pi')
        acc_mw = run_loocv('molecular_weight')
        
        print(f"LOOCV Accuracy - Whole-Sequence GRAVY : {acc_whole:.2%}")
        print(f"LOOCV Accuracy - Max Window GRAVY (19): {acc_window:.2%}")
        print(f"LOOCV Accuracy - Isoelectric Point (pI): {acc_pi:.2%}")
        print(f"LOOCV Accuracy - Molecular Weight (MW) : {acc_mw:.2%}")
        print()

        # === 4. PLOT COMPARATIVE DISTRIBUTIONS ===
        print("--- Plotting Property Distributions ---")
        fig_dir = PROJECT_ROOT / "results" / "figures"
        fig_dir.mkdir(parents=True, exist_ok=True)
        fig_path = fig_dir / "uniprot_distribution_comparison.png"
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=300, sharey=True)
        
        # Left Panel: Whole-Sequence GRAVY
        axes[0].hist(df[df['label'] == 1]['whole_gravy'], bins=10, alpha=0.6, label='Transmembrane', color='darkorange', edgecolor='black')
        axes[0].hist(df[df['label'] == 0]['whole_gravy'], bins=10, alpha=0.6, label='Soluble', color='royalblue', edgecolor='black')
        axes[0].axvline(x=0.0, color='red', linestyle='--', linewidth=1)
        axes[0].set_xlabel('Whole-Sequence Average GRAVY', fontsize=11)
        axes[0].set_ylabel('Protein Count', fontsize=11)
        axes[0].set_title('Whole-Sequence GRAVY\n(Dilution Effect Present)', fontsize=12, fontweight='bold')
        axes[0].grid(True, linestyle=':', alpha=0.6)
        axes[0].legend()
        
        # Right Panel: Max Window GRAVY
        axes[1].hist(df[df['label'] == 1]['max_window_gravy'], bins=10, alpha=0.6, label='Transmembrane', color='darkorange', edgecolor='black')
        axes[1].hist(df[df['label'] == 0]['max_window_gravy'], bins=10, alpha=0.6, label='Soluble', color='royalblue', edgecolor='black')
        axes[1].axvline(x=0.0, color='red', linestyle='--', linewidth=1)
        axes[1].set_xlabel('Max 19-Residue Window GRAVY', fontsize=11)
        axes[1].set_title('Max 19-Residue Window GRAVY\n(Bypasses Dilution Effect)', fontsize=12, fontweight='bold')
        axes[1].grid(True, linestyle=':', alpha=0.6)
        axes[1].legend()
        
        plt.suptitle('Biophysical Feature Distributions: Real Human Proteins', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(fig_path, bbox_inches='tight')
        plt.close()
        print(f"Saved comparative distribution plot to: {fig_path}")
        print()

        # === 5. VALIDATE BIOPHYSICAL HYPOTHESIS ===
        print("--- Validating Hypothesis 03 Predictions ---")
        
        # Prediction 1: Performance degradation of whole-sequence GRAVY compared to synthetic
        # Synthetic accuracy was 100.0%. Let's check if real whole-sequence drops to <= 85.0%
        print(f"  Whole-Sequence GRAVY Accuracy: {acc_whole:.2%}")
        is_diluted = (acc_whole <= 0.85)
        print(f"  Whole-Sequence accuracy <= 85%? {is_diluted}")
        
        # Prediction 2: Sliding window GRAVY outperforms whole sequence and achieves >= 90%
        print(f"  Max Window GRAVY Accuracy: {acc_window:.2%}")
        is_restored = (acc_window >= 0.90)
        print(f"  Max Window accuracy >= 90%? {is_restored}")
        
        # Compare
        gain = acc_window - acc_whole
        print(f"  Biophysical Feature Accuracy Gain: +{gain:.2%}")
        
        print()
        print("=" * 70)
        print("=== EXPERIMENT 04 COMPLETED SUCCESSFULLY ===")
        print("=" * 70)

if __name__ == "__main__":
    main()
