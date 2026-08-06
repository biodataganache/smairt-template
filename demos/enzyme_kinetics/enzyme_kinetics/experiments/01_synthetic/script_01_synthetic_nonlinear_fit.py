#!/usr/bin/env python3
"""Iteration 01: script_01_synthetic_nonlinear_fit

Hypothesis: HYPOTHESIS_01
Kind: single point

Plants known Michaelis-Menten parameters, generates low-noise synthetic velocity data, fits Km
and Vmax by direct nonlinear least squares, and reports recovery error against the known truth.

This is a positive control. The initial guess is offset from the planted truth so that
convergence is doing the work rather than the starting point.
"""

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, record_run_status, setup_logging, write_provenance

SCRIPT_NAME = "script_01_synthetic_nonlinear_fit"
ITERATION_NUMBER = 1
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"

CONFIG = {
    "seed": 1024,
    "true_vmax": 100.0,
    "true_km": 5.0,
    "substrate_min": 0.5,
    "substrate_max": 50.0,
    "n_substrate_points": 12,
    "relative_noise": 0.03,
    "initial_guess": [90.0, 4.0],
    "max_relative_error_for_credibility": 0.10,
}


def michaelis_menten(substrate_concentration, vmax, km):
    """Return Michaelis-Menten velocity for substrate concentration [S]."""
    return vmax * substrate_concentration / (km + substrate_concentration)


def relative_error(estimate, truth):
    return abs(estimate - truth) / abs(truth)


def r_squared(observed, predicted):
    residual = np.sum((observed - predicted) ** 2)
    total = np.sum((observed - np.mean(observed)) ** 2)
    return 1.0 - residual / total


def generate_synthetic_data(config):
    """Generate low-noise synthetic data from the planted parameters."""
    rng = np.random.default_rng(config["seed"])
    substrate = np.geomspace(
        config["substrate_min"], config["substrate_max"], config["n_substrate_points"]
    )
    clean = michaelis_menten(substrate, config["true_vmax"], config["true_km"])
    noise_sd = config["relative_noise"] * clean
    return substrate, clean, clean + rng.normal(0.0, noise_sd), noise_sd


def fit_nonlinear(substrate, velocity, config):
    """Fit on the original velocity scale, bounded to physically meaningful parameters."""
    parameters, covariance = curve_fit(
        michaelis_menten,
        substrate,
        velocity,
        p0=config["initial_guess"],
        bounds=(0.0, np.inf),
        maxfev=10000,
    )
    return parameters[0], parameters[1], covariance


def save_fit_plot(substrate, noisy_velocity, fitted_vmax, fitted_km, config):
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    figure_path = FIGURE_DIR / f"{SCRIPT_NAME}_fit_curve.png"
    grid = np.linspace(config["substrate_min"], config["substrate_max"], 300)

    plt.figure(figsize=(8, 5.5))
    plt.scatter(substrate, noisy_velocity, color="tab:blue", label="Noisy observations", zorder=3)
    plt.plot(
        grid,
        michaelis_menten(grid, config["true_vmax"], config["true_km"]),
        "--",
        color="tab:green",
        linewidth=2,
        label="Planted truth",
    )
    plt.plot(
        grid,
        michaelis_menten(grid, fitted_vmax, fitted_km),
        color="tab:red",
        linewidth=2,
        label="Nonlinear fit",
    )
    plt.xlabel("Substrate concentration [S]")
    plt.ylabel("Reaction velocity v")
    plt.title("Synthetic Michaelis-Menten parameter recovery")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(figure_path, dpi=200)
    plt.close()
    return figure_path


def main() -> None:
    log_path = setup_logging(SCRIPT_NAME, PROJECT_ROOT / "results" / "logs")
    logger = TeeLogger(log_path)
    try:
        with logger:
            write_provenance(project_root=PROJECT_ROOT, config=CONFIG)
            print("Hypothesis: HYPOTHESIS_01")
            print(
                "Prediction: nonlinear least squares recovers both planted parameters "
                f"within {100 * CONFIG['max_relative_error_for_credibility']:.0f}% at "
                f"{100 * CONFIG['relative_noise']:.0f}% noise."
            )
            print()

            substrate, clean, noisy, noise_sd = generate_synthetic_data(CONFIG)

            assert len(substrate) == CONFIG["n_substrate_points"], "unexpected substrate count"
            assert np.all(substrate > 0), "substrate concentrations must be positive"
            assert np.all(noisy > 0), "velocities must be positive at this noise level"

            print("=== GENERATED DATA ===")
            print(f"Samples: {len(substrate)}")
            print("index\t[S]\tclean_v\tnoise_sd\tobserved_v")
            for index, values in enumerate(zip(substrate, clean, noise_sd, noisy), start=1):
                print(
                    f"{index:02d}\t{values[0]:.6f}\t{values[1]:.6f}"
                    f"\t{values[2]:.6f}\t{values[3]:.6f}"
                )
            print()

            fitted_vmax, fitted_km, covariance = fit_nonlinear(substrate, noisy, CONFIG)
            fitted = michaelis_menten(substrate, fitted_vmax, fitted_km)
            vmax_error = relative_error(fitted_vmax, CONFIG["true_vmax"])
            km_error = relative_error(fitted_km, CONFIG["true_km"])
            threshold = CONFIG["max_relative_error_for_credibility"]
            credible = (
                vmax_error <= threshold and km_error <= threshold and fitted_vmax > 0 and fitted_km > 0
            )

            print("=== NONLINEAR LEAST-SQUARES RESULTS ===")
            print(f"Fitted Vmax: {fitted_vmax:.6f}  (true {CONFIG['true_vmax']:.6g})")
            print(f"Fitted Km: {fitted_km:.6f}  (true {CONFIG['true_km']:.6g})")
            print(f"Vmax relative error: {100 * vmax_error:.3f}%")
            print(f"Km relative error: {100 * km_error:.3f}%")
            print(f"Residual sum of squares: {np.sum((noisy - fitted) ** 2):.6f}")
            print(f"R^2 on noisy observations: {r_squared(noisy, fitted):.6f}")
            print(f"Standard errors: {np.sqrt(np.diag(covariance))}")
            print()

            figure_path = save_fit_plot(substrate, noisy, fitted_vmax, fitted_km, CONFIG)

            print("=== CRITERIA ===")
            print(f"1. Vmax error <= {100 * threshold:.0f}%: {vmax_error <= threshold}")
            print(f"2. Km error <= {100 * threshold:.0f}%: {km_error <= threshold}")
            print(f"3. Parameters positive: {fitted_vmax > 0 and fitted_km > 0}")
            print(f"Criteria met: {credible}")
            print()
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
