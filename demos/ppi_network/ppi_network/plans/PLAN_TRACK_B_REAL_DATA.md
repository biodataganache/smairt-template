# Plan: Track B — Real Biological Network Benchmark Validation

## Status: ACTIVE

## Problem Statement

While synthetic networks are excellent for testing algorithm performance under controlled conditions, they do not fully capture the complexity, bias, and noise profiles of real biological data. In biological networks:
- Communities are overlapping (proteins participate in multiple complexes and pathways).
- Node degree distributions follow a scale-free power law, leading to many low-degree nodes and a few massive hubs.
- High rates of false-positive and false-negative interactions are present due to experimental limitations (e.g., yeast two-hybrid vs. mass spectrometry).

To make our workflow practical and illustrative for researchers, we need a clear, well-curated real-world biological dataset where we can test whether our validated pipeline successfully recovers real biological complexes (modules) and essential proteins (hubs).

## Proposed Dataset: Yeast Core PPI (Saccharomyces cerevisiae)

We select **Yeast (Saccharomyces cerevisiae)** as our model biological organism because it is the most well-characterized eukaryote with highly curated, high-confidence interaction networks and comprehensive ground-truth annotations.

### 1. The Interaction Network (Data Source)
We will target high-confidence physical interactions. Two primary source options exist:
- **STRING Database (Core Subnetwork)**: We can programmatically fetch the top 200–500 highest-confidence yeast interactions (confidence score >= 700 or 900) using STRING's public API or download a subset from BioGRID.
- **BioGRID Yeast physical interactions**: A well-curated set of physical interactions confirmed by low-throughput or multiple high-throughput experiments.

### 2. Ground-Truth Biological Modules
To evaluate community recovery without needing a domain expert's manual interpretation, we use standard curated databases:
- **MIPS/CORUM Complexes**: Curated lists of physical protein complexes (e.g., the **Ribosome**, **Proteasome**, **RNA Polymerase II**, and **Nucleosome**).
- **Gene Ontology (GO) Slim Terms**: Broad functional classes (e.g., "DNA repair", "translation", "transcription").

### 3. Ground-Truth Hubs (Biological Essentiality)
- Curated databases like the **Saccharomyces Genome Deletion Project** specify which yeast genes are **essential** (lethal when deleted).
- We will test if our top-ranked centrality hubs correspond to these known essential proteins.

---

## Technical Approach

### Step 1: Programmatic Data Acquisition
We will write a download script `script_B01_download_yeast_data.py` to fetch:
1. A high-confidence Yeast PPI network from STRING's public API (e.g., mapping to 100-300 proteins for a clean, clear visualization).
2. Curated complex membership annotations (e.g., mapping proteins to standard complexes).
3. Essentiality annotation tables.

### Step 2: Hub & Community Evaluation
We will write `script_B02_yeast_benchmark.py`:
- **Hub Evaluation**: Run degree and betweenness centrality. Calculate precision/recall against known essential yeast genes.
- **Community Evaluation**: Run greedy modularity community detection. Compare detected clusters against known protein complex assignments (e.g., Ribosome, Proteasome) using the Adjusted Rand Index (ARI).
- **Visualization**: Plot the real yeast subnetwork with nodes colored by detected communities, sized by degree, and labeled with actual gene names (e.g., *ACT1*, *MYC*, *HTA1*) to make the network highly readable and meaningful.

---

## Success Criteria

1. **Automation**: A single, reproducible download script fetches all necessary files.
2. **Hub Association**: Standard centrality measures successfully identify known essential yeast genes as top hubs with high statistical significance (e.g., Enrich score or Precision >= 0.70).
3. **Community Biological Coherence**: Detected communities align strongly with known biological complexes (Ribosome/Proteasome), achieving an ARI >= 0.60 against curated assignments.
4. **Readability**: The final network figure uses actual gene names (not arbitrary IDs) and clearly highlights recognized complexes.

---

## Steps

1. [ ] **Step 1**: Write and execute `script_B01_download_yeast_data.py` to retrieve high-confidence physical interactions and GO/complex annotations for Yeast.
2. [ ] **Step 2**: Create `hypotheses/HYPOTHESIS_B01.md` detailing the biological recovery expectations.
3. [ ] **Step 3**: Write and execute `script_B02_yeast_benchmark.py` to perform the evaluations, produce metrics, and generate a beautiful gene-labeled visualization.
4. [ ] **Step 4**: Summarize results in `analysis/ANALYSIS_B01.md`.

---

## Expected Outputs

- `experiments/02_downloaded/script_B01_download_yeast_data.py` — Programmatic downloader
- `experiments/02_downloaded/script_B02_yeast_benchmark.py` — Evaluation & biological mapping
- `results/figures/script_B02_yeast_network.png` — Beautiful, gene-labeled biological network visualization
- `analysis/ANALYSIS_B01.md` — Interpretation of the biological findings and algorithmic limitations on real-world noisy networks
