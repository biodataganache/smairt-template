#!/usr/bin/env python3
"""
Fetch two real protein families from UniProt (Swiss-Prot) for Rung 3.

Hypothesis: HYPOTHESIS_09.md (real ESM-2 family separation)
Phase: real_data
Iteration: 9 (data acquisition step)

Purpose:
  Download ~N_PER_FAMILY reviewed sequences for each of two structurally distinct
  Pfam families via the UniProt REST API, filter by length, and write a single
  combined FASTA to data/downloaded/. Deterministic queries (sorted by accession)
  so the set is reproducible; caches to disk so the embedding step can run offline.

Families:
  - Globin            Pfam PF00042
  - Cytochrome c      Pfam PF00034

Depends on:
  - Python stdlib (urllib, json); internet access to rest.uniprot.org
"""

import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

SCRIPT_NAME = "fetch_uniprot_families"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
DATA_DIR = PROJECT_ROOT / "data" / "downloaded"

N_PER_FAMILY = 30
LEN_MIN, LEN_MAX = 50, 400

FAMILIES = [
    {"name": "globin", "pfam": "PF00042", "label": 0},
    {"name": "cytochrome_c", "pfam": "PF00034", "label": 1},
]

UNIPROT_URL = "https://rest.uniprot.org/uniprotkb/search"


def fetch_family(pfam, n):
    """Query UniProt for reviewed seqs in a Pfam family, length-filtered, sorted by
    accession for determinism. Returns list of (accession, sequence)."""
    query = (f"(xref:pfam-{pfam}) AND (reviewed:true) AND "
             f"(length:[{LEN_MIN} TO {LEN_MAX}])")
    params = {
        "query": query,
        "format": "fasta",
        "size": str(n),
        "sort": "accession asc",
    }
    url = UNIPROT_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "smairt-demo/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        text = resp.read().decode("utf-8")
    return parse_fasta(text)


def parse_fasta(text):
    """Parse FASTA text -> list of (header, sequence)."""
    records = []
    header, seq = None, []
    for line in text.splitlines():
        if line.startswith(">"):
            if header is not None:
                records.append((header, "".join(seq)))
            header, seq = line[1:].strip(), []
        elif line.strip():
            seq.append(line.strip())
    if header is not None:
        records.append((header, "".join(seq)))
    return records


def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / "rung3_two_families.fasta"
    with TeeLogger(log_path):
        print(f"{'='*60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Target: {N_PER_FAMILY} reviewed seqs/family, length {LEN_MIN}-{LEN_MAX}")
        print(f"{'='*60}\n")

        all_records = []
        counts = {}
        for fam in FAMILIES:
            print(f"[FETCH]  {fam['name']} (Pfam {fam['pfam']}) ...")
            recs = fetch_family(fam["pfam"], N_PER_FAMILY)
            print(f"         got {len(recs)} sequences")
            for header, seq in recs:
                acc = header.split("|")[1] if "|" in header else header.split()[0]
                # Tag the FASTA header with the family label for downstream parsing.
                tagged = f"{fam['name']}|{fam['label']}|{acc}"
                all_records.append((tagged, seq))
            counts[fam["name"]] = len(recs)
            time.sleep(1)  # be polite to the API

        with open(out_path, "w") as fh:
            for header, seq in all_records:
                fh.write(f">{header}\n")
                for i in range(0, len(seq), 60):
                    fh.write(seq[i:i + 60] + "\n")

        print(f"\n[WRITE]  {len(all_records)} sequences -> "
              f"{out_path.relative_to(PROJECT_ROOT)}")
        print(f"[WRITE]  per-family counts: {counts}")
        lens = [len(s) for _, s in all_records]
        print(f"[STATS]  length min/mean/max = "
              f"{min(lens)}/{sum(lens)//len(lens)}/{max(lens)}")
        print(f"\n{'='*60}")
        print("=== COMPLETE ===")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
