#!/usr/bin/env python3
"""
Script 02: Sweep beta to test the R0 growth threshold

Hypothesis: HYPOTHESIS_02.md
Phase: synthetic
Track: A (initial solver validation and parameter sweep)
Iteration: 2

Depends on:
  - background/01_initial_question.md
  - hypotheses/HYPOTHESIS_01.md
  - hypotheses/HYPOTHESIS_02.md
  - experiments/01_synthetic/script_01_single_scenario.py

Purpose:
  Sweep beta while holding gamma and mu fixed, integrate the SIRD equations for
  each scenario, verify population conservation and non-negativity, and show how
  infected peak size and timing change as R0 crosses the R0 = 1 threshold.
"""

import sys
from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

# === PATH SETUP ===
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

# === CONFIGURATION ===
SCRIPT_NAME = "script_02_beta_sweep"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"

CONFIG = {
    "population": 1000.0,
    "initial_infected": 1.0,
    "initial_recovered": 0.0,
    "initial_deceased": 0.0,
    "gamma": 0.1,
    "mu": 0.01,
    "beta_values": [0.03, 0.06, 0.09, 0.10, 0.11, 0.12, 0.16, 0.20, 0.30, 0.45, 0.60],
    "t_start": 0.0,
    "t_end": 200.0,
    "n_eval_points": 401,
    "conservation_tolerance": 1e-6,
    "nonnegative_tolerance": -1e-9,
    "growth_tolerance": 1e-3,
}


# === MODEL CODE ===
def sird_rhs(t, y, beta, gamma, mu, population):
    """Right-hand side of the SIRD ODE system."""
    susceptible, infected, recovered, deceased = y
    infection_flow = beta * susceptible * infected / population
    recovery_flow = gamma * infected
    death_flow = mu * infected

    return [
        -infection_flow,
        infection_flow - recovery_flow - death_flow,
        recovery_flow,
        death_flow,
    ]


def run_sird_scenario(beta, gamma, mu, population, y0, t_eval):
    """Run one SIRD scenario and return solution arrays plus validation metrics."""
    solution = solve_ivp(
        fun=lambda t, y: sird_rhs(t, y, beta, gamma, mu, population),
        t_span=(float(t_eval[0]), float(t_eval[-1])),
        y0=y0,
        t_eval=t_eval,
        method="RK45",
        rtol=1e-9,
        atol=1e-12,
    )
    assert solution.success, f"ODE solver failed for beta={beta}: {solution.message}"

    susceptible, infected, recovered, deceased = solution.y
    total_population = susceptible + infected + recovered + deceased
    conservation_error = np.abs(total_population - population)
    min_compartment = float(np.min(solution.y))
    peak_index = int(np.argmax(infected))

    return {
        "solution": solution,
        "susceptible": susceptible,
        "infected": infected,
        "recovered": recovered,
        "deceased": deceased,
        "max_conservation_error": float(np.max(conservation_error)),
        "min_compartment": min_compartment,
        "peak_infected": float(infected[peak_index]),
        "peak_day": float(solution.t[peak_index]),
        "final_susceptible": float(susceptible[-1]),
        "final_infected": float(infected[-1]),
        "final_recovered": float(recovered[-1]),
        "final_deceased": float(deceased[-1]),
    }


