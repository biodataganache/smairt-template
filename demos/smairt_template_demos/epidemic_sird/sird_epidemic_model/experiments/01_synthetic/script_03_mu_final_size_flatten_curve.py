#!/usr/bin/env python3
"""
Script 03: Mu sweep, final size, and flatten-the-curve interpretation

Hypothesis: HYPOTHESIS_03.md
Phase: synthetic
Track: A (initial solver validation and parameter sweeps)
Iteration: 3

Depends on:
  - background/01_initial_question.md
  - hypotheses/HYPOTHESIS_01.md
  - hypotheses/HYPOTHESIS_02.md
  - hypotheses/HYPOTHESIS_03.md
  - experiments/01_synthetic/script_01_single_scenario.py
  - experiments/01_synthetic/script_02_beta_sweep.py

Purpose:
  Sweep mu to report final recovered-vs-deceased size, verify that D/R matches
  mu/gamma, and compare beta values to interpret lowering beta as flattening the
  curve.
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
SCRIPT_NAME = "script_03_mu_final_size_flatten_curve"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"

CONFIG = {
    "population": 1000.0,
    "initial_infected": 1.0,
    "initial_recovered": 0.0,
    "initial_deceased": 0.0,
    "baseline_beta": 0.3,
    "baseline_gamma": 0.1,
    "baseline_mu": 0.01,
    "mu_values": [0.0, 0.005, 0.01, 0.02, 0.04, 0.06, 0.08],
    "flatten_beta_values": [0.12, 0.16, 0.20, 0.30],
    "t_start": 0.0,
    "t_end": 500.0,
    "n_eval_points": 1001,
    "conservation_tolerance": 1e-6,
    "nonnegative_tolerance": -1e-9,
    "ratio_tolerance": 1e-4,
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


def run_sird(beta, gamma, mu, population, y0, t_eval):
    """Run one SIRD scenario and return solution arrays plus summary metrics."""
    solution = solve_ivp(
        fun=lambda t, y: sird_rhs(t, y, beta, gamma, mu, population),
        t_span=(float(t_eval[0]), float(t_eval[-1])),
        y0=y0,
        t_eval=t_eval,
        method="RK45",
        rtol=1e-9,
        atol=1e-12,
    )
    assert solution.success, f"ODE solver failed for beta={beta}, gamma={gamma}, mu={mu}: {solution.message}"

    susceptible, infected, recovered, deceased = solution.y
    total_population = susceptible + infected + recovered + deceased
    conservation_error = np.abs(total_population - population)
    peak_index = int(np.argmax(infected))
    expected_d_over_r = mu / gamma if gamma > 0 else np.nan
    observed_d_over_r = deceased[-1] / recovered[-1] if recovered[-1] > 0 else np.nan
    ratio_error = abs(observed_d_over_r - expected_d_over_r) if np.isfinite(observed_d_over_r) else np.nan

    return {
        "solution": solution,
        "susceptible": susceptible,
        "infected": infected,
        "recovered": recovered,
        "deceased": deceased,
        "r0_basic": beta / (gamma + mu),
        "max_conservation_error": float(np.max(conservation_error)),
        "min_compartment": float(np.min(solution.y)),
        "peak_infected": float(infected[peak_index]),
        "peak_day": float(solution.t[peak_index]),
        "final_susceptible": float(susceptible[-1]),
        "final_infected": float(infected[-1]),
        "final_recovered": float(recovered[-1]),
        "final_deceased": float(deceased[-1]),
        "expected_d_over_r": float(expected_d_over_r),
        "observed_d_over_r": float(observed_d_over_r),
        "ratio_error": float(ratio_error),
    }


def validate_metrics(metrics, label):
    """Assert conservation, non-negativity, and D/R ratio checks for one run."""
    assert metrics["max_conservation_error"] < CONFIG["conservation_tolerance"], (
        f"Population conservation check failed for {label}"
    )
    assert metrics["min_compartment"] >= CONFIG["nonnegative_tolerance"], (
        f"A compartment became negative beyond tolerance for {label}"
    )
    if np.isfinite(metrics["ratio_error"]):
        assert metrics["ratio_error"] < CONFIG["ratio_tolerance"], (
            f"D/R ratio check failed for {label}"
        )


def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    with TeeLogger(log_path):
        print(f"{'=' * 60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("Hypothesis: Mu controls final recovered/deceased split, while lowering beta flattens the infected curve.")
        print(f"Log file: {log_path}")
        print(f"{'=' * 60}")
        print()

        # ========================================
        # PARAMETERS
        # ========================================
        population = CONFIG["population"]
        initial_infected = CONFIG["initial_infected"]
        initial_recovered = CONFIG["initial_recovered"]
        initial_deceased = CONFIG["initial_deceased"]
        initial_susceptible = population - initial_infected - initial_recovered - initial_deceased
        baseline_beta = CONFIG["baseline_beta"]
        gamma = CONFIG["baseline_gamma"]
        baseline_mu = CONFIG["baseline_mu"]
        t_eval = np.linspace(CONFIG["t_start"], CONFIG["t_end"], CONFIG["n_eval_points"])
        y0 = [initial_susceptible, initial_infected, initial_recovered, initial_deceased]

        print("Shared setup:")
        print(f"  N = {population:.0f}")
        print(f"  S0 = {initial_susceptible:.0f}")
        print(f"  I0 = {initial_infected:.0f}")
        print(f"  R0 compartment = {initial_recovered:.0f}")
        print(f"  D0 = {initial_deceased:.0f}")
        print(f"  integration interval = [{CONFIG['t_start']:.0f}, {CONFIG['t_end']:.0f}] days")
        print(f"  conservation tolerance = {CONFIG['conservation_tolerance']:.1e}")
        print(f"  nonnegative tolerance = {CONFIG['nonnegative_tolerance']:.1e}")
        print()

        print("Experiment A: mu sweep for final recovered/deceased size")
        print(f"  fixed beta = {baseline_beta:.4f} /day")
        print(f"  fixed gamma = {gamma:.4f} /day")
        print(f"  mu values = {CONFIG['mu_values']}")
        print()

        # ========================================
        # MU SWEEP
        # ========================================
        mu_results = []
        for mu in CONFIG["mu_values"]:
            metrics = run_sird(baseline_beta, gamma, mu, population, y0, t_eval)
            validate_metrics(metrics, label=f"mu={mu}")
            mu_results.append({"mu": mu, **metrics})

        print("Mu sweep results:")
        header = (
            "mu      R0_basic  peak_I     peak_day  final_S_frac  final_I_frac  "
            "final_R_frac  final_D_frac  expected_D/R  observed_D/R  ratio_error   max_cons_err  min_comp"
        )
        print(header)
        print("-" * len(header))
        for row in mu_results:
            print(
                f"{row['mu']:<7.3f} "
                f"{row['r0_basic']:<9.4f} "
                f"{row['peak_infected']:<10.4f} "
                f"{row['peak_day']:<9.2f} "
                f"{row['final_susceptible'] / population:<13.4%} "
                f"{row['final_infected'] / population:<13.6%} "
                f"{row['final_recovered'] / population:<13.4%} "
                f"{row['final_deceased'] / population:<13.4%} "
                f"{row['expected_d_over_r']:<12.6f} "
                f"{row['observed_d_over_r']:<12.6f} "
                f"{row['ratio_error']:<13.3e} "
                f"{row['max_conservation_error']:<13.3e} "
                f"{row['min_compartment']:<.3e}"
            )
        print()

        final_deceased_fractions = np.array([row["final_deceased"] / population for row in mu_results])
        final_deceased_non_decreasing = bool(np.all(np.diff(final_deceased_fractions) >= -1e-9))
        print(f"Final deceased fraction non-decreasing across tested mu values = {final_deceased_non_decreasing}")
        assert final_deceased_non_decreasing, "Final deceased fraction did not increase monotonically across tested mu values"
        print()

        print("Experiment B: flatten-the-curve beta comparison")
        print(f"  fixed gamma = {gamma:.4f} /day")
        print(f"  fixed mu = {baseline_mu:.4f} /day")
        print(f"  beta values = {CONFIG['flatten_beta_values']}")
        print()

        # ========================================
        # FLATTEN-THE-CURVE BETA COMPARISON
        # ========================================
        flatten_results = []
        flatten_curves = []
        for beta in CONFIG["flatten_beta_values"]:
            metrics = run_sird(beta, gamma, baseline_mu, population, y0, t_eval)
            validate_metrics(metrics, label=f"flatten_beta={beta}")
            flatten_results.append({"beta": beta, **metrics})
            flatten_curves.append((beta, metrics["r0_basic"], metrics["infected"]))

        print("Flatten-the-curve comparison:")
        header = "beta    R0_basic  peak_I     peak_day  final_R_frac  final_D_frac  max_cons_err  min_comp"
        print(header)
        print("-" * len(header))
        for row in flatten_results:
            print(
                f"{row['beta']:<7.3f} "
                f"{row['r0_basic']:<9.4f} "
                f"{row['peak_infected']:<10.4f} "
                f"{row['peak_day']:<9.2f} "
                f"{row['final_recovered'] / population:<13.4%} "
                f"{row['final_deceased'] / population:<13.4%} "
                f"{row['max_conservation_error']:<13.3e} "
                f"{row['min_compartment']:<.3e}"
            )
        print()

        peak_by_beta = np.array([row["peak_infected"] for row in flatten_results])
        peak_day_by_beta = np.array([row["peak_day"] for row in flatten_results])
        peak_increases_with_beta = bool(np.all(np.diff(peak_by_beta) > 0))
        peak_day_decreases_with_beta = bool(np.all(np.diff(peak_day_by_beta) < 0))
        print(f"Peak infected increases with beta = {peak_increases_with_beta}")
        print(f"Peak day shifts earlier as beta increases = {peak_day_decreases_with_beta}")
        assert peak_increases_with_beta, "Peak infected did not increase monotonically with beta"
        assert peak_day_decreases_with_beta, "Peak day did not shift earlier as beta increased"
        print()

        print("Interpretation summary:")
        print("  Increasing mu shifts a larger fraction of removed individuals into the deceased compartment.")
        print("  The observed final D/R ratio matches mu/gamma for every mu value tested.")
        print("  Lowering beta flattens the curve by reducing the infected peak and delaying peak timing.")
        print("  Scientific judgment call: prioritize lowering beta first because it directly reduces simultaneous infections and hospital burden; shortening infectious period also lowers R0 but requires rapid detection/isolation/treatment capacity.")
        print()

        # ========================================
        # FIGURES
        # ========================================
        mu_final_size_path = FIGURE_DIR / f"{SCRIPT_NAME}_mu_final_size.png"
        mu_values = np.array([row["mu"] for row in mu_results])
        recovered_fracs = np.array([row["final_recovered"] / population for row in mu_results])
        deceased_fracs = np.array([row["final_deceased"] / population for row in mu_results])
        r0_values = np.array([row["r0_basic"] for row in mu_results])

        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax1.plot(mu_values, recovered_fracs, marker="o", linewidth=2, label="Final recovered fraction")
        ax1.plot(mu_values, deceased_fracs, marker="o", linewidth=2, label="Final deceased fraction")
        ax1.set_xlabel("mu (death rate per day)")
        ax1.set_ylabel("Fraction of population")
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc="upper left")
        ax2 = ax1.twinx()
        ax2.plot(mu_values, r0_values, marker="s", linestyle="--", color="purple", label="R0")
        ax2.set_ylabel("R0 = beta / (gamma + mu)")
        ax2.legend(loc="upper right")
        fig.suptitle("Mu sweep: final recovered/deceased split and changing R0")
        fig.tight_layout()
        fig.savefig(mu_final_size_path, dpi=300)
        plt.close(fig)

        flatten_curves_path = FIGURE_DIR / f"{SCRIPT_NAME}_flatten_curve_beta_comparison.png"
        plt.figure(figsize=(10, 6))
        for beta, r0_basic, infected in flatten_curves:
            plt.plot(t_eval, infected, linewidth=2, label=f"beta={beta:.2f}, R0={r0_basic:.2f}")
        plt.title("Flatten the curve: lower beta reduces and delays infected peak")
        plt.xlabel("Time (days)")
        plt.ylabel("Infected people")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(flatten_curves_path, dpi=300)
        plt.close()

        print("Figures generated:")
        print(f"  {mu_final_size_path}")
        print(f"  {flatten_curves_path}")
        print()

        print("Next experiment direction:")
        print("  Move from synthetic validation to downloaded/real data: fit beta, gamma, and mu to a small published outbreak time series.")
        print("  Report estimated R0 with uncertainty and clearly state SIRD limitations: closed population, homogeneous mixing, fixed rates, no latent period, no interventions, and observation/reporting noise.")

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
#   2026-07-13T12:19:57 local run completed successfully.
#   Fixed setup: N=1000, I0=1, gamma=0.1/day; mu sweep at beta=0.3/day;
#   flatten-the-curve beta comparison at mu=0.01/day.
#
# Key checks from results/logs/script_03_mu_final_size_flatten_curve_20260713_121957.log:
#   - All conservation checks: passed; max errors ranged from 3.411e-13 to 1.364e-12.
#   - All nonnegative checks: passed within tolerance -1e-9; tiny negative values were numerical roundoff.
#   - Mu sweep final deceased fraction: increased from 0.0000% at mu=0.000 to 30.0649% at mu=0.080.
#   - D/R ratio agreement: observed D/R matched mu/gamma for every mu value tested.
#   - Flatten-the-curve beta comparison: lowering beta reduced and delayed the infected peak.
#     beta=0.12: peak_I=4.4900 on day 249.50; beta=0.30: peak_I=265.8146 on day 39.50.
#   - Judgment call: prioritize lowering beta first because it directly reduces simultaneous infections and hospital burden.
#   - Figure paths: results/figures/script_03_mu_final_size_flatten_curve_mu_final_size.png and
#     results/figures/script_03_mu_final_size_flatten_curve_flatten_curve_beta_comparison.png
# ============================================================================
