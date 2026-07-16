# Hypothesis 03 — Multi-Loop (3-Revolution) Resonant Lunar Free-Return Orbits

## Status: PENDING

## Background

In Iteration 1, we successfully discovered and mapped the single flyby circumlunar free-return trajectory corridor ($\approx 10.9300\text{ km/s}$, $\phi = 245.0^\circ$). In Iteration 2, we mapped the low-energy direct lunar intercept corridor ($10.920 \text{ to } 10.970\text{ km/s}$, $\phi \in [224^\circ, 238^\circ]$). 

In this iteration, we push the boundaries of multi-body orbital mechanics within the Circular Restricted Three-Body Problem (CR3BP) by searching for **multi-loop (multi-revolution) lunar free-return trajectories**. We seek a highly discrete, resonant orbit that enters the Moon's vicinity, executes exactly 3 distinct loops around the Moon, and is then slung back on a free-return path to a low-Earth perigee ($< 10,000\text{ km}$) without any maneuvers.

## Hypothesis Statement

**Prediction**:
There exist highly discrete, resonant, non-collision orbits within the Earth-Moon CR3BP where a spacecraft injected from LEO can complete exactly 3 revolutions (loops) around the Moon (accumulating $\ge 6\pi$ radians of selenocentric angular displacement) before returning directly to a low-Earth perigee altitude of $< 10,000\text{ km}$ with no post-TLI maneuvers. These orbits reside in highly sensitive, chaotic regions near the $L_1$ and $L_2$ libration points, acting as temporary/transient captures before returning.

**Rationale**:
By leveraging three-body dynamics (specifically the stable and unstable manifolds of the $L_1$ or $L_2$ Lagrange points), a spacecraft can be captured temporarily in the Moon's vicinity. In a rotating frame, the gravitational forces of the Earth and Moon balance with centrifugal and Coriolis terms to allow temporary orbits around the secondary mass. If the spacecraft's energy and launch phase angle are precisely targeted, it will execute exactly 3 revolutions around the Moon before its unstable manifold kicks it out on a trajectory that routes it back into a grazing Earth re-entry.

**Success criteria**:
1. **Exactly 3 Loops**: The trajectory completes exactly 3 complete, non-colliding revolutions around the Moon. This is defined as a total accumulated angular displacement ($\theta_{\text{selene}}$) of at least $6\pi$ radians ($1080^\circ$) around the Moon's center while inside the Moon's region of influence ($d_{\text{moon}} < 0.15$ ND units $\approx 57,600\text{ km}$), terminating with the spacecraft successfully exiting the lunar vicinity.
2. **Safe Flight**: The closest approach to the Moon's surface is greater than the Moon's radius ($1,737.4\text{ km}$), and the closest approach to Earth's surface during the looping phase is greater than the Earth's radius ($6,371\text{ km}$), ensuring no premature collision.
3. **Low Earth Return**: The post-flyby return perigee altitude back at Earth is $< 10,000\text{ km}$ (the target re-entry corridor).
4. **Jacobi Constant Conservation**: The drift in the non-dimensional Jacobi Constant ($C$) is $< 10^{-6}$ over the entire simulation duration (which will be significantly longer than Iterations 1 and 2, likely 15–25 days).

## Experimental Design

- **Script**: `experiments/01_synthetic/script_03_multi_loop_return.py`
- **Phase**: synthetic
- **Track**: Core
- **Data**: Synthetic (pure numerical propagation in normalized Earth-Moon CR3BP rotating frame)
- **Controls**: Trajectories that result in single-loop flybys, direct impacts, or immediate escapes
- **Key metrics**:
  - $C$ (Jacobi constant) drift (absolute difference: $|C_{\text{final}} - C_{\text{initial}}|$)
  - $N_{\text{loops}}$ (number of complete revolutions around the Moon, tracked via cumulative angular sweep)
  - $d_{\text{min,moon}}$ (closest lunar approach distance, km)
  - $r_{\text{min,earth}}$ (return perigee altitude after exiting the Moon's vicinity, km)
  - Time-of-flight from TLI to Earth return (days)

## Dependencies

- Phase 1 baseline constants and CR3BP equations of motion.
- Programmatic tracking of cumulative selenocentric angle:
  $\theta(t) = \int \frac{x_{\text{rel}} v_{y,\text{rel}} - y_{\text{rel}} v_{x,\text{rel}}}{r^2} dt$ to accurately count loops.

## Results

*(Filled in after experiment runs — see analysis/ANALYSIS_03.md for full interpretation)*

## Notes

- The Moon sits at $(x, y) = (1 - \mu, 0)$.
- Selenocentric state: $x_{\text{rel}} = x - (1-\mu)$, $y_{\text{rel}} = y$, $v_{x,\text{rel}} = v_x + y$ (accounting for rotating frame velocity), $v_{y,\text{rel}} = v_y - x_{\text{rel}}$ (or simply $v_x, v_y$ in rotating coordinates as the Moon is fixed).
- The accumulated angle is calculated as $\theta_{\text{selene}} = \sum |\Delta \phi_i|$ where $\phi_i = \arctan2(y_{\text{rel},i}, x_{\text{rel},i})$.
