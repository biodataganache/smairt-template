# 01_initial_question.md

## Brief Background

Proteins rarely act alone; they form **interaction networks** where each protein
is a node and each physical or functional interaction is an edge. The shape of
that network is informative: a few proteins (**hubs**) interact with many
partners and are often essential, and groups of proteins that interact heavily
with each other (**modules** or **communities**) tend to share a function or a
pathway.

This SMAIRT project builds the analysis on a **synthetic network with a known
structure**: you plant a small number of hub proteins and a few dense modules,
then check whether standard graph methods **recover what you planted**. Once the
methods are trusted on known-truth data, the same pipeline can be pointed at a
real interaction list later.

It is CPU-only, pure Python (networkx/numpy/pandas/matplotlib), and needs no
external data to get started.

## Question

In a protein-protein interaction network, can standard graph methods reliably
**identify the most important proteins (hubs)** and **detect the functional
modules (communities)** that are actually present?

## Hypothesis

Centrality measures (especially **degree** and **betweenness** centrality) will
rank the planted hub proteins at the top, and a community-detection algorithm
will recover the planted modules with high agreement, as long as the modules are
denser internally than the background random connections.

## Evidence / metrics

- **Hub recovery:** the planted hubs appear in the top-k by centrality
  (precision/recall against the planted hub set).
- **Community recovery:** agreement between detected communities and planted
  module labels (e.g. adjusted Rand index or normalized mutual information).
- **Robustness:** how recovery degrades as you add random "noise" edges or remove
  true edges.
- **Visual check:** the network drawing should show the hubs and modules if the
  methods agree with the plant.

## Domain Context

### The structures we plant
- **Hub:** a node with unusually high degree (many interaction partners). Often
  biologically essential.
- **Module / community:** a set of nodes that interact much more with each other
  than with the rest of the network; usually a shared pathway or complex.

### Graph methods
- **Degree centrality:** how many partners a protein has. Simplest hub measure.
- **Betweenness centrality:** how often a protein lies on shortest paths between
  others; flags "bottleneck" connectors.
- **Community detection:** algorithms (e.g. greedy modularity or the Louvain
  method in networkx) that partition the graph into densely connected groups.

### Fidelity ladder (SMAIRT data progression)
1. **Synthetic / planted:** generate a graph with a known number of hubs and
   modules (e.g. a stochastic block model plus a few high-degree nodes); confirm
   centrality finds the hubs and community detection finds the modules.
   (Start here.)
2. **Synthetic, harder:** add random noise edges and rewire some true edges, then
   measure how hub/community recovery degrades. Find the noise level where the
   methods break down.
3. **Real (optional, later):** load a small published interaction list (e.g. a
   subset of STRING or BioGRID for one organism or complex). Truth is now real
   biology, so discuss which detected hubs/modules make biological sense and
   which are artifacts.

### Caveats
- Real PPI data is noisy and incomplete: false-positive interactions and missing
  edges are common, and "importance" in a network does not always equal
  biological essentiality. Community boundaries are fuzzy. Naming these limits
  next to the result is part of the SMAIRT method.

## Known design values (for validation)

| Item | Value |
|------|-------|
| Number of nodes | your choice (e.g. ~100-300) |
| Planted hubs | a small known set (e.g. 3-5) |
| Planted modules | a known count with known membership |
| Within-module edge probability | higher than between-module (so modules are real) |
| Hub recovery metric | precision/recall of planted hubs in top-k centrality |
| Community recovery metric | adjusted Rand index / NMI vs. planted labels |
| random seed | fixed (reproducibility) |
