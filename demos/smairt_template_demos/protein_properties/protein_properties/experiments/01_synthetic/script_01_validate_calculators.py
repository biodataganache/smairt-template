#!/usr/bin/env python3
"""
Script 01: Validate sequence property calculators against hand-checked and reference proteins

Hypothesis: hypotheses/HYPOTHESIS_01.md
Phase: synthetic (Phase 1)
Track: Track A (Initial baseline property calculation)
Iteration: 1

Depends on:
  - background/01_initial_question.md
  - hypotheses/HYPOTHESIS_01.md
"""

import sys
from pathlib import Path
from datetime import datetime

# === PATH SETUP ===
# Path to protein_properties root directory (2 levels up from experiments/01_synthetic)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

# === CONSTANTS & SCALES ===
AMINO_ACID_MASSES = {
    'A': 71.08, 'R': 156.19, 'N': 114.10, 'D': 115.09, 'C': 103.14,
    'Q': 128.13, 'E': 129.12, 'G': 57.05, 'H': 137.14, 'I': 113.16,
    'L': 113.16, 'K': 128.17, 'M': 131.20, 'F': 147.18, 'P': 97.12,
    'S': 87.08, 'T': 101.10, 'W': 186.21, 'Y': 163.18, 'V': 99.13
}
WATER_MASS = 18.015

KYTE_DOOLITTLE = {
    'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5, 'Q': -3.5,
    'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5, 'L': 3.8, 'K': -3.9,
    'M': 1.9, 'F': 2.8, 'P': -1.6, 'S': -0.8, 'T': -0.7, 'W': -0.9,
    'Y': -1.3, 'V': 4.2
}

EMBOSS_PKA = {
    'N_term': 8.6,
    'C_term': 3.6,
    'K': 10.8,
    'R': 12.5,
    'H': 6.5,
    'D': 3.9,
    'E': 4.1,
    'C': 8.5,
    'Y': 10.1
}

# === CALCULATOR FUNCTIONS ===

def clean_sequence(sequence: str) -> str:
    """Normalize and validate the input sequence."""
    seq = sequence.strip().upper()
    for char in seq:
        if char not in AMINO_ACID_MASSES:
            raise ValueError(f"Invalid amino acid residue found in sequence: {char}")
    return seq

def calculate_molecular_weight(sequence: str) -> float:
    """Calculate average molecular weight of peptide sequence with terminal water."""
    seq = clean_sequence(sequence)
    if not seq:
        return 0.0
    return sum(AMINO_ACID_MASSES[aa] for aa in seq) + WATER_MASS

def calculate_gravy(sequence: str) -> float:
    """Calculate the Grand Average of Hydropathy (GRAVY) for a sequence."""
    seq = clean_sequence(sequence)
    if not seq:
        return 0.0
    return sum(KYTE_DOOLITTLE[aa] for aa in seq) / len(seq)

def calculate_net_charge(sequence: str, ph: float) -> float:
    """Calculate the net charge of a sequence at a given pH using EMBOSS pKa values."""
    seq = clean_sequence(sequence)
    
    # Termini contributions
    n_term = 1.0 / (1.0 + 10**(ph - EMBOSS_PKA['N_term']))
    c_term = -1.0 / (1.0 + 10**(EMBOSS_PKA['C_term'] - ph))
    
    net_charge = n_term + c_term
    
    # Side-chain contributions
    for aa in seq:
        if aa in ['K', 'R', 'H']:
            net_charge += 1.0 / (1.0 + 10**(ph - EMBOSS_PKA[aa]))
        elif aa in ['D', 'E', 'C', 'Y']:
            net_charge -= 1.0 / (1.0 + 10**(EMBOSS_PKA[aa] - ph))
            
    return net_charge

def calculate_pi(sequence: str, tol: float = 1e-5, max_iter: int = 100) -> float:
    """Find the isoelectric point (pI) using bisection search on pH range [0, 14]."""
    low = 0.0
    high = 14.0
    
    # Fail-safe check
    if calculate_net_charge(sequence, low) < 0:
        return low
    if calculate_net_charge(sequence, high) > 0:
        return high
        
    for _ in range(max_iter):
        mid = (low + high) / 2.0
        charge = calculate_net_charge(sequence, mid)
        if abs(charge) < tol:
            return mid
        if charge > 0:
            low = mid
        else:
            high = mid
            
    return (low + high) / 2.0

# === MAIN VALIDATION RUN ===

