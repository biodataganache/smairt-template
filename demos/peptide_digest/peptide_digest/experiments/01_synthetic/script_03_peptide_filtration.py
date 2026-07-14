#!/usr/bin/env python3
"""
Script 03: Peptide monoisotopic mass calculation and physical constraint filtering.

Hypothesis: hypotheses/HYPOTHESIS_03.md
Phase: synthetic (with validation on real BSA sequence)
Track: None
Iteration: 3

Depends on:
  - script_01_tryptic_digestion_smoke_test.py
  - script_02_missed_cleavages_validation.py
"""

import sys
from pathlib import Path
from datetime import datetime

# === PATH SETUP ===
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

# === CONFIGURATION ===
SCRIPT_NAME = "script_03_peptide_filtration"
LOG_DIR = PROJECT_ROOT / "results" / "logs"

# Standard IUPAC Monoisotopic Amino Acid Residue Masses
MONOISOTOPIC_MASSES = {
    'A': 71.03711, 'C': 103.00919, 'D': 115.02694, 'E': 129.04259, 'F': 147.06841,
    'G': 57.02146, 'H': 137.05891, 'I': 113.08406, 'K': 128.09496, 'L': 113.08406,
    'M': 131.04049, 'N': 114.04293, 'P': 97.05276, 'Q': 128.05858, 'R': 156.10111,
    'S': 87.03203, 'T': 101.04768, 'V': 99.06841, 'W': 186.07931, 'Y': 163.06333
}
WATER_MASS = 18.01056  # standard H2O monoisotopic mass (can round to 18.0106)

# Bovine Serum Albumin (BSA, UniProt P02769, mature form: residues 25-607)
BSA_SEQUENCE = (
    "DTHKSEIAHRFKDLGEEHFKGLVLIAFSQYLQQCPFDEHVKLVNELTEFAKTCVADESHAGCEKSLHTLF"
    "GDELCKVASLRETYGDMADCCEKQEPERNECFLSHKDDSPDLPKLKPDPNTLCDEFKADEKKFWGKYLYE"
    "IARRHPYFYAPELLYYANKYNGVFQECCQAEDKGACLLPKIETMREKVLASSARQRLRCASIQKFGERAL"
    "KAWSVARLSQKFPKAEFVEVTKLVTDLTKVHKECCHGDLLECADDRADLAKYICDNQDTISSKLKECCDK"
    "PLLEKSHCIAEVEKDAIPENLPPLTADFAEDKDVCKNYQEAKDAFLGSFLYEYSRRHPEYAVSVLLRLAK"
    "EYEATLEECCAKDDPHACYSTVFDKLKHLVDEPQNLIKQNCDQFEKLGEYGFQNALIVRYTRKVPQVSTP"
    "TLVEVSRSLGKVGTRCCTKPESERMPCTEDYLSLILNRLCVLHEKTPVSEKVTKCCTESLVNRRPCFSAL"
    "TPDETYVPKAFDEKLFTFHADICTLPDTEKQIKKQTALVELLKHKPKATEEQLKTVMENFVAFVDKCCAA"
    "DDKEACFAVEGPKLVVSTQTALA"
)

# === MASS CALCULATOR ===
def calculate_monoisotopic_mass(peptide: str) -> float:
    """
    Calculate the monoisotopic mass of a peptide sequence.
    
    Formula: Sum of residue masses + mass of H2O.
    """
    try:
        residue_sum = sum(MONOISOTOPIC_MASSES[aa] for aa in peptide)
        return residue_sum + WATER_MASS
    except KeyError as e:
        raise ValueError(f"Unknown amino acid residue '{e.args[0]}' in peptide '{peptide}'")

# === DIGESTER WITH MISSED CLEAVAGES ===
def digest_trypsin_with_missed(sequence: str, max_missed_cleavages: int = 0) -> list[str]:
    """Perform in-silico tryptic digestion supporting missed cleavages (from Iteration 2)."""
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
        
    if max_missed_cleavages <= 0:
        return base_peptides
        
    all_peptides = []
    num_segments = len(base_peptides)
    for k in range(1, max_missed_cleavages + 2):
        for start_idx in range(num_segments - k + 1):
            combined_peptide = "".join(base_peptides[start_idx : start_idx + k])
            all_peptides.append(combined_peptide)
            
    return all_peptides

