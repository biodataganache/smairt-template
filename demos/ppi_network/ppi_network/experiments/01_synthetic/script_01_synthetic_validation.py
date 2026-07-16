#!/usr/bin/env python3
"""
Script 01: Baseline Hub and Community Recovery in Synthetic PPI Networks

Hypothesis: hypotheses/HYPOTHESIS_01.md
Phase: synthetic
Track: Track-free
Iteration: 1

Depends on:
  - None (Initial script)
"""

import sys
import random
from pathlib import Path
from datetime import datetime
import numpy as np
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

# === PATH SETUP ===
# Path to script: ppi_network/experiments/01_synthetic/script_01_synthetic_validation.py
# Parents[2] gets us to: ppi_network
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

# === CONFIGURATION ===
SCRIPT_NAME = "script_01_synthetic_validation"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIG_DIR = PROJECT_ROOT / "results" / "figures"
SEED = 1024

def set_seeds(seed=SEED):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)

def generate_synthetic_network(seed=SEED):
    """
    Generate synthetic network with known modules and hubs.
    - 3 modules of 50 nodes each (nodes 0 to 149)
    - p_in = 0.3, p_out = 0.02
    - 3 hubs (nodes 150, 151, 152) each connected to 40 randomly selected community nodes
    """
    set_seeds(seed)
    G = nx.Graph()
    
    # 1. Create community nodes and assign ground truth labels
    num_communities = 3
    nodes_per_comm = 50
    total_comm_nodes = num_communities * nodes_per_comm
    
    community_assignments = {}
    for i in range(total_comm_nodes):
        comm_idx = i // nodes_per_comm
        community_assignments[i] = comm_idx
        G.add_node(i, type="community", true_community=comm_idx)
        
    # 2. Add edges within and between communities (SBM-like)
    p_in = 0.3
    p_out = 0.02
    
    # Generate edges for community nodes
    for u in range(total_comm_nodes):
        for v in range(u + 1, total_comm_nodes):
            u_comm = community_assignments[u]
            v_comm = community_assignments[v]
            if u_comm == v_comm:
                if random.random() < p_in:
                    G.add_edge(u, v)
            else:
                if random.random() < p_out:
                    G.add_edge(u, v)
                    
    # 3. Add planted hubs
    num_hubs = 3
    hub_nodes = list(range(total_comm_nodes, total_comm_nodes + num_hubs))
    edges_per_hub = 40
    
    for hub in hub_nodes:
        G.add_node(hub, type="hub", true_community=-1) # -1 represents hub
        # Select 40 distinct random community nodes to connect to
        targets = random.sample(range(total_comm_nodes), edges_per_hub)
        for t in targets:
            G.add_edge(hub, t)
            
    return G, community_assignments, hub_nodes

def evaluate_hubs(G, true_hubs):
    """Compute centrality metrics and calculate precision/recall at top-k."""
    k = len(true_hubs)
    true_hub_set = set(true_hubs)
    
    # Degree centrality
    deg_cent = nx.degree_centrality(G)
    top_deg_nodes = sorted(deg_cent, key=deg_cent.get, reverse=True)[:k]
    deg_precision = len(set(top_deg_nodes) & true_hub_set) / k
    deg_recall = len(set(top_deg_nodes) & true_hub_set) / len(true_hub_set)
    
    # Betweenness centrality
    bet_cent = nx.betweenness_centrality(G, seed=SEED)
    top_bet_nodes = sorted(bet_cent, key=bet_cent.get, reverse=True)[:k]
    bet_precision = len(set(top_bet_nodes) & true_hub_set) / k
    bet_recall = len(set(top_bet_nodes) & true_hub_set) / len(true_hub_set)
    
    return {
        "deg_centrality": deg_cent,
        "bet_centrality": bet_cent,
        "deg_top_k": top_deg_nodes,
        "deg_precision": deg_precision,
        "deg_recall": deg_recall,
        "bet_top_k": top_bet_nodes,
        "bet_precision": bet_precision,
        "bet_recall": bet_recall,
    }

def evaluate_communities(G, true_communities, hub_nodes):
    """
    Remove hub nodes and run community detection on remaining subgraph.
    Compare with ground-truth community assignments.
    """
    # Create subgraph without hubs
    G_sub = G.copy()
    G_sub.remove_nodes_from(hub_nodes)
    
    # Run modularity-based community detection
    detected_comm_sets = list(nx.community.greedy_modularity_communities(G_sub))
    
    # Map detected communities to labels
    detected_labels = {}
    for comm_idx, comm_set in enumerate(detected_comm_sets):
        for node in comm_set:
            detected_labels[node] = comm_idx
            
    # Align labels for scikit-learn metrics
    nodes_sorted = sorted(true_communities.keys())
    y_true = [true_communities[n] for n in nodes_sorted]
    y_pred = [detected_labels[n] for n in nodes_sorted]
    
    ari = adjusted_rand_score(y_true, y_pred)
    nmi = normalized_mutual_info_score(y_true, y_pred)
    
    return {
        "detected_communities": detected_comm_sets,
        "detected_labels": detected_labels,
        "ari": ari,
        "nmi": nmi,
    }

