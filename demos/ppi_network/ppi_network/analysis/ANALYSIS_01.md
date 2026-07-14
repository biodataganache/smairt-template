# Analysis 01 — Baseline Hub and Community Recovery in Synthetic PPI Networks

## Executive Summary

We evaluated standard graph-theoretic centrality metrics and a modularity-based community detection algorithm on a synthetic, noise-free Protein-Protein Interaction (PPI) network containing 3 dense planted modules and 3 high-degree planted hubs. Under these ideal conditions, both degree and betweenness centrality achieved perfect hub recovery (Precision@3 = 1.0, Recall@3 = 1.0), and greedy modularity community detection perfectly partitioned the non-hub nodes back into their planted community structures (ARI = 1.0, NMI = 1.0). The results fully support our hypothesis, establishing a reliable, noise-free baseline for subsequent iteration phases.

## Experiment Details

- **Script**: `experiments/01_synthetic/script_01_synthetic_validation.py`
- **Hypothesis**: `hypotheses/HYPOTHESIS_01.md`
- **Log**: `results/logs/script_01_synthetic_validation_20260629_125128.log`
- **Track**: Track-free (Initial validation)
- **Phase**: synthetic

## Key Results

Our first iteration successfully verified the primary functionalities of network generation, centrality tracking, and modularity community detection:
1. **Network Properties**: Generated a graph with 153 nodes and 1,297 edges. The average degree of non-hub nodes was 16.49, whereas each of the 3 planted hubs had a degree of exactly 40 (significantly higher than the background average).
2. **Hub Centrality Rankings**:
   - **Degree Centrality**: The top 3 nodes were exactly the planted hubs: 150, 151, and 152 (Centrality: 0.2632 each).
   - **Betweenness Centrality**: Planted hubs also ranked 1st, 2nd, and 3rd: 151 (0.0735), 150 (0.0720), and 152 (0.0704).
3. **Community Partitioning**:
   - Partitioning the 150 non-hub community nodes using greedy modularity successfully yielded 3 communities matching ground-truth modules.

| Metric | Expected | Observed | Status |
|--------|----------|----------|--------|
| Degree Centrality Precision@3 | 1.00 | 1.00 | ✓ |
| Degree Centrality Recall@3 | 1.00 | 1.00 | ✓ |
| Betweenness Centrality Precision@3 | 1.00 | 1.00 | ✓ |
| Betweenness Centrality Recall@3 | 1.00 | 1.00 | ✓ |
| Community Recovery ARI | 1.00 | 1.00 | ✓ |
| Community Recovery NMI | 1.00 | 1.00 | ✓ |

## Hypothesis Assessment

### SUPPORTED

The hypothesis was **fully supported**.
- **Hub Recovery**: Both degree centrality and betweenness centrality perfectly ranked the 3 planted hubs at the top. The substantial degree separation (40 vs. 16.49) made degree centrality extremely robust. The hubs' wide, random connection profile across all modules also made them critical bottlenecks for shortest paths, leading to high betweenness centrality.
- **Community Detection**: Because within-module edge density ($p_{in} = 0.3$) was 15× larger than between-module noise density ($p_{out} = 0.02$), greedy modularity community detection faced no issues in partitioning nodes correctly after hubs were removed (ARI = 1.00, NMI = 1.00).

### Where It Works (Boundaries)
- **High Modular Density Contrast**: Succeeded where $p_{in} / p_{out} = 15$. This high signal-to-noise ratio leaves modular boundaries sharp and unambiguous.
- **Hub Prominence**: Succeeded where hubs have a degree ($d = 40$) that is $2.4\times$ greater than the non-hub average degree ($d_{avg} = 16.49$).
- **Hub Exclusion during Community Detection**: Removing global hub nodes before executing partitioning was successful. Leaving them in would have blurred the module boundaries and degraded modularity partitioning.

### Where It Breaks Down
- **No Noise/Edge Loss**: Under current ideal conditions, no true edges are missing and no background noise exists. Real PPI networks are notoriously noisy, with high false-positive and false-negative edge rates, which will likely degrade these metrics.

## Comparison to Prior Work

*(First experiment in this project, establishing the absolute baseline).*

| Comparison | Previous Best | This Result | Delta |
|-----------|--------------|-------------|-------|
| Hub Recovery Precision@3 | N/A | 1.00 | Baseline |
| Community Recovery ARI | N/A | 1.00 | Baseline |

## Implications

Our results show that graph theory algorithms function exactly as expected under noise-free, highly structured synthetic conditions. This proves that our network generation pipeline, logging setups, evaluation metrics (precision/recall, ARI, NMI), and visualization plots are correct and reliable.

## Next Steps

1. **Test Robustness under Structural Noise (Fidelity Ladder Level 2)**:
   - Introduce random noise to the synthetic network by:
     - **Adding random noise edges** (false positives).
     - **Removing true edges** (false negatives / missing data).
   - Trace how hub precision/recall and community ARI degrade as noise levels increase from 0% to 50%.
2. **Determine the Breakdown Threshold**:
   - Locate the exact noise boundary where community detection (ARI < 0.8) and hub recovery (Precision < 0.8) break down.

## Files Generated

- `results/logs/script_01_synthetic_validation_20260629_125128.log` — Raw execution output
- `results/figures/script_01_synthetic_validation_network.png` — High-DPI network visualization
- `results/figures/script_01_synthetic_validation_network.pdf` — Publication-ready vector network visualization

## Intellectual Contribution Notes

- The initial question was supplied by the background research files.
- The experiment layout, including removing hubs before community detection and calculating modularity metrics, was designed and executed following standard SMAIRT principles.
