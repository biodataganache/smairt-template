# Final Publication Figures

{% if cookiecutter.project_mode == 'paper_driven' %}
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

Each figure should be traceable to its source analysis.
Check `FINAL_MANIFEST.md` for the mapping.

| Figure | Source Analysis | Iteration |
|--------|-----------------|-----------|
| Fig 1 | 01_first_analysis | iter_02 |
| Fig 2 | 02_second_analysis | iter_03 |
{% else %}
This directory is only used in paper-driven mode.
{% endif %}
