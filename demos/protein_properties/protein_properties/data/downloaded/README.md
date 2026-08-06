# Downloaded data

| Filename | Rows | Source | Used by |
|---|---|---|---|
| `uniprot_benchmark.csv` | header + 12 | UniProtKB REST API | iterations 03 and 04 |

- **SHA-256**: `9a391e99a7246ebebb7cddee153e20620522aec2f85ccbd7a04537a83c8c9e7f`
- **Accessions**: P08183, P00533, P11274, P16473, P04626, O15303 (transmembrane);
  P62988, P68032, P00558, P04075, P06733, P14618 (soluble)

## Provenance

- **Source organization**: UniProt Consortium
- **Dataset**: UniProtKB reviewed (Swiss-Prot) human protein entries
- **Endpoint**: `https://rest.uniprot.org/uniprotkb/search`
- **Retrieved**: 2026-07 by `script_03_download_benchmark.py`
- **License**: CC BY 4.0.
- **Queries**, both restricted to `reviewed:true AND organism_id:9606`:
  - transmembrane: `(cc_transmembrane:helical OR cc_transmembrane:beta)`
  - soluble: `cc_subunit:cytoplasm NOT (cc_transmembrane:* OR cc_subcellular_location:membrane)`

## Transformation, which affects the result

**Sequences are truncated to the first 200 residues** (`script_03_download_benchmark.py:179,194`),
then the committed file retains 12 of the 60 requested entries. Recorded here because it is not
recoverable from the data itself and it bounds what the experiment can show:

- Iteration 04's sliding-window calculator uses a 19-residue window, so truncation does not break
  the method — a transmembrane helix fits inside 200 residues.
- But truncation **removes transmembrane segments that occur after residue 200**. A protein labelled
  transmembrane whose only helix is downstream would appear soluble by any hydropathy measure. The
  reported accuracy is therefore for the truncated sequences, not for the full proteins.
- `label` and `class_name` come from the query that retrieved each entry, not from a per-entry
  UniProt annotation field.

## Reproducing

```bash
BASE="https://rest.uniprot.org/uniprotkb/search"
curl -sfL --get "$BASE" --data-urlencode \
  'query=reviewed:true AND organism_id:9606 AND (cc_transmembrane:helical OR cc_transmembrane:beta)' \
  --data 'format=json&size=30'
```

UniProt releases update roughly every eight weeks and no release version was recorded at retrieval,
so this query is **not** expected to reproduce the committed file. Individual entries are stable and
citable by accession: `https://rest.uniprot.org/uniprotkb/P08183.json`. Fetching the twelve
accessions above and truncating to 200 residues is the reliable reconstruction.

## Caveat

Twelve proteins is a demonstration, not a benchmark. Iteration 04's accuracy figures illustrate the
dilution effect that motivates a sliding-window calculator; they do not establish its performance.