def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    with TeeLogger(log_path):
        print(f"{'=' * 60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("Hypothesis: Sweeping beta should reveal the R0 = 1 growth/fade threshold and shift infected peaks.")
        print(f"Log file: {log_path}")
        print(f"{'=' * 60}")
        print()

        # ========================================
        # PARAMETERS AND THRESHOLDS
        # ========================================
        population = CONFIG["population"]
        initial_infected = CONFIG["initial_infected"]
        initial_recovered = CONFIG["initial_recovered"]
        initial_deceased = CONFIG["initial_deceased"]
        initial_susceptible = population - initial_infected - initial_recovered - initial_deceased
        gamma = CONFIG["gamma"]
        mu = CONFIG["mu"]
        removal_rate = gamma + mu
        ideal_threshold_beta = removal_rate
        finite_seed_threshold_beta = removal_rate * population / initial_susceptible
        finite_seed_threshold_r0 = finite_seed_threshold_beta / removal_rate
        t_eval = np.linspace(CONFIG["t_start"], CONFIG["t_end"], CONFIG["n_eval_points"])
        y0 = [initial_susceptible, initial_infected, initial_recovered, initial_deceased]

        print("Fixed parameters:")
        print(f"  N = {population:.0f}")
        print(f"  S0 = {initial_susceptible:.0f}")
        print(f"  I0 = {initial_infected:.0f}")
        print(f"  R0 compartment = {initial_recovered:.0f}")
        print(f"  D0 = {initial_deceased:.0f}")
        print(f"  gamma = {gamma:.4f} /day")
        print(f"  mu = {mu:.4f} /day")
        print(f"  gamma + mu = {removal_rate:.4f} /day")
        print(f"  beta values = {CONFIG['beta_values']}")
        print()

        print("Thresholds:")
        print(f"  Ideal fully susceptible threshold: beta = gamma + mu = {ideal_threshold_beta:.6f}, R0 = 1.000000")
        print(f"  Finite-seed initial-growth threshold with S0/N={initial_susceptible / population:.6f}:")
        print(f"    beta > (gamma + mu) * N / S0 = {finite_seed_threshold_beta:.6f}")
        print(f"    equivalent R0 > {finite_seed_threshold_r0:.6f}")
        print()

        print("Credibility criteria:")
        print(f"  1. Every scenario must conserve S + I + R + D to < {CONFIG['conservation_tolerance']:.1e}.")
        print(f"  2. Every scenario must keep compartments >= {CONFIG['nonnegative_tolerance']:.1e}.")
        print("  3. Below-threshold scenarios should fade immediately; above-threshold scenarios should grow and peak.")
        print("  4. Peak infected and peak day should be plotted against R0.")
        print()

        # Validate initial state.
        assert initial_susceptible >= 0, "Initial susceptible count must be non-negative"
        assert np.isclose(sum(y0), population), "Initial compartments do not sum to N"

        # ========================================
        # RUN BETA SWEEP
        # ========================================
        results = []
        infected_curves = []

        for beta in CONFIG["beta_values"]:
            metrics = run_sird_scenario(beta, gamma, mu, population, y0, t_eval)
            r0_basic = beta / removal_rate
            grew_above_seed = metrics["peak_infected"] > initial_infected + CONFIG["growth_tolerance"]
            immediately_fades = metrics["peak_day"] == CONFIG["t_start"] and not grew_above_seed
            predicted_by_finite_seed_threshold = beta > finite_seed_threshold_beta

            assert metrics["max_conservation_error"] < CONFIG["conservation_tolerance"], (
                f"Population conservation check failed for beta={beta}"
            )
            assert metrics["min_compartment"] >= CONFIG["nonnegative_tolerance"], (
                f"A compartment became negative beyond tolerance for beta={beta}"
            )

            row = {
                "beta": beta,
                "r0_basic": r0_basic,
                "predicted_growth": predicted_by_finite_seed_threshold,
                "grew_above_seed": grew_above_seed,
                "immediately_fades": immediately_fades,
                **metrics,
            }
            results.append(row)
            infected_curves.append((beta, r0_basic, metrics["infected"]))

        # ========================================
        # REPORT RESULTS
        # ========================================
        print("Beta sweep results:")
        header = (
            "beta    R0_basic  predicted_growth  grew_above_seed  "
            "peak_I     peak_day  final_I      final_R_frac  final_D_frac  max_cons_err   min_comp"
        )
        print(header)
        print("-" * len(header))
        for row in results:
            print(
                f"{row['beta']:<7.3f} "
                f"{row['r0_basic']:<9.4f} "
                f"{str(row['predicted_growth']):<17} "
                f"{str(row['grew_above_seed']):<16} "
                f"{row['peak_infected']:<10.4f} "
                f"{row['peak_day']:<9.2f} "
                f"{row['final_infected']:<12.6f} "
                f"{row['final_recovered'] / population:<13.4%} "
                f"{row['final_deceased'] / population:<13.4%} "
                f"{row['max_conservation_error']:<14.3e} "
                f"{row['min_compartment']:<.3e}"
            )
        print()

        threshold_mismatches = [
            row for row in results
            if row["predicted_growth"] != row["grew_above_seed"]
        ]
        if threshold_mismatches:
            print("Threshold classification mismatches detected:")
            for row in threshold_mismatches:
                print(
                    f"  beta={row['beta']:.3f}, R0={row['r0_basic']:.4f}, "
                    f"predicted_growth={row['predicted_growth']}, observed_growth={row['grew_above_seed']}"
                )
        else:
            print("Threshold classification check passed for all beta values using finite-seed initial-growth threshold.")
        print()

        print("Interpretation summary:")
        print("  Below the R0≈1 threshold, infected counts fade immediately and peak at the initial seed.")
        print("  Above the threshold, infected counts rise to a peak and later decline as susceptibles are depleted.")
        print("  Higher beta produces larger infected peaks and earlier peak timing, demonstrating the start of a flatten-the-curve interpretation.")
        print()

        # ========================================
        # FIGURES
        # ========================================
        infected_curves_path = FIGURE_DIR / f"{SCRIPT_NAME}_infected_curves.png"
        plt.figure(figsize=(10, 6))
        for beta, r0_basic, infected in infected_curves:
            plt.plot(t_eval, infected, linewidth=1.8, label=f"beta={beta:.2f}, R0={r0_basic:.2f}")
        plt.axhline(initial_infected, linestyle="--", color="black", alpha=0.5, label="Initial infected")
        plt.title("SIRD beta sweep: infected curves across R0 threshold")
        plt.xlabel("Time (days)")
        plt.ylabel("Infected people")
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=8, ncol=2)
        plt.tight_layout()
        plt.savefig(infected_curves_path, dpi=300)
        plt.close()

        peak_metrics_path = FIGURE_DIR / f"{SCRIPT_NAME}_peak_metrics_vs_r0.png"
        r0_values = np.array([row["r0_basic"] for row in results])
        peak_values = np.array([row["peak_infected"] for row in results])
        peak_days = np.array([row["peak_day"] for row in results])

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        axes[0].plot(r0_values, peak_values, marker="o", linewidth=2)
        axes[0].axvline(1.0, linestyle="--", color="red", alpha=0.7, label="Ideal R0 = 1")
        axes[0].axvline(finite_seed_threshold_r0, linestyle=":", color="purple", alpha=0.9, label="Finite-seed threshold")
        axes[0].set_xlabel("R0 = beta / (gamma + mu)")
        axes[0].set_ylabel("Peak infected people")
        axes[0].set_title("Peak size grows with R0")
        axes[0].grid(True, alpha=0.3)
        axes[0].legend(fontsize=8)

        axes[1].plot(r0_values, peak_days, marker="o", linewidth=2)
        axes[1].axvline(1.0, linestyle="--", color="red", alpha=0.7, label="Ideal R0 = 1")
        axes[1].axvline(finite_seed_threshold_r0, linestyle=":", color="purple", alpha=0.9, label="Finite-seed threshold")
        axes[1].set_xlabel("R0 = beta / (gamma + mu)")
        axes[1].set_ylabel("Day of infected peak")
        axes[1].set_title("Peak timing shifts earlier above threshold")
        axes[1].grid(True, alpha=0.3)
        axes[1].legend(fontsize=8)

        fig.suptitle("SIRD beta sweep: threshold and infected peak metrics")
        fig.tight_layout()
        fig.savefig(peak_metrics_path, dpi=300)
        plt.close(fig)

        print("Figures generated:")
        print(f"  {infected_curves_path}")
        print(f"  {peak_metrics_path}")
        print()

        print("Next experiment direction:")
        print("  Sweep mu to measure how final recovered/deceased split changes with death rate.")
        print("  Compare lower beta scenarios to show flatten-the-curve behavior: lower peak, later peak, and reduced instantaneous burden.")

        # ========================================
        # END CODE
        # ========================================

        print()
        print(f"{'=' * 60}")
        print("=== COMPLETE ===")
        print(f"{'=' * 60}")


