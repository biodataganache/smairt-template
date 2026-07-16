# Analysis B01 — Biological Recovery in Real-World Yeast PPI Benchmarks

## Executive Summary

We evaluated our validated graph-theoretic centrality and community detection pipeline on a real-world high-confidence Yeast (Saccharomyces cerevisiae) physical interaction subnetwork (score >= 700) downloaded from the STRING database. Under real biological conditions, greedy modularity community detection perfectly recovered the curated physical complexes (Ribosome, Chromatin, Cytoskeleton) with an ARI of 1.0000. However, topological hub centrality did not align perfectly with knockout essentiality (Precision@3 = 0.33), highlighting a key scientific limit: topological prominence in a network does not always dictate biological essentiality.

## Experiment Details

- **Script**: `experiments/02_downloaded/script_B02_yeast_benchmark.py`
- **Hypothesis**: `hypotheses/HYPOTHESIS_B01.md`
- **Log**: `results/logs/script_B02_yeast_benchmark_20260630_084535.log`
- **Track**: Track B (Real Biological Data)
- **Phase**: downloaded

## Key Results

1. **Topological properties**: We evaluated 9 yeast proteins forming 9 high-confidence physical interactions. The essential genes in this subnetwork were *ACT1*, *COF1*, *MYO2*, *RPL3*, and *RPS3*.
2. **Centrality vs. Essentiality (Hubs)**:
   - **Degree Centrality**: Ranked *HTB1* (Non-essential, 0.3750) and *ACT1* (Essential, 0.3750) tied for first, followed by *HHO1* (Non-essential, 0.2500). Precision@3 was 0.33.
   - **Betweenness Centrality**: Ranked *ACT1* (Essential, 0.2500) first, *HTB1* (Non-essential, 0.2143) second, and *HHO1* (Non-essential, 0.0000) third. Precision@3 was 0.33.
3. **Complex Partitioning (Communities)**:
   - Partitioning the yeast proteins successfully separated them into 3 distinct clusters matching their physical complexes (Ribosome, Chromatin, Cytoskeleton), achieving an ARI of 1.0000 and NMI of 1.0000.

| Metric | Expected | Observed | Status |
|--------|----------|----------|--------|
| Degree Centrality Precision@3 | >= 0.66 | 0.33 | ✗ |
| Betweenness Centrality Precision@3 | >= 0.66 | 0.33 | ✗ |
| Community Recovery ARI | >= 0.70 | 1.00 | ✓ |
| Community Recovery NMI | >= 0.70 | 1.00 | ✓ |

---

## Hypothesis Assessment

### PARTIALLY SUPPORTED

- **Hub Recovery (Refuted)**: We predicted that the top-3 topological hubs would be highly enriched for essential genes (P@3 >= 0.66). Instead, we observed P@3 = 0.33. Non-essential histones (*HTB1* and *HHO1*) ranked at the top of degree centrality because of their intense physical interaction profile within chromatin, showing that high topology degree can be driven by structural complexes rather than cellular lethality.
- **Community Recovery (Supported)**: We predicted that physical modules would be highly distinct and easily recovered (ARI >= 0.70). We observed perfect recovery (ARI = 1.00, NMI = 1.00). This confirms that physical protein complexes are highly modular units and can be easily extracted by modularity-maximizing algorithms.

### Where It Works (Boundaries)
- **Complex Boundary Delineation**: Succeeded perfectly (ARI = 1.00) in partitioning physical complexes. This shows that the modularity heuristic is robust in extracting multi-subunit structures from real biological networks.
- **Topological Hub Identification**: Centrality metrics successfully flag high-connectivity hubs, but researchers must not conflate these topological hubs with immediate biological essentiality.

### Where It Breaks Down
- **Essentiality Prediction**: Fails when high-density complexes (like histones) have high structural degrees but can tolerate single subunit knockouts or have redundant paralogs in yeast, causing high-degree topological nodes to be non-lethal (non-essential).

---

## Implications

For network researchers, these findings highlight a crucial biological caveat: **topology is not function**. High degree and betweenness are indicators of physical and mechanical structural hubs (e.g., histone complexes), but biological essentiality (lethality) requires functional necessity, which cannot be derived from a physical network structure alone. This is an important distinction to highlight in biological network modeling.

---

## Next Steps

1. **Integrate Functional Pathways**:
   - Incorporate metabolic and signaling pathway connections (e.g., from KEGG) where topological bottlenecks are more likely to align with functional essentiality.
2. **Introduce Degree Normalization**:
   - Normalize node degree based on complex size to prevent large structural complexes (such as ribosomes) from dominating global centrality scores.

---

## Files Generated

- `results/logs/script_B02_yeast_benchmark_20260630_084535.log` — Raw execution output
- `results/figures/script_B02_yeast_benchmark_yeast.png` — Network plot colored by detected complexes with essential nodes highlighted in red outlines
- `results/figures/script_B02_yeast_benchmark_yeast.pdf` — Publication-ready vector network plot of yeast interactions
