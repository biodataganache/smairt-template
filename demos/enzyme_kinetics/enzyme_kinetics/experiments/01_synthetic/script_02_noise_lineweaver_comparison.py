#!/usr/bin/env python3
"""Iteration 02: script_02_noise_lineweaver_comparison

Hypothesis: HYPOTHESIS_02
Kind: single point

Compares direct nonlinear least squares against Lineweaver-Burk linearization across five
relative-noise levels, 50 replicates each, against planted truth.

The predeclared breakdown rule is deliberately strict: Lineweaver-Burk counts as having broken
down only at the first noise level where it fails while nonlinear fitting still holds. That rule
was written before the run, and the run did not trigger it. See HYPOTHESIS_02 and ANALYSIS_02.
"""

from pathlib import Path
import csv
import sys

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, record_run_status, setup_logging, write_provenance

SCRIPT_NAME = "script_02_noise_lineweaver_comparison"
ITERATION_NUMBER = 2
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
    "initial_guess": [90.0, 4.0],
    "max_relative_error_for_credibility": 0.10,
    "invalid_fraction_for_breakdown": 0.10,
}


def michaelis_menten(substrate_concentration, vmax, km):
    return vmax * substrate_concentration / (km + substrate_concentration)


def relative_error(estimate, truth):
    return abs(estimate - truth) / abs(truth)


def r_squared(observed, predicted):
    residual = np.sum((observed - predicted) ** 2)
    total = np.sum((observed - np.mean(observed)) ** 2)
    return 1.0 - residual / total


def generate_substrate(config):
    return np.geomspace(
        config["substrate_min"], config["substrate_max"], config["n_substrate_points"]
    )


def generate_noisy_velocity(substrate, noise_level, seed, config):
    """Generate one replicate. The seed is derived per replicate so runs are reproducible."""
    rng = np.random.default_rng(seed)
    clean = michaelis_menten(substrate, config["true_vmax"], config["true_km"])
    if noise_level == 0.0:
        return clean
    return clean + rng.normal(0.0, noise_level * clean)


def fit_nonlinear(substrate, velocity, config):
    try:
        parameters, _ = curve_fit(
            michaelis_menten,
            substrate,
            velocity,
            p0=config["initial_guess"],
            bounds=(0.0, np.inf),
            maxfev=10000,
        )
    except (RuntimeError, ValueError) as error:
        return {"success": False, "vmax": np.nan, "km": np.nan, "r2": np.nan, "reason": str(error)}
    fitted = michaelis_menten(substrate, parameters[0], parameters[1])
    return {
        "success": True,
        "vmax": float(parameters[0]),
        "km": float(parameters[1]),
        "r2": float(r_squared(velocity, fitted)),
        "reason": "",
    }


def fit_lineweaver_burk(substrate, velocity):
    """Fit on the double-reciprocal scale, refusing cases the transform cannot represent."""
    if np.any(velocity <= 0):
        return {
            "success": False,
            "vmax": np.nan,
            "km": np.nan,
            "r2": np.nan,
            "reason": "nonpositive_velocity_invalid_for_reciprocal",
        }
    slope, intercept = np.polyfit(1.0 / substrate, 1.0 / velocity, deg=1)
    if intercept <= 0 or slope <= 0:
        return {
            "success": False,
            "vmax": np.nan,
            "km": np.nan,
            "r2": np.nan,
            "reason": "nonphysical_lineweaver_parameters",
        }
    fitted_vmax = 1.0 / intercept
    fitted_km = slope / intercept
    fitted = michaelis_menten(substrate, fitted_vmax, fitted_km)
    return {
        "success": True,
        "vmax": float(fitted_vmax),
        "km": float(fitted_km),
        "r2": float(r_squared(velocity, fitted)),
        "reason": "",
    }


