# Downloaded data

| Path | Contents | Provenance |
|---|---|---|
| `covid19_jhu_italy/` | Offline fixture: Italy rows from the JHU CSSE global time series | [`covid19_jhu_italy/README.md`](covid19_jhu_italy/README.md) |
| `covid19_jhu/` | Created at runtime by a verified download. Not committed. | same pinned commit and checksums |

## The global files are fetched, not stored

`script_04_fit_published_outbreak.py` downloads the three JHU global CSVs from a pinned commit and
verifies each against a recorded SHA-256 before fitting. They land in `covid19_jhu/`, which is a
runtime cache: a corrupt or truncated cache is detected and re-fetched rather than used.

The 3.9 MB snapshot that used to be committed here was removed. It was three rows of interest in
files the script can reproduce exactly, and the previous code fetched from a mutable `master` URL
with no checksum, so what the demo fitted depended on when it ran.

For a run with no network:

```bash
python3 experiments/02_downloaded/script_04_fit_published_outbreak.py --offline
```

That reads the committed Italy fixture — a subset of the same pinned data, not a synthetic
stand-in — and produces the same fit: beta 0.23081955, gamma 0.05206253, mu 0.03663978,
R0 2.60218185.

## Caveat on the science

Reported confirmed, recovered, and deaths are not direct measurements of the SIRD compartments.
`analysis/ANALYSIS_04.md` states what that limits.
