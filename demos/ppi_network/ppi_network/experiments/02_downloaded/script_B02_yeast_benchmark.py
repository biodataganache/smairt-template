#!/usr/bin/env python3
"""
Script B02: Yeast Biological PPI Benchmark Evaluation

Hypothesis: hypotheses/HYPOTHESIS_B01.md
Phase: downloaded
Track: Track B (Real Biological Data)
Iteration: 3

Depends on:
  - experiments/02_downloaded/script_B01_download_yeast_data.py
  - data/downloaded/yeast_ppi.csv
"""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

# === PATH SETUP ===
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

# === CONFIGURATION ===
SCRIPT_NAME = "script_B02_yeast_benchmark"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIG_DIR = PROJECT_ROOT / "results" / "figures"
DATA_FILE = PROJECT_ROOT / "data" / "downloaded" / "yeast_ppi.csv"
SEED = 1024

def load_yeast_network(file_path):
    """
    Load the yeast interaction CSV and construct a NetworkX graph.
    Extract biological ground-truth labels for essentiality and complexes.
    """
    df = pd.read_csv(file_path)
    
    # Filter for high-confidence physical interactions
    df_high = df[df["score"] >= 700].copy()
    
    G = nx.Graph()
    essential_genes = set()
    complex_labels = {}
    
    # Selected proteins to check complex memberships
    # If the interaction is annotated with a specific module, we map both proteins
    for _, row in df_high.iterrows():
        p1, p2 = row["p1"], row["p2"]
        score = row["score"]
        
        G.add_edge(p1, p2, weight=score)
        
        # Track essentiality annotations
        if row["p1_essential"]:
            essential_genes.add(p1)
        if row["p2_essential"]:
            essential_genes.add(p2)
            
        # Track complex modules
        module = row["module"]
        if module != "Background":
            complex_labels[p1] = module
            complex_labels[p2] = module
            
    # Default proteins to their respective clusters if not captured in module rows
    # Standard biological complexes mappings:
    default_mapping = {
        "RPL3": "Ribosome", "RPL4": "Ribosome", "RPS3": "Ribosome", "RPS4": "Ribosome",
        "HTA1": "Chromatin", "HTB1": "Chromatin", "HHO1": "Chromatin",
        "ACT1": "Cytoskeleton", "MYO2": "Cytoskeleton", "COF1": "Cytoskeleton"
    }
    for node in G.nodes():
        if node not in complex_labels and node in default_mapping:
            complex_labels[node] = default_mapping[node]
        elif node not in complex_labels:
            complex_labels[node] = "Other"
            
    return G, essential_genes, complex_labels

def evaluate_yeast_hubs(G, essential_genes):
    """
    Rank proteins by centrality and calculate precision and recall 
    against known biological essential genes (lethal deletions).
    """
    k = 3
    
    # Degree centrality
    deg_cent = nx.degree_centrality(G)
    top_deg = sorted(deg_cent, key=deg_cent.get, reverse=True)[:k]
    deg_precision = len(set(top_deg) & essential_genes) / k
    deg_recall = len(set(top_deg) & essential_genes) / len(essential_genes)
    
    # Betweenness centrality
    bet_cent = nx.betweenness_centrality(G, seed=SEED)
    top_bet = sorted(bet_cent, key=bet_cent.get, reverse=True)[:k]
    bet_precision = len(set(top_bet) & essential_genes) / k
    bet_recall = len(set(top_bet) & essential_genes) / len(essential_genes)
    
    return {
        "deg_centrality": deg_cent,
        "bet_centrality": bet_cent,
        "deg_top_k": top_deg,
        "deg_precision": deg_precision,
        "deg_recall": deg_recall,
        "bet_top_k": top_bet,
        "bet_precision": bet_precision,
        "bet_recall": bet_recall,
    }

def evaluate_yeast_communities(G, complex_labels):
    """
    Run greedy modularity partitioning and compare detected clusters 
    against curated protein complex annotations.
    """
    # Exclude nodes labeled as 'Other' to get a clean evaluation on core complex nodes
    eval_nodes = [n for n in G.nodes() if complex_labels.get(n) != "Other"]
    G_sub = G.subgraph(eval_nodes)
    
    detected_comm_sets = list(nx.community.greedy_modularity_communities(G_sub))
    detected_labels = {}
    for comm_idx, comm_set in enumerate(detected_comm_sets):
        for node in comm_set:
            detected_labels[node] = comm_idx
            
    nodes_sorted = sorted(eval_nodes)
    y_true = [complex_labels[n] for n in nodes_sorted]
    y_pred = [detected_labels.get(n, -1) for n in nodes_sorted]
    
    ari = adjusted_rand_score(y_true, y_pred)
    nmi = normalized_mutual_info_score(y_true, y_pred)
    
    return {
        "detected_labels": detected_labels,
        "detected_communities": detected_comm_sets,
        "ari": ari,
        "nmi": nmi,
    }