# === FILTRATION LOGIC ===
def is_ms_observable(peptide: str, mass: float, min_len: int = 6, max_len: int = 40, min_mass: float = 500.0, max_mass: float = 5000.0) -> bool:
    """
    Determine if a peptide lies within standard mass spectrometry observation windows.
    """
    length = len(peptide)
    return (min_len <= length <= max_len) and (min_mass <= mass <= max_mass)

# === MAIN CODE ===
def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)

    with TeeLogger(log_path):
        print(f"{'='*60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Hypothesis: Filtering against physical MS constraints excludes short/long peptides and yield is maximized at standard missed cleavages (N=1,2).")
        print(f"{'='*60}")
        print()

        # Part 1: Mass accuracy validation on hand-curated cases
        print("--- PART 1: MASS ACCURACY VALIDATION ---")
        validation_peptides = [
            {"sequence": "MK", "expected_mass": 277.14605, "should_pass": False, "reason": "Too short and light"},
            {"sequence": "WVTFISLLR", "expected_mass": 1133.65969, "should_pass": True, "reason": "Standard tryptic segment"}
        ]

        all_passed = True
        for i, val in enumerate(validation_peptides, 1):
            seq = val["sequence"]
            exp = val["expected_mass"]
            should_pass = val["should_pass"]
            reason = val["reason"]
            
            calc = calculate_monoisotopic_mass(seq)
            error = abs(calc - exp)
            passed = error <= 0.001
            
            print(f"\nValidation Peptide {i}: {seq} ({reason})")
            print(f"  Calculated Mass: {calc:.5f} Da")
            print(f"  Expected Mass:   {exp:.5f} Da")
            print(f"  Absolute Error:  {error:.5f} Da")
            print(f"  Mass Accuracy:   {'PASSED' if passed else 'FAILED'}")
            
            # Filtration check
            observable = is_ms_observable(seq, calc)
            print(f"  MS-Observable:   {observable} (Expected: {should_pass})")
            
            if observable != should_pass:
                print("  Filter Check:    FAILED")
                all_passed = False
            else:
                print("  Filter Check:    PASSED")
                
            if not passed:
                all_passed = False

        print("\n" + "="*60)
        print("--- PART 2: REAL PROTEIN DIGESTION (BSA) ---")
        print(f"Target Sequence: Bovine Serum Albumin (BSA, Mature Form)")
        print(f"Total Sequence Length: {len(BSA_SEQUENCE)} residues")
        print("="*60)

        # Run digestion for N = 0, 1, 2
        for n in (0, 1, 2):
            print(f"\n--- Allowed Missed Cleavages: {n} ---")
            raw_peptides = digest_trypsin_with_missed(BSA_SEQUENCE, n)
            print(f"  Raw Peptides Generated:       {len(raw_peptides)}")
            
            # Calculate masses and apply filters
            filtered_peptides = []
            excluded_short = 0
            excluded_long = 0
            excluded_light = 0
            excluded_heavy = 0
            
            for peptide in raw_peptides:
                mass = calculate_monoisotopic_mass(peptide)
                length = len(peptide)
                
                if is_ms_observable(peptide, mass):
                    filtered_peptides.append((peptide, mass))
                else:
                    if length < 6:
                        excluded_short += 1
                    elif length > 40:
                        excluded_long += 1
                    
                    if mass < 500.0:
                        excluded_light += 1
                    elif mass > 5000.0:
                        excluded_heavy += 1
                        
            obs_fraction = (len(filtered_peptides) / len(raw_peptides)) * 100 if raw_peptides else 0
            print(f"  MS-Observable Peptides:       {len(filtered_peptides)} ({obs_fraction:.2f}%)")
            print(f"  Peptides Excluded by Length:")
            print(f"    Too Short (< 6 residues):   {excluded_short}")
            print(f"    Too Long (> 40 residues):   {excluded_long}")
            print(f"  Peptides Excluded by Mass:")
            print(f"    Too Light (< 500.0 Da):     {excluded_light}")
            print(f"    Too Heavy (> 5000.0 Da):    {excluded_heavy}")
            
            # Print a few sample observable peptides
            print(f"\n  Sample MS-Observable Peptides (first 5):")
            for j, (pep, mass) in enumerate(filtered_peptides[:5], 1):
                print(f"    {j}. {pep:<15} (Length: {len(pep):>2}, Mass: {mass:.4f} Da)")

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
