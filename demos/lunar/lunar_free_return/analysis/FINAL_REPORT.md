# Final Report — Lunar Free Return

> **Imported record.** This report was written before the project moved onto the current SMAIRT
> scaffold. The scripts, figures, and interpretations below are original. The raw execution logs
> from those runs were **not retained**, so entries marked "(not retained)" name the log that was
> produced rather than one you can open. See `analysis/RUN_HISTORY.md` for why no execution rows
> were reconstructed.


| Field | Details |
|---|---|
| Research Project | Lunar Free Return |
| Study Scope | Artemis II-style free-return trajectory in the Earth-Moon Circular Restricted Three-Body Problem |
| Methodological Approach | Hypothesis-driven computational astrodynamics study |
| Generated | 2026-07-10 |
| Primary Sources | [background/01_initial_question.md](../background/01_initial_question.md); [ANALYSIS_01.md](ANALYSIS_01.md); [ANALYSIS_02.md](ANALYSIS_02.md); [ANALYSIS_03.md](ANALYSIS_03.md) |

---

## 1. Executive Summary

This project tested whether a simplified but physically meaningful Earth-Moon Circular Restricted Three-Body Problem model can reproduce mission-relevant lunar transfer behaviors from a low-Earth parking orbit. Across three synthetic numerical experiments, the project successfully identified a narrow passive free-return corridor, mapped a direct lunar-impact corridor, and then discovered a physical boundary limiting passive multi-loop lunar returns.

The main positive result is that a single impulsive translunar injection can place the spacecraft onto a free-return trajectory that loops behind the Moon and returns to Earth without further burns. The best standard free-return case occurred at a translunar injection speed of 10.9300 km/s and launch phase angle of 245.0 degrees, returning to a 118.0 km Earth perigee after a safe lunar flyby. The main negative-but-informative result is that purely passive three-loop lunar free-returns were not found; instead, the simulation identified a hard practical boundary near 1.27 loops, implying that longer-lived lunar looping returns require active correction or station-keeping.

This report serves as a comprehensive synthesis of the lunar free-return investigation: what was attempted, what worked, what failed, what evidence was produced, and what should happen next.

---

## 2. Project Question and Model Scope

### Central Question

Can a translunar-injection burn from low-Earth orbit produce a free-return trajectory: one that loops behind the Moon and returns to a low Earth perigee with no further burns?

Source: [background/01_initial_question.md](../background/01_initial_question.md)

### Model Used

This study uses the planar Earth-Moon Circular Restricted Three-Body Problem. The model assumes:

- Earth and Moon are point masses in circular orbit.
- The spacecraft has negligible mass.
- The simulation is run in a rotating non-dimensional frame.
- The Moon is fixed in the rotating frame at x = 1 - mu.
- Numerical fidelity is checked using Jacobi-constant drift.

### What This Model Is Good For

This model is well suited for an initial computational investigation because it is fast, reproducible, CPU-only, and requires no external data. It captures the qualitative geometry of free-return, direct-intercept, and weak-stability-boundary behavior while preserving a clear path toward higher-fidelity modeling.

### What This Model Is Not

This is not a mission-grade trajectory design model. It omits lunar eccentricity, solar gravity, Earth oblateness, ephemeris variation, non-planar motion, launch-site constraints, finite burn duration, navigation uncertainty, and operational mid-course correction design.

---

## 3. Research Audit Trail

The research record connects each hypothesis to its implementation, interpretation, and final status. The run logs from these original executions were not retained, so the log column names what was produced rather than a file you can open:

| Iteration | Hypothesis | Script | Log | Analysis | Status |
|---|---|---|---|---|---|
| 01 | [HYPOTHESIS_01.md](../hypotheses/HYPOTHESIS_01.md) | [script_01_trajectory_sweep.py](../experiments/01_synthetic/script_01_trajectory_sweep.py) | `script_01_trajectory_sweep_20260625_095910.log` (not retained) | [ANALYSIS_01.md](ANALYSIS_01.md) | Supported |
| 02 | [HYPOTHESIS_02.md](../hypotheses/HYPOTHESIS_02.md) | [script_02_lunar_intercept.py](../experiments/01_synthetic/script_02_lunar_intercept.py) | `script_02_lunar_intercept_20260625_112846.log` (not retained) | [ANALYSIS_02.md](ANALYSIS_02.md) | Supported |
| 03 | [HYPOTHESIS_03.md](../hypotheses/HYPOTHESIS_03.md) | [script_03_multi_loop_return.py](../experiments/01_synthetic/script_03_multi_loop_return.py) | `script_03_multi_loop_return_20260625_122118.log` (not retained) | [ANALYSIS_03.md](ANALYSIS_03.md) | Partially supported; physical constraint discovered |

