#!/usr/bin/env python3
"""
Script 01: Low-noise synthetic Michaelis-Menten nonlinear fit

Hypothesis: HYPOTHESIS_01.md
Phase: synthetic
Iteration: 01

Depends on:
  - background/01_initial_question.md
  - hypotheses/HYPOTHESIS_01.md

This script plants known Michaelis-Menten parameters, generates low-noise
synthetic velocity-vs-substrate data, fits Km and Vmax by direct nonlinear
least squares, and reports recovery error against the known truth.
"""

import sys
from pathlib import Path
from datetime import datetime

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

# === PATH SETUP ===
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

# === CONFIGURATION ===
SCRIPT_NAME = "script_01_synthetic_nonlinear_fit"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"

CONFIG = {
    "seed": 1024,
    "true_vmax": 100.0,
    "true_km": 5.0,
    "substrate_min": 0.5,
    "substrate_max": 50.0,
    "n_substrate_points": 12,
    "relative_noise": 0.03,
    "initial_guess": [90.0, 4.0],  # [Vmax, Km]
    "max_relative_error_for_credibility": 0.10,
}


# === MODEL ===
def michaelis_menten(substrate_concentration, vmax, km):
    """Compute Michaelis-Menten velocity for substrate concentration [S]."""
    return vmax * substrate_concentration / (km + substrate_concentration)


# === HELPERS ===
def relative_error(estimate, truth):
    """Return absolute relative error against known truth."""
    return abs(estimate - truth) / abs(truth)


def r_squared(observed, predicted):
    """Return coefficient of determination for observed vs. predicted values."""
    residual_sum_squares = np.sum((observed - predicted) ** 2)
    total_sum_squares = np.sum((observed - np.mean(observed)) ** 2)
    return 1.0 - residual_sum_squares / total_sum_squares


def generate_synthetic_data(config):
    """Generate low-noise synthetic Michaelis-Menten data with known truth."""
    rng = np.random.default_rng(config["seed"])
    substrate = np.geomspace(
        config["substrate_min"],
        config["substrate_max"],
        config["n_substrate_points"],
    )
    clean_velocity = michaelis_menten(
        substrate,
        config["true_vmax"],
        config["true_km"],
    )
    noise_sd = config["relative_noise"] * clean_velocity
    noisy_velocity = clean_velocity + rng.normal(loc=0.0, scale=noise_sd)

    return substrate, clean_velocity, noisy_velocity, noise_sd


def fit_nonlinear(substrate, velocity, config):
    """Fit Michaelis-Menten parameters by nonlinear least squares."""
    fitted_params, covariance = curve_fit(
        michaelis_menten,
        substrate,
        velocity,
        p0=config["initial_guess"],
        bounds=(0.0, np.inf),
        maxfev=10000,
    )
    fitted_vmax, fitted_km = fitted_params
    return fitted_vmax, fitted_km, covariance


def save_fit_plot(substrate, clean_velocity, noisy_velocity, fitted_vmax, fitted_km, config):
    """Save fitted Michaelis-Menten curve over generated synthetic observations."""
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    figure_path = FIGURE_DIR / f"{SCRIPT_NAME}_fit_curve.png"

    substrate_grid = np.linspace(
        config["substrate_min"],
        config["substrate_max"],
        300,
    )
    clean_curve = michaelis_menten(
        substrate_grid,
        config["true_vmax"],
        config["true_km"],
    )
    fitted_curve = michaelis_menten(substrate_grid, fitted_vmax, fitted_km)

    plt.figure(figsize=(8, 5.5))
    plt.scatter(
        substrate,
        noisy_velocity,
        color="tab:blue",
        label="Noisy synthetic observations",
        zorder=3,
    )
    plt.plot(
        substrate_grid,
        clean_curve,
        color="tab:green",
        linestyle="--",
        linewidth=2,
        label="Planted truth curve",
    )
    plt.plot(
        substrate_grid,
        fitted_curve,
        color="tab:red",
        linewidth=2,
        label="Nonlinear least-squares fit",
    )
    plt.xlabel("Substrate concentration [S]")
    plt.ylabel("Reaction velocity v")
    plt.title("Synthetic Michaelis-Menten parameter recovery")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(figure_path, dpi=300)
    plt.close()

    return figure_path


