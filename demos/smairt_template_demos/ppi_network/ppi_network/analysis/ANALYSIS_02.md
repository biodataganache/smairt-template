# Analysis 02 — Robustness of Hub and Community Recovery under Edge Noise

## Executive Summary

We evaluated the robustness of degree centrality, betweenness centrality, and modularity-based community detection on a synthetic PPI network across 11 noise levels (random edge rewiring fractions from 0% to 50%). Our findings show that both hub and community recovery are remarkably robust:
1. Hub recovery (both degree and betweenness) maintains highly reliable performance (Precision@3 >= 0.8) up to 30% edge noise, though it degrades rapidly above 30%.
2. Community detection is surprisingly resilient to noise: instead of breaking down at 15% noise as expected, the partition alignment (ARI) remained above 0.80 up to 45% noise, only collapsing when 50% of the edges were rewired.

These results partially support our hub robustness predictions but strongly refute our community sensitivity predictions, demonstrating that global modularity partitions tolerate massive edge noise.

## Experiment Details

- **Script**: `experiments/01_synthetic/script_02_noise_robustness.py`
- **Hypothesis**: `hypotheses/HYPOTHESIS_02.md`
- **Log**: `results/logs/script_02_noise_robustness_20260630_083436.log`
- **Track**: Track-free (Robustness evaluation)
- **Phase**: synthetic

## Key Results

The average performance (and standard deviation) across 5 trials per noise level is detailed below:

| Noise Fraction ($r$) | Deg Centrality P@3 | Bet Centrality P@3 | Community ARI | Community NMI |
|----------------------|--------------------|--------------------|---------------|---------------|
| 0.00 (Baseline)      | 1.000 ± 0.00       | 1.000 ± 0.00       | 1.000 ± 0.00  | 1.000 ± 0.00  |
| 0.05                 | 1.000 ± 0.00       | 1.000 ± 0.00       | 0.996 ± 0.01  | 0.994 ± 0.01  |
| 0.10                 | 1.000 ± 0.00       | 1.000 ± 0.00       | 0.988 ± 0.02  | 0.982 ± 0.02  |
| 0.15                 | 0.933 ± 0.13       | 0.933 ± 0.13       | 0.988 ± 0.02  | 0.982 ± 0.02  |
| 0.20                 | 0.933 ± 0.13       | 1.000 ± 0.00       | 0.976 ± 0.01  | 0.966 ± 0.02  |
| 0.25                 | 0.867 ± 0.16       | 0.867 ± 0.16       | 0.968 ± 0.02  | 0.954 ± 0.03  |
| 0.30                 | 1.000 ± 0.00       | 1.000 ± 0.00       | 0.922 ± 0.04  | 0.906 ± 0.04  |
| 0.35                 | 0.667 ± 0.21       | 0.733 ± 0.25       | 0.916 ± 0.09  | 0.903 ± 0.08  |
| 0.40                 | 0.800 ± 0.16       | 0.800 ± 0.16       | 0.850 ± 0.03  | 0.818 ± 0.02  |
| 0.45                 | 0.667 ± 0.30       | 0.667 ± 0.21       | 0.829 ± 0.05  | 0.800 ± 0.06  |
| 0.50                 | 0.467 ± 0.16       | 0.533 ± 0.16       | 0.556 ± 0.14  | 0.551 ± 0.13  |

### Summary of Performance Against Thresholds

- **Degree Centrality P@3 >= 0.8**: Maintained up to $r = 0.30$ (Observed: 1.000). Drops to 0.667 at $r = 0.35$.
- **Betweenness Centrality P@3 >= 0.8**: Maintained up to $r = 0.30$ (Observed: 1.000). Drops to 0.733 at $r = 0.35$.
- **Community Detection ARI >= 0.8**: Maintained up to $r = 0.45$ (Observed: 0.829). Drops to 0.556 at $r = 0.50$.

---

## Hypothesis Assessment

### PARTIALLY SUPPORTED