Note: [HYPOTHESIS_03.md](../hypotheses/HYPOTHESIS_03.md) still lists its status as pending, but [ANALYSIS_03.md](ANALYSIS_03.md) provides the post-run assessment: the original exactly-three-loop prediction was not supported, while the broader multi-loop return concept was partially supported through the discovery of a 1.25-loop passive return boundary.

---

## 4. Final Results Matrix

| Result Area | Best Case | Main Quantitative Outcome | Interpretation |
|---|---:|---:|---|
| Standard passive free-return | v = 10.9300 km/s, phi = 245.0 degrees | Return perigee altitude = 118.0 km; closest lunar approach = 23,938.3 km; max Jacobi drift = 6.32e-10 | A real free-return corridor exists in the simplified model and is extremely narrow. |
| Direct lunar intercept | v = 10.9700 km/s, phi = 224.0 degrees | 106 direct impact trajectories; 88 leading-face impacts; best time-of-flight = 2.441 days; max Jacobi drift = 1.79e-10 | Direct lunar impacts occupy a related but distinct low-energy phase-angle corridor. |
| Multi-loop passive return | v = 10.97800 km/s, phi = 225.800 degrees | Accumulated loops = 1.2458; return altitude = 0.0 km; flight time = 32.426 days; Jacobi drift = 8.62e-10 | Passive multi-loop returns exist, but the model identified a practical passive limit near 1.27 loops rather than the hypothesized 3 loops. |

---

## 5. Iteration 1 — Standard Circumlunar Free Return

### Goal

Find a narrow translunar injection speed corridor that sends the spacecraft behind the Moon and returns it to a low-Earth perigee without post-injection propulsion.

Sources: [HYPOTHESIS_01.md](../hypotheses/HYPOTHESIS_01.md), [ANALYSIS_01.md](ANALYSIS_01.md)

### Method

The experiment swept 301 injection speeds from 10.850 km/s to 11.150 km/s from a 200 km low-Earth circular parking orbit. The original simple launch geometry failed, so the final run used a Coriolis-compensated launch phase angle of 245.0 degrees.

### Key Findings

| Metric | Expected | Observed | Assessment |
|---|---:|---:|---|
| Return perigee altitude | Below 10,000 km | 118.0 km | Success |
| Closest lunar approach | Greater than Moon radius | 23,938.3 km | Success |
| Jacobi drift | Below 1e-6 | 6.32e-10 maximum | Success |
| Free-return velocity corridor | Narrow transition band | 10.9270 to 10.9360 km/s | Success |

### Interpretation

The hypothesis was supported. The free-return trajectory sits on a sharp transition boundary between fallback cases at lower energy and escape or high-apogee cases at higher energy. The result also demonstrated that launch phase angle is not a minor setup detail; it is a controlling variable. A naive phase angle of 180 degrees missed the Moon by more than 213,000 km, while the optimized 245.0 degree launch phase recovered the free-return behavior.

### Generated Artifacts

- Log: `script_01_trajectory_sweep_20260625_095910.log` (not retained)
- Trajectory figure: [script_01_trajectory_sweep_trajectories.png](../results/figures/script_01_trajectory_sweep_trajectories.png)
- Metrics figure: [script_01_trajectory_sweep_metrics.png](../results/figures/script_01_trajectory_sweep_metrics.png)

---

## 6. Iteration 2 — Direct Minimum-Energy Lunar Intercept

### Goal

Shift from a safe lunar flyby to a direct lunar intercept and determine whether low-energy trajectories preferentially hit the Moon's leading hemisphere.