# === MAIN CODE ===
def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)

    with TeeLogger(log_path):
        print(f"{'='*60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("Hypothesis: Low-noise synthetic Michaelis-Menten data allow direct nonlinear least-squares recovery of planted Km and Vmax within 10% relative error.")
        print(f"{'='*60}")
        print()

        print("=== PLANTED PARAMETERS AND CREDIBILITY CRITERION ===")
        print(f"True Vmax: {CONFIG['true_vmax']:.6g}")
        print(f"True Km: {CONFIG['true_km']:.6g}")
        print(f"Substrate range: {CONFIG['substrate_min']:.6g} to {CONFIG['substrate_max']:.6g}")
        print(f"Substrate points: {CONFIG['n_substrate_points']}")
        print(f"Relative Gaussian noise: {100 * CONFIG['relative_noise']:.2f}% of clean velocity")
        print(f"Random seed: {CONFIG['seed']}")
        print(f"Credible recovery threshold: <= {100 * CONFIG['max_relative_error_for_credibility']:.1f}% relative error for both Km and Vmax")
        print()

        substrate, clean_velocity, noisy_velocity, noise_sd = generate_synthetic_data(CONFIG)

        # Validate synthetic data before fitting.
        assert substrate is not None, "Substrate data failed to generate"
        assert clean_velocity is not None, "Clean velocity data failed to generate"
        assert noisy_velocity is not None, "Noisy velocity data failed to generate"
        assert len(substrate) == CONFIG["n_substrate_points"], "Unexpected number of substrate points"
        assert len(substrate) == len(noisy_velocity), "Substrate and velocity lengths differ"
        assert np.all(substrate > 0), "Substrate concentrations must be positive"
        assert np.all(noisy_velocity > 0), "Generated velocities must be positive for this low-noise test"

        print("=== GENERATED DATA VALIDATION ===")
        print(f"Loaded/generated samples: {len(substrate)}")
        print(f"Substrate shape: {substrate.shape}")
        print(f"Velocity shape: {noisy_velocity.shape}")
        print(f"Minimum noisy velocity: {np.min(noisy_velocity):.6f}")
        print(f"Maximum noisy velocity: {np.max(noisy_velocity):.6f}")
        print()

        print("=== SYNTHETIC DATA TABLE ===")
        print("index\t[S]\tclean_v\tnoise_sd\tobserved_v")
        for index, (s_value, clean_v, sd_value, observed_v) in enumerate(
            zip(substrate, clean_velocity, noise_sd, noisy_velocity),
            start=1,
        ):
            print(f"{index:02d}\t{s_value:.6f}\t{clean_v:.6f}\t{sd_value:.6f}\t{observed_v:.6f}")
        print()

        fitted_vmax, fitted_km, covariance = fit_nonlinear(substrate, noisy_velocity, CONFIG)
        fitted_velocity = michaelis_menten(substrate, fitted_vmax, fitted_km)

        vmax_absolute_error = abs(fitted_vmax - CONFIG["true_vmax"])
        km_absolute_error = abs(fitted_km - CONFIG["true_km"])
        vmax_relative_error = relative_error(fitted_vmax, CONFIG["true_vmax"])
        km_relative_error = relative_error(fitted_km, CONFIG["true_km"])
        residual_sum_squares = np.sum((noisy_velocity - fitted_velocity) ** 2)
        fit_r_squared = r_squared(noisy_velocity, fitted_velocity)
        credible = (
            vmax_relative_error <= CONFIG["max_relative_error_for_credibility"]
            and km_relative_error <= CONFIG["max_relative_error_for_credibility"]
            and fitted_vmax > 0
            and fitted_km > 0
        )

        figure_path = save_fit_plot(
            substrate,
            clean_velocity,
            noisy_velocity,
            fitted_vmax,
            fitted_km,
            CONFIG,
        )

        print("=== NONLINEAR LEAST-SQUARES RESULTS ===")
        print(f"Fitted Vmax: {fitted_vmax:.6f}")
        print(f"Fitted Km: {fitted_km:.6f}")
        print(f"Vmax absolute error: {vmax_absolute_error:.6f}")
        print(f"Km absolute error: {km_absolute_error:.6f}")
        print(f"Vmax relative error: {100 * vmax_relative_error:.3f}%")
        print(f"Km relative error: {100 * km_relative_error:.3f}%")
        print(f"Residual sum of squares: {residual_sum_squares:.6f}")
        print(f"R^2 on noisy observations: {fit_r_squared:.6f}")
        print(f"Fit covariance matrix:\n{covariance}")
        print(f"Credible under <=10% criterion: {credible}")
        print()

        print("=== OUTPUT FILES ===")
        print(f"Log file: {log_path}")
        print(f"Figure file: {figure_path}")
        print()

        print("=== NEXT ITERATIONS ===")
        print("Script 02 should repeat the same nonlinear fit across increasing noise levels to find where recovery degrades.")
        print("Script 03 should add the Lineweaver-Burk double-reciprocal comparison and quantify its bias under noise.")

        print()
        print(f"{'='*60}")
        print("=== COMPLETE ===")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()


# ============================================================================
# OUTPUT COMMENT BLOCK
# ============================================================================
# Run: python enzyme_kinetics/experiments/01_synthetic/script_01_synthetic_nonlinear_fit.py
# Timestamp: 2026-07-13T13:52:05.747216
#
# Planted parameters:
# - True Vmax: 100
# - True Km: 5
# - Substrate range: 0.5 to 50
# - Substrate points: 12
# - Relative Gaussian noise: 3.00% of clean velocity
# - Random seed: 1024
# - Credible recovery threshold: <= 10.0% relative error for both Km and Vmax
#
# Generated data validation:
# - Loaded/generated samples: 12
# - Substrate shape: (12,)
# - Velocity shape: (12,)
# - Minimum noisy velocity: 8.967179
# - Maximum noisy velocity: 89.894077
#
# Nonlinear least-squares results:
# - Fitted Vmax: 97.373584
# - Fitted Km: 4.678811
# - Vmax absolute error: 2.626416
# - Km absolute error: 0.321189
# - Vmax relative error: 2.626%
# - Km relative error: 6.424%
# - Residual sum of squares: 14.675522
# - R^2 on noisy observations: 0.998404
# - Credible under <=10% criterion: True
#
# Output files:
# - Log file: enzyme_kinetics/results/logs/script_01_synthetic_nonlinear_fit_20260713_135205.log
# - Figure file: enzyme_kinetics/results/figures/script_01_synthetic_nonlinear_fit_fit_curve.png
#
# Interpretation:
# The low-noise synthetic positive control passed. The fitted saturation curve
# visually tracks the noisy data and remains close to the planted truth curve.
# Vmax and Km were both recovered within the predeclared 10% relative-error
# credibility threshold, supporting nonlinear least-squares fitting as a valid
# baseline before increasing noise or adding Lineweaver-Burk comparison scripts.
# ============================================================================
