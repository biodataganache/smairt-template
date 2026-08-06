# Downloaded data

| Filename | Sequences | Source | Used by |
|---|---|---|---|
| `rung3_two_families.fasta` | 60 (30 globin, 30 cytochrome c) | UniProtKB REST API | `script_09_esm2_family_separation.py` |

- **SHA-256**: `8fb504f9b75faea7a392fc6a73a7b1d7334d97ccdb5b0f85c40246bd89618721`
- **Header format**: `>{family}|{label}|{accession}`, so each sequence carries its family label and
  its UniProt accession inline.

## Provenance

- **Source organization**: UniProt Consortium
- **Dataset**: UniProtKB reviewed (Swiss-Prot) entries in two Pfam families
- **Endpoint**: `https://rest.uniprot.org/uniprotkb/search`
- **Retrieved**: 2026-07 by `experiments/03_real_data/fetch_uniprot_families.py`
- **License**: CC BY 4.0.
- **Queries**, one per family, both `reviewed:true` and length-filtered:
  - globin: `(xref:pfam-PF00042) AND (reviewed:true)`
  - cytochrome c: `(xref:pfam-PF00034) AND (reviewed:true)`
- **Transformation**: 30 sequences retained per family and rewritten into FASTA with the labelled
  header above. Sequences themselves are unmodified.

## Why two distant families

The rung this feeds asks whether ESM-2 embeddings separate protein families. Globin and cytochrome c
are both small, ancient, heme-binding families with **low sequence identity to each other**, so
separation cannot be explained by trivial sequence similarity. That also makes it an easy case: a
positive result here does not show that the embeddings separate *close* homologues.

## Reproducing

```bash
python3 experiments/03_real_data/fetch_uniprot_families.py
```

Individual entries are stable by accession and the headers record them, so any sequence can be
checked directly:

```bash
curl -sfL https://rest.uniprot.org/uniprotkb/A0A072TK64.fasta
```

No UniProt release version was recorded at retrieval, and reviewed family membership grows between
releases, so re-running the fetch is **not** expected to reproduce this file byte-for-byte. The
committed file plus its checksum is what makes the recorded result checkable; the accessions in the
headers are how to verify any individual sequence.

## Status

This demo is **legacy** — see the banner in `demos/protein_lm/DEMO.md`. The provenance above is
recorded so the retained payload is citable, not because the demo is a current workflow example.