Sources: [HYPOTHESIS_02.md](../hypotheses/HYPOTHESIS_02.md), [ANALYSIS_02.md](ANALYSIS_02.md)

### Method

A high-density two-dimensional sweep explored injection speeds from 10.920 km/s to 10.970 km/s and launch phase angles from 224.0 degrees to 238.0 degrees. The simulation used a terminating event when the spacecraft crossed the Moon's physical radius.

### Key Findings

| Metric | Expected | Observed | Assessment |
|---|---:|---:|---|
| Direct impact | Distance to Moon at or below lunar radius | 106 impacts found | Success |
| Leading-face target | Positive rotating-frame lunar y-coordinate | 88 of 106 impacts | Success |
| Best impact case | Low-energy fast intercept | v = 10.9700 km/s, phi = 224.0 degrees | Success |
| Time of flight | Shorter than free-return | 2.441 days | Success |
| Jacobi drift | Below 1e-6 | 1.79e-10 maximum | Success |

### Interpretation

The hypothesis was supported. Direct impacts occur in a different phase-angle corridor than the standard free-return. Most impacts fell on the leading lunar hemisphere, supporting the physical explanation that the slower spacecraft near apogee is swept up by the faster-moving Moon.

### Generated Artifacts

- Log: `script_02_lunar_intercept_20260625_112846.log` (not retained)
- Trajectory figure: [script_02_lunar_intercept_trajectories.png](../results/figures/script_02_lunar_intercept_trajectories.png)
- Impact-distribution figure: [script_02_lunar_intercept_impacts.png](../results/figures/script_02_lunar_intercept_impacts.png)

---

## 7. Iteration 3 — Multi-Loop Passive Return Boundary

### Goal

Search for resonant passive lunar free-return trajectories that execute exactly three loops around the Moon before returning to Earth.

Sources: [HYPOTHESIS_03.md](../hypotheses/HYPOTHESIS_03.md), [ANALYSIS_03.md](ANALYSIS_03.md), [script_03_multi_loop_return_summary.txt](../results/logs/script_03_multi_loop_return_summary.txt)

### Method

The experiment used a two-stage numerical search. First, a coarse diagnostic sweep tested 861 cases across injection speeds from 10.850 km/s to 11.050 km/s and phase angles from 210.0 degrees to 270.0 degrees. Then, a fine refinement sweep tested 561 cases near the discovered multi-loop basin boundary.

### Key Findings

| Metric | Expected | Observed | Assessment |
|---|---:|---:|---|
| Exactly three passive loops | 3.0 to 4.0 loops | Maximum valid active case near 1.2711 loops | Not supported |
| Best passive multi-loop return | Closest to three loops while returning | 1.2458 loops | Partial success |
| Low Earth return | Below 10,000 km | 0.0 km atmospheric-entry altitude | Success |
| Closest lunar approach | No impact | 468.3 km altitude above lunar surface | Success |
| Time of flight | Long multi-loop transfer | 32.426 days | Success |
| Jacobi drift | Below 1e-6 | 8.62e-10 in best case | Success |

### Interpretation

The original exactly-three-loop hypothesis was not supported. However, the failed target produced a stronger scientific conclusion: purely passive multi-loop free-return trajectories appear constrained by weak-stability-boundary dynamics. The simulations discovered a practical passive boundary near 1.25 to 1.27 loops. Beyond that region, trajectories tend to impact the Moon, escape, or return to Earth in undesirable high-altitude paths.

This is a scientifically useful outcome: the analysis did not force a positive result. It documented where the concept works and where the physics appears to prevent the original expectation.

### Generated Artifacts

- Log: `script_03_multi_loop_return_20260625_122118.log` (not retained)
- Summary table: [script_03_multi_loop_return_summary.txt](../results/logs/script_03_multi_loop_return_summary.txt)
- Trajectory figure: [script_03_multi_loop_return_trajectories.png](../results/figures/script_03_multi_loop_return_trajectories.png)
- Lunar close-up figure: [script_03_multi_loop_return_lunar_closeup.png](../results/figures/script_03_multi_loop_return_lunar_closeup.png)

---

## 8. Cross-Iteration Comparison

