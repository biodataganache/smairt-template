#!/usr/bin/env python3
"""
Script 01: Canonical trypsin digestion smoke test and validation.

Hypothesis: hypotheses/HYPOTHESIS_01.md
Phase: synthetic
Track: None
Iteration: 1

Depends on:
  - None (this is the initial script)
"""

import sys
from pathlib import Path
from datetime import datetime

# === PATH SETUP ===
# Path to the peptide_digest root inside the demos folder:
# Current file: smairt_template_demos/peptide_digest/peptide_digest/experiments/01_synthetic/script_01_tryptic_digestion_smoke_test.py
# Root should be: smairt_template_demos/peptide_digest/peptide_digest/
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

# === CONFIGURATION ===
SCRIPT_NAME = "script_01_tryptic_digestion_smoke_test"
LOG_DIR = PROJECT_ROOT / "results" / "logs"

# === DIGESTER IMPLEMENTATION ===
def digest_trypsin(sequence: str) -> list[str]:
    """
    Perform in-silico tryptic digestion on an amino acid sequence.
    
    Canonical rule: Cleave C-terminal to Lysine (K) and Arginine (R), 
    except when followed by Proline (P).
    
    Args:
        sequence: String of single-letter amino acid codes.
        
    Returns:
        List of peptide strings.
    """
    peptides = []
    current_peptide = []
    
    n = len(sequence)
    for i, residue in enumerate(sequence):
        current_peptide.append(residue)
        
        # Check if this is a cleavage site
        if residue in ('K', 'R'):
            # Exception check: next residue must not be proline
            if i + 1 < n and sequence[i + 1] == 'P':
                # Cleavage is blocked by proline exception
                continue
            else:
                # Cleave here
                peptides.append("".join(current_peptide))
                current_peptide = []
                
    # Append the remaining terminal peptide if not empty
    if current_peptide:
        peptides.append("".join(current_peptide))
        
    return peptides

# === MAIN CODE ===
def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)

    with TeeLogger(log_path):
        print(f"{'='*60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Hypothesis: Canonical trypsin rule perfectly reconstructs expected peptides for hand-curated test cases.")
        print(f"{'='*60}")
        print()

        # Define hand-curated test cases
        test_cases = [
            {
                "sequence": "AKPR",
                "expected": ["AKPR"],
                "description": "K-P block exception check (no cuts)"
            },
            {
                "sequence": "MKWVTFISLLR",
                "expected": ["MK", "WVTFISLLR"],
                "description": "Standard cleavage and terminal check"
            },
            {
                "sequence": "GPKPLR",
                "expected": ["GPKPLR"],
                "description": "K-P block exception with a prefix"
            },
            {
                "sequence": "KPR",
                "expected": ["KPR"],
                "description": "Very short sequence with K-P block"
            },
            {
                "sequence": "RGPK",
                "expected": ["R", "GPK"],
                "description": "Cleavage near the N-terminus"
            }
        ]

        print("--- RUNNING VALIDATION TEST SUITE ---")
        all_passed = True
        failed_count = 0
        passed_count = 0

        for i, test in enumerate(test_cases, 1):
            seq = test["sequence"]
            expected = test["expected"]
            desc = test["description"]

            print(f"\nTest {i}: {desc}")
            print(f"  Sequence: {seq}")
            print(f"  Expected: {expected}")
            
            # Run digestion
            result = digest_trypsin(seq)
            print(f"  Result:   {result}")

            # Verify against expectations
            try:
                assert result == expected, f"Validation failed! Expected {expected}, got {result}"
                print("  Status:   PASSED")
                passed_count += 1
            except AssertionError as e:
                print(f"  Status:   FAILED - {e}")
                failed_count += 1
                all_passed = False

        print("\n" + "="*60)
        print("--- SUMMARY ---")
        print(f"Total Tests Run: {len(test_cases)}")
        print(f"Passed:         {passed_count}")
        print(f"Failed:         {failed_count}")
        print("="*60)

        # Print check for proline exception violation rate
        print("\nVerifying Proline blockage exception rule explicitly...")
        violation_detected = False
        for test in test_cases:
            seq = test["sequence"]
            peptides = digest_trypsin(seq)
            for peptide in peptides:
                # If a peptide ends with K or R, check if the next character in original sequence was 'P'
                if peptide[-1] in ('K', 'R'):
                    idx = seq.find(peptide)
                    if idx != -1:
                        next_char_idx = idx + len(peptide)
                        if next_char_idx < len(seq) and seq[next_char_idx] == 'P':
                            print(f"Violation! Peptide '{peptide}' in sequence '{seq}' ends with '{peptide[-1]}' and is followed by 'P'")
                            violation_detected = True
        
        if not violation_detected:
            print("Confirmed: Proline exception block is completely respected (0% violation rate).")
        else:
            print("Error: Proline exception block violated.")
            all_passed = False

        if all_passed:
            print("\nOverall Status: ALL SUCCESS CRITERIA MET")
        else:
            print("\nOverall Status: CRITERIA FAILED")
            sys.exit(1)

        print()
        print(f"{'='*60}")
        print("=== COMPLETE ===")
        print(f"{'='*60}")

if __name__ == "__main__":
    main()
