"""
Sequence property calculators for Molecular Weight, Isoelectric Point, and GRAVY.
Validated in script_01_validate_calculators.py.
"""

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
