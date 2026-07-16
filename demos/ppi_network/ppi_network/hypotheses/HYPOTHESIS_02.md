# Hypothesis 02 — Robustness of Hub and Community Recovery under Edge Noise

## Status: PARTIALLY SUPPORTED

## Background

In [Analysis 01](smairt_template_demos/ppi_network/ppi_network/analysis/ANALYSIS_01.md), we showed that standard graph algorithms perfectly recovered planted hubs and modular communities under noise-free conditions (Fidelity Ladder Level 1). However, real-world Protein-Protein Interaction (PPI) networks are notoriously noisy, featuring high rates of both false positives (spurious edges) and false negatives (missing interactions). To transition toward real-world applicability (Fidelity Ladder Level 2), we must assess how these algorithms degrade when subjected to controlled structural noise.

## Hypothesis Statement

**Prediction**:
As we systematically randomize (rewire) a fraction $r$ of the network's edges:
1. **Hub Recovery**: Degree centrality will be more robust than betweenness centrality. Degree centrality will maintain a Precision@3 >= 0.8 for noise levels up to 30% ($r \le 0.3$), whereas betweenness centrality will drop below 0.8 at lower noise levels ($r > 0.15$).
2. **Community Recovery**: Community detection (greedy modularity) is highly sensitive to noise; the Adjusted Rand Index (ARI) and Normalized Mutual Information (NMI) will drop below 0.8 when $r > 0.15$.

**Rationale**:
- **Hubs**: Hub nodes have an extremely high baseline degree (40 connections). Rewiring edges at random is highly unlikely to uniformly target a single node, so the hub nodes will retain a substantially higher degree than the background non-hub nodes (mean degree ~16.5) even at moderate noise levels. Betweenness centrality, however, relies on specific shortest-path bottlenecks; random rewiring quickly provides alternative paths through the network, destroying these bottlenecks and rapidly degrading betweenness-based hub recovery.
- **Communities**: Greedy modularity maximizes the difference between within-community edge density and background edge density. Rewiring edges transfers edges from dense within-community connections to sparse between-community connections, quickly eroding the community contrast and confusing the greedy partitioning heuristic.

**Success criteria**:
- Confirm that degree centrality maintains Precision@3 >= 0.8 up to $r = 0.3$.
- Confirm that betweenness centrality Precision@3 drops below 0.8 before degree centrality does.
- Identify the exact noise threshold $r$ where modular community detection ARI drops below 0.8.

## Experimental Design

- **Script**: `experiments/01_synthetic/script_02_noise_robustness.py`
- **Phase**: synthetic
- **Track**: Track-free (Robustness evaluation)
- **Data**: Synthetic network of 153 nodes generated as in Script 01, but with random edge rewiring applied.
- **Controls**: Baseline comparison with noise-free results ($r = 0.0$).
- **Key metrics**:
  - Precision@3 and Recall@3 for both Degree and Betweenness centrality.
  - Adjusted Rand Index (ARI) and Normalized Mutual Information (NMI) for Community Recovery.
  - Swept parameter: Edge rewiring fraction $r \in [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]$.
  - Number of trials: 5 independent random initializations (seeds) per noise level to obtain average and standard deviation error bars.

## Dependencies

- Network generation code from `script_01_synthetic_validation.py`.
- Shared library: `scripts/shared/logging.py` for `TeeLogger` and `setup_logging`.

## Results

The hypothesis was **partially supported**:
- **Hub Recovery**: Degree and betweenness centrality both maintained robust performance (P@3 >= 0.8) up to 30% noise ($r \le 0.30$), but we refuted the prediction that betweenness centrality is less robust than degree centrality. In fact, betweenness centrality matched or exceeded degree centrality across almost all noise levels.
- **Community Recovery**: Refuted the prediction that modular community detection is sensitive and drops below 0.8 when $r > 0.15$. Modularity community detection proved highly robust, keeping ARI >= 0.8 up to 45% noise ($r = 0.45$).

See [`analysis/ANALYSIS_02.md`](smairt_template_demos/ppi_network/ppi_network/analysis/ANALYSIS_02.md) for full details and visualizations.

## Notes

- An edge rewiring is defined as: randomly selecting an existing edge $(u, v)$ in the graph, removing it, and adding a new edge $(x, y)$ between two random nodes $x$ and $y$ that are not currently connected, preserving the total edge count.
- Standard error of the mean (SEM) or standard deviation (SD) will be plotted to ensure statistically meaningful findings.
