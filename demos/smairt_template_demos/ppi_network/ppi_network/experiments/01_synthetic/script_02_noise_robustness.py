#!/usr/bin/env python3
"""
Script 02: Robustness of Hub and Community Recovery under Edge Noise

Hypothesis: hypotheses/HYPOTHESIS_02.md
Phase: synthetic
Track: Track-free
Iteration: 2

Depends on:
  - experiments/01_synthetic/script_01_synthetic_validation.py
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
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

# === CONFIGURATION ===
SCRIPT_NAME = "script_02_noise_robustness"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIG_DIR = PROJECT_ROOT / "results" / "figures"
BASE_SEED = 2026

# Noise levels (fraction of rewired edges)
NOISE_LEVELS = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
NUM_TRIALS = 5

def set_seeds(seed):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)

def generate_synthetic_network(seed):
    """
    Generate synthetic network with known modules and hubs (same structure as script_01).
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
        
    # 2. Add edges within and between communities
    p_in = 0.3
    p_out = 0.02
    
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
        G.add_node(hub, type="hub", true_community=-1)
        targets = random.sample(range(total_comm_nodes), edges_per_hub)
        for t in targets:
            G.add_edge(hub, t)
            
    return G, community_assignments, hub_nodes

def apply_edge_noise(G, noise_fraction, seed):
    """
    Randomly rewire a fraction of the graph's edges.
    Returns a rewired copy of G.
    """
    set_seeds(seed)
    G_noisy = G.copy()
    num_edges = G_noisy.number_of_edges()
    num_to_rewire = int(round(noise_fraction * num_edges))
    
    if num_to_rewire == 0:
        return G_noisy
        
    edges = list(G_noisy.edges())
    # Pick edges to remove
    edges_to_remove = random.sample(edges, num_to_rewire)
    G_noisy.remove_edges_from(edges_to_remove)
    
    nodes = list(G_noisy.nodes())
    num_nodes = len(nodes)
    
    rewired_count = 0
    attempts = 0
    max_attempts = num_to_rewire * 10
    
    # Add new random edges to keep edge count conserved
    while rewired_count < num_to_rewire and attempts < max_attempts:
        attempts += 1
        u, v = random.sample(nodes, 2)
        if u != v and not G_noisy.has_edge(u, v):
            G_noisy.add_edge(u, v)
            rewired_count += 1
            
    return G_noisy

def evaluate_hubs(G, true_hubs, seed):
    """Compute centrality metrics and return Precision@3."""
    k = len(true_hubs)
    true_hub_set = set(true_hubs)
    
    # Degree centrality
    deg_cent = nx.degree_centrality(G)
    top_deg_nodes = sorted(deg_cent, key=deg_cent.get, reverse=True)[:k]
    deg_precision = len(set(top_deg_nodes) & true_hub_set) / k
    
    # Betweenness centrality
    bet_cent = nx.betweenness_centrality(G, seed=seed)
    top_bet_nodes = sorted(bet_cent, key=bet_cent.get, reverse=True)[:k]
    bet_precision = len(set(top_bet_nodes) & true_hub_set) / k
    
    return deg_precision, bet_precision

def evaluate_communities(G, true_communities, hub_nodes):
    """Remove hubs, run greedy modularity partition, and return ARI and NMI."""
    G_sub = G.copy()
    G_sub.remove_nodes_from(hub_nodes)
    
    try:
        detected_comm_sets = list(nx.community.greedy_modularity_communities(G_sub))
        detected_labels = {}
        for comm_idx, comm_set in enumerate(detected_comm_sets):
            for node in comm_set:
                detected_labels[node] = comm_idx
                
        nodes_sorted = sorted(true_communities.keys())
        y_true = [true_communities[n] for n in nodes_sorted]
        y_pred = [detected_labels.get(n, -1) for n in nodes_sorted]
        
        ari = adjusted_rand_score(y_true, y_pred)
        nmi = normalized_mutual_info_score(y_true, y_pred)
    except Exception as e:
        # In case community detection fails completely under extremely high noise
        print(f"Warning: Community detection failed with error {e}")
        ari, nmi = 0.0, 0.0
        
    return ari, nmi