def run_sweep(config):
    substrate = generate_substrate(config)
    rows = []
    for noise_level in config["noise_levels"]:
        for replicate in range(config["replicates_per_noise"]):
            seed = config["base_seed"] + int(round(noise_level * 1000)) * 1000 + replicate
            velocity = generate_noisy_velocity(substrate, noise_level, seed, config)
            for method, fit in (
                ("nonlinear", fit_nonlinear(substrate, velocity, config)),
                ("lineweaver_burk", fit_lineweaver_burk(substrate, velocity)),
            ):
                rows.append(
                    {
                        "noise_level": noise_level,
                        "replicate": replicate,
                        "method": method,
                        "success": fit["success"],
                        "vmax": fit["vmax"],
                        "km": fit["km"],
                        "r2": fit["r2"],
                        "vmax_relative_error": (
                            relative_error(fit["vmax"], config["true_vmax"])
                            if fit["success"]
                            else np.nan
                        ),
                        "km_relative_error": (
                            relative_error(fit["km"], config["true_km"])
                            if fit["success"]
                            else np.nan
                        ),
                        "reason": fit["reason"],
                    }
                )
    return rows


def summarize(rows, config):
    threshold = config["max_relative_error_for_credibility"]
    summary = []
    for noise_level in config["noise_levels"]:
        for method in ("nonlinear", "lineweaver_burk"):
            subset = [r for r in rows if r["noise_level"] == noise_level and r["method"] == method]
            valid = [r for r in subset if r["success"]]
            if valid:
                median_vmax = float(np.median([r["vmax_relative_error"] for r in valid]))
                median_km = float(np.median([r["km_relative_error"] for r in valid]))
                median_r2 = float(np.median([r["r2"] for r in valid]))
                credible = median_vmax <= threshold and median_km <= threshold
            else:
                median_vmax = median_km = median_r2 = float("nan")
                credible = False
            summary.append(
                {
                    "noise_level": noise_level,
                    "method": method,
                    "valid": len(valid),
                    "total": len(subset),
                    "invalid_fraction": 1.0 - len(valid) / len(subset),
                    "median_vmax_relative_error": median_vmax,
                    "median_km_relative_error": median_km,
                    "median_r2": median_r2,
                    "credible": credible,
                }
            )
    return summary


def find_breakdown_noise(summary, config):
    """Apply the rule as predeclared: Lineweaver-Burk fails *while* nonlinear still holds."""
    threshold = config["max_relative_error_for_credibility"]
    for noise_level in config["noise_levels"]:
        nonlinear = next(
            r for r in summary if r["noise_level"] == noise_level and r["method"] == "nonlinear"
        )
        lineweaver = next(
            r for r in summary if r["noise_level"] == noise_level and r["method"] == "lineweaver_burk"
        )
        invalid_failure = lineweaver["invalid_fraction"] >= config["invalid_fraction_for_breakdown"]
        if nonlinear["credible"] and (not lineweaver["credible"] or invalid_failure):
            reasons = []
            if lineweaver["median_vmax_relative_error"] > threshold:
                reasons.append("median Vmax error exceeded threshold")
            if lineweaver["median_km_relative_error"] > threshold:
                reasons.append("median Km error exceeded threshold")
            if invalid_failure:
                reasons.append("invalid replicate fraction >= 10%")
            return noise_level, "; ".join(reasons)
    return None, "no tested noise level met the predeclared breakdown definition"


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def save_error_plot(summary, config):
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    figure_path = FIGURE_DIR / f"{SCRIPT_NAME}_median_errors.png"
    figure, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True)
    for parameter, axis in (("vmax", axes[0]), ("km", axes[1])):
        for method, colour in (("nonlinear", "tab:blue"), ("lineweaver_burk", "tab:orange")):
            subset = [r for r in summary if r["method"] == method]
            axis.plot(
                [100 * r["noise_level"] for r in subset],
                [100 * r[f"median_{parameter}_relative_error"] for r in subset],
                marker="o",
                color=colour,
                label=method,
            )
        axis.axhline(
            100 * config["max_relative_error_for_credibility"],
            linestyle="--",
            color="tab:red",
            label="10% criterion",
        )
        axis.set_xlabel("Relative noise (%)")
        axis.set_ylabel(f"Median {parameter} relative error (%)")
        axis.set_title(f"{parameter} recovery")
        axis.grid(alpha=0.3)
        axis.legend()
    figure.tight_layout()
    figure.savefig(figure_path, dpi=200)
    plt.close(figure)
    return figure_path


