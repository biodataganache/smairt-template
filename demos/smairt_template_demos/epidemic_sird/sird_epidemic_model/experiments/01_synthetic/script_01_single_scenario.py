#!/usr/bin/env python3
"""
Script 01: Single-scenario SIRD validation

Hypothesis: HYPOTHESIS_01.md
Phase: synthetic
Track: A (initial solver validation)
Iteration: 1

Depends on:
  - background/01_initial_question.md
  - hypotheses/HYPOTHESIS_01.md

Purpose:
  Implement the SIRD equations for one checkable synthetic scenario, integrate
  them with a numerical ODE solver, verify population conservation, and plot the
  S, I, R, and D curves.
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
SCRIPT_NAME = "script_01_single_scenario"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"

CONFIG = {
    "population": 1000.0,
    "initial_infected": 1.0,
    "initial_recovered": 0.0,
    "initial_deceased": 0.0,
    "beta": 0.3,      # infection/transmission rate per day
    "gamma": 0.1,     # recovery rate per day
    "mu": 0.01,       # disease death rate per day
    "t_start": 0.0,
    "t_end": 160.0,
    "n_eval_points": 161,
    "conservation_tolerance": 1e-6,
    "ratio_tolerance": 1e-4,
    "nonnegative_tolerance": -1e-9,
}


# === MODEL CODE ===
def sird_rhs(t, y, beta, gamma, mu, population):
    """Right-hand side of the SIRD ODE system."""
    susceptible, infected, recovered, deceased = y
    infection_flow = beta * susceptible * infected / population
    recovery_flow = gamma * infected
    death_flow = mu * infected

    d_susceptible_dt = -infection_flow
    d_infected_dt = infection_flow - recovery_flow - death_flow
    d_recovered_dt = recovery_flow
    d_deceased_dt = death_flow

    return [d_susceptible_dt, d_infected_dt, d_recovered_dt, d_deceased_dt]


def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    with TeeLogger(log_path):
        print(f"{'=' * 60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("Hypothesis: With R0 > 1, the infected curve should rise to a peak, decline, and conserve total population.")
        print(f"Log file: {log_path}")
        print(f"{'=' * 60}")
        print()

        # ========================================
        # PARAMETERS AND CREDIBILITY CRITERIA
        # ========================================
        population = CONFIG["population"]
        initial_infected = CONFIG["initial_infected"]
        initial_recovered = CONFIG["initial_recovered"]
        initial_deceased = CONFIG["initial_deceased"]
        initial_susceptible = population - initial_infected - initial_recovered - initial_deceased
        beta = CONFIG["beta"]
        gamma = CONFIG["gamma"]
        mu = CONFIG["mu"]
        r0_basic = beta / (gamma + mu)
        t_eval = np.linspace(CONFIG["t_start"], CONFIG["t_end"], CONFIG["n_eval_points"])
        y0 = [initial_susceptible, initial_infected, initial_recovered, initial_deceased]

        print("Parameters used:")
        print(f"  N = {population:.0f}")
        print(f"  S0 = {initial_susceptible:.0f}")
        print(f"  I0 = {initial_infected:.0f}")
        print(f"  R0 compartment = {initial_recovered:.0f}")
        print(f"  D0 = {initial_deceased:.0f}")
        print(f"  beta = {beta:.4f} /day")
        print(f"  gamma = {gamma:.4f} /day")
        print(f"  mu = {mu:.4f} /day")
        print(f"  basic reproduction number R0 = beta / (gamma + mu) = {r0_basic:.6f}")
        print(f"  integration interval = [{CONFIG['t_start']:.0f}, {CONFIG['t_end']:.0f}] days")
        print(f"  evaluation points = {CONFIG['n_eval_points']}")
        print()

        print("Credibility criteria for this first scenario:")
        print(f"  1. Conservation: max |S + I + R + D - N| < {CONFIG['conservation_tolerance']:.1e}")
        print("  2. Sensible epidemic shape: because R0 > 1, infected should rise above I0, peak, then decline.")
        print("  3. Final outcome: recovered and deceased should accumulate while infected approaches zero.")
        print("  4. Future scripts will sweep beta to vary R0 across the R0 = 1 threshold.")
        print()

        # Validate initial state.
        assert initial_susceptible >= 0, "Initial susceptible count must be non-negative"
        assert np.isclose(sum(y0), population), "Initial compartments do not sum to N"
        print("Initial condition validation passed.")
        print()

        # ========================================
        # NUMERICAL INTEGRATION
        # ========================================
        solution = solve_ivp(
            fun=lambda t, y: sird_rhs(t, y, beta, gamma, mu, population),
            t_span=(CONFIG["t_start"], CONFIG["t_end"]),
            y0=y0,
            t_eval=t_eval,
            method="RK45",
            rtol=1e-9,
            atol=1e-12,
        )

        assert solution.success, f"ODE solver failed: {solution.message}"
        susceptible, infected, recovered, deceased = solution.y
        time_days = solution.t

        print("ODE solver completed successfully.")
        print(f"  Solver message: {solution.message}")
        print(f"  Number of time points returned: {len(time_days)}")
        print()

        # ========================================
        # VALIDATION AND METRICS
        # ========================================
        total_population = susceptible + infected + recovered + deceased
        conservation_error = np.abs(total_population - population)
        max_conservation_error = float(np.max(conservation_error))
        min_susceptible = float(np.min(susceptible))
        min_infected = float(np.min(infected))
        min_recovered = float(np.min(recovered))
        min_deceased = float(np.min(deceased))
        min_compartment_value = min(min_susceptible, min_infected, min_recovered, min_deceased)
        compartments_nonnegative = min_compartment_value >= CONFIG["nonnegative_tolerance"]
        peak_index = int(np.argmax(infected))
        peak_infected = float(infected[peak_index])
        peak_day = float(time_days[peak_index])
        final_susceptible = float(susceptible[-1])
        final_infected = float(infected[-1])
        final_recovered = float(recovered[-1])
        final_deceased = float(deceased[-1])
        final_total = float(total_population[-1])
        final_recovered_fraction = final_recovered / population
        final_deceased_fraction = final_deceased / population
        expected_deceased_recovered_ratio = mu / gamma
        observed_deceased_recovered_ratio = final_deceased / final_recovered if final_recovered > 0 else np.nan
        ratio_error = abs(observed_deceased_recovered_ratio - expected_deceased_recovered_ratio)
        grows_above_seed = peak_infected > initial_infected
        peak_after_start = peak_day > CONFIG["t_start"]
        infected_declines_after_peak = final_infected < peak_infected

        print("Validation metrics:")
        print(f"  Max conservation error = {max_conservation_error:.12e}")
        print(f"  Conservation tolerance = {CONFIG['conservation_tolerance']:.12e}")
        print(f"  Conservation check passed = {max_conservation_error < CONFIG['conservation_tolerance']}")
        print(f"  Minimum S value = {min_susceptible:.12e}")
        print(f"  Minimum I value = {min_infected:.12e}")
        print(f"  Minimum R value = {min_recovered:.12e}")
        print(f"  Minimum D value = {min_deceased:.12e}")
        print(f"  Nonnegative tolerance = {CONFIG['nonnegative_tolerance']:.12e}")
        print(f"  Nonnegative compartment check passed = {compartments_nonnegative}")
        print()

        print("Epidemic-shape metrics:")
        print(f"  Initial infected = {initial_infected:.6f}")
        print(f"  Peak infected = {peak_infected:.6f}")
        print(f"  Day of peak infection = {peak_day:.2f}")
        print(f"  Final infected = {final_infected:.12f}")
        print(f"  Grows above seed = {grows_above_seed}")
        print(f"  Peak occurs after start = {peak_after_start}")
        print(f"  Final infected below peak = {infected_declines_after_peak}")
        print()

        print("Final compartment values:")
        print(f"  S(final) = {final_susceptible:.6f} ({final_susceptible / population:.4%})")
        print(f"  I(final) = {final_infected:.6f} ({final_infected / population:.4%})")
        print(f"  R(final) = {final_recovered:.6f} ({final_recovered_fraction:.4%})")
        print(f"  D(final) = {final_deceased:.6f} ({final_deceased_fraction:.4%})")
        print(f"  Total(final) = {final_total:.6f}")
        print(f"  Expected D/R ratio = mu/gamma = {expected_deceased_recovered_ratio:.6f}")
        print(f"  Observed D/R ratio = {observed_deceased_recovered_ratio:.6f}")
        print(f"  D/R ratio error = {ratio_error:.12e}")
        print()

        assert max_conservation_error < CONFIG["conservation_tolerance"], "Population conservation check failed"
        assert compartments_nonnegative, "At least one SIRD compartment became negative beyond numerical tolerance"
        assert grows_above_seed, "Infected did not rise above the one-person seed despite R0 > 1"
        assert peak_after_start, "Peak did not occur after the start time"
        assert infected_declines_after_peak, "Infected population did not decline after peak"
        assert ratio_error < CONFIG["ratio_tolerance"], "Final D/R ratio does not match mu/gamma"

        print("All core validation checks passed.")
        print()

        # ========================================
        # PLOT FOUR SIRD CURVES
        # ========================================
        figure_path = FIGURE_DIR / f"{SCRIPT_NAME}_sird_curves.png"
        plt.figure(figsize=(10, 6))
        plt.plot(time_days, susceptible, label="Susceptible", linewidth=2)
        plt.plot(time_days, infected, label="Infected", linewidth=2)
        plt.plot(time_days, recovered, label="Recovered", linewidth=2)
        plt.plot(time_days, deceased, label="Deceased", linewidth=2)
        plt.axvline(peak_day, linestyle="--", color="gray", alpha=0.7, label=f"Peak infected: day {peak_day:.0f}")
        plt.title(f"SIRD single scenario: beta={beta}, gamma={gamma}, mu={mu}, R0={r0_basic:.2f}")
        plt.xlabel("Time (days)")
        plt.ylabel("People")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(figure_path, dpi=300)
        plt.close()

        print("Figure generated:")
        print(f"  {figure_path}")
        print()

        print("Next experiment direction:")
        print("  Use this validated solver in script_02_beta_sweep.py to sweep beta values.")
        print("  The sweep should vary R0 = beta / (gamma + mu) across below-threshold and above-threshold regimes.")
        print("  Key outputs should include peak infected count, peak timing, final size, and whether I(t) grows or fades.")

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
#   2026-07-13T12:14:06 local rerun completed successfully after adding the
#   explicit all-time nonnegative compartment assertion.
#   Parameters: N=1000, I0=1, beta=0.3/day, gamma=0.1/day, mu=0.01/day.
#   R0 = beta / (gamma + mu) = 2.727273, so epidemic growth was expected.
#
# Key checks from results/logs/script_01_single_scenario_20260713_121406.log:
#   - Max conservation error: 7.958078640513e-13 (passed tolerance 1e-6)
#   - Minimum S/I/R/D: 81.62661453748 / 0.02026808144263 / 0.0 / 0.0
#   - Nonnegative compartment check: passed with tolerance -1e-9
#   - Peak infected and day: 265.618355 people on day 39.00
#   - Final S/I/R/D: 81.626615 / 0.020268 / 834.866470 / 83.486647
#   - D/R ratio: 0.100000, matching mu/gamma = 0.100000
#   - Figure path: results/figures/script_01_single_scenario_sird_curves.png
# ============================================================================