def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)

    with TeeLogger(log_path):
        print(f"{'='*60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Hypothesis: Robustness of recovery under random edge rewiring noise")
        print(f"{'='*60}")
        print()

        print(f"Running robustness sweep across {len(NOISE_LEVELS)} noise levels, {NUM_TRIALS} trials each.")
        print(f"Noise Levels: {NOISE_LEVELS}")
        print()

        # Placeholders for results
        results = []

        for noise in NOISE_LEVELS:
            deg_precisions = []
            bet_precisions = []
            aris = []
            nmis = []
            
            for trial in range(NUM_TRIALS):
                # Use unique seed for each trial
                trial_seed = BASE_SEED + trial
                
                # 1. Generate baseline clean graph
                G, true_communities, hub_nodes = generate_synthetic_network(trial_seed)
                
                # 2. Apply random edge noise
                # Use a distinct noise seed
                noise_seed = trial_seed + 1000
                G_noisy = apply_edge_noise(G, noise, noise_seed)
                
                # 3. Evaluate hubs
                deg_p, bet_p = evaluate_hubs(G_noisy, hub_nodes, noise_seed)
                deg_precisions.append(deg_p)
                bet_precisions.append(bet_p)
                
                # 4. Evaluate communities
                ari, nmi = evaluate_communities(G_noisy, true_communities, hub_nodes)
                aris.append(ari)
                nmis.append(nmi)
                
            results.append({
                "noise": noise,
                "deg_p_mean": np.mean(deg_precisions),
                "deg_p_std": np.std(deg_precisions),
                "bet_p_mean": np.mean(bet_precisions),
                "bet_p_std": np.std(bet_precisions),
                "ari_mean": np.mean(aris),
                "ari_std": np.std(aris),
                "nmi_mean": np.mean(nmis),
                "nmi_std": np.std(nmis),
            })
            
            print(f"Noise: {noise:.2f} | "
                  f"Deg P: {np.mean(deg_precisions):.3f}±{np.std(deg_precisions):.2f} | "
                  f"Bet P: {np.mean(bet_precisions):.3f}±{np.std(bet_precisions):.2f} | "
                  f"ARI: {np.mean(aris):.3f}±{np.std(aris):.2f} | "
                  f"NMI: {np.mean(nmis):.3f}±{np.std(nmis):.2f}")

        df_results = pd.DataFrame(results)
        csv_path = LOG_DIR.parent / "results_noise_robustness.csv"
        df_results.to_csv(csv_path, index=False)
        print(f"\nSaved CSV results to: {csv_path}")

        # Plot and save results
        FIG_DIR.mkdir(parents=True, exist_ok=True)
        plt.figure(figsize=(10, 6))
        
        plt.errorbar(df_results["noise"], df_results["deg_p_mean"], yerr=df_results["deg_p_std"], 
                     fmt="-o", label="Degree Centrality P@3", capsize=4, color="blue", linewidth=2)
        plt.errorbar(df_results["noise"], df_results["bet_p_mean"], yerr=df_results["bet_p_std"], 
                     fmt="-s", label="Betweenness Centrality P@3", capsize=4, color="orange", linewidth=2)
        plt.errorbar(df_results["noise"], df_results["ari_mean"], yerr=df_results["ari_std"], 
                     fmt="-^", label="Community Partition ARI", capsize=4, color="green", linewidth=2)
        plt.errorbar(df_results["noise"], df_results["nmi_mean"], yerr=df_results["nmi_std"], 
                     fmt="-v", label="Community Partition NMI", capsize=4, color="purple", linewidth=1.5, linestyle="--")
        
        plt.axhline(0.80, color="red", linestyle=":", label="Breakdown Threshold (0.80)")
        plt.xlabel("Edge Rewiring Noise Fraction (r)", fontsize=12)
        plt.ylabel("Performance Metric", fontsize=12)
        plt.title("Robustness of Graph Methods under Controlled Edge Rewiring Noise", fontsize=14)
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.ylim(-0.05, 1.05)
        plt.legend(loc="lower left", fontsize=10)
        
        plot_path = FIG_DIR / f"{SCRIPT_NAME}_metrics.png"
        plt.savefig(plot_path, dpi=300)
        plt.savefig(plot_path.with_suffix(".pdf"), dpi=300)
        plt.close()
        print(f"Saved robustness plot to: {plot_path} (and .pdf)")
        print()

        # Sanity Checks
        assert df_results.loc[0, "deg_p_mean"] == 1.0, f"Expected 1.0 baseline degree precision, got {df_results.loc[0, 'deg_p_mean']}"
        assert df_results.loc[0, "ari_mean"] == 1.0, f"Expected 1.0 baseline community ARI, got {df_results.loc[0, 'ari_mean']}"
        print("All assertions passed!")
        print()

        print(f"{'='*60}")
        print("=== COMPLETE ===")
        print(f"{'='*60}")

if __name__ == "__main__":
    main()
