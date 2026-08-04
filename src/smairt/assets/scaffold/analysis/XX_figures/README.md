# Final Publication Figures

This directory contains the final, publication-ready figures.

## Structure

```
XX_figures/
├── main/           # Main paper figures
│   ├── fig_01_*.pdf
│   ├── fig_02_*.pdf
│   └── ...
└── supplementary/  # Supplementary figures
    ├── fig_s01_*.pdf
    └── ...
```

## Naming Convention

- Main figures: `fig_01_description.{ext}`
- Supplementary: `fig_s01_description.{ext}`
- Save in multiple formats: `.png`, `.pdf`, `.svg`

## Checklist Before Submission

- [ ] All figures saved at 300 DPI minimum
- [ ] Font sizes readable (minimum 8pt in final size)
- [ ] Color scheme consistent across figures
- [ ] Legends complete and clear
- [ ] Axis labels include units
- [ ] PDF versions for vector graphics
- [ ] PNG versions for raster/photos
- [ ] Figure captions drafted in paper

## Source Tracking

Every figure traces to the run that produced it. The log is the link that makes a figure
checkable, because it records the code, inputs, and output of that run.

| Figure | Claim it supports | Iteration | Script | Log |
|---|---|---|---|---|
| Fig 1 | [What the figure is evidence for] | 02 | `script_02_baseline.py` | `results/logs/script_02_baseline_<timestamp>.log` |
| Fig 2 | [What the figure is evidence for] | 05 | `script_05_sweep.py` | `results/logs/script_05_sweep_<timestamp>.log` |

A figure that cannot name its log is not yet evidence. If a figure was assembled by hand
from several runs, list each one.

With the Paper capability, `FINAL_MANIFEST.md` carries the same mapping for every paper
element, not just figures.