| Metric | Iteration 1: Free Return | Iteration 2: Direct Intercept | Iteration 3: Multi-Loop Boundary |
|---|---:|---:|---:|
| Primary outcome | Safe passive Earth return | Lunar surface impact | Long passive return after partial lunar looping |
| Best injection speed | 10.9300 km/s | 10.9700 km/s | 10.97800 km/s |
| Best phase angle | 245.0 degrees | 224.0 degrees | 225.800 degrees |
| Time of flight | About 8.3 days to return | 2.441 days to impact | 32.426 days to return |
| Lunar interaction | Safe flyby | Impact | Temporary weak capture |
| Closest lunar result | 23,938.3 km closest approach | Lunar surface impact | 468.3 km altitude |
| Earth return | 118.0 km perigee altitude | Not applicable | 0.0 km atmospheric-entry altitude |
| Numerical fidelity | 6.32e-10 max Jacobi drift | 1.79e-10 max Jacobi drift | 8.62e-10 best-case Jacobi drift |
| Hypothesis outcome | Supported | Supported | Partially supported; original three-loop target not supported |

### Trend Across the Study

The project moved from a basic free-return proof, to a targeted collision corridor, to a more ambitious resonant weak-capture search. Each step increased the dimensionality and sensitivity of the problem:

1. Iteration 1 established that the free-return corridor exists.
2. Iteration 2 showed that related corridors can target the Moon directly.
3. Iteration 3 exposed the boundary between passive weak capture and chaotic loss.

---

## 9. Key Scientific Conclusions

1. A simplified CR3BP model can reproduce a qualitatively realistic lunar free-return safety corridor.
2. The standard passive free-return is extremely sensitive, with a velocity corridor only about 9 m/s wide in the tested geometry.
3. Launch phase angle is as important as injection speed; a one-dimensional speed sweep is insufficient.
4. Direct lunar-intercept trajectories occupy a nearby but distinct corridor and strongly favor leading-face impacts under low-energy conditions.
5. Passive multi-loop lunar returns are possible only up to a limited loop count in this model; the original three-loop passive return target appears physically blocked without active correction.
6. Jacobi-constant drift stayed far below the specified threshold in all final analyses, increasing confidence that the observed behavior is dynamical rather than numerical.

---

## 10. Human Intellectual Contributions

The human contribution log is recorded in [intellectual_contribution.md](../prompts/intellectual_contribution.md). The most important human-guided turning points were:

| Iteration | Human Contribution | Why It Mattered |
|---|---|---|
| 01 | Recognized that the failed 180 degree launch geometry was a phase-angle problem, not simply a speed problem. | Converted a failed one-dimensional sweep into a successful two-dimensional search and found the 245.0 degree corridor. |
| 02 | Shifted the search bounds after early no-impact failures and reasoned about leading-face lunar impacts. | Found the actual direct-impact corridor and explained why 83 percent of impacts landed on the leading hemisphere. |
| 03 | Lowered the loop threshold during candidate search and reframed the negative result as a physical boundary. | Converted a failed three-loop search into a useful map of the passive multi-loop limit near 1.27 loops. |

This provenance is scientifically important: assumptions were actively tested, failed search regions were not hidden, and the interpretation was redirected when the evidence showed a physical boundary rather than the originally hypothesized three-loop solution.

---

## 11. Reproducibility Manifest

### Scripts

| Script | Purpose |
|---|---|
| [script_01_trajectory_sweep.py](../experiments/01_synthetic/script_01_trajectory_sweep.py) | Standard free-return trajectory sweep. |
| [script_02_lunar_intercept.py](../experiments/01_synthetic/script_02_lunar_intercept.py) | Direct lunar impact corridor search. |
| [script_03_multi_loop_return.py](../experiments/01_synthetic/script_03_multi_loop_return.py) | Multi-loop passive return search and boundary mapping. |
| [search_intercept.py](../experiments/01_synthetic/search_intercept.py) | Exploratory intercept search helper. |
| [fine_intercept_search.py](../experiments/01_synthetic/fine_intercept_search.py) | Fine exploratory intercept search helper. |

### Logs

