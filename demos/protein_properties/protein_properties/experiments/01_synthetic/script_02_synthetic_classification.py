#!/usr/bin/env python3
"""
Script 02: Classification of synthetic membrane-like vs soluble-like protein sequences using physical/chemical features

Hypothesis: hypotheses/HYPOTHESIS_02.md
Phase: synthetic (Phase 1)
Track: Track A (Initial baseline property calculation & downstream classification)
Iteration: 2

Depends on:
  - background/01_initial_question.md
  - hypotheses/HYPOTHESIS_02.md
  - scripts/shared/calculators.py
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# ML Imports
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report

# === PATH SETUP ===
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import (
    TeeLogger,
    setup_logging,
    calculate_molecular_weight,
    calculate_gravy,
    calculate_pi,
    AMINO_ACID_MASSES
)

# === SEED SETTING ===
RANDOM_SEED = 1024
np.random.seed(RANDOM_SEED)

# === SYNTHETIC SEQUENCE GENERATOR ===

# Define standard amino acids
ALL_AAS = list(AMINO_ACID_MASSES.keys())

# Define custom frequencies to bias pools
# Membrane-like: high hydrophobics (I, L, V, F, A, M)
MEMBRANE_BIAS = {
    'I': 0.12, 'L': 0.12, 'V': 0.12, 'F': 0.08, 'A': 0.10, 'M': 0.06, # ~60% hydrophobic
    'G': 0.06, 'P': 0.04, 'S': 0.04, 'T': 0.04, 'W': 0.02, 'Y': 0.02,
    'K': 0.03, 'R': 0.03, 'H': 0.02, 'D': 0.03, 'E': 0.03, 'C': 0.02, 'N': 0.03, 'Q': 0.03
}
# Normalize just to be absolutely safe
sum_mem = sum(MEMBRANE_BIAS.values())
MEM_PROBS = [MEMBRANE_BIAS[aa] / sum_mem for aa in ALL_AAS]

# Soluble-like: high polar/charged (K, R, H, D, E, N, Q)
SOLUBLE_BIAS = {
    'K': 0.10, 'R': 0.10, 'H': 0.05, 'D': 0.10, 'E': 0.10, 'N': 0.08, 'Q': 0.07, # ~60% charged/polar
    'G': 0.06, 'P': 0.04, 'S': 0.05, 'T': 0.05, 'W': 0.01, 'Y': 0.02, 'C': 0.01,
    'I': 0.03, 'L': 0.04, 'V': 0.04, 'F': 0.02, 'A': 0.05, 'M': 0.02
}
sum_sol = sum(SOLUBLE_BIAS.values())
SOL_PROBS = [SOLUBLE_BIAS[aa] / sum_sol for aa in ALL_AAS]

def generate_sequence(pool_type: str, min_len: int = 100, max_len: int = 150) -> str:
    """Generate a single biased amino acid sequence."""
    length = np.random.randint(min_len, max_len + 1)
    probs = MEM_PROBS if pool_type == "membrane" else SOL_PROBS
    seq_list = np.random.choice(ALL_AAS, size=length, p=probs)
    return "".join(seq_list)

# === MAIN PIPELINE ===

def main():
    script_name = "script_02_synthetic_classification"
    log_dir = PROJECT_ROOT / "results" / "logs"
    log_path = setup_logging(script_name, log_dir)

    with TeeLogger(log_path):
        print("=" * 70)
        print(f"Script: {script_name}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("Hypothesis: hypotheses/HYPOTHESIS_02.md")
        print("=" * 70)
        print()

        # === 1. DATASET GENERATION ===
        print("--- Generating Synthetic Dataset ---")
        N_SAMPLES = 500
        
        data_rows = []
        
        print(f"Generating {N_SAMPLES} membrane-like sequences (Class 1) and {N_SAMPLES} soluble-like sequences (Class 0)...")
        for _ in range(N_SAMPLES):
            # Membrane-like
            seq = generate_sequence("membrane")
            data_rows.append({
                'sequence': seq,
                'length': len(seq),
                'label': 1,
                'class_name': 'membrane-like'
            })
            # Soluble-like
            seq = generate_sequence("soluble")
            data_rows.append({
                'sequence': seq,
                'length': len(seq),
                'label': 0,
                'class_name': 'soluble-like'
            })
            
        df = pd.DataFrame(data_rows)
        
        # === 2. PROPERTY EXTRACTION ===
        print("--- Extracting Sequence Properties (Features) ---")
        df['molecular_weight'] = df['sequence'].apply(calculate_molecular_weight)
        df['gravy'] = df['sequence'].apply(calculate_gravy)
        df['pi'] = df['sequence'].apply(calculate_pi)
        
        # Save dataset to CSV for persistence
        out_data_dir = PROJECT_ROOT / "data" / "synthetic"
        out_data_dir.mkdir(parents=True, exist_ok=True)
        dataset_path = out_data_dir / "synthetic_protein_dataset.csv"
        df.to_csv(dataset_path, index=False)
        print(f"Persisted synthetic dataset ({len(df)} samples) to: {dataset_path}")
        print()
        
        # Print summary statistics
        print("Summary statistics by pool class:")
        summary_stats = df.groupby('class_name')[['molecular_weight', 'pi', 'gravy']].mean()
        print(summary_stats.to_string())
        print()
        
        # Confirm that membrane average GRAVY is positive and soluble average is negative
        mean_gravy_mem = summary_stats.loc['membrane-like', 'gravy']
        mean_gravy_sol = summary_stats.loc['soluble-like', 'gravy']
        print(f"Mean GRAVY - Membrane: {mean_gravy_mem:.3f} | Soluble: {mean_gravy_sol:.3f}")
        assert mean_gravy_mem > 0.0, "Membrane-like pool average GRAVY is not positive!"
        assert mean_gravy_sol < 0.0, "Soluble-like pool average GRAVY is not negative!"
        print("  => Confirm: Membrane GRAVY > 0 and Soluble GRAVY < 0 holds successfully.")
        print()

        # === 3. DISTRIBUTIONS PLOTTING ===
        print("--- Plotting Property Distributions ---")
        fig_dir = PROJECT_ROOT / "results" / "figures"
        fig_dir.mkdir(parents=True, exist_ok=True)
        fig_path = fig_dir / "gravy_distributions.png"
        
        plt.figure(figsize=(10, 5), dpi=300)
        plt.hist(df[df['label'] == 1]['gravy'], bins=30, alpha=0.6, label='Membrane-like (Class 1)', color='darkorange', edgecolor='black')
        plt.hist(df[df['label'] == 0]['gravy'], bins=30, alpha=0.6, label='Soluble-like (Class 0)', color='royalblue', edgecolor='black')
        plt.axvline(x=0.0, color='red', linestyle='--', linewidth=1.5, label='GRAVY Neutral (0.0)')
        plt.xlabel('GRAVY Score (Kyte-Doolittle)', fontsize=12)
        plt.ylabel('Sequence Count', fontsize=12)
        plt.title('GRAVY Distribution Comparison: Synthetic Labeled Pools', fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.tight_layout()
        plt.savefig(fig_path)
        plt.close()
        print(f"Saved GRAVY distribution histogram to: {fig_path}")
        print()

        # === 4. MACHINE LEARNING CLASSIFICATION ===
        print("--- Training and Evaluating Classifiers ---")
        
        # Train-Test Split (80/20)
        X = df[['molecular_weight', 'pi', 'gravy']]
        y = df['label']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=RANDOM_SEED, stratify=y
        )
        print(f"Train set size: {len(X_train)} samples | Test set size: {len(X_test)} samples")
        print()
        
        features_to_test = {
            'GRAVY-only': ['gravy'],
            'pI-only': ['pi'],
            'MW-only': ['molecular_weight'],
            'Multi-feature (MW, pI, GRAVY)': ['molecular_weight', 'pi', 'gravy']
        }
        
        results_records = []
        
        for name, feats in features_to_test.items():
            print(f"Model: Logistic Regression using {name}")
            model = LogisticRegression(random_state=RANDOM_SEED)
            model.fit(X_train[feats], y_train)
            
            y_pred = model.predict(X_test[feats])
            y_proba = model.predict_proba(X_test[feats])[:, 1]
            
            acc = accuracy_score(y_test, y_pred)
            auc = roc_auc_score(y_test, y_proba)
            
            print(f"  Test Accuracy : {acc:.2%}")
            print(f"  Test AUROC    : {auc:.4f}")
            print()
            
            results_records.append({
                'Model Name': name,
                'Accuracy': acc,
                'AUROC': auc
            })
            
            # Print detailed report for multi-feature model
            if name == 'Multi-feature (MW, pI, GRAVY)':
                print("Detailed Classification Report (Multi-feature):")
                print(classification_report(y_test, y_pred, target_names=['soluble-like', 'membrane-like']))
                
                # Get coefficients as feature importance
                coeffs = model.coef_[0]
                print("Logistic Regression Normalized Coefficients (Feature Importance):")
                # Normalize features to compare coefficients fairly
                # Standardize train features manually for printing weights
                X_train_mean = X_train[feats].mean()
                X_train_std = X_train[feats].std()
                X_train_scaled = (X_train[feats] - X_train_mean) / X_train_std
                
                scaled_model = LogisticRegression(random_state=RANDOM_SEED)
                scaled_model.fit(X_train_scaled, y_train)
                scaled_coeffs = scaled_model.coef_[0]
                
                for f, coef, scaled_coef in zip(feats, coeffs, scaled_coeffs):
                    print(f"  Feature: {f:<18} | Raw Coef: {coef:.4e} | Scaled Coef (Standardized): {scaled_coef:+.4f}")
                print()
                
        # Validate that GRAVY classification matches expectations
        gravy_record = results_records[0] # GRAVY-only
        pi_record = results_records[1]    # pI-only
        mw_record = results_records[2]    # MW-only
        
        print("--- Validating Success Criteria ---")
        assert gravy_record['AUROC'] >= 0.90, f"GRAVY-only AUROC ({gravy_record['AUROC']:.4f}) is below 0.90 target!"
        print(f"  => SUCCESS: GRAVY-only AUROC ({gravy_record['AUROC']:.4f}) meets the success target (>= 0.90)")
        
        assert abs(pi_record['Accuracy'] - 0.50) <= 0.10, f"pI-only Accuracy ({pi_record['Accuracy']:.2%}) is not near-random (50% +/- 10%)!"
        print(f"  => SUCCESS: pI-only Accuracy ({pi_record['Accuracy']:.2%}) is random-chance as expected.")
        
        assert abs(mw_record['Accuracy'] - 0.50) <= 0.10, f"MW-only Accuracy ({mw_record['Accuracy']:.2%}) is not near-random (50% +/- 10%)!"
        print(f"  => SUCCESS: MW-only Accuracy ({mw_record['Accuracy']:.2%}) is random-chance as expected.")
        
        print()
        print("=" * 70)
        print("=== EXPERIMENT 02 COMPLETED SUCCESSFULLY ===")
        print("=" * 70)

if __name__ == "__main__":
    main()
