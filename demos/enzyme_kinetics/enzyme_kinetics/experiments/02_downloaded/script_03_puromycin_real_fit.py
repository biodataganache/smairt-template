#!/usr/bin/env python3
"""Iteration 03: script_03_puromycin_real_fit

Hypothesis: HYPOTHESIS_03
Kind: single point

Fits the Michaelis-Menten equation to the public Puromycin initial-rate dataset for treated and
untreated conditions, using the method iterations 01 and 02 established.

There is no planted truth here, so this iteration cannot claim the estimates are *correct*. It
checks that they are credible: converged, finite, positive, with finite intervals and residuals
that show no systematic failure of the model. Lineweaver-Burk is reported only as a diagnostic,
because iteration 02 showed it is the less trustworthy of the two.
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

SCRIPT_NAME = "script_03_puromycin_real_fit"
ITERATION_NUMBER = 3
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"
DATA_PATH = PROJECT_ROOT / "data" / "downloaded" / "puromycin_rates.csv"

CONFIG = {
    "data_path": str(DATA_PATH.relative_to(PROJECT_ROOT)),
    "expected_states": ["treated", "untreated"],
    "minimum_observations_per_state": 5,
    "minimum_unique_concentrations": 4,
    "initial_guess": [200.0, 0.1],
    "confidence_level": 0.95,
}


def michaelis_menten(substrate_concentration, vmax, km):
    return vmax * substrate_concentration / (km + substrate_concentration)


def r_squared(observed, predicted):
    residual = np.sum((observed - predicted) ** 2)
    total = np.sum((observed - np.mean(observed)) ** 2)
    return 1.0 - residual / total


def load_puromycin_csv(path):
    """Load the cached dataset with the standard library, so this needs no pandas."""
    if not path.exists():
        raise FileNotFoundError(
            f"{path} is missing. Its provenance is recorded in data/downloaded/README.md."
        )
    by_state: dict[str, list[tuple[float, float]]] = {}
    with path.open() as handle:
        reader = csv.DictReader(handle)
        missing = {"conc", "rate", "state"} - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} is missing required columns: {sorted(missing)}")
        for record in reader:
            by_state.setdefault(record["state"], []).append(
                (float(record["conc"]), float(record["rate"]))
            )
    return {
        state: (
            np.array([pair[0] for pair in pairs]),
            np.array([pair[1] for pair in pairs]),
        )
        for state, pairs in by_state.items()
    }


def fit_with_uncertainty(substrate, velocity, config):
    """Fit and propagate parameter uncertainty from the covariance matrix."""
    parameters, covariance = curve_fit(
        michaelis_menten,
        substrate,
        velocity,
        p0=config["initial_guess"],
        bounds=(0.0, np.inf),
        maxfev=20000,
    )
    standard_errors = np.sqrt(np.diag(covariance))
    # 1.96 is the normal approximation at 95%. With ~11 points this is approximate, which is
    # why the criterion asks only that the interval be finite.
    half_width = 1.96 * standard_errors
    fitted = michaelis_menten(substrate, parameters[0], parameters[1])
    residuals = velocity - fitted
    return {
        "vmax": float(parameters[0]),
        "km": float(parameters[1]),
        "vmax_se": float(standard_errors[0]),
        "km_se": float(standard_errors[1]),
        "vmax_ci": (float(parameters[0] - half_width[0]), float(parameters[0] + half_width[0])),
        "km_ci": (float(parameters[1] - half_width[1]), float(parameters[1] + half_width[1])),
        "rss": float(np.sum(residuals**2)),
        "r2": float(r_squared(velocity, fitted)),
        "residuals": residuals,
    }


def fit_lineweaver_burk(substrate, velocity):
    """Diagnostic only. Iteration 02 is the reason this is not the primary fit."""
    slope, intercept = np.polyfit(1.0 / substrate, 1.0 / velocity, deg=1)
    if intercept <= 0 or slope <= 0:
        return None
    return {"vmax": float(1.0 / intercept), "km": float(slope / intercept)}


def save_figures(data, fits):
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    colours = {"treated": "tab:blue", "untreated": "tab:orange"}

    fit_path = FIGURE_DIR / f"{SCRIPT_NAME}_fits.png"
    plt.figure(figsize=(8, 5.5))
    for state, (substrate, velocity) in sorted(data.items()):
        grid = np.linspace(min(substrate) * 0.5, max(substrate) * 1.1, 300)
        plt.scatter(substrate, velocity, color=colours[state], label=f"{state} observations", zorder=3)
        plt.plot(
            grid,
            michaelis_menten(grid, fits[state]["vmax"], fits[state]["km"]),
            color=colours[state],
            linewidth=2,
            label=f"{state} fit",
        )
    plt.xlabel("Substrate concentration (ppm)")
    plt.ylabel("Initial reaction rate")
    plt.title("Puromycin public dataset: Michaelis-Menten fits")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(fit_path, dpi=200)
    plt.close()

    residual_path = FIGURE_DIR / f"{SCRIPT_NAME}_residuals.png"
    plt.figure(figsize=(8, 5))
    for state, (substrate, _) in sorted(data.items()):
        plt.scatter(substrate, fits[state]["residuals"], color=colours[state], label=state)
    plt.axhline(0.0, linestyle="--", color="grey")
    plt.xlabel("Substrate concentration (ppm)")
    plt.ylabel("Residual (observed - fitted)")
    plt.title("Residuals: structure here would indicate model failure")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(residual_path, dpi=200)
    plt.close()
    return fit_path, residual_path


def main() -> None:
    log_path = setup_logging(SCRIPT_NAME, PROJECT_ROOT / "results" / "logs")
    logger = TeeLogger(log_path)
    try:
        with logger:
            write_provenance(project_root=PROJECT_ROOT, config=CONFIG)
            print("Hypothesis: HYPOTHESIS_03")
            print(
                "Prediction: nonlinear fitting yields positive, finite, plausible parameters for "
                "both conditions, with an interpretable treated/untreated difference."
            )
            print()

            data = load_puromycin_csv(DATA_PATH)

            print("=== DATA VALIDATION ===")
            print(f"Source: {CONFIG['data_path']} (provenance in data/downloaded/README.md)")
            observed_states = sorted(data)
            print(f"States found: {observed_states}")
            assert observed_states == sorted(CONFIG["expected_states"]), (
                f"expected {sorted(CONFIG['expected_states'])}, found {observed_states}"
            )
            for state, (substrate, velocity) in sorted(data.items()):
                unique = len(set(substrate.tolist()))
                print(
                    f"{state}: {len(substrate)} observations, {unique} unique concentrations, "
                    f"rate range {velocity.min():.1f} to {velocity.max():.1f}"
                )
                assert np.all(substrate > 0), f"{state} has a nonpositive concentration"
                assert np.all(velocity > 0), f"{state} has a nonpositive rate"
                assert len(substrate) >= CONFIG["minimum_observations_per_state"], (
                    f"{state} has too few observations"
                )
                assert unique >= CONFIG["minimum_unique_concentrations"], (
                    f"{state} has too few unique concentrations to identify Km"
                )
            print()

            fits = {
                state: fit_with_uncertainty(substrate, velocity, CONFIG)
                for state, (substrate, velocity) in data.items()
            }

            print("=== NONLINEAR FITS (PRIMARY) ===")
            for state in sorted(fits):
                fit = fits[state]
                print(f"{state}:")
                print(f"  Vmax {fit['vmax']:.6f}  SE {fit['vmax_se']:.6f}  "
                      f"95% CI [{fit['vmax_ci'][0]:.6f}, {fit['vmax_ci'][1]:.6f}]")
                print(f"  Km   {fit['km']:.6f}  SE {fit['km_se']:.6f}  "
                      f"95% CI [{fit['km_ci'][0]:.6f}, {fit['km_ci'][1]:.6f}]")
                print(f"  RSS {fit['rss']:.6f}  R^2 {fit['r2']:.6f}")
            print()

            print("=== TREATED VERSUS UNTREATED ===")
            vmax_ratio = fits["treated"]["vmax"] / fits["untreated"]["vmax"]
            km_ratio = fits["treated"]["km"] / fits["untreated"]["km"]
            print(f"Vmax ratio: {vmax_ratio:.6f}")
            print(f"Km ratio: {km_ratio:.6f}")
            print(f"Treated Vmax higher: {fits['treated']['vmax'] > fits['untreated']['vmax']}")
            print()

            print("=== LINEWEAVER-BURK (DIAGNOSTIC ONLY) ===")
            for state in sorted(data):
                substrate, velocity = data[state]
                diagnostic = fit_lineweaver_burk(substrate, velocity)
                if diagnostic is None:
                    print(f"{state}: nonphysical reciprocal parameters")
                    continue
                vmax_difference = abs(diagnostic["vmax"] - fits[state]["vmax"]) / fits[state]["vmax"]
                km_difference = abs(diagnostic["km"] - fits[state]["km"]) / fits[state]["km"]
                print(
                    f"{state}: Vmax {diagnostic['vmax']:.6f} ({100 * vmax_difference:.3f}% from "
                    f"nonlinear), Km {diagnostic['km']:.6f} ({100 * km_difference:.3f}% from nonlinear)"
                )
            print()

            print("=== CRITERIA ===")
            all_finite = all(
                np.isfinite(
                    [f["vmax"], f["km"], f["vmax_se"], f["km_se"], *f["vmax_ci"], *f["km_ci"]]
                ).all()
                for f in fits.values()
            )
            all_positive = all(f["vmax"] > 0 and f["km"] > 0 for f in fits.values())
            print(f"Fits converged for both conditions: True")
            print(f"Parameters positive: {all_positive}")
            print(f"Standard errors and intervals finite: {all_finite}")
            print(f"Criteria met: {all_positive and all_finite}")
            print()

            fit_path, residual_path = save_figures(data, fits)
            print(f"Figures: {fit_path.relative_to(PROJECT_ROOT)}, "
                  f"{residual_path.relative_to(PROJECT_ROOT)}")
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
