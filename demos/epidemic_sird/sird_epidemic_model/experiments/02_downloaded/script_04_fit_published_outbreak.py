#!/usr/bin/env python3
"""
Script 04: Fit SIRD parameters to downloaded COVID-19 time series

Hypothesis: HYPOTHESIS_04.md
Phase: downloaded
Track: A (baseline SIRD fitting)
Iteration: 4

Depends on:
  - background/01_initial_question.md
  - hypotheses/HYPOTHESIS_04.md
  - experiments/01_synthetic/script_01_single_scenario.py
  - experiments/01_synthetic/script_02_beta_sweep.py
  - experiments/01_synthetic/script_03_mu_final_size_flatten_curve.py

Purpose:
  Download or read cached JHU CSSE COVID-19 time series, construct an early
  country-level outbreak trajectory, fit beta/gamma/mu in a deterministic SIRD
  model, estimate bootstrap uncertainty for R0, and state limitations honestly.
"""

import csv
import sys
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares

# === PATH SETUP ===
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

# === CONFIGURATION ===
SCRIPT_NAME = "script_04_fit_published_outbreak"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"
DATA_DIR = PROJECT_ROOT / "data" / "downloaded" / "covid19_jhu"

JHU_BASE_URL = (
    "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/"
    "csse_covid_19_data/csse_covid_19_time_series"
)

FILES = {
    "confirmed": "time_series_covid19_confirmed_global.csv",
    "deaths": "time_series_covid19_deaths_global.csv",
    "recovered": "time_series_covid19_recovered_global.csv",
}

CONFIG = {
    "country": "Italy",
    "population": 60_461_826.0,
    "start_confirmed_threshold": 100.0,
    "window_days": 60,
    "min_positive_for_log": 1.0,
    "parameter_bounds": {
        "lower": [1e-5, 1e-5, 1e-7],
        "upper": [2.0, 1.0, 0.5],
    },
    "initial_guess": {
        "beta": 0.35,
        "gamma": 0.08,
        "mu": 0.01,
    },
    "bootstrap_samples": 60,
    "bootstrap_seed": 1024,
    "bootstrap_max_nfev": 250,
    "fit_max_nfev": 1000,
    "conservation_tolerance": 1e-4,
    "nonnegative_tolerance": -1e-6,
}


@dataclass
class FitResult:
    beta: float
    gamma: float
    mu: float
    r0: float
    rmse_log: float
    predicted: np.ndarray
    residuals: np.ndarray
    success: bool
    message: str


