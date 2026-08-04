# Figure Generation Prompt

## Context

You are helping generate publication-quality figures for a paper-driven SMAIRT project.

## Project Style

Figures across a paper must look like they belong to the same paper. This project does
not ship a styling module, so the first figure script establishes the style and later
ones reuse it.

Once a second figure needs the same styling, extract it to
`scripts/shared/figure_style.py` and import it:

```python
from scripts.shared.figure_style import setup_plot_style, save_figure, COLORS

setup_plot_style()
color = COLORS["primary"]
save_figure(figure, "results/figures/fig_01_name")
```

Until that module exists, define the style in the figure script itself rather than
importing something that is not there. Extract on the second use, not the first.

## Figure Requirements

### For Main Figures
- High resolution (300 DPI minimum)
- Clear, readable labels (12pt minimum)
- Consistent color scheme
- Proper legends
- Save in PNG, PDF, and SVG formats

### For Supplementary Figures
- Same quality standards as main figures
- Can be more detailed/technical
- Clear numbering (S1, S2, etc.)

## Naming Convention

```
fig_01_description.png
fig_02_description.png
fig_s01_supplementary_description.png
```

## Information to Provide

When requesting a figure, please share:
1. **Figure number** (e.g., Fig 1, Fig S1)
2. **Purpose** - What should this figure communicate?
3. **Data source** - Which analysis/iteration produced the data?
4. **Figure type** - Bar chart, line plot, heatmap, etc.
5. **Specific requirements** - Axis labels, legend, annotations

## Common Figure Types

### Comparison Plots
```python
import matplotlib.pyplot as plt
from lib.visualization.style import setup_plot_style, save_figure, COLORS

setup_plot_style()

fig, ax = plt.subplots(figsize=(8, 6))
ax.bar(categories, values, color=COLORS['primary'])
ax.set_xlabel('Category')
ax.set_ylabel('Value')
ax.set_title('Comparison of Methods')

save_figure(fig, 'figures/fig_01_comparison')
```

### Multi-Panel Figures
```python
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Panel A
axes[0, 0].plot(...)
axes[0, 0].set_title('A) First Panel')

# Panel B
axes[0, 1].plot(...)
axes[0, 1].set_title('B) Second Panel')

# etc.

plt.tight_layout()
save_figure(fig, 'figures/fig_02_multipanel')
```

## Output Location

- Main figures: `analysis/XX_figures/main/`
- Supplementary: `analysis/XX_figures/supplementary/`
- Also copy final versions to `results/figures/`