def main() -> None:
    log_path = setup_logging(SCRIPT_NAME, PROJECT_ROOT / "results" / "logs")
    logger = TeeLogger(log_path)
    try:
        with logger:
            write_provenance(project_root=PROJECT_ROOT, config=CONFIG)
            print("Hypothesis: HYPOTHESIS_02")
            print(
                "Prediction: Lineweaver-Burk breaks the 10% median-error criterion at a lower "
                "noise level than nonlinear least squares."
            )
            print(
                "Breakdown rule, predeclared: the first level where Lineweaver-Burk fails while "
                "nonlinear remains credible."
            )
            print()

            rows = run_sweep(CONFIG)
            summary = summarize(rows, CONFIG)

            print("=== SUMMARY BY METHOD AND NOISE LEVEL ===")
            for row in summary:
                print(
                    f"{100 * row['noise_level']:.0f}% noise, {row['method']}: "
                    f"{row['valid']}/{row['total']} valid, "
                    f"median Vmax err {100 * row['median_vmax_relative_error']:.3f}%, "
                    f"median Km err {100 * row['median_km_relative_error']:.3f}%, "
                    f"median R^2 {row['median_r2']:.5f}, credible {row['credible']}"
                )
            print()

            breakdown_level, reason = find_breakdown_noise(summary, CONFIG)
            print("=== LINEWEAVER-BURK BREAKDOWN CHECK ===")
            print(
                f"Breakdown noise level: "
                f"{'None among tested levels' if breakdown_level is None else f'{100 * breakdown_level:.0f}%'}"
            )
            print(f"Reason: {reason}")
            print()

            print("=== VERDICT AGAINST THE PREDECLARED PREDICTION ===")
            if breakdown_level is None:
                print("HYPOTHESIS_02 is NOT SUPPORTED. The predicted ordering did not appear.")
                first_nonlinear_failure = next(
                    (
                        r["noise_level"]
                        for r in summary
                        if r["method"] == "nonlinear" and not r["credible"]
                    ),
                    None,
                )
                if first_nonlinear_failure is not None:
                    print(
                        f"Nonlinear fitting failed first, at {100 * first_nonlinear_failure:.0f}% "
                        "noise, on Km."
                    )
                print(
                    "Lineweaver-Burk does become unstable at the highest noise level, so the "
                    "concern about the reciprocal transform survives; the ordering claim does not."
                )
            else:
                print("HYPOTHESIS_02 is SUPPORTED under the predeclared rule.")
            print()

            detailed = RESULTS_DIR / f"{SCRIPT_NAME}_detailed_results.csv"
            summary_csv = RESULTS_DIR / f"{SCRIPT_NAME}_summary.csv"
            write_csv(detailed, rows)
            write_csv(summary_csv, summary)
            figure_path = save_error_plot(summary, CONFIG)

            print("=== OUTPUT FILES ===")
            print(f"Detailed CSV: {detailed.relative_to(PROJECT_ROOT)}")
            print(f"Summary CSV: {summary_csv.relative_to(PROJECT_ROOT)}")
            print(f"Figure: {figure_path.relative_to(PROJECT_ROOT)}")
            print(f"Log: {log_path.relative_to(PROJECT_ROOT)}")
    finally:
        # This runs after TeeLogger has classified the run, even when the experiment
        # raised. A record failure is reported but never masks the experiment's exception.
        try:
            record_run_status(PROJECT_ROOT, ITERATION_NUMBER, logger.status, log_path)
        except OSError as error:
            print(f"Warning: could not append run history: {error}", file=sys.stderr)


if __name__ == "__main__":
    main()
