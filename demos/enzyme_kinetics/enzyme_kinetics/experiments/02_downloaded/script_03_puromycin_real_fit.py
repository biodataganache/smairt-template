#!/usr/bin/env python3
"""
Script 03: Public Puromycin dataset Michaelis-Menten fit

Hypothesis: HYPOTHESIS_03.md
Phase: downloaded
Iteration: 03

Depends on:
  - background/01_initial_question.md
  - hypotheses/HYPOTHESIS_03.md
  - data/downloaded/puromycin_rates.csv

This script fits direct nonlinear Michaelis-Menten curves to the public R
Puromycin initial-rate dataset for treated and untreated conditions. Because
this is public real data rather than synthetic planted-truth data, output
correctness is evaluated with schema checks, positivity checks, convergence,
positive finite parameters, approximate confidence intervals, residual
diagnostics, visual saturation-curve agreement, and reproducible logged output.
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
from scipy.stats import t

# === PATH SETUP ===
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

# === CONFIGURATION ===
SCRIPT_NAME = "script_03_puromycin_real_fit"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"
RESULTS_DIR = PROJECT_ROOT / "results"
DATA_PATH = PROJECT_ROOT / "data" / "downloaded" / "puromycin_rates.csv"

CONFIG = {
    "required_columns": ["conc", "rate", "state"],
    "expected_states": ["treated", "untreated"],
    "min_observations_per_state": 5,
    "min_unique_concentrations_per_state": 4,
    "initial_guess_strategy": "vmax=max_rate; km=median_concentration",
    "lineweaver_material_difference_threshold": 0.20,
}


# === MODEL ===
def michaelis_menten(substrate_concentration, vmax, km):
    """Compute Michaelis-Menten velocity for substrate concentration [S]."""
    return vmax * substrate_concentration / (km + substrate_concentration)


# === HELPERS ===
def r_squared(observed, predicted):
    """Return coefficient of determination for observed vs. predicted values."""
    residual_sum_squares = np.sum((observed - predicted) ** 2)
    total_sum_squares = np.sum((observed - np.mean(observed)) ** 2)
    if total_sum_squares == 0:
        return np.nan
    return 1.0 - residual_sum_squares / total_sum_squares


def relative_difference(value_a, value_b):
    """Return relative absolute difference using value_a as denominator."""
    if value_a == 0 or not np.isfinite(value_a) or not np.isfinite(value_b):
        return np.nan
    return abs(value_b - value_a) / abs(value_a)


def load_puromycin_csv(path):
    """Load cached Puromycin CSV using the Python standard library."""
    rows = []
    with open(path, "r", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        for row in reader:
            parsed = dict(row)
            parsed["conc"] = float(parsed["conc"])
            parsed["rate"] = float(parsed["rate"])
            rows.append(parsed)
    return rows, fieldnames


def validate_data(rows, fieldnames, config):
    """Validate schema and basic real-data constraints."""
    validation_messages = []
    validation_passed = True

    missing_columns = [column for column in config["required_columns"] if column not in fieldnames]
    if missing_columns:
        validation_messages.append(f"Missing required columns: {missing_columns}")
        validation_passed = False
    else:
        validation_messages.append(f"Required columns present: {config['required_columns']}")

    if len(rows) == 0:
        validation_messages.append("Data file contains no rows")
        validation_passed = False
    else:
        validation_messages.append(f"Loaded rows: {len(rows)}")

    concentrations = np.array([row["conc"] for row in rows], dtype=float)
    rates = np.array([row["rate"] for row in rows], dtype=float)
    if np.all(np.isfinite(concentrations)) and np.all(concentrations > 0):
        validation_messages.append("All substrate concentrations are positive and finite")
    else:
        validation_messages.append("Substrate concentrations must be positive and finite")
        validation_passed = False

    if np.all(np.isfinite(rates)) and np.all(rates > 0):
        validation_messages.append("All reaction rates are positive and finite")
    else:
        validation_messages.append("Reaction rates must be positive and finite")
        validation_passed = False

    observed_states = sorted(set(row["state"] for row in rows))
    if observed_states == sorted(config["expected_states"]):
        validation_messages.append(f"Observed expected states: {observed_states}")
    else:
        validation_messages.append(
            f"Observed states {observed_states} differ from expected {config['expected_states']}"
        )
        validation_passed = False

    for state in observed_states:
        state_rows = [row for row in rows if row["state"] == state]
        unique_concentrations = sorted(set(row["conc"] for row in state_rows))
        if len(state_rows) >= config["min_observations_per_state"]:
            validation_messages.append(f"{state}: observation count OK ({len(state_rows)})")
        else:
            validation_messages.append(f"{state}: too few observations ({len(state_rows)})")
            validation_passed = False
        if len(unique_concentrations) >= config["min_unique_concentrations_per_state"]:
            validation_messages.append(
                f"{state}: unique concentration count OK ({len(unique_concentrations)})"
            )
        else:
            validation_messages.append(
                f"{state}: too few unique concentrations ({len(unique_concentrations)})"
            )
            validation_passed = False

    return validation_passed, validation_messages


def rows_for_state(rows, state):
    """Return sorted concentration and rate arrays for one condition."""
    state_rows = sorted([row for row in rows if row["state"] == state], key=lambda row: row["conc"])
    concentrations = np.array([row["conc"] for row in state_rows], dtype=float)
    rates = np.array([row["rate"] for row in state_rows], dtype=float)
    return concentrations, rates


def fit_nonlinear(concentrations, rates):
    """Fit Michaelis-Menten parameters by nonlinear least squares."""
    initial_guess = [float(np.max(rates)), float(np.median(concentrations))]
    fitted_params, covariance = curve_fit(
        michaelis_menten,
        concentrations,
        rates,
        p0=initial_guess,
        bounds=(0.0, np.inf),
        maxfev=10000,
    )
    fitted_vmax, fitted_km = fitted_params
    fitted_rates = michaelis_menten(concentrations, fitted_vmax, fitted_km)
    residuals = rates - fitted_rates
    rss = float(np.sum(residuals ** 2))
    return {
        "success": True,
        "vmax": float(fitted_vmax),
        "km": float(fitted_km),
        "covariance": covariance,
        "initial_guess": initial_guess,
        "fitted_rates": fitted_rates,
        "residuals": residuals,
        "rss": rss,
        "r2": float(r_squared(rates, fitted_rates)),
        "failure_reason": "",
    }


def parameter_uncertainty(fit_result, n_observations):
    """Compute approximate standard errors and 95% confidence intervals."""
    covariance = fit_result["covariance"]
    dof = max(0, n_observations - 2)
    multiplier = float(t.ppf(0.975, dof)) if dof > 0 else np.nan
    standard_errors = np.sqrt(np.diag(covariance))
    vmax_se = float(standard_errors[0])
    km_se = float(standard_errors[1])
    return {
        "dof": dof,
        "ci_multiplier": multiplier,
        "vmax_se": vmax_se,
        "km_se": km_se,
        "vmax_ci_low": float(fit_result["vmax"] - multiplier * vmax_se),
        "vmax_ci_high": float(fit_result["vmax"] + multiplier * vmax_se),
        "km_ci_low": float(fit_result["km"] - multiplier * km_se),
        "km_ci_high": float(fit_result["km"] + multiplier * km_se),
    }


def fit_lineweaver_burk(concentrations, rates):
    """Fit Michaelis-Menten parameters using Lineweaver-Burk linearization."""
    if np.any(concentrations <= 0) or np.any(rates <= 0):
        return {
            "success": False,
            "vmax": np.nan,
            "km": np.nan,
            "r2": np.nan,
            "failure_reason": "nonpositive_values_invalid_for_reciprocal",
        }

    reciprocal_concentration = 1.0 / concentrations
    reciprocal_rate = 1.0 / rates
    slope, intercept = np.polyfit(reciprocal_concentration, reciprocal_rate, deg=1)
    if slope <= 0 or intercept <= 0:
        return {
            "success": False,
            "vmax": np.nan,
            "km": np.nan,
            "r2": np.nan,
            "failure_reason": "nonphysical_lineweaver_parameters",
        }

    vmax = 1.0 / intercept
    km = slope / intercept
    fitted_rates = michaelis_menten(concentrations, vmax, km)
    return {
        "success": True,
        "vmax": float(vmax),
        "km": float(km),
        "r2": float(r_squared(rates, fitted_rates)),
        "failure_reason": "",
    }


def save_fit_plot(rows, fit_results):
    """Save Michaelis-Menten fitted curves over the Puromycin data."""
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    figure_path = FIGURE_DIR / f"{SCRIPT_NAME}_fit_curves.png"
    colors = {"treated": "tab:blue", "untreated": "tab:orange"}

    plt.figure(figsize=(8, 5.5))
    for state in CONFIG["expected_states"]:
        concentrations, rates = rows_for_state(rows, state)
        plt.scatter(
            concentrations,
            rates,
            color=colors[state],
            label=f"{state} observations",
            zorder=3,
        )
        concentration_grid = np.linspace(np.min(concentrations), np.max(concentrations), 300)
        fit_result = fit_results[state]["nonlinear"]
        plt.plot(
            concentration_grid,
            michaelis_menten(concentration_grid, fit_result["vmax"], fit_result["km"]),
            color=colors[state],
            linewidth=2,
            label=f"{state} nonlinear fit",
        )

    plt.xlabel("Substrate concentration")
    plt.ylabel("Reaction rate")
    plt.title("Puromycin public dataset: Michaelis-Menten fits")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(figure_path, dpi=300)
    plt.close()
    return figure_path


def save_residual_plot(rows, fit_results):
    """Save residuals versus substrate concentration by condition."""
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    figure_path = FIGURE_DIR / f"{SCRIPT_NAME}_residuals.png"
    colors = {"treated": "tab:blue", "untreated": "tab:orange"}

    plt.figure(figsize=(8, 5.5))
    for state in CONFIG["expected_states"]:
        concentrations, rates = rows_for_state(rows, state)
        residuals = fit_results[state]["nonlinear"]["residuals"]
        plt.axhline(0, color="black", linewidth=1, alpha=0.5)
        plt.scatter(
            concentrations,
            residuals,
            color=colors[state],
            label=f"{state} residuals",
            zorder=3,
        )

    plt.xlabel("Substrate concentration")
    plt.ylabel("Observed - fitted rate")
    plt.title("Puromycin nonlinear fit residuals")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(figure_path, dpi=300)
    plt.close()
    return figure_path


def write_fit_summary_csv(path, fit_results):
    """Save condition-level fit summaries to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "state",
        "method",
        "success",
        "vmax",
        "km",
        "vmax_se",
        "km_se",
        "vmax_ci_low",
        "vmax_ci_high",
        "km_ci_low",
        "km_ci_high",
        "rss",
        "r2",
        "failure_reason",
    ]
    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for state, state_results in fit_results.items():
            nonlinear = state_results["nonlinear"]
            uncertainty = state_results["uncertainty"]
            writer.writerow({
                "state": state,
                "method": "nonlinear",
                "success": nonlinear["success"],
                "vmax": nonlinear["vmax"],
                "km": nonlinear["km"],
                "vmax_se": uncertainty["vmax_se"],
                "km_se": uncertainty["km_se"],
                "vmax_ci_low": uncertainty["vmax_ci_low"],
                "vmax_ci_high": uncertainty["vmax_ci_high"],
                "km_ci_low": uncertainty["km_ci_low"],
                "km_ci_high": uncertainty["km_ci_high"],
                "rss": nonlinear["rss"],
                "r2": nonlinear["r2"],
                "failure_reason": nonlinear["failure_reason"],
            })
            lineweaver = state_results["lineweaver_burk"]
            writer.writerow({
                "state": state,
                "method": "lineweaver_burk_diagnostic",
                "success": lineweaver["success"],
                "vmax": lineweaver["vmax"],
                "km": lineweaver["km"],
                "vmax_se": np.nan,
                "km_se": np.nan,
                "vmax_ci_low": np.nan,
                "vmax_ci_high": np.nan,
                "km_ci_low": np.nan,
                "km_ci_high": np.nan,
                "rss": np.nan,
                "r2": lineweaver["r2"],
                "failure_reason": lineweaver["failure_reason"],
            })