def visualize_network(G, detected_labels, hub_nodes, fig_path):
    """Plot network and save visualization."""
    fig_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(12, 10))
    
    # Position nodes using spring layout
    pos = nx.spring_layout(G, seed=SEED, k=0.15, iterations=50)
    
    # Determine colors based on community detection + hubs
    node_colors = []
    node_sizes = []
    
    for node in G.nodes():
        # Size proportional to degree
        node_sizes.append(G.degree(node) * 10)
        
        if node in hub_nodes:
            node_colors.append("red") # Red for hubs
        else:
            # Color by detected community label
            comm_color = detected_labels.get(node, 0)
            node_colors.append(comm_color)
            
    # Draw network
    # Non-hubs
    non_hub_nodes = [n for n in G.nodes() if n not in hub_nodes]
    nx.draw_networkx_nodes(
        G, pos, 
        nodelist=non_hub_nodes, 
        node_color=[node_colors[n] for n in non_hub_nodes],
        node_size=[node_sizes[n] for n in non_hub_nodes],
        cmap=plt.cm.tab10, 
        alpha=0.8
    )
    
    # Hubs
    nx.draw_networkx_nodes(
        G, pos, 
        nodelist=hub_nodes, 
        node_color="red", 
        node_shape="D", # Diamond shape for hubs
        node_size=[node_sizes[n] * 1.5 for n in hub_nodes],
        edgecolors="black",
        linewidths=1.5
    )
    
    # Edges
    nx.draw_networkx_edges(G, pos, alpha=0.1, edge_color="gray")
    
    plt.title("Synthetic PPI Network: Planted Hubs (Red Diamonds) and Modules (Colored Circles)", fontsize=14)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=300)
    plt.savefig(fig_path.with_suffix(".pdf"), dpi=300)
    plt.close()

def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)

    with TeeLogger(log_path):
        print(f"{'='*60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Hypothesis: baseline hub & community recovery in synthetic network")
        print(f"{'='*60}")
        print()

        # 1. Generate Synthetic Network
        print("--- NETWORK GENERATION ---")
        G, true_communities, hub_nodes = generate_synthetic_network()
        print(f"Nodes: {G.number_of_nodes()}")
        print(f"Edges: {G.number_of_edges()}")
        print(f"Planted hubs: {hub_nodes}")
        print(f"Planted communities: 3 modules of 50 nodes each (total 150 community nodes)")
        print()
        
        # Calculate some network stats
        degrees = [G.degree(n) for n in G.nodes()]
        avg_degree = np.mean(degrees)
        max_degree = np.max(degrees)
        print(f"Average Degree: {avg_degree:.2f}")
        print(f"Max Degree: {max_degree}")
        for hn in hub_nodes:
            print(f"  - Hub {hn} degree: {G.degree(hn)}")
        non_hub_degrees = [G.degree(n) for n in G.nodes() if n not in hub_nodes]
        print(f"Average Non-Hub Degree: {np.mean(non_hub_degrees):.2f}")
        print()

        # 2. Evaluate Hub Recovery
        print("--- HUB RECOVERY EVALUATION ---")
        hub_results = evaluate_hubs(G, hub_nodes)
        
        print("Degree Centrality Top 3:")
        for idx, node in enumerate(hub_results["deg_top_k"]):
            print(f"  {idx+1}. Node {node} (Centrality: {hub_results['deg_centrality'][node]:.4f})")
        print(f"Degree Centrality Precision@3: {hub_results['deg_precision']:.2f}")
        print(f"Degree Centrality Recall@3: {hub_results['deg_recall']:.2f}")
        print()
        
        print("Betweenness Centrality Top 3:")
        for idx, node in enumerate(hub_results["bet_top_k"]):
            print(f"  {idx+1}. Node {node} (Centrality: {hub_results['bet_centrality'][node]:.4f})")
        print(f"Betweenness Centrality Precision@3: {hub_results['bet_precision']:.2f}")
        print(f"Betweenness Centrality Recall@3: {hub_results['bet_recall']:.2f}")
        print()

        # 3. Evaluate Community Detection (with hubs removed)
        print("--- COMMUNITY RECOVERY EVALUATION ---")
        comm_results = evaluate_communities(G, true_communities, hub_nodes)
        print(f"Number of communities detected: {len(comm_results['detected_communities'])}")
        print(f"Adjusted Rand Index (ARI): {comm_results['ari']:.4f}")
        print(f"Normalized Mutual Information (NMI): {comm_results['nmi']:.4f}")
        print()

        # 4. Visualization
        print("--- GENERATING VISUALIZATION ---")
        fig_path = FIG_DIR / f"{SCRIPT_NAME}_network.png"
        visualize_network(G, comm_results["detected_labels"], hub_nodes, fig_path)
        print(f"Saved visualization to {fig_path} (and .pdf)")
        print()

        # 5. Sanity Checks & Data Validation
        print("--- SANITY CHECKS ---")
        assert G.number_of_nodes() == 153, f"Unexpected node count: {G.number_of_nodes()}"
        assert len(hub_nodes) == 3, f"Unexpected hub count: {len(hub_nodes)}"
        for hn in hub_nodes:
            assert G.degree(hn) == 40, f"Hub {hn} degree is not 40: {G.degree(hn)}"
        print("All assertions passed!")
        print()

        print(f"{'='*60}")
        print("=== COMPLETE ===")
        print(f"{'='*60}")

if __name__ == "__main__":
    main()