# === DATA LOADING ===
def download_if_needed(name, filename):
    """Download one JHU CSV if it is not already cached."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / filename
    url = f"{JHU_BASE_URL}/{filename}"

    if path.exists() and path.stat().st_size > 0:
        print(f"Using cached {name} data: {path}")
        return path, False, url

    print(f"Downloading {name} data from: {url}")
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            content = response.read()
        path.write_bytes(content)
        print(f"  Saved to: {path}")
        return path, True, url
    except Exception as exc:
        raise RuntimeError(
            f"Could not download {name} data and no cache exists at {path}. "
            f"Original error: {exc}"
        ) from exc


def aggregate_country_series(csv_path, country):
    """Aggregate all rows for a country from a JHU time-series CSV."""
    with open(csv_path, newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        assert fieldnames is not None, f"Missing header in {csv_path}"
        date_columns = fieldnames[4:]
        totals = np.zeros(len(date_columns), dtype=float)
        matched_rows = 0
        for row in reader:
            if row.get("Country/Region") == country:
                matched_rows += 1
                totals += np.array([float(row[col] or 0.0) for col in date_columns], dtype=float)

    assert matched_rows > 0, f"No rows found for country={country} in {csv_path}"
    dates = [datetime.strptime(col, "%m/%d/%y") for col in date_columns]
    return dates, totals, matched_rows


def load_covid_country_data(country):
    """Download/read cached JHU data and return aligned country-level arrays."""
    paths = {}
    provenance_rows = []
    for name, filename in FILES.items():
        path, downloaded, url = download_if_needed(name, filename)
        paths[name] = path
        # Use relative path so we don't leak user's personal/absolute paths in the provenance file.
        try:
            rel_path = path.relative_to(PROJECT_ROOT)
        except ValueError:
            rel_path = path
        provenance_rows.append((name, filename, url, str(rel_path), downloaded))

    dates, confirmed, confirmed_rows = aggregate_country_series(paths["confirmed"], country)
    death_dates, deaths, death_rows = aggregate_country_series(paths["deaths"], country)
    recovered_dates, recovered, recovered_rows = aggregate_country_series(paths["recovered"], country)

    assert dates == death_dates == recovered_dates, "JHU date columns are not aligned across files"
    active = confirmed - recovered - deaths
    active = np.maximum(active, 0.0)

    provenance_path = DATA_DIR / f"{country.lower()}_provenance.txt"
    with open(provenance_path, "w") as handle:
        handle.write("JHU CSSE COVID-19 country-level time-series provenance\n")
        handle.write(f"Generated: {datetime.now().isoformat()}\n")
        handle.write(f"Country: {country}\n")
        handle.write(f"Rows matched: confirmed={confirmed_rows}, deaths={death_rows}, recovered={recovered_rows}\n")
        for name, filename, url, path, downloaded in provenance_rows:
            handle.write(f"{name}: filename={filename}; url={url}; local_path={path}; downloaded_now={downloaded}\n")
        handle.write("Source repository: Johns Hopkins University CSSE COVID-19 Data\n")
        handle.write("Use caveat: reported confirmed/recovered/deaths are not direct true SIRD compartments.\n")

    return {
        "dates": dates,
        "confirmed": confirmed,
        "active": active,
        "recovered": recovered,
        "deaths": deaths,
        "provenance_path": provenance_path,
        "paths": paths,
    }


def select_early_window(data):
    """Select early outbreak window after confirmed cases exceed threshold."""
    confirmed = data["confirmed"]
    threshold = CONFIG["start_confirmed_threshold"]
    eligible = np.where(confirmed >= threshold)[0]
    assert len(eligible) > 0, f"No dates with confirmed >= {threshold}"
    start_idx = int(eligible[0])
    end_idx = min(start_idx + CONFIG["window_days"], len(confirmed))
    assert end_idx - start_idx >= 14, "Selected window is too short for fitting"

    window = slice(start_idx, end_idx)
    selected = {
        "dates": data["dates"][window],
        "confirmed": data["confirmed"][window],
        "active": data["active"][window],
        "recovered": data["recovered"][window],
        "deaths": data["deaths"][window],
        "start_idx": start_idx,
        "end_idx": end_idx,
    }
    selected["days"] = np.arange(len(selected["dates"]), dtype=float)
    return selected


# === MODEL AND FITTING ===
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


def simulate_sird(beta, gamma, mu, population, y0, days):
    """Simulate SIRD at requested day offsets."""
    solution = solve_ivp(
        fun=lambda t, y: sird_rhs(t, y, beta, gamma, mu, population),
        t_span=(float(days[0]), float(days[-1])),
        y0=y0,
        t_eval=days,
        method="RK45",
        rtol=1e-7,
        atol=1e-9,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    return solution.y


def pack_params(beta, gamma, mu):
    """Log-transform positive parameters for unconstrained optimization."""
    return np.log(np.array([beta, gamma, mu], dtype=float))


def unpack_params(theta):
    """Invert log-transform."""
    beta, gamma, mu = np.exp(theta)
    return float(beta), float(gamma), float(mu)


def make_observation_matrix(active, recovered, deaths):
    """Stack observed I/R/D as rows matching model output rows 1/2/3."""
    return np.vstack([active, recovered, deaths])


def log_transform_counts(counts):
    """Log-transform counts with floor to reduce dominance by large values."""
    return np.log(np.maximum(counts, CONFIG["min_positive_for_log"]))


def fit_sird(days, observed_ird, population, y0, initial_guess=None, max_nfev=None):
    """Fit beta/gamma/mu by least-squares on log active/recovered/deceased."""
    if initial_guess is None:
        initial_guess = CONFIG["initial_guess"]
    if max_nfev is None:
        max_nfev = CONFIG["fit_max_nfev"]

    target_log = log_transform_counts(observed_ird)
    lower = np.log(np.array(CONFIG["parameter_bounds"]["lower"], dtype=float))
    upper = np.log(np.array(CONFIG["parameter_bounds"]["upper"], dtype=float))
    theta0 = pack_params(initial_guess["beta"], initial_guess["gamma"], initial_guess["mu"])
    theta0 = np.minimum(np.maximum(theta0, lower + 1e-9), upper - 1e-9)

    def residual_function(theta):
        beta, gamma, mu = unpack_params(theta)
        try:
            trajectory = simulate_sird(beta, gamma, mu, population, y0, days)
            predicted_ird = trajectory[[1, 2, 3], :]
            residuals = (log_transform_counts(predicted_ird) - target_log).ravel()
            if not np.all(np.isfinite(residuals)):
                return np.full(target_log.size, 1e6)
            return residuals
        except Exception:
            return np.full(target_log.size, 1e6)

    result = least_squares(
        residual_function,
        theta0,
        bounds=(lower, upper),
        max_nfev=max_nfev,
        xtol=1e-8,
        ftol=1e-8,
        gtol=1e-8,
    )

    beta, gamma, mu = unpack_params(result.x)
    predicted = simulate_sird(beta, gamma, mu, population, y0, days)
    predicted_ird = predicted[[1, 2, 3], :]
    residuals = log_transform_counts(predicted_ird) - target_log
    rmse_log = float(np.sqrt(np.mean(residuals ** 2)))
    r0 = beta / (gamma + mu)
    return FitResult(
        beta=beta,
        gamma=gamma,
        mu=mu,
        r0=r0,
        rmse_log=rmse_log,
        predicted=predicted,
        residuals=residuals,
        success=bool(result.success),
        message=str(result.message),
    )


def bootstrap_r0(days, observed_ird, fit, population, y0):
    """Residual bootstrap on log counts to estimate parameter/R0 uncertainty."""
    rng = np.random.default_rng(CONFIG["bootstrap_seed"])
    predicted_ird = fit.predicted[[1, 2, 3], :]
    predicted_log = log_transform_counts(predicted_ird)
    residuals = fit.residuals
    bootstrap_rows = []

    for index in range(CONFIG["bootstrap_samples"]):
        sampled_residuals = np.empty_like(residuals)
        for compartment_idx in range(residuals.shape[0]):
            sampled_residuals[compartment_idx, :] = rng.choice(
                residuals[compartment_idx, :],
                size=residuals.shape[1],
                replace=True,
            )
        pseudo_log = predicted_log + sampled_residuals
        pseudo_observed = np.exp(pseudo_log)
        pseudo_observed = np.maximum(pseudo_observed, 0.0)

        try:
            boot_fit = fit_sird(
                days,
                pseudo_observed,
                population,
                y0,
                initial_guess={"beta": fit.beta, "gamma": fit.gamma, "mu": fit.mu},
                max_nfev=CONFIG["bootstrap_max_nfev"],
            )
            if boot_fit.success and np.isfinite(boot_fit.r0):
                bootstrap_rows.append([boot_fit.beta, boot_fit.gamma, boot_fit.mu, boot_fit.r0, boot_fit.rmse_log])
        except Exception:
            continue

        if (index + 1) % 10 == 0:
            print(f"  Bootstrap progress: {index + 1}/{CONFIG['bootstrap_samples']} attempted; {len(bootstrap_rows)} successful")

    return np.array(bootstrap_rows, dtype=float)


def summarize_interval(values):
    """Return median and 2.5/97.5 percentile interval."""
    return {
        "median": float(np.percentile(values, 50)),
        "lower": float(np.percentile(values, 2.5)),
        "upper": float(np.percentile(values, 97.5)),
    }


# === MAIN CODE ===
def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with TeeLogger(log_path):
        print(f"{'=' * 60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("Hypothesis: SIRD can fit an early downloaded COVID-19 curve, but uncertainty and limitations will be substantial.")
        print(f"Log file: {log_path}")
        print(f"{'=' * 60}")
        print()

        # ========================================
        # LOAD DATA
        # ========================================
        print("Data source:")
        print("  Johns Hopkins University CSSE COVID-19 global time series")
        print(f"  Base URL: {JHU_BASE_URL}")
        print(f"  Cache directory: {DATA_DIR}")
        print()

        data = load_covid_country_data(CONFIG["country"])
        window = select_early_window(data)

        print("Selected fitting window:")
        print(f"  Country = {CONFIG['country']}")
        print(f"  Population used as closed SIRD N = {CONFIG['population']:.0f}")
        print(f"  Start date = {window['dates'][0].date().isoformat()}")
        print(f"  End date = {window['dates'][-1].date().isoformat()}")
        print(f"  Window length = {len(window['days'])} days")
        print(f"  Start confirmed = {window['confirmed'][0]:.0f}")
        print(f"  Start active = {window['active'][0]:.0f}")
        print(f"  Start recovered = {window['recovered'][0]:.0f}")
        print(f"  Start deaths = {window['deaths'][0]:.0f}")
        print(f"  End confirmed = {window['confirmed'][-1]:.0f}")
        print(f"  End active = {window['active'][-1]:.0f}")
        print(f"  End recovered = {window['recovered'][-1]:.0f}")
        print(f"  End deaths = {window['deaths'][-1]:.0f}")
        print(f"  Provenance file = {data['provenance_path']}")
        print()

        observed_ird = make_observation_matrix(window["active"], window["recovered"], window["deaths"])
        initial_infected = float(window["active"][0])
        initial_recovered = float(window["recovered"][0])
        initial_deceased = float(window["deaths"][0])
        initial_susceptible = CONFIG["population"] - initial_infected - initial_recovered - initial_deceased
        y0 = [initial_susceptible, initial_infected, initial_recovered, initial_deceased]

        assert initial_infected > 0, "Initial active infected must be positive for fitting"
        assert initial_susceptible > 0, "Initial susceptible count must be positive"
        assert np.isclose(sum(y0), CONFIG["population"]), "Initial compartments do not sum to N"
        assert np.all(observed_ird >= 0), "Observed active/recovered/deaths contain negative values"

        # ========================================
        # FIT SIRD MODEL
        # ========================================
        print("Fitting SIRD parameters with bounded least squares on log active/recovered/deaths...")
        fit = fit_sird(window["days"], observed_ird, CONFIG["population"], y0)
        total_population = np.sum(fit.predicted, axis=0)
        max_conservation_error = float(np.max(np.abs(total_population - CONFIG["population"])))
        min_compartment = float(np.min(fit.predicted))
        print(f"  Optimizer success = {fit.success}")
        print(f"  Optimizer message = {fit.message}")
        print(f"  beta = {fit.beta:.8f} /day")
        print(f"  gamma = {fit.gamma:.8f} /day")
        print(f"  mu = {fit.mu:.8f} /day")
        print(f"  R0 = beta / (gamma + mu) = {fit.r0:.8f}")
        print(f"  log-scale RMSE = {fit.rmse_log:.6f}")
        print(f"  Max conservation error = {max_conservation_error:.12e}")
        print(f"  Minimum fitted compartment value = {min_compartment:.12e}")
        print()

        assert fit.success, "Optimizer did not report success"
        assert fit.beta >= 0 and fit.gamma >= 0 and fit.mu >= 0, "Fitted parameters must be non-negative"
        assert max_conservation_error < CONFIG["conservation_tolerance"], "Fitted trajectory failed conservation check"
        assert min_compartment >= CONFIG["nonnegative_tolerance"], "Fitted trajectory failed non-negativity check"

        # ========================================
        # BOOTSTRAP UNCERTAINTY
        # ========================================
        print("Estimating uncertainty with residual bootstrap...")
        bootstrap = bootstrap_r0(window["days"], observed_ird, fit, CONFIG["population"], y0)
        print(f"  Bootstrap successful fits = {len(bootstrap)} / {CONFIG['bootstrap_samples']}")
        assert len(bootstrap) >= max(10, CONFIG["bootstrap_samples"] // 4), "Too few successful bootstrap fits"

        beta_ci = summarize_interval(bootstrap[:, 0])
        gamma_ci = summarize_interval(bootstrap[:, 1])
        mu_ci = summarize_interval(bootstrap[:, 2])
        r0_ci = summarize_interval(bootstrap[:, 3])
        print("Bootstrap percentile intervals (2.5%, 50%, 97.5%):")
        print(f"  beta:  {beta_ci['lower']:.8f}, {beta_ci['median']:.8f}, {beta_ci['upper']:.8f}")
        print(f"  gamma: {gamma_ci['lower']:.8f}, {gamma_ci['median']:.8f}, {gamma_ci['upper']:.8f}")
        print(f"  mu:    {mu_ci['lower']:.8f}, {mu_ci['median']:.8f}, {mu_ci['upper']:.8f}")
        print(f"  R0:    {r0_ci['lower']:.8f}, {r0_ci['median']:.8f}, {r0_ci['upper']:.8f}")
        print()

        # ========================================
        # DIAGNOSTICS AND FIGURES
        # ========================================
        predicted_ird = fit.predicted[[1, 2, 3], :]
        residuals = fit.residuals
        fit_figure_path = FIGURE_DIR / f"{SCRIPT_NAME}_fit.png"
        residual_figure_path = FIGURE_DIR / f"{SCRIPT_NAME}_residuals_uncertainty.png"

        fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), sharex=True)
        labels = ["Active infected", "Recovered", "Deceased"]
        observed_series = [window["active"], window["recovered"], window["deaths"]]
        predicted_series = [predicted_ird[0], predicted_ird[1], predicted_ird[2]]
        for ax, label, observed, predicted in zip(axes, labels, observed_series, predicted_series):
            ax.plot(window["days"], observed, marker="o", linestyle="", markersize=3, label="Observed")
            ax.plot(window["days"], predicted, linewidth=2, label="Fitted SIRD")
            ax.set_title(label)
            ax.set_xlabel("Days since window start")
            ax.grid(True, alpha=0.3)
            ax.set_yscale("log")
        axes[0].set_ylabel("Reported people (log scale)")
        axes[-1].legend()
        fig.suptitle(f"SIRD fit to {CONFIG['country']} early COVID-19 data: R0={fit.r0:.2f}")
        fig.tight_layout()
        fig.savefig(fit_figure_path, dpi=300)
        plt.close(fig)

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        for residual_row, label in zip(residuals, labels):
            axes[0].plot(window["days"], residual_row, marker="o", markersize=3, linewidth=1.5, label=label)
        axes[0].axhline(0.0, linestyle="--", color="black", alpha=0.6)
        axes[0].set_xlabel("Days since window start")
        axes[0].set_ylabel("Log residual: fitted - observed")
        axes[0].set_title("Fit residuals")
        axes[0].grid(True, alpha=0.3)
        axes[0].legend(fontsize=8)

        axes[1].hist(bootstrap[:, 3], bins=20, color="steelblue", alpha=0.8)
        axes[1].axvline(fit.r0, color="red", linewidth=2, label=f"Fit R0={fit.r0:.2f}")
        axes[1].axvline(r0_ci["lower"], color="black", linestyle="--", label="95% bootstrap interval")
        axes[1].axvline(r0_ci["upper"], color="black", linestyle="--")
        axes[1].set_xlabel("Bootstrap R0")
        axes[1].set_ylabel("Count")
        axes[1].set_title("R0 uncertainty")
        axes[1].grid(True, alpha=0.3)
        axes[1].legend(fontsize=8)
        fig.suptitle("SIRD real-data fit diagnostics")
        fig.tight_layout()
        fig.savefig(residual_figure_path, dpi=300)
        plt.close(fig)

        print("Figures generated:")
        print(f"  {fit_figure_path}")
        print(f"  {residual_figure_path}")
        print()

        print("Limitations to carry into analysis:")
        print("  - Reported confirmed/recovered/deaths are not true SIRD compartments.")
        print("  - Testing policy, reporting delays, interventions, and undercounting changed over time.")
        print("  - The model assumes fixed rates, homogeneous mixing, closed population, no latency, and no reinfection.")
        print("  - Fitted beta/gamma/mu should be interpreted as effective parameters for this selected window only.")

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
#   2026-07-13T12:59:31 local run completed successfully.
#
# Key checks from results/logs/script_04_fit_published_outbreak_20260713_125931.log:
#   - Data source/cache: JHU CSSE global COVID-19 time series downloaded to
#     data/downloaded/covid19_jhu/ with provenance in italy_provenance.txt.
#   - Fitting window: Italy, 2020-02-23 through 2020-04-22, 60 days.
#   - Start active/recovered/deaths: 150 / 2 / 3; end active/recovered/deaths:
#     107699 / 54543 / 25085.
#   - beta/gamma/mu: 0.23081955 / 0.05206253 / 0.03663978 per day.
#   - R0 point estimate: 2.60218185.
#   - Bootstrap R0 interval (2.5%, 50%, 97.5%): 1.74888496, 2.00616651, 2.28267311.
#   - Conservation/non-negativity: max conservation error 5.960464477539e-08;
#     minimum fitted compartment value 2.000000000000e+00.
#   - Fit diagnostics: log-scale RMSE 1.035406; limitations are substantial.
#   - Figure paths: results/figures/script_04_fit_published_outbreak_fit.png and
#     results/figures/script_04_fit_published_outbreak_residuals_uncertainty.png
# ============================================================================