# === MAIN CODE ===
def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)

    with TeeLogger(log_path):
        print(f"{'='*60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("Hypothesis: Public Puromycin initial-rate data can be fit with positive finite Michaelis-Menten parameters and interpretable condition differences.")
        print(f"{'='*60}")
        print()

        print("=== DATA SOURCE ===")
        print("Source: R datasets::Puromycin")
        print(f"Cached CSV: {DATA_PATH}")
        print("Note: This is public real/downloaded data; no planted truth is assumed.")
        print()

        rows, fieldnames = load_puromycin_csv(DATA_PATH)
        validation_passed, validation_messages = validate_data(rows, fieldnames, CONFIG)

        print("=== DATA VALIDATION ===")
        for message in validation_messages:
            print(f"- {message}")
        print(f"Validation passed: {validation_passed}")
        if not validation_passed:
            raise ValueError("Puromycin data validation failed")
        print()

        fit_results = {}
        for state in CONFIG["expected_states"]:
            concentrations, rates = rows_for_state(rows, state)
            nonlinear = fit_nonlinear(concentrations, rates)
            uncertainty = parameter_uncertainty(nonlinear, len(rates))
            lineweaver = fit_lineweaver_burk(concentrations, rates)
            fit_results[state] = {
                "concentrations": concentrations,
                "rates": rates,
                "nonlinear": nonlinear,
                "uncertainty": uncertainty,
                "lineweaver_burk": lineweaver,
            }

        summary_csv_path = RESULTS_DIR / f"{SCRIPT_NAME}_fit_summary.csv"
        write_fit_summary_csv(summary_csv_path, fit_results)
        fit_figure_path = save_fit_plot(rows, fit_results)
        residual_figure_path = save_residual_plot(rows, fit_results)

        print("=== NONLINEAR MICHAELIS-MENTEN FITS ===")
        for state in CONFIG["expected_states"]:
            result = fit_results[state]["nonlinear"]
            uncertainty = fit_results[state]["uncertainty"]
            concentrations = fit_results[state]["concentrations"]
            rates = fit_results[state]["rates"]
            residuals = result["residuals"]
            finite_uncertainty = all(
                np.isfinite(value)
                for value in [
                    uncertainty["vmax_se"],
                    uncertainty["km_se"],
                    uncertainty["vmax_ci_low"],
                    uncertainty["vmax_ci_high"],
                    uncertainty["km_ci_low"],
                    uncertainty["km_ci_high"],
                ]
            )
            positive_finite_parameters = (
                np.isfinite(result["vmax"])
                and np.isfinite(result["km"])
                and result["vmax"] > 0
                and result["km"] > 0
            )
            saturation_coverage = np.max(concentrations) > result["km"]
            print(f"State: {state}")
            print(f"  Observations: {len(rates)}")
            print(f"  Unique concentrations: {len(set(concentrations))}")
            print(f"  Initial guess [Vmax, Km]: {result['initial_guess']}")
            print(f"  Fitted Vmax: {result['vmax']:.6f}")
            print(f"  Fitted Km: {result['km']:.6f}")
            print(f"  Vmax SE: {uncertainty['vmax_se']:.6f}")
            print(f"  Km SE: {uncertainty['km_se']:.6f}")
            print(f"  Vmax 95% CI: [{uncertainty['vmax_ci_low']:.6f}, {uncertainty['vmax_ci_high']:.6f}]")
            print(f"  Km 95% CI: [{uncertainty['km_ci_low']:.6f}, {uncertainty['km_ci_high']:.6f}]")
            print(f"  RSS: {result['rss']:.6f}")
            print(f"  R^2: {result['r2']:.6f}")
            print(f"  Residual mean: {np.mean(residuals):.6f}")
            print(f"  Residual max absolute value: {np.max(np.abs(residuals)):.6f}")
            print(f"  Positive finite parameters: {positive_finite_parameters}")
            print(f"  Finite uncertainty estimates: {finite_uncertainty}")
            print(f"  Max concentration exceeds fitted Km: {saturation_coverage}")
            print()

        print("=== CONDITION COMPARISON ===")
        treated = fit_results["treated"]["nonlinear"]
        untreated = fit_results["untreated"]["nonlinear"]
        vmax_ratio = treated["vmax"] / untreated["vmax"]
        km_ratio = treated["km"] / untreated["km"]
        print(f"Treated / untreated Vmax ratio: {vmax_ratio:.6f}")
        print(f"Treated / untreated Km ratio: {km_ratio:.6f}")
        print(f"Treated Vmax higher than untreated Vmax: {treated['vmax'] > untreated['vmax']}")
        print()

        print("=== LINEWEAVER-BURK DIAGNOSTIC COMPARISON ===")
        material_disagreement_found = False
        for state in CONFIG["expected_states"]:
            nonlinear = fit_results[state]["nonlinear"]
            lineweaver = fit_results[state]["lineweaver_burk"]
            if lineweaver["success"]:
                vmax_difference = relative_difference(nonlinear["vmax"], lineweaver["vmax"])
                km_difference = relative_difference(nonlinear["km"], lineweaver["km"])
                material_disagreement = (
                    vmax_difference >= CONFIG["lineweaver_material_difference_threshold"]
                    or km_difference >= CONFIG["lineweaver_material_difference_threshold"]
                )
                material_disagreement_found = material_disagreement_found or material_disagreement
                print(f"State: {state}")
                print(f"  Lineweaver-Burk Vmax: {lineweaver['vmax']:.6f}")
                print(f"  Lineweaver-Burk Km: {lineweaver['km']:.6f}")
                print(f"  Lineweaver-Burk R^2 on original rate scale: {lineweaver['r2']:.6f}")
                print(f"  Relative Vmax difference vs nonlinear: {100 * vmax_difference:.3f}%")
                print(f"  Relative Km difference vs nonlinear: {100 * km_difference:.3f}%")
                print(f"  Material diagnostic disagreement: {material_disagreement}")
            else:
                material_disagreement_found = True
                print(f"State: {state}")
                print(f"  Lineweaver-Burk failed: {lineweaver['failure_reason']}")
            print()
        print(f"Any material Lineweaver-Burk disagreement: {material_disagreement_found}")
        print()

        print("=== OUTPUT CORRECTNESS CHECKLIST ===")
        all_nonlinear_success = all(fit_results[state]["nonlinear"]["success"] for state in CONFIG["expected_states"])
        all_positive_finite = all(
            fit_results[state]["nonlinear"]["vmax"] > 0
            and fit_results[state]["nonlinear"]["km"] > 0
            and np.isfinite(fit_results[state]["nonlinear"]["vmax"])
            and np.isfinite(fit_results[state]["nonlinear"]["km"])
            for state in CONFIG["expected_states"]
        )
        all_uncertainty_finite = all(
            np.isfinite(fit_results[state]["uncertainty"][key])
            for state in CONFIG["expected_states"]
            for key in ["vmax_se", "km_se", "vmax_ci_low", "vmax_ci_high", "km_ci_low", "km_ci_high"]
        )
        all_saturation_covered = all(
            np.max(fit_results[state]["concentrations"]) > fit_results[state]["nonlinear"]["km"]
            for state in CONFIG["expected_states"]
        )
        print(f"Data validation passed: {validation_passed}")
        print(f"All nonlinear fits converged: {all_nonlinear_success}")
        print(f"All nonlinear parameters positive and finite: {all_positive_finite}")
        print(f"All approximate uncertainty estimates finite: {all_uncertainty_finite}")
        print(f"All conditions sample above fitted Km: {all_saturation_covered}")
        print("Visual correctness requires inspecting the saved fitted-curve and residual plots.")
        output_correctness_passed = (
            validation_passed
            and all_nonlinear_success
            and all_positive_finite
            and all_uncertainty_finite
            and all_saturation_covered
        )
        print(f"Non-visual output correctness checks passed: {output_correctness_passed}")
        print()

        print("=== OUTPUT FILES ===")
        print(f"Log file: {log_path}")
        print(f"Fit summary CSV: {summary_csv_path}")
        print(f"Fitted curve figure: {fit_figure_path}")
        print(f"Residual figure: {residual_figure_path}")

        print()
        print(f"{'='*60}")
        print("=== COMPLETE ===")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()


# ============================================================================
# OUTPUT COMMENT BLOCK
# ============================================================================
# Run: python enzyme_kinetics/experiments/02_downloaded/script_03_puromycin_real_fit.py
# Timestamp: 2026-07-13T14:14:24.711150
#
# Data source:
# - Source: R datasets::Puromycin
# - Cached CSV: enzyme_kinetics/data/downloaded/puromycin_rates.csv
# - Public real/downloaded data; no planted truth is assumed.
#
# Data validation:
# - Required columns present: ['conc', 'rate', 'state']
# - Loaded rows: 23
# - All substrate concentrations are positive and finite
# - All reaction rates are positive and finite
# - Observed expected states: ['treated', 'untreated']
# - treated: observation count OK (12)
# - treated: unique concentration count OK (6)
# - untreated: observation count OK (11)
# - untreated: unique concentration count OK (6)
# - Validation passed: True
#
# Nonlinear Michaelis-Menten fits:
# - Treated Vmax: 212.683859
# - Treated Km: 0.064121
# - Treated Vmax SE: 6.947162
# - Treated Km SE: 0.008281
# - Treated Vmax 95% CI: [197.204618, 228.163100]
# - Treated Km 95% CI: [0.045670, 0.082573]
# - Treated RSS: 1195.448814
# - Treated R^2: 0.961261
# - Untreated Vmax: 160.280124
# - Untreated Km: 0.047708
# - Untreated Vmax SE: 6.480251
# - Untreated Km SE: 0.007782
# - Untreated Vmax 95% CI: [145.620777, 174.939470]
# - Untreated Km 95% CI: [0.030104, 0.065312]
# - Untreated RSS: 859.604294
# - Untreated R^2: 0.935572
#
# Condition comparison:
# - Treated / untreated Vmax ratio: 1.326951
# - Treated / untreated Km ratio: 1.344031
# - Treated Vmax higher than untreated Vmax: True
#
# Lineweaver-Burk diagnostic comparison:
# - Treated Lineweaver-Burk Vmax: 195.802709
# - Treated Lineweaver-Burk Km: 0.048407
# - Treated relative Vmax difference vs nonlinear: 7.937%
# - Treated relative Km difference vs nonlinear: 24.508%
# - Untreated Lineweaver-Burk Vmax: 143.428116
# - Untreated Lineweaver-Burk Km: 0.030837
# - Untreated relative Vmax difference vs nonlinear: 10.514%
# - Untreated relative Km difference vs nonlinear: 35.363%
# - Any material Lineweaver-Burk disagreement: True
#
# Output correctness checklist:
# - Data validation passed: True
# - All nonlinear fits converged: True
# - All nonlinear parameters positive and finite: True
# - All approximate uncertainty estimates finite: True
# - All conditions sample above fitted Km: True
# - Non-visual output correctness checks passed: True
# - Visual check: fitted curves follow the observed saturation pattern; residuals
#   are moderate with no obvious monotone model failure across the full range.
#
# Output files:
# - Log file: enzyme_kinetics/results/logs/script_03_puromycin_real_fit_20260713_141424.log
# - Fit summary CSV: enzyme_kinetics/results/script_03_puromycin_real_fit_fit_summary.csv
# - Fitted curve figure: enzyme_kinetics/results/figures/script_03_puromycin_real_fit_fit_curves.png
# - Residual figure: enzyme_kinetics/results/figures/script_03_puromycin_real_fit_residuals.png
#
# Interpretation:
# The Puromycin public-data fit passes the non-visual correctness checks and the
# saved figures show sensible saturation-shaped fits for both treated and
# untreated conditions. Treated cells have a higher fitted Vmax than untreated
# cells and a slightly higher fitted Km. Lineweaver-Burk estimates materially
# disagree for Km in both conditions, supporting its use here as a diagnostic
# comparator rather than the trusted primary fit.
# ============================================================================