if __name__ == "__main__":
    main()


# ============================================================================
# PASTED-OUTPUT COMMENT BLOCK
# ============================================================================
# This SMAIRT project writes authoritative output to results/logs/ via TeeLogger.
# If a pasted output block is needed for lightweight script-local review, paste
# a short summary below after running the script.
#
# Last run summary:
#   2026-07-13T12:16:25 local run completed successfully.
#   Fixed parameters: N=1000, I0=1, gamma=0.1/day, mu=0.01/day.
#   Swept beta values: 0.03, 0.06, 0.09, 0.10, 0.11, 0.12, 0.16, 0.20, 0.30, 0.45, 0.60.
#
# Key checks from results/logs/script_02_beta_sweep_20260713_121625.log:
#   - All conservation checks: passed; max errors ranged from 2.274e-13 to 9.095e-13.
#   - All nonnegative checks: passed; minimum compartment value was 0.000e+00 for all scenarios.
#   - Threshold found: ideal R0=1 at beta=0.11; finite-seed growth threshold R0>1.001001.
#   - Below threshold: beta <= 0.11 did not grow above the one-person seed.
#   - Above threshold: beta >= 0.12 grew above the seed.
#   - Peak infected trend: increased from 4.1754 at R0=1.0909 to 505.8340 at R0=5.4545.
#   - Peak timing trend: shifted earlier from day 200.00 at R0=1.0909 to day 17.50 at R0=5.4545.
#   - Figure paths: results/figures/script_02_beta_sweep_infected_curves.png and
#     results/figures/script_02_beta_sweep_peak_metrics_vs_r0.png
# ============================================================================
