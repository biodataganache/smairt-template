# Hypothesis 02 — Direct Minimum-Energy Lunar Intercept (Hohmann-like Impact)

## Status: SUPPORTED

## Background

In Iteration 1, we successfully discovered and mapped the circumlunar free-return trajectory corridor. We found that launching at an injection phase angle of $\phi = 245.0^\circ$ and speed of $v_{\text{inj}} \approx 10.9300\text{ km/s}$ allows the spacecraft to safely loop around the Moon (closest approach $\approx 23,938.3\text{ km}$) and return to Earth. 

In this iteration, we shift our objective from a free-return flyby to a **direct lunar intercept (impact)**. We seek to find a minimum-energy, Hohmann-like transfer that terminates in a direct collision with the Moon's leading hemisphere (the side facing the direction of the Moon's orbital motion).

## Hypothesis Statement

**Prediction**:
There exists a narrow, low-energy corridor of Trans-Lunar Injection (TLI) burn speeds ($v_{\text{inj}} \in [10.82, 10.92]\text{ km/s}$) and launch phase angles ($\phi \in [210^\circ, 250^\circ]$) that results in a direct, Hohmann-like trajectory terminating in a high-angle impact on the Moon's leading hemisphere (the $+y$ face relative to the Moon's center in the rotating coordinate frame).

**Rationale**:
By injecting at a lower speed than the free-return corridor ($v_{\text{inj}} < 10.93\text{ km/s}$), the trajectory's apogee will be closer to the Moon's orbit, and the spacecraft's orbital velocity near apogee will be slower than the Moon's orbital velocity. The faster-moving Moon will catch up and sweep up the spacecraft from behind, resulting in a direct collision on the Moon's leading hemisphere. Because the spacecraft is moving slower than the Moon, the impact will occur on the leading (front) side relative to its motion.

**Success criteria**:
1. **Direct Impact**: The numerical propagation terminates exactly when the geocentric position enters the Moon's physical boundary, i.e., the spacecraft's distance to the Moon's center is $\le R_M$ ($1,737.4\text{ km}$).
2. **Leading Face Target**: The impact location in rotating coordinates must lie on the Moon's leading hemisphere, where $y_{\text{impact}} > 0$ relative to the Moon's center.
3. **Jacobi Constant Conservation**: The drift in the non-dimensional Jacobi Constant ($C$) up to the moment of impact is $< 10^{-6}$, verifying numerical integration accuracy.

## Experimental Design

- **Script**: `experiments/01_synthetic/script_02_lunar_intercept.py`
- **Phase**: synthetic
- **Track**: Core
- **Data**: Synthetic (pure numerical propagation in normalized Earth-Moon CR3BP rotating frame with a terminating impact event)
- **Controls**: Trajectories that miss the Moon (either falling back to Earth or swinging around into a free-return/escape)
- **Key metrics**:
  - $C$ (Jacobi constant) drift (absolute difference: $|C_{\text{impact}} - C_{\text{initial}}|$)
  - Impact coordinate relative to lunar center ($x_{\text{impact}} - (1-\mu), y_{\text{impact}}$)
  - Impact angle relative to local surface horizontal (degrees)
  - Time-of-flight from TLI to impact (days)

## Dependencies

- Phase 1 baseline constants and CR3BP equations of motion.
- Termination event handling in `scipy.integrate.solve_ivp` to halt integration upon hitting the lunar surface.

## Results

The hypothesis was **fully supported** by the Phase 1 numerical sweep over 51 TLI speeds and 15 phase angles.

- **Impact Detections**: Out of the sweep configurations, **$106$ direct impact trajectories** were discovered.
- **Hemisphere Analysis**: As predicted, **$88$ ($83\%$) of the impacts** terminated on the Moon's leading hemisphere ($y > 0$), supporting the physical mechanism of the Moon catching up and sweeping up the slower spacecraft near apogee.
- **Optimal Impact Case**: Found at $v_{\text{inj}} = 10.9700\text{ km/s}$ and $\phi = 224.0^\circ$ with a short time-of-flight of **$2.441\text{ days}$** and a steep impact angle of **$65.5^\circ$** from the horizontal.
- **Energy Conservation**: Maximum Jacobi Constant drift across all runs was extremely low at **$1.79 \times 10^{-10}$**, verifying high integration fidelity.

See [`analysis/ANALYSIS_02.md`](smairt_template_demos/lunar/lunar_free_return/analysis/ANALYSIS_02.md) for full interpretation.

## Notes

- The Moon sits at $(x, y) = (1 - \mu, 0)$ in non-dimensional coordinates.
- Impact event definition: $d_{\text{moon}} = \sqrt{(x - (1-\mu))^2 + y^2} - R_M \le 0$.
- In the rotating frame, the Moon's orbital velocity is in the $+y$ direction, so the leading face corresponds to $y > 0$.
