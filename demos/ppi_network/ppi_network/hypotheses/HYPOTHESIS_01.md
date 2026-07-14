# Hypothesis 01 — Baseline Hub and Community Recovery in Synthetic PPI Networks

## Status: SUPPORTED

## Background

Protein-protein interaction (PPI) networks biologically consist of highly connected hub proteins (which are often essential) and densely clustered communities/modules (which represent shared pathways or complexes). This is the initial iteration of the SMAIRT workflow. We generate a synthetic network with a known ground-truth structure (planted hubs and communities) to verify if standard graph-theoretic centrality metrics and partition algorithms can accurately recover what was planted.

## Hypothesis Statement

**Prediction**:
In a noise-free synthetic graph:
1. Standard centrality metrics (degree and betweenness centrality) will perfectly identify the planted hub proteins at the top (Precision@3 = 1.0, Recall@3 = 1.0).
2. Greedy modularity community detection will perfectly recover the original community membership of non-hub nodes (Adjusted Rand Index [ARI] = 1.0 and Normalized Mutual Information [NMI] = 1.0), provided that the intra-community edge probability ($p_{in} = 0.3$) is significantly higher than the inter-community edge probability ($p_{out} = 0.02$).

**Rationale**:
Since there is zero background noise or random rewiring, the structural gap between the dense communities and sparse background connections, and between the hub connections and background degrees, is extremely high. Graph algorithms designed to maximize modularity and node centrality should easily resolve these distinct structures under ideal, noise-free conditions.

**Success criteria**:
- **Hub Recovery**: Precision@3 = 1.0, Recall@3 = 1.0 for degree centrality and betweenness centrality.
- **Community Recovery**: ARI = 1.0 and NMI = 1.0 for detected communities vs. planted communities on non-hub nodes.

## Experimental Design

- **Script**: `experiments/01_synthetic/script_01_synthetic_validation.py`
- **Phase**: synthetic
- **Track**: Track-free (Initial validation)
- **Data**: Synthetic network of 153 nodes:
  - 3 planted modules of 50 nodes each ($p_{in} = 0.3, p_{out} = 0.02$)
  - 3 planted hub nodes, each connected to 40 randomly chosen nodes in the graph
- **Controls**: Since this is a baseline, we compare performance against ideal ground-truth labels.
- **Key metrics**:
  - Precision@3 and Recall@3 for Hub Recovery
  - Adjusted Rand Index (ARI) and Normalized Mutual Information (NMI) for Community Recovery

## Dependencies

- None (Initial script; CPU-only pure Python)
- Shared library: `scripts/shared/logging.py` for `TeeLogger` and `setup_logging`

## Results

The hypothesis was **fully supported**:
- Both **Degree Centrality** and **Betweenness Centrality** achieved perfect hub recovery, ranking the 3 planted hubs (nodes 150, 151, and 152) at the top (Precision@3 = 1.0, Recall@3 = 1.0).
- Modularity community detection perfectly recovered the 3 dense planted modules on the 150 non-hub nodes (Adjusted Rand Index [ARI] = 1.0, Normalized Mutual Information [NMI] = 1.0).

See [`analysis/ANALYSIS_01.md`](smairt_template_demos/ppi_network/ppi_network/analysis/ANALYSIS_01.md) for full details and visualizations.

## Notes

- Hubs must be removed before running community detection, as their global connections can bridge modules and degrade modularity partitioning.
- Seed is fixed to 1024 for reproducibility.