def main():
    script_name = "script_01_validate_calculators"
    log_dir = PROJECT_ROOT / "results" / "logs"
    log_path = setup_logging(script_name, log_dir)

    with TeeLogger(log_path):
        print("=" * 70)
        print(f"Script: {script_name}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("Hypothesis: hypotheses/HYPOTHESIS_01.md")
        print("=" * 70)
        print()

        print("--- PHASE 1: Validate on Hand-Checkable Peptides ---")
        
        # Test case 1: AAA (Tri-alanine)
        seq_aaa = "AAA"
        calc_mw_aaa = calculate_molecular_weight(seq_aaa)
        calc_gravy_aaa = calculate_gravy(seq_aaa)
        calc_pi_aaa = calculate_pi(seq_aaa)
        
        expected_mw_aaa = 231.255
        expected_gravy_aaa = 1.8
        expected_pi_aaa = 6.1
        
        print(f"Peptide: {seq_aaa}")
        print(f"  MW    - Calc: {calc_mw_aaa:.3f} Da | Expected: {expected_mw_aaa:.3f} Da | Diff: {abs(calc_mw_aaa - expected_mw_aaa):.3e} Da")
        print(f"  GRAVY - Calc: {calc_gravy_aaa:.3f}    | Expected: {expected_gravy_aaa:.3f}    | Diff: {abs(calc_gravy_aaa - expected_gravy_aaa):.3e}")
        print(f"  pI    - Calc: {calc_pi_aaa:.3f}     | Expected: {expected_pi_aaa:.3f}     | Diff: {abs(calc_pi_aaa - expected_pi_aaa):.3e}")
        
        # Simple assertions for hand-checkable cases
        assert abs(calc_mw_aaa - expected_mw_aaa) < 1e-3, "AAA MW calculation failed!"
        assert abs(calc_gravy_aaa - expected_gravy_aaa) < 1e-5, "AAA GRAVY calculation failed!"
        assert abs(calc_pi_aaa - expected_pi_aaa) < 1e-2, "AAA pI calculation failed!"
        print("  => PASS (AAA)")
        print()

        # Test case 2: MVR (Methionine-Valine-Arginine)
        seq_mvr = "MVR"
        calc_mw_mvr = calculate_molecular_weight(seq_mvr)
        calc_gravy_mvr = calculate_gravy(seq_mvr)
        calc_pi_mvr = calculate_pi(seq_mvr)
        
        expected_mw_mvr = 404.535
        expected_gravy_mvr = 0.5333333333333333
        expected_pi_mvr = 10.55
        
        print(f"Peptide: {seq_mvr}")
        print(f"  MW    - Calc: {calc_mw_mvr:.3f} Da | Expected: {expected_mw_mvr:.3f} Da | Diff: {abs(calc_mw_mvr - expected_mw_mvr):.3e} Da")
        print(f"  GRAVY - Calc: {calc_gravy_mvr:.3f}    | Expected: {expected_gravy_mvr:.3f}    | Diff: {abs(calc_gravy_mvr - expected_gravy_mvr):.3e}")
        print(f"  pI    - Calc: {calc_pi_mvr:.3f}     | Expected: {expected_pi_mvr:.3f}    | Diff: {abs(calc_pi_mvr - expected_pi_mvr):.3e}")
        
        assert abs(calc_mw_mvr - expected_mw_mvr) < 1e-3, "MVR MW calculation failed!"
        assert abs(calc_gravy_mvr - expected_gravy_mvr) < 1e-3, "MVR GRAVY calculation failed!"
        assert abs(calc_pi_mvr - expected_pi_mvr) < 1e-2, "MVR pI calculation failed!"
        print("  => PASS (MVR)")
        print()

        print("--- PHASE 2: Validate on Reference Protein (Human Ubiquitin) ---")
        
        seq_ubiquitin = "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG"
        calc_mw_ubi = calculate_molecular_weight(seq_ubiquitin)
        calc_gravy_ubi = calculate_gravy(seq_ubiquitin)
        calc_pi_ubi = calculate_pi(seq_ubiquitin)
        
        expected_mw_ubi = 8564.8
        expected_pi_ubi = 7.54
        expected_gravy_ubi = -0.489
        
        mw_rel_diff = abs(calc_mw_ubi - expected_mw_ubi) / expected_mw_ubi
        pi_diff = abs(calc_pi_ubi - expected_pi_ubi)
        gravy_diff = abs(calc_gravy_ubi - expected_gravy_ubi)
        
        print(f"Protein: Human Ubiquitin ({len(seq_ubiquitin)} residues)")
        print(f"  MW    - Calc: {calc_mw_ubi:.3f} Da | Expected: {expected_mw_ubi:.3f} Da | Rel Diff: {mw_rel_diff:.3%}")
        print(f"  GRAVY - Calc: {calc_gravy_ubi:.3f}    | Expected: {expected_gravy_ubi:.3f}    | Diff: {gravy_diff:.3e}")
        print(f"  pI    - Calc: {calc_pi_ubi:.3f}     | Expected: {expected_pi_ubi:.3f}     | Diff: {pi_diff:.3e}")
        
        # Verify within tolerance thresholds
        assert mw_rel_diff <= 0.001, f"Ubiquitin MW relative difference ({mw_rel_diff:.3%}) exceeds tolerance (0.1%)"
        assert pi_diff <= 0.05, f"Ubiquitin pI difference ({pi_diff:.3e}) exceeds tolerance (0.05 pH units)"
        assert gravy_diff <= 0.01, f"Ubiquitin GRAVY difference ({gravy_diff:.3e}) exceeds tolerance (0.01)"
        
        print("  => PASS (Human Ubiquitin)")
        print()
        
        print("=" * 70)
        print("=== ALL CALCULATORS SUCCESSFULLY VALIDATED WITH ZERO ERRORS ===")
        print("=" * 70)

if __name__ == "__main__":
    main()