| Log | Notes |
|---|---|
| `script_01_trajectory_sweep_20260625_095910.log` (not retained) | Final selected Iteration 1 run. |
| `script_02_lunar_intercept_20260625_112846.log` (not retained) | Final selected Iteration 2 run. |
| `script_03_multi_loop_return_20260625_122118.log` (not retained) | Final selected Iteration 3 run. |
| [script_03_multi_loop_return_summary.txt](../results/logs/script_03_multi_loop_return_summary.txt) | Sorted valid multi-loop return trajectories. |

### Figures

| Figure | Notes |
|---|---|
| [script_01_trajectory_sweep_trajectories.png](../results/figures/script_01_trajectory_sweep_trajectories.png) | Free-return trajectory paths. |
| [script_01_trajectory_sweep_metrics.png](../results/figures/script_01_trajectory_sweep_metrics.png) | Free-return sensitivity metrics. |
| [script_02_lunar_intercept_trajectories.png](../results/figures/script_02_lunar_intercept_trajectories.png) | Direct-intercept trajectory paths. |
| [script_02_lunar_intercept_impacts.png](../results/figures/script_02_lunar_intercept_impacts.png) | Lunar impact point distribution. |
| [script_03_multi_loop_return_trajectories.png](../results/figures/script_03_multi_loop_return_trajectories.png) | Multi-loop return trajectories. |
| [script_03_multi_loop_return_lunar_closeup.png](../results/figures/script_03_multi_loop_return_lunar_closeup.png) | Lunar-vicinity close-up of looping behavior. |

### Interpretation Files

| File | Purpose |
|---|---|
| [ANALYSIS_01.md](ANALYSIS_01.md) | Interprets standard free-return discovery. |
| [ANALYSIS_02.md](ANALYSIS_02.md) | Interprets direct lunar intercept mapping. |
| [ANALYSIS_03.md](ANALYSIS_03.md) | Interprets passive multi-loop boundary discovery. |

---

## 12. Limitations and Caveats

1. The model is planar and does not include out-of-plane lunar transfer geometry.
2. The Moon is assumed to move on a circular orbit rather than an ephemeris-based eccentric orbit.
3. The Sun, Earth oblateness, lunar gravity harmonics, solar radiation pressure, and other perturbations are omitted.
4. Injection is modeled as an ideal impulsive burn rather than a finite-duration maneuver.
5. Navigation uncertainty and burn execution errors are not modeled.
6. Atmospheric entry is represented only through Earth-return altitude, not through full entry-interface dynamics.
7. The multi-loop result should be interpreted as a constraint within this simplified CR3BP setup, not as a universal proof that all real multi-loop returns require propulsion.

---

## 13. Recommended Next Steps

1. Upgrade from planar CR3BP to a higher-fidelity ephemeris model using real Moon positions.
2. Add the Sun as a third-body perturbation and measure how the free-return corridor shifts.
3. Add stochastic injection errors and compute the mid-course correction budget needed to preserve safe return.
4. Extend the model to three dimensions and evaluate inclination effects.
5. Model active correction maneuvers near apolune to test whether exactly three-loop returns can be stabilized.
6. Build a paper-style narrative from the selected results and figures. This project was
   created without the Paper capability; enable it with `smairt paper enable .` to
   get a `paper/` workspace and a `FINAL_MANIFEST.md` claim map.

---

## 14. Final Assessment

This investigation establishes a reproducible baseline for passive lunar-return trajectory analysis in the planar Earth-Moon CR3BP.

### Primary Findings

- A narrow standard free-return corridor exists in the tested model.
- A distinct direct lunar-intercept corridor can be mapped by jointly varying injection speed and launch phase angle.
- Purely passive multi-loop returns appear constrained to roughly the 1.25-loop regime under the tested assumptions.

### Research Significance

The work provides both positive trajectory candidates and a clear boundary condition for subsequent higher-fidelity modeling. The standard free-return and direct-intercept cases demonstrate controllable trajectory families, while the multi-loop result identifies where passive dynamics stop supporting the original trajectory objective.

### Methodological Assessment

The strongest methodological result is that the successful findings came from systematically expanding the search space and interpreting failures directly. The free-return corridor was not found by the first obvious geometry, and the three-loop return was not forced into a false success. Both outcomes strengthen the research record by distinguishing robust dynamical behavior from unsupported initial assumptions.