- **Hub Recovery Sensitivity (Refuted)**: We hypothesized that betweenness centrality would drop below 0.8 at lower noise levels ($r > 0.15$) than degree centrality. In fact, betweenness centrality matched or outperformed degree centrality across nearly all noise levels. At $r = 0.20$, betweenness centrality kept a perfect $1.000$ precision while degree centrality fell to $0.933$. At $r = 0.35$, betweenness centrality remained higher ($0.733 \pm 0.25$) than degree centrality ($0.667 \pm 0.21$). Both methods successfully sustained P@3 >= 0.8 up to $r = 0.30$.
- **Community Recovery Sensitivity (Strongly Refuted)**: We hypothesized that community partitions would drop below ARI/NMI of 0.8 when $r > 0.15$. However, modular community detection proved incredibly robust, keeping ARI >= 0.90 up to $r = 0.35$ and only dropping below 0.8 at $r = 0.50$ (ARI = 0.556).

### Where It Works (Boundaries)
- **High-Quality Hub Identification**: Succeeded (Precision@3 >= 0.86) for noise levels up to 30%. Within this range, the structural signals are strong enough that both local (degree) and global (betweenness) metrics easily separate the hubs.
- **Resilient Community Partitions**: Succeeded (ARI >= 0.8) for edge noise up to 45%. This suggests that the dense modular structures ($p_{in} = 0.3$, $p_{out} = 0.02$) retain sufficient structural contrast even when nearly half of the edges are rewired uniformly at random.

### Where It Breaks Down
- **Severe Noise ($r \ge 35\%$)**: Above 35% edge rewiring, hub recovery degrades rapidly and becomes highly volatile (high standard deviation). At 50% noise, both hub recovery and community detection collapse (Hub precision ~0.50, Community ARI ~0.55).

---

## Comparison to Prior Work

Compared to the noise-free baseline in [Analysis 01](smairt_template_demos/ppi_network/ppi_network/analysis/ANALYSIS_01.md), we observe a gradual degradation under noise rather than a sudden precipitous drop.

| Comparison | Previous Best ($r=0$) | This Result ($r=0.30$) | Delta |
|-----------|--------------|-------------|-------|
| Hub Recovery Precision@3 | 1.00 | 1.00 (Deg) / 1.00 (Bet) | 0.00 |
| Community Recovery ARI | 1.00 | 0.922 | -0.078 |

At $r = 0.45$, community recovery remains remarkably high ($0.829$) but hub recovery drops below the acceptable threshold ($0.667$).

---

## Implications

1. **Greedy Modularity Robustness**: The community detection method is mathematically robust to random edge additions/removals because it globally optimizes a partition score, which aggregates signals across all nodes in a community.
2. **Hub Centrality Alignment**: Degree and betweenness centrality degrade in tandem. This suggests that the bottleneck nature of hubs is strongly coupled with their high connection counts, even in noisy networks.

---

## Next Steps

1. **Transition to Benchmark Data (Fidelity Ladder Level 3 / Phase 2)**:
   - Having established robust performance on synthetic structures, we should move to download or load a real-world PPI network benchmark dataset (e.g., from STRING, BioGRID, or a standard subset of yeast/human protein interaction databases).
   - In benchmark data, the ground-truth communities may be represented by known biological pathways or functional families (e.g., Gene Ontology terms, KEGG pathways, or protein complexes like MIPS/CORUM).
2. **Handle Fuzzy / Overlapping Communities**:
   - In real-world data, modules overlap (a protein can belong to multiple pathways). We should consider evaluating a community detection method that handles overlap, or document how traditional partitioning handles overlapping ground-truth sets.

---

## Files Generated

- `results/results_noise_robustness.csv` — CSV of sweep metrics across trials
- `results/logs/script_02_noise_robustness_20260630_083436.log` — Full execution output
- `results/figures/script_02_noise_robustness_metrics.png` — Plot showing metric means and SD error bars
- `results/figures/script_02_noise_robustness_metrics.pdf` — Publication-quality vector plot of the results