def visualize_yeast_network(G, detected_labels, essential_genes, fig_path):
    """Plot Yeast network with actual gene labels and community coloring."""
    fig_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 8))
    
    # Spring layout
    pos = nx.spring_layout(G, seed=SEED, k=0.35, iterations=60)
    
    # Map colors and sizes
    node_colors = []
    node_sizes = []
    node_edge_colors = []
    node_linewidths = []
    
    for node in G.nodes():
        # Node size scaled by degree
        node_sizes.append(100 + G.degree(node) * 120)
        
        # Color by detected community cluster (fallback to a default if not evaluated)
        comm_idx = detected_labels.get(node, 9)
        node_colors.append(comm_idx)
        
        # Outline: Highlight essential biological genes in bold red
        if node in essential_genes:
            node_edge_colors.append("red")
            node_linewidths.append(2.5)
        else:
            node_edge_colors.append("black")
            node_linewidths.append(1.0)
            
    # Draw network
    nx.draw_networkx_nodes(
        G, pos,
        node_color=node_colors,
        node_size=node_sizes,
        edgecolors=node_edge_colors,
        linewidths=node_linewidths,
        cmap=plt.cm.Set2,
        alpha=0.85
    )
    
    # Draw edges with weight transparency
    edges = G.edges()
    weights = [G[u][v].get("weight", 500) / 1000.0 for u, v in edges]
    nx.draw_networkx_edges(G, pos, width=2.0, alpha=0.25, edge_color="gray")
    
    # Draw labels with actual Gene Names (e.g. RPL3, ACT1, HTA1)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold", font_color="black")
    
    plt.title("Yeast High-Confidence Interaction Network\n"
              "(Node Size: Degree Centrality | Node Color: Detected Complex | Red Outline: Essential Gene)", 
              fontsize=12)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=300)
    plt.savefig(fig_path.with_suffix(".pdf"), dpi=300)
    plt.close()

def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)
    
    # Data Validation Check
    assert DATA_FILE.exists(), f"Benchmark data file is missing: {DATA_FILE}. Run script_B01 first!"

    with TeeLogger(log_path):
        print(f"{'='*60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Hypothesis: biological hub and community recovery in Yeast PPI networks")
        print(f"{'='*60}")
        print()

        # 1. Load Data
        print("--- LOAD & PREPROCESS YEAST DATA ---")
        G, essential_genes, complex_labels = load_yeast_network(DATA_FILE)
        print(f"Unique Proteins (Nodes): {G.number_of_nodes()}")
        print(f"High-Confidence Interactions (Edges): {G.number_of_edges()}")
        print(f"Essential Genes in network: {[g for g in sorted(G.nodes()) if g in essential_genes]}")
        print()

        # 2. Hub Recovery Evaluation (Essentiality)
        print("--- BIOLOGICAL HUB EVALUATION ---")
        hub_results = evaluate_yeast_hubs(G, essential_genes)
        
        print("Degree Centrality Top 3:")
        for idx, node in enumerate(hub_results["deg_top_k"]):
            is_ess = "ESSENTIAL" if node in essential_genes else "NON-ESSENTIAL"
            print(f"  {idx+1}. Gene {node} ({is_ess} | Centrality: {hub_results['deg_centrality'][node]:.4f})")
        print(f"Degree Centrality Precision@3: {hub_results['deg_precision']:.2f}")
        print(f"Degree Centrality Recall@3: {hub_results['deg_recall']:.2f}")
        print()
        
        print("Betweenness Centrality Top 3:")
        for idx, node in enumerate(hub_results["bet_top_k"]):
            is_ess = "ESSENTIAL" if node in essential_genes else "NON-ESSENTIAL"
            print(f"  {idx+1}. Gene {node} ({is_ess} | Centrality: {hub_results['bet_centrality'][node]:.4f})")
        print(f"Betweenness Centrality Precision@3: {hub_results['bet_precision']:.2f}")
        print(f"Betweenness Centrality Recall@3: {hub_results['bet_recall']:.2f}")
        print()

        # 3. Community Detection Evaluation (Curated Complexes)
        print("--- BIOLOGICAL COMMUNITY EVALUATION ---")
        comm_results = evaluate_yeast_communities(G, complex_labels)
        print(f"Number of communities detected: {len(comm_results['detected_communities'])}")
        print(f"Adjusted Rand Index (ARI): {comm_results['ari']:.4f}")
        print(f"Normalized Mutual Information (NMI): {comm_results['nmi']:.4f}")
        print()

        # 4. Generate Visualization
        print("--- GENERATING VISUALIZATION ---")
        fig_path = FIG_DIR / f"{SCRIPT_NAME}_yeast.png"
        visualize_yeast_network(G, comm_results["detected_labels"], essential_genes, fig_path)
        print(f"Saved Yeast network plot to {fig_path} (and .pdf)")
        print()

        # 5. Sanity Checks
        print("--- SANITY CHECKS ---")
        assert G.number_of_nodes() >= 5, f"Expected at least 5 yeast proteins, got {G.number_of_nodes()}"
        print("All assertions passed!")
        print()

        print(f"{'='*60}")
        print("=== COMPLETE ===")
        print(f"{'='*60}")

if __name__ == "__main__":
    main()
