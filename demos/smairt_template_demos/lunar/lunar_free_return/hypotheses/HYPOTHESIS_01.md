# Hypothesis 01 — Discovery of Free-Return Trajectory Band in CR3BP

## Status: SUPPORTED

## Background

In the Circular Restricted Three-Body Problem (CR3BP) model representing the Earth-Moon system, a free-return trajectory allows a spacecraft injected from a low-Earth parking orbit (LEO) to fly behind the Moon, utilize its gravitational field to turn around, and return directly to LEO perigee without firing any engines after the initial Translunar Injection (TLI) burn. This is the safety principle that Apollo 13 relied upon and that Artemis II will implement. To verify and explore this behavior in a controlled, noise-free numerical environment, we begin with a normalized, non-dimensional synthetic simulation (Phase 1).

## Hypothesis Statement

**Prediction**: 
There is a narrow, highly sensitive band of Translunar Injection (TLI) burn velocities ($v_{tli}$) just below the system's escape velocity for which the spacecraft is injected onto a path that loops behind the Moon and returns to a low-Earth perigee (an altitude less than 10,000 km relative to the Earth's surface, corresponding to the re-entry corridor) with no further maneuvers. 

**Rationale**: 
Below this velocity band, the spacecraft's apogee is too low to reach the Moon's sphere of influence, causing a direct fallback to Earth before a lunar flyby. Above this velocity band, the spacecraft's energy exceeds the escape velocity of the Earth-Moon system, causing it to escape entirely. The free-return trajectory resides at a sharp transition boundary (separatrix) between these two qualitative states.

**Success criteria**:
1. **Low Return Perigee**: Identify at least one TLI velocity that achieves a post-flyby return perigee altitude of $< 10,000\text{ km}$ from the Earth's surface.
2. **Safe Lunar Flyby**: The closest lunar approach distance ($d_{min, moon}$) is greater than the Moon's radius ($1,737.4\text{ km}$), ensuring no collision.
3. **Jacobi Constant Conservation**: The drift in the non-dimensional Jacobi Constant ($C$) is $< 10^{-6}$ over the entire simulation duration, verifying numerical integration accuracy.

## Experimental Design

- **Script**: `experiments/01_synthetic/script_01_trajectory_sweep.py`
- **Phase**: synthetic
- **Track**: Core
- **Data**: Synthetic (pure numerical propagation in normalized Earth-Moon CR3BP rotating frame)
- **Controls**: Baseline cases of lower $v_{tli}$ (resulting in direct fallback) and higher $v_{tli}$ (resulting in escape)
- **Key metrics**:
  - $C$ (Jacobi constant) drift (absolute difference: $|C_{final} - C_{initial}|$)
  - $d_{min, moon}$ (closest lunar approach distance, km)
  - $r_{min, earth}$ (return perigee distance, km, evaluated after lunar flyby)
  - $r_{max, earth}$ (maximum geocentric distance, km)

## Dependencies

- None (pure Python standard library plus NumPy/SciPy for numerical solver and plotting)
- Shared library: `scripts/shared/logging.py` (TeeLogger)

## Results

The hypothesis was **fully supported** by the Phase 1 numerical sweep over 301 TLI injection speeds.

- **Corridor Boundaries**: A narrow free-return corridor was discovered between **$10.9270\text{ km/s}$** and **$10.9360\text{ km/s}$**.
- **Best Return Case**: At a TLI speed of **$10.9300\text{ km/s}$**, the return perigee altitude is **$118.0\text{ km}$** (within the $100\text{ km}$ Earth re-entry corridor).
- **Lunar Flyby Distance**: At this nominal speed, the closest approach to the lunar surface is **$23,938.3\text{ km}$** (safely above the Moon's radius of $1,737.4\text{ km}$).
- **Energy Conservation**: Jacobi Constant drift was exceptionally low, with a maximum drift of **$6.32 \times 10^{-10}$** across all simulation runs, well below the success threshold of $10^{-6}$.

See [`analysis/ANALYSIS_01.md`](smairt_template_demos/lunar/lunar_free_return/analysis/ANALYSIS_01.md) for full interpretation.

## Notes

- Physical scales for conversion:
  - Earth-Moon distance: $D = 384,400\text{ km}$
  - Earth radius: $R_E = 6,371\text{ km}$
  - Moon radius: $R_M = 1,737.4\text{ km}$
  - Mass ratio: $\mu = 0.012150585609624$
- The return perigee must be evaluated *after* the spacecraft passes behind the Moon (crossing the $x = 1 - \mu$ plane or exiting the lunar vicinity).
