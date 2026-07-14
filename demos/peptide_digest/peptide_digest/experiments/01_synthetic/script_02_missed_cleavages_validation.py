#!/usr/bin/env python3
"""
Script 02: Verification of tryptic digestion with missed cleavages.

Hypothesis: hypotheses/HYPOTHESIS_02.md
Phase: synthetic
Track: None
Iteration: 2

Depends on:
  - script_01_tryptic_digestion_smoke_test.py
"""

import sys
from pathlib import Path
from datetime import datetime

# === PATH SETUP ===
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

# === CONFIGURATION ===
SCRIPT_NAME = "script_02_missed_cleavages_validation"
LOG_DIR = PROJECT_ROOT / "results" / "logs"

# === DIGESTER WITH MISSED CLEAVAGES ===
def digest_trypsin_with_missed(sequence: str, max_missed_cleavages: int = 0) -> list[str]:
    """
    Perform in-silico tryptic digestion supporting missed cleavages.
    
    Args:
        sequence: String of single-letter amino acid codes.
        max_missed_cleavages: Max number of internal missed cleavage sites allowed per peptide.
        
    Returns:
        List of peptide strings.
    """
    # Step 1: Obtain the base (fully cleaved) segments (N=0)
    # We can reuse the logic from Iteration 1 to split into atomic tryptic pieces.
    base_peptides = []
    current_peptide = []
    n = len(sequence)
    
    for i, residue in enumerate(sequence):
        current_peptide.append(residue)
        if residue in ('K', 'R'):
            if i + 1 < n and sequence[i + 1] == 'P':
                continue
            else:
                base_peptides.append("".join(current_peptide))
                current_peptide = []
    if current_peptide:
        base_peptides.append("".join(current_peptide))
        
    # If N = 0, we just return the fully cleaved segments
    if max_missed_cleavages <= 0:
        return base_peptides
        
    # Step 2: Combine adjacent segments to generate missed cleavages
    # A peptide with M missed cleavages consists of M+1 consecutive base peptides stitched together.
    # We want to yield all combinations of length 1 up to max_missed_cleavages + 1 consecutive segments.
    all_peptides = []
    num_segments = len(base_peptides)
    
    for k in range(1, max_missed_cleavages + 2):  # k is number of segments combined (1 to max_missed + 1)
        for start_idx in range(num_segments - k + 1):
            combined_peptide = "".join(base_peptides[start_idx : start_idx + k])
            all_peptides.append(combined_peptide)
            
    return all_peptides

# === MAIN CODE ===
def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)

    with TeeLogger(log_path):
        print(f"{'='*60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Hypothesis: Allowing missed cleavages expands peptide pool in a bounded, predictable way.")
        print(f"{'='*60}")
        print()

        # Define validation test suite
        test_cases = [
            {
                "sequence": "MKWVTFISLLR",
                "max_missed": 0,
                "expected": ["MK", "WVTFISLLR"],
                "description": "Case A (N=0)"
            },
            {
                "sequence": "MKWVTFISLLR",
                "max_missed": 1,
                "expected": ["MK", "WVTFISLLR", "MKWVTFISLLR"],
                "description": "Case A (N=1)"
            },
            {
                "sequence": "MKWVTFISLLR",
                "max_missed": 2,
                "expected": ["MK", "WVTFISLLR", "MKWVTFISLLR"],
                "description": "Case A (N=2 - bounded by segments)"
            },
            {
                "sequence": "AKR",
                "max_missed": 0,
                "expected": ["AK", "R"],
                "description": "Case B (N=0)"
            },
            {
                "sequence": "AKR",
                "max_missed": 1,
                "expected": ["AK", "R", "AKR"],
                "description": "Case B (N=1)"
            },
            {
                "sequence": "AKRGPK",
                "max_missed": 0,
                "expected": ["AK", "R", "GPK"],
                "description": "Case C (N=0)"
            },
            {
                "sequence": "AKRGPK",
                "max_missed": 1,
                "expected": ["AK", "R", "GPK", "AKR", "RGPK"],
                "description": "Case C (N=1)"
            },
            {
                "sequence": "AKRGPK",
                "max_missed": 2,
                "expected": ["AK", "R", "GPK", "AKR", "RGPK", "AKRGPK"],
                "description": "Case C (N=2)"
            }
        ]

        print("--- RUNNING VALIDATION TEST SUITE ---")
        all_passed = True
        failed_count = 0
        passed_count = 0

        for i, test in enumerate(test_cases, 1):
            seq = test["sequence"]
            n_missed = test["max_missed"]
            expected = test["expected"]
            desc = test["description"]

            print(f"\nTest {i}: {desc}")
            print(f"  Sequence: {seq} (Allowed Missed: {n_missed})")
            print(f"  Expected: {expected}")
            
            result = digest_trypsin_with_missed(seq, n_missed)
            print(f"  Result:   {result}")

            try:
                # We sort lists for comparison so that order of combinations is not sensitive,
                # though our implementation yields them sequentially by combination size.
                # Standardizing comparison: sets or sorted lists
                assert sorted(result) == sorted(expected), f"Validation failed! Expected {expected}, got {result}"
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

        # Analyze average length trend on a longer template sequence
        print("\nAnalyzing average peptide length trend on a mock protein sequence...")
        template_protein = "MKWVTFISLLRLVAKRGPKPLRLVAKR"
        # Digested segments at N=0: MK, WVTFISLLR, LVAK, R, GPKPLR, LVAK, R (M = 7 segments)
        
        lengths = []
        counts = []
        for n in (0, 1, 2):
            peptides = digest_trypsin_with_missed(template_protein, n)
            avg_len = sum(len(p) for p in peptides) / len(peptides) if peptides else 0
            lengths.append(avg_len)
            counts.append(len(peptides))
            print(f"Allowed Missed: {n}")
            print(f"  Unique Peptide Count: {len(peptides)}")
            print(f"  Average Peptide Length: {avg_len:.2f} residues")
            print(f"  Peptides: {peptides}")

        # Check for monotonic increase in average length and peptide count
        monotonic_len = lengths[1] > lengths[0] and lengths[2] > lengths[1]
        monotonic_count = counts[1] > counts[0] and counts[2] > counts[1]
        
        if monotonic_len and monotonic_count:
            print("\nVerification: Average peptide length and peptide counts monotonically increase as expected.")
        else:
            print("\nError: Monotonic increase trend violated!")
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
