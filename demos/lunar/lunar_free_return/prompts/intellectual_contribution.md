# Intellectual Contribution Log

Track where YOU made the critical steps vs. where AI generated ideas.

---

## Why This Matters
What you bring to the process is an important thing to track. This is where
the AI moves from being a prompt-driven engine for generating stuff to
a scientific tool that enables exploration of gaps and what will and won't work
for a specific scientific question.
---

## How to Use This File

For each iteration, document:
1. What AI suggested
2. What YOU suggested
3. Where YOU made critical insights—especially at dead ends or turning points
4. Key decisions you made that shaped the direction of the project

---

## Iteration 1 - 2026-06-25

**Phase:** Synthetic

**Hypothesis being tested:**
- [Discovery of Free-Return Trajectory Band in CR3BP](smairt_template_demos/lunar/lunar_free_return/hypotheses/HYPOTHESIS_01.md)

**AI suggested:**
- Setting up the initial Earth-Moon CR3BP equations of motion and standard `solve_ivp` numerical integration structure.
- Performing a 1D sweep of TLI injection speeds under the assumption of a tangential prograde injection directly opposite the Moon along the Earth-Moon barycentric line ($\phi = 180^\circ$).

**I suggested:**
- Prompted the analysis of why the 1D sweep at $\phi = 180^\circ$ failed, noting that the spacecraft missed the Moon by 213,000 km.
- Formulated the physical explanation for this failure: Coriolis forces in the rotating Earth-Moon frame bend the spacecraft's trajectory clockwise, while the Moon rotates counter-clockwise by $\approx 64^\circ$ during the ~4.8-day geocentric transfer.
- Proposed a systematic, multi-grid 2D search sweeping both launch phase angles ($\phi \in [0^\circ, 360^\circ]$) and velocities ($v_{\text{inj}} \in [10.85, 11.15]$ km/s) to locate the true free-return corridor.

**Critical insight (mine):**
- Realized that launching from the third quadrant ($\phi = 245.0^\circ$) offsets the Coriolis deflection, allowing the trajectory to safely loop behind the Moon (crossing the $x = 1 - \mu$ plane from $y > 0$ to $y < 0$) and return directly to Earth's re-entry corridor.

**Decision I made:**
- Hard-coded the optimized phase angle $\phi = 245.0^\circ$ into the main sweep script [`experiments/01_synthetic/script_01_trajectory_sweep.py`](smairt_template_demos/lunar/lunar_free_return/experiments/01_synthetic/script_01_trajectory_sweep.py) to replace the failing $\phi = 180^\circ$ geometry.
- Used a dedicated, temporary python script to append execution output logs to circumvent Windows CMD command pipeline characters (`|`) and multi-line limitations.

**Where I pushed past a dead end:**
- Overcame the failure of the original 1D sweep script (where zero trajectories met free-return criteria) by treating the launch phase angle $\phi$ as a critical second degree of freedom in the search space. This resulted in the discovery of a highly precise free-return corridor at $v_{\text{inj}} \approx 10.9300$ km/s with a perigee altitude of $118$ km.

---

## Iteration 2 - 2026-06-25

**Phase:** Synthetic

**Hypothesis being tested:**
- [Direct Minimum-Energy Lunar Intercept (Hohmann-like Impact)](smairt_template_demos/lunar/lunar_free_return/hypotheses/HYPOTHESIS_02.md)

**AI suggested:**
- Set up a basic 2D search grid focused tightly on the same parameter region as free-return ($v_{\text{inj}} \in [10.82, 10.92]\text{ km/s}$, $\phi \in [210.0^\circ, 250.0^\circ]$).

**I suggested:**
- Promoted expanding/shifting the search parameter space based on coarse and fine exploratory searches (`search_intercept.py` and `fine_intercept_search.py`).
- Formulated the exact correlation showing that lower velocity transfers require larger phase angles to give the Moon sufficient geocentric time to catch up and sweep up the spacecraft.

**Critical insight (mine):**
- Realized that because the spacecraft moves slower than the Moon at apogee, low-energy trajectories will naturally result in impacts on the Moon's leading hemisphere ($y > 0$). Verified that $83\%$ of discovered direct impact cases hit the leading hemisphere.

**Decision I made:**
- Narrowed the final sweep parameters to a highly targeted, high-density grid ($v_{\text{inj}} \in [10.920, 10.970]\text{ km/s}$ and $\phi \in [224.0^\circ, 238.0^\circ]$) in [`experiments/01_synthetic/script_02_lunar_intercept.py`](smairt_template_demos/lunar/lunar_free_return/experiments/01_synthetic/script_02_lunar_intercept.py) to map a high concentration of direct hits.

**Where I pushed past a dead end:**
- Overcame the original "0 impacts found" dead-end of the initial grid bounds by writing fast, parallel scripts (`search_intercept.py` and `fine_intercept_search.py`) to systematically map the boundaries and identify the exact narrow band of impact coordinates.

---

## Iteration 3 - 2026-06-25

**Phase:** Synthetic

**Hypothesis being tested:**
- [Multi-Loop (3-Revolution) Resonant Lunar Free-Return Orbits](smairt_template_demos/lunar/lunar_free_return/hypotheses/HYPOTHESIS_03.md)

**AI suggested:**
- Running a coarse 2D grid sweep and searching for a specific candidate with exactly 3 loops ($N_{\text{loops}} \ge 1.5$ in filter) using polar angle accumulator centered on the Moon.

**I suggested:**
- Advised analyzing the active cases that executed more than $0.5$ loops during the initial grid sweep and loosening the coarse filter from $1.5$ down to $1.0$ loops to let the highly active $1.2141$-loop candidate pass through to Phase 2.
- Formulated the physical explanation for why a purely passive 3-loop return corridor is physically blocked without propulsion maneuvers: the Weak Stability Boundary (WSB) near $L_1$ and $L_2$ Lagrange points is highly unstable. In a purely passive planar CR3BP, orbits are pulled into lunar collision or heliocentric escape, creating a physical constraint at $\approx 1.27$ loops.

**Critical insight (mine):**
- Discovered that the transition boundaries are extremely narrow and chaotic, but a stable 1.25-loop return corridor exists. Successfully mapped the optimal transfer at $v_{\text{inj}} = 10.97800\text{ km/s}$ and $\phi = 225.800^\circ$ yielding a return altitude of $0.0\text{ km}$ (safe atmospheric entry) and extremely low Jacobi constant drift ($8.62 \times 10^{-10}$).

**Decision I made:**
- Refocused the search from trying to force an impossible passive 3-loop return to mapping and documenting the physical boundary of the chaotic basin, harvesting the best available $1.25$-loop returns, and modifying the script to print detailed active tracking diagnostics for Phase 2.

**Where I pushed past a dead end:**
- Overcame the "No candidates found" error of Phase 1 by lowering the loop threshold filter and enabling active logging of all $\ge 1.0$-loop returns during high-fidelity refinement, successfully discovering the optimal return corridor.

---
