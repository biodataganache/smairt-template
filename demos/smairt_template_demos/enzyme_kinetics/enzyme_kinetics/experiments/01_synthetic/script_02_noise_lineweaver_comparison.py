#!/usr/bin/env python3
"""
Script 02: Noise sweep comparing nonlinear and Lineweaver-Burk fits

Hypothesis: HYPOTHESIS_02.md
Phase: synthetic
Iteration: 02

Depends on:
  - background/01_initial_question.md
  - hypotheses/HYPOTHESIS_01.md
  - hypotheses/HYPOTHESIS_02.md
  - experiments/01_synthetic/script_01_synthetic_nonlinear_fit.py

This script plants known Michaelis-Menten parameters, generates synthetic
velocity-vs-substrate datasets across increasing measurement-noise levels,
fits Km and Vmax with both direct nonlinear least squares and the
Lineweaver-Burk double-reciprocal linearization, and reports recovery error
against planted truth.
"""

import csv
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
SCRIPT_NAME = "script_02_noise_lineweaver_comparison"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"
RESULTS_DIR = PROJECT_ROOT / "results"

CONFIG = {
    "base_seed": 2048,
    "true_vmax": 100.0,
    "true_km": 5.0,
    "substrate_min": 0.5,
    "substrate_max": 50.0,
    "n_substrate_points": 12,
    "noise_levels": [0.0, 0.03, 0.10, 0.20, 0.40],
    "replicates_per_noise": 50,
    "initial_guess": [90.0, 4.0],  # [Vmax, Km]
    "max_relative_error_for_credibility": 0.10,
    "representative_noise_level": 0.20,
    "representative_replicate": 0,
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
    if total_sum_squares == 0:
        return np.nan
    return 1.0 - residual_sum_squares / total_sum_squares


def generate_substrate(config):
    """Generate substrate concentrations spanning below and above planted Km."""
    return np.geomspace(
        config["substrate_min"],
        config["substrate_max"],
        config["n_substrate_points"],
    )


def generate_noisy_velocity(substrate, noise_level, seed, config):
    """Generate one synthetic dataset at the requested relative noise level."""
    rng = np.random.default_rng(seed)
    clean_velocity = michaelis_menten(
        substrate,
        config["true_vmax"],
        config["true_km"],
    )
    noise_sd = noise_level * clean_velocity
    noisy_velocity = clean_velocity + rng.normal(loc=0.0, scale=noise_sd)
    return clean_velocity, noisy_velocity, noise_sd


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
    fitted_velocity = michaelis_menten(substrate, fitted_vmax, fitted_km)
    return {
        "success": True,
        "vmax": fitted_vmax,
        "km": fitted_km,
        "r2": r_squared(velocity, fitted_velocity),
        "covariance": covariance,
        "failure_reason": "",
    }


def fit_lineweaver_burk(substrate, velocity):
    """Fit Michaelis-Menten parameters using Lineweaver-Burk linearization."""
    if np.any(substrate <= 0):
        return {
            "success": False,
            "vmax": np.nan,
            "km": np.nan,
            "r2": np.nan,
            "slope": np.nan,
            "intercept": np.nan,
            "failure_reason": "nonpositive_substrate",
        }

    if np.any(velocity <= 0):
        return {
            "success": False,
            "vmax": np.nan,
            "km": np.nan,
            "r2": np.nan,
            "slope": np.nan,
            "intercept": np.nan,
            "failure_reason": "nonpositive_velocity_invalid_for_reciprocal",
        }

    reciprocal_substrate = 1.0 / substrate
    reciprocal_velocity = 1.0 / velocity
    slope, intercept = np.polyfit(reciprocal_substrate, reciprocal_velocity, deg=1)

    if intercept <= 0 or slope <= 0:
        return {
            "success": False,
            "vmax": np.nan,
            "km": np.nan,
            "r2": np.nan,
            "slope": slope,
            "intercept": intercept,
            "failure_reason": "nonphysical_lineweaver_parameters",
        }

    fitted_vmax = 1.0 / intercept
    fitted_km = slope / intercept
    fitted_velocity = michaelis_menten(substrate, fitted_vmax, fitted_km)

    return {
        "success": True,
        "vmax": fitted_vmax,
        "km": fitted_km,
        "r2": r_squared(velocity, fitted_velocity),
        "slope": slope,
        "intercept": intercept,
        "failure_reason": "",
    }


def summarize_rows(rows, config):
    """Summarize recovery errors by method and noise level."""
    summary_rows = []
    for noise_level in config["noise_levels"]:
        for method in ["nonlinear", "lineweaver_burk"]:
            method_rows = [
                row for row in rows
                if row["noise_level"] == noise_level and row["method"] == method
            ]
            valid_rows = [row for row in method_rows if row["success"]]
            invalid_count = len(method_rows) - len(valid_rows)
            invalid_fraction = invalid_count / len(method_rows)

            if valid_rows:
                vmax_errors = np.array([row["vmax_relative_error"] for row in valid_rows])
                km_errors = np.array([row["km_relative_error"] for row in valid_rows])
                r2_values = np.array([row["r2"] for row in valid_rows])
                median_vmax_error = float(np.median(vmax_errors))
                median_km_error = float(np.median(km_errors))
                credible = (
                    median_vmax_error <= config["max_relative_error_for_credibility"]
                    and median_km_error <= config["max_relative_error_for_credibility"]
                )
                summary_rows.append({
                    "noise_level": noise_level,
                    "method": method,
                    "n_total": len(method_rows),
                    "n_valid": len(valid_rows),
                    "n_invalid": invalid_count,
                    "invalid_fraction": invalid_fraction,
                    "median_vmax_relative_error": median_vmax_error,
                    "median_km_relative_error": median_km_error,
                    "mean_vmax_relative_error": float(np.mean(vmax_errors)),
                    "mean_km_relative_error": float(np.mean(km_errors)),
                    "max_vmax_relative_error": float(np.max(vmax_errors)),
                    "max_km_relative_error": float(np.max(km_errors)),
                    "median_r2": float(np.nanmedian(r2_values)),
                    "credible": credible,
                })
            else:
                summary_rows.append({
                    "noise_level": noise_level,
                    "method": method,
                    "n_total": len(method_rows),
                    "n_valid": 0,
                    "n_invalid": invalid_count,
                    "invalid_fraction": invalid_fraction,
                    "median_vmax_relative_error": np.nan,
                    "median_km_relative_error": np.nan,
                    "mean_vmax_relative_error": np.nan,
                    "mean_km_relative_error": np.nan,
                    "max_vmax_relative_error": np.nan,
                    "max_km_relative_error": np.nan,
                    "median_r2": np.nan,
                    "credible": False,
                })

    return summary_rows


def find_breakdown_noise(summary_rows, config):
    """Find first noise level where Lineweaver-Burk fails while nonlinear remains credible."""
    threshold = config["max_relative_error_for_credibility"]
    for noise_level in config["noise_levels"]:
        nonlinear_summary = next(
            row for row in summary_rows
            if row["noise_level"] == noise_level and row["method"] == "nonlinear"
        )
        lineweaver_summary = next(
            row for row in summary_rows
            if row["noise_level"] == noise_level and row["method"] == "lineweaver_burk"
        )
        lineweaver_error_failure = not lineweaver_summary["credible"]
        lineweaver_invalid_failure = lineweaver_summary["invalid_fraction"] >= 0.10
        nonlinear_still_credible = nonlinear_summary["credible"]
        if nonlinear_still_credible and (lineweaver_error_failure or lineweaver_invalid_failure):
            reasons = []
            if lineweaver_error_failure:
                if lineweaver_summary["median_vmax_relative_error"] > threshold:
                    reasons.append("median Vmax error exceeded threshold")
                if lineweaver_summary["median_km_relative_error"] > threshold:
                    reasons.append("median Km error exceeded threshold")
            if lineweaver_invalid_failure:
                reasons.append("invalid replicate fraction >= 10%")
            return noise_level, "; ".join(reasons)
    return None, "No tested noise level met the breakdown definition"


def write_csv(path, rows, fieldnames):
    """Write row dictionaries to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_error_plot(summary_rows):
    """Save median relative recovery-error plot across noise levels."""
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    figure_path = FIGURE_DIR / f"{SCRIPT_NAME}_median_errors.png"

    plt.figure(figsize=(9, 6))
    styles = {
        ("nonlinear", "vmax"): ("tab:blue", "o", "Nonlinear Vmax"),
        ("nonlinear", "km"): ("tab:orange", "o", "Nonlinear Km"),
        ("lineweaver_burk", "vmax"): ("tab:green", "s", "Lineweaver-Burk Vmax"),
        ("lineweaver_burk", "km"): ("tab:red", "s", "Lineweaver-Burk Km"),
    }

    for (method, parameter), (color, marker, label) in styles.items():
        method_rows = [row for row in summary_rows if row["method"] == method]
        noise_percent = [100 * row["noise_level"] for row in method_rows]
        if parameter == "vmax":
            errors_percent = [100 * row["median_vmax_relative_error"] for row in method_rows]
        else:
            errors_percent = [100 * row["median_km_relative_error"] for row in method_rows]
        plt.plot(
            noise_percent,
            errors_percent,
            color=color,
            marker=marker,
            linewidth=2,
            label=label,
        )

    plt.axhline(
        100 * CONFIG["max_relative_error_for_credibility"],
        color="black",
        linestyle="--",
        linewidth=1.5,
        label="10% credibility threshold",
    )
    plt.xlabel("Relative noise level (% of clean velocity)")
    plt.ylabel("Median parameter relative error (%)")
    plt.title("Parameter recovery error vs. measurement noise")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(figure_path, dpi=300)
    plt.close()

    return figure_path


def save_representative_fit_plot(representative, config):
    """Save original-scale curves for one representative noisy dataset."""
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    figure_path = FIGURE_DIR / f"{SCRIPT_NAME}_representative_fit.png"

    substrate = representative["substrate"]
    noisy_velocity = representative["noisy_velocity"]
    substrate_grid = np.linspace(
        config["substrate_min"],
        config["substrate_max"],
        300,
    )
    clean_curve = michaelis_menten(substrate_grid, config["true_vmax"], config["true_km"])

    plt.figure(figsize=(8, 5.5))
    plt.scatter(
        substrate,
        noisy_velocity,
        color="tab:blue",
        label="Noisy observations",
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

    nonlinear_fit = representative["nonlinear_fit"]
    if nonlinear_fit["success"]:
        plt.plot(
            substrate_grid,
            michaelis_menten(substrate_grid, nonlinear_fit["vmax"], nonlinear_fit["km"]),
            color="tab:red",
            linewidth=2,
            label="Nonlinear fit",
        )

    lineweaver_fit = representative["lineweaver_fit"]
    if lineweaver_fit["success"]:
        plt.plot(
            substrate_grid,
            michaelis_menten(substrate_grid, lineweaver_fit["vmax"], lineweaver_fit["km"]),
            color="tab:purple",
            linestyle=":",
            linewidth=2.5,
            label="Lineweaver-Burk fit",
        )

    plt.xlabel("Substrate concentration [S]")
    plt.ylabel("Reaction velocity v")
    plt.title(
        "Representative fit at "
        f"{100 * representative['noise_level']:.0f}% noise, replicate "
        f"{representative['replicate']}"
    )
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
        print("Hypothesis: Increasing measurement noise reveals larger Lineweaver-Burk recovery bias than direct nonlinear Michaelis-Menten fitting.")
        print(f"{'='*60}")
        print()

        print("=== PLANTED PARAMETERS AND EXPERIMENT DESIGN ===")
        print(f"True Vmax: {CONFIG['true_vmax']:.6g}")
        print(f"True Km: {CONFIG['true_km']:.6g}")
        print(f"Substrate range: {CONFIG['substrate_min']:.6g} to {CONFIG['substrate_max']:.6g}")
        print(f"Substrate points: {CONFIG['n_substrate_points']}")
        print(f"Noise levels: {[f'{100 * level:.0f}%' for level in CONFIG['noise_levels']]}")
        print(f"Replicates per noise level: {CONFIG['replicates_per_noise']}")
        print(f"Base random seed: {CONFIG['base_seed']}")
        print(f"Nonlinear initial guess [Vmax, Km]: {CONFIG['initial_guess']}")
        print(f"Credible recovery threshold: <= {100 * CONFIG['max_relative_error_for_credibility']:.1f}% median relative error for both Km and Vmax")
        print()

        substrate = generate_substrate(CONFIG)
        assert substrate is not None, "Substrate generation failed"
        assert len(substrate) == CONFIG["n_substrate_points"], "Unexpected number of substrate points"
        assert np.all(substrate > 0), "Substrate concentrations must be positive"

        rows = []
        representative = None

        for noise_index, noise_level in enumerate(CONFIG["noise_levels"]):
            for replicate in range(CONFIG["replicates_per_noise"]):
                seed = CONFIG["base_seed"] + noise_index * 10000 + replicate
                clean_velocity, noisy_velocity, noise_sd = generate_noisy_velocity(
                    substrate,
                    noise_level,
                    seed,
                    CONFIG,
                )

                nonlinear_fit = fit_nonlinear(substrate, noisy_velocity, CONFIG)
                lineweaver_fit = fit_lineweaver_burk(substrate, noisy_velocity)

                for method, fit_result in [
                    ("nonlinear", nonlinear_fit),
                    ("lineweaver_burk", lineweaver_fit),
                ]:
                    if fit_result["success"]:
                        vmax_absolute_error = abs(fit_result["vmax"] - CONFIG["true_vmax"])
                        km_absolute_error = abs(fit_result["km"] - CONFIG["true_km"])
                        vmax_relative_error = relative_error(fit_result["vmax"], CONFIG["true_vmax"])
                        km_relative_error = relative_error(fit_result["km"], CONFIG["true_km"])
                    else:
                        vmax_absolute_error = np.nan
                        km_absolute_error = np.nan
                        vmax_relative_error = np.nan
                        km_relative_error = np.nan

                    rows.append({
                        "noise_level": noise_level,
                        "noise_percent": 100 * noise_level,
                        "replicate": replicate,
                        "seed": seed,
                        "method": method,
                        "success": fit_result["success"],
                        "failure_reason": fit_result["failure_reason"],
                        "fitted_vmax": fit_result["vmax"],
                        "fitted_km": fit_result["km"],
                        "vmax_absolute_error": vmax_absolute_error,
                        "km_absolute_error": km_absolute_error,
                        "vmax_relative_error": vmax_relative_error,
                        "km_relative_error": km_relative_error,
                        "r2": fit_result["r2"],
                    })

                if (
                    noise_level == CONFIG["representative_noise_level"]
                    and replicate == CONFIG["representative_replicate"]
                ):
                    representative = {
                        "noise_level": noise_level,
                        "replicate": replicate,
                        "substrate": substrate.copy(),
                        "clean_velocity": clean_velocity.copy(),
                        "noisy_velocity": noisy_velocity.copy(),
                        "noise_sd": noise_sd.copy(),
                        "nonlinear_fit": nonlinear_fit,
                        "lineweaver_fit": lineweaver_fit,
                    }

        summary_rows = summarize_rows(rows, CONFIG)
        breakdown_noise, breakdown_reason = find_breakdown_noise(summary_rows, CONFIG)

        detailed_csv_path = RESULTS_DIR / f"{SCRIPT_NAME}_detailed_results.csv"
        summary_csv_path = RESULTS_DIR / f"{SCRIPT_NAME}_summary.csv"
        detailed_fieldnames = [
            "noise_level",
            "noise_percent",
            "replicate",
            "seed",
            "method",
            "success",
            "failure_reason",
            "fitted_vmax",
            "fitted_km",
            "vmax_absolute_error",
            "km_absolute_error",
            "vmax_relative_error",
            "km_relative_error",
            "r2",
        ]
        summary_fieldnames = [
            "noise_level",
            "method",
            "n_total",
            "n_valid",
            "n_invalid",
            "invalid_fraction",
            "median_vmax_relative_error",
            "median_km_relative_error",
            "mean_vmax_relative_error",
            "mean_km_relative_error",
            "max_vmax_relative_error",
            "max_km_relative_error",
            "median_r2",
            "credible",
        ]
        write_csv(detailed_csv_path, rows, detailed_fieldnames)
        write_csv(summary_csv_path, summary_rows, summary_fieldnames)

        error_figure_path = save_error_plot(summary_rows)
        representative_figure_path = save_representative_fit_plot(representative, CONFIG)

        print("=== SUMMARY BY METHOD AND NOISE LEVEL ===")
        print("noise\tmethod\tvalid/total\tinvalid%\tmedian_Vmax_err\tmedian_Km_err\tmedian_R2\tcredible")
        for row in summary_rows:
            print(
                f"{100 * row['noise_level']:>5.0f}%\t"
                f"{row['method']:<16}\t"
                f"{row['n_valid']:>2}/{row['n_total']:<2}\t"
                f"{100 * row['invalid_fraction']:>7.2f}%\t"
                f"{100 * row['median_vmax_relative_error']:>14.3f}%\t"
                f"{100 * row['median_km_relative_error']:>12.3f}%\t"
                f"{row['median_r2']:>9.5f}\t"
                f"{row['credible']}"
            )
        print()

        print("=== LINEWEAVER-BURK BREAKDOWN CHECK ===")
        if breakdown_noise is None:
            print(f"Breakdown noise level: None among tested levels")
        else:
            print(f"Breakdown noise level: {100 * breakdown_noise:.0f}%")
        print(f"Breakdown reason: {breakdown_reason}")
        print()

        print("=== REPRESENTATIVE DATASET ===")
        print(f"Noise level: {100 * representative['noise_level']:.0f}%")
        print(f"Replicate: {representative['replicate']}")
        print("method\tVmax\tKm\tVmax_err\tKm_err\tsuccess\tfailure_reason")
        for method, fit_result in [
            ("nonlinear", representative["nonlinear_fit"]),
            ("lineweaver_burk", representative["lineweaver_fit"]),
        ]:
            if fit_result["success"]:
                vmax_error = relative_error(fit_result["vmax"], CONFIG["true_vmax"])
                km_error = relative_error(fit_result["km"], CONFIG["true_km"])
                print(
                    f"{method}\t{fit_result['vmax']:.6f}\t{fit_result['km']:.6f}\t"
                    f"{100 * vmax_error:.3f}%\t{100 * km_error:.3f}%\t"
                    f"{fit_result['success']}\t{fit_result['failure_reason']}"
                )
            else:
                print(
                    f"{method}\tnan\tnan\tnan\tnan\t"
                    f"{fit_result['success']}\t{fit_result['failure_reason']}"
                )
        print()

        print("=== OUTPUT FILES ===")
        print(f"Log file: {log_path}")
        print(f"Detailed CSV: {detailed_csv_path}")
        print(f"Summary CSV: {summary_csv_path}")
        print(f"Median error figure: {error_figure_path}")
        print(f"Representative fit figure: {representative_figure_path}")
        print()

        print("=== NEXT ITERATION ===")
        print("Script 03 should generate competitive or noncompetitive inhibition data and confirm the expected apparent Km/Vmax shift.")

        print()
        print(f"{'='*60}")
        print("=== COMPLETE ===")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()


# ============================================================================
# OUTPUT COMMENT BLOCK
# ============================================================================
# Run: python enzyme_kinetics/experiments/01_synthetic/script_02_noise_lineweaver_comparison.py
# Timestamp: 2026-07-13T13:58:01.251454
#
# Planted parameters and experiment design:
# - True Vmax: 100
# - True Km: 5
# - Substrate range: 0.5 to 50
# - Substrate points: 12
# - Noise levels: 0%, 3%, 10%, 20%, 40%
# - Replicates per noise level: 50
# - Base random seed: 2048
# - Nonlinear initial guess [Vmax, Km]: [90.0, 4.0]
# - Credible recovery threshold: <= 10.0% median relative error for both Km and Vmax
#
# Summary by method and noise level:
# - 0% noise, nonlinear: 50/50 valid, median Vmax err 0.000%, median Km err 0.000%, median R^2 1.00000, credible True
# - 0% noise, Lineweaver-Burk: 50/50 valid, median Vmax err 0.000%, median Km err 0.000%, median R^2 1.00000, credible True
# - 3% noise, nonlinear: 50/50 valid, median Vmax err 1.093%, median Km err 3.732%, median R^2 0.99776, credible True
# - 3% noise, Lineweaver-Burk: 50/50 valid, median Vmax err 2.328%, median Km err 3.113%, median R^2 0.99662, credible True
# - 10% noise, nonlinear: 50/50 valid, median Vmax err 5.000%, median Km err 12.666%, median R^2 0.97462, credible False
# - 10% noise, Lineweaver-Burk: 50/50 valid, median Vmax err 7.880%, median Km err 8.856%, median R^2 0.95395, credible True
# - 20% noise, nonlinear: 50/50 valid, median Vmax err 11.064%, median Km err 25.296%, median R^2 0.89899, credible False
# - 20% noise, Lineweaver-Burk: 50/50 valid, median Vmax err 16.635%, median Km err 23.219%, median R^2 0.80635, credible False
# - 40% noise, nonlinear: 50/50 valid, median Vmax err 21.212%, median Km err 33.566%, median R^2 0.68147, credible False
# - 40% noise, Lineweaver-Burk: 40/50 valid, median Vmax err 36.584%, median Km err 47.898%, median R^2 0.37478, credible False
#
# Lineweaver-Burk breakdown check:
# - Breakdown noise level: None among tested levels under the predeclared rule
# - Reason: no tested noise level had Lineweaver-Burk fail while nonlinear remained credible
#
# Representative 20% noise replicate 0:
# - Nonlinear: Vmax 82.538767, Km 2.693782, Vmax err 17.461%, Km err 46.124%, success True
# - Lineweaver-Burk: Vmax 133.258717, Km 8.082860, Vmax err 33.259%, Km err 61.657%, success True
#
# Output files:
# - Log file: enzyme_kinetics/results/logs/script_02_noise_lineweaver_comparison_20260713_135801.log
# - Detailed CSV: enzyme_kinetics/results/script_02_noise_lineweaver_comparison_detailed_results.csv
# - Summary CSV: enzyme_kinetics/results/script_02_noise_lineweaver_comparison_summary.csv
# - Median error figure: enzyme_kinetics/results/figures/script_02_noise_lineweaver_comparison_median_errors.png
# - Representative fit figure: enzyme_kinetics/results/figures/script_02_noise_lineweaver_comparison_representative_fit.png
#
# Interpretation:
# Both methods recovered planted Vmax and Km exactly at 0% noise and remained
# credible at 3% noise. At 10% noise, nonlinear Km median error exceeded the
# 10% credibility threshold while Lineweaver-Burk median errors remained below
# threshold, so the predeclared hypothesis that Lineweaver-Burk breaks earlier
# was not supported under this relative-noise design. At 20% noise both methods
# failed the 10% threshold. At 40% noise Lineweaver-Burk was clearly worse,
# including 20% invalid replicates and larger median errors than nonlinear
# fitting. This suggests the reciprocal method's bias/failure is visible at high
# noise, but the exact breakdown point depends on the noise model and criterion.
# ============================================================================
