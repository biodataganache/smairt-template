#!/usr/bin/env python3
"""
Script 01: Parameter Sweep over TLI Burn Velocities to Discover Free-Return Trajectories

Hypothesis: HYPOTHESIS_01.md
Phase: synthetic
Track: Core
Iteration: 1

Depends on:
  - None (this is the initial synthetic baseline)
"""

import sys
from pathlib import Path
from datetime import datetime
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# === PATH SETUP ===
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

# === PHYSICAL CONSTANTS & CONVERSIONS ===
D = 384400.0          # Earth-Moon distance (km)
R_E = 6371.0          # Earth radius (km)
R_M = 1737.4          # Moon radius (km)

# Gravitational parameters (km^3 / s^2)
GM_EARTH = 398600.44
GM_MOON = 4902.80
GM_TOTAL = GM_EARTH + GM_MOON

# Non-dimensional system parameters (CR3BP)
MU = GM_MOON / GM_TOTAL  # Mass ratio (~0.0121505856)

# Scaling factors
L_UNIT = D                      # length unit (km)
V_UNIT = np.sqrt(GM_TOTAL / D)  # velocity unit (km/s) ~ 1.02445 km/s
T_UNIT = np.sqrt(D**3 / GM_TOTAL) # time unit (seconds) ~ 4.34 days

# Non-dimensional radii
R_E_ND = R_E / L_UNIT
R_M_ND = R_M / L_UNIT

# Low Earth Orbit (LEO) parameters
LEO_ALTITUDE = 200.0            # km
R_PARK = (R_E + LEO_ALTITUDE) / L_UNIT  # Non-dimensional radius of circular parking orbit

# === CONFIGURATION ===
SCRIPT_NAME = "script_01_trajectory_sweep"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
FIG_DIR = PROJECT_ROOT / "results" / "figures"

# === CR3BP EQUATIONS OF MOTION ===
def cr3bp_equations(t, state, mu):
    """
    State vector: [x, y, vx, vy]
    """
    x, y, vx, vy = state
    
    # Distances to primaries
    r1 = np.sqrt((x + mu)**2 + y**2)
    r2 = np.sqrt((x - 1.0 + mu)**2 + y**2)
    
    # Guard against collision/singularity division by zero
    r1 = max(r1, 1e-6)
    r2 = max(r2, 1e-6)
    
    # Gravitational accelerations
    ax_g = -(1.0 - mu) * (x + mu) / r1**3 - mu * (x - 1.0 + mu) / r2**3
    ay_g = -(1.0 - mu) * y / r1**3 - mu * y / r2**3
    
    # Equations of motion including Coriolis and centrifugal terms
    ax = 2.0 * vy + x + ax_g
    ay = -2.0 * vx + y + ay_g
    
    return [vx, vy, ax, ay]

def get_jacobi_constant(state, mu):
    """
    Compute the Jacobi Constant C for a given state.
    C = x^2 + y^2 + 2*(1-mu)/r1 + 2*mu/r2 - (vx^2 + vy^2)
    """
    x, y, vx, vy = state
    r1 = np.sqrt((x + mu)**2 + y**2)
    r2 = np.sqrt((x - 1.0 + mu)**2 + y**2)
    
    potential = 0.5 * (x**2 + y**2) + (1.0 - mu) / r1 + mu / r2
    kinetic = 0.5 * (vx**2 + vy**2)
    
    return 2.0 * potential - 2.0 * kinetic

# === INTEGRATION TERMINATION EVENTS ===
def earth_collision_event(t, state, mu):
    r1 = np.sqrt((state[0] + mu)**2 + state[1]**2)
    return r1 - R_E_ND
earth_collision_event.terminal = True
earth_collision_event.direction = -1

def moon_collision_event(t, state, mu):
    r2 = np.sqrt((state[0] - 1.0 + mu)**2 + state[1]**2)
    return r2 - R_M_ND
moon_collision_event.terminal = True
moon_collision_event.direction = -1

def escape_event(t, state, mu):
    r1 = np.sqrt((state[0] + mu)**2 + state[1]**2)
    return r1 - 1.5  # Escape if geocentric distance exceeds 1.5 units (~576,000 km)
escape_event.terminal = True
escape_event.direction = 1

# === MAIN SIMULATION ===
def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    
    with TeeLogger(log_path):
        print("="*60)
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("Hypothesis: Discovering the free-return trajectory band in the Earth-Moon CR3BP")
        print("="*60)
        print()
        
        print("System Parameters:")
        print(f"  Earth GM: {GM_EARTH:.2f} km^3/s^2")
        print(f"  Moon GM: {GM_MOON:.2f} km^3/s^2")
        print(f"  Earth-Moon Distance: {D:.1f} km")
        print(f"  Mass ratio mu: {MU:.10f}")
        print(f"  LEO Parking Altitude: {LEO_ALTITUDE:.1f} km")
        print(f"  LEO Radius in ND units: {R_PARK:.6f} ({R_PARK*D:.2f} km)")
        print(f"  Non-dimensional Velocity Unit: {V_UNIT:.6f} km/s")
        print(f"  Non-dimensional Time Unit: {T_UNIT / 86400.0:.4f} days")
        print()
        
        # 1. Establish the LEO speed
        # Inertial circular orbit speed around Earth: V = sqrt(GM_Earth / R_LEO)
        v_circ_inertial_nd = np.sqrt((1.0 - MU) / R_PARK)
        # Convert to rotating coordinates: v_rot = v_inertial - omega * r_park, with omega = 1
        v_circ_rot_nd = v_circ_inertial_nd - R_PARK
        
        print(f"Circular Parking Orbit Baseline (LEO):")
        print(f"  Inertial Circular Speed: {v_circ_inertial_nd * V_UNIT:.4f} km/s (ND: {v_circ_inertial_nd:.6f})")
        print(f"  Rotating Circular Speed: {v_circ_rot_nd * V_UNIT:.4f} km/s (ND: {v_circ_rot_nd:.6f})")
        print()
        
        # 2. Define the parameter sweep for physical TLI burn velocity (km/s)
        # Sweeping from 10.85 km/s to 11.15 km/s to capture fallback, free-return, and escape
        v_inj_sweep = np.linspace(10.85, 11.15, 301)  # Physical TLI injection speed in km/s
        
        results = []
        trajectories = {}
        
        print(f"Running sweep over {len(v_inj_sweep)} TLI injection speeds from {v_inj_sweep[0]:.3f} to {v_inj_sweep[-1]:.3f} km/s...")
        
        # We will save representative trajectories for plotting
        plot_speeds = [10.88, 10.92, 10.95, 11.02, 11.10]
        
        for v_inj in v_inj_sweep:
            # Convert physical injection speed to non-dimensional inertial speed
            v_inj_nd = v_inj / V_UNIT
            # Convert to rotating frame velocity magnitude
            v_rot_nd = v_inj_nd - R_PARK
            
            # Initial state: spacecraft on opposite side of Earth from Moon (x < 0)
            # Position: x = -mu - r_park, y = 0
            # Velocity: vx = 0, vy = -v_rot_nd (negative y-direction for prograde orbit)
            phi_deg = 245.0
            phi = np.radians(phi_deg)
            x0 = -MU + R_PARK * np.cos(phi)
            y0 = R_PARK * np.sin(phi)
            vx0 = -(v_inj_nd - R_PARK) * np.sin(phi)
            vy0 = (v_inj_nd - R_PARK) * np.cos(phi)
            
            initial_state = [x0, y0, vx0, vy0]
            C_initial = get_jacobi_constant(initial_state, MU)
            
            # Integrate up to t = 2.5 non-dimensional units (~10.8 days)
            t_span = (0, 2.5)
            t_eval = np.linspace(0, 2.5, 5000)
            
            sol = solve_ivp(
                fun=cr3bp_equations,
                t_span=t_span,
                y0=initial_state,
                args=(MU,),
                t_eval=t_eval,
                method='DOP853',
                rtol=1e-12,
                atol=1e-12,
                events=(earth_collision_event, moon_collision_event, escape_event)
            )
            
            # Analyze the completed trajectory
            times = sol.t
            states = sol.y # state coordinates shape (4, N)
            xs, ys = states[0], states[1]
            vxs, vys = states[2], states[3]
            
            # Check for termination reasons
            outcome = "completed"
            if sol.status == 1: # An event terminated integration
                # Determine which event triggered
                if len(sol.t_events[0]) > 0:
                    outcome = "earth_collision"
                elif len(sol.t_events[1]) > 0:
                    outcome = "moon_collision"
                elif len(sol.t_events[2]) > 0:
                    outcome = "escape"
            
            # Compute geocentric and selenocentric distances along path
            r1s = np.sqrt((xs + MU)**2 + ys**2)
            r2s = np.sqrt((xs - 1.0 + MU)**2 + ys**2)
            
            # Jacobi constant along the path
            Cs = [get_jacobi_constant(states[:, i], MU) for i in range(len(times))]
            C_drift = np.max(np.abs(Cs - C_initial))
            
            # Minimum distance to Moon (selocentric approach)
            d_min_moon_nd = np.min(r2s)
            d_min_moon_km = d_min_moon_nd * D
            idx_closest_moon = np.argmin(r2s)
            t_closest_moon = times[idx_closest_moon]
            
            # Did we perform a lunar flyby?
            # Let's define it as entering the Moon's sphere of influence or passing the Moon on the far side
            # Moon is at x = 1 - mu = 0.98785. A classic free-return loops behind the Moon (x > 1 - mu).
            passed_behind_moon = np.any(xs > (1.0 - MU))
            
            # Return perigee is the minimum geocentric distance reached AFTER the closest lunar approach
            if idx_closest_moon < len(times) - 10:
                post_flyby_r1s = r1s[idx_closest_moon:]
                r_min_earth_nd = np.min(post_flyby_r1s)
                r_min_earth_km = r_min_earth_nd * D
                return_alt_km = r_min_earth_km - R_E
            else:
                r_min_earth_km = np.nan
                return_alt_km = np.nan
                
            max_earth_dist_km = np.max(r1s) * D
            
            # Store results
            result_entry = {
                "v_inj": v_inj,
                "outcome": outcome,
                "C_initial": C_initial,
                "C_drift": C_drift,
                "d_min_moon": d_min_moon_km,
                "passed_behind_moon": passed_behind_moon,
                "return_alt": return_alt_km,
                "max_earth_dist": max_earth_dist_km,
                "t_flight": times[-1] * T_UNIT / 86400.0  # days
            }
            results.append(result_entry)
            
            # Store full trajectory for selected speeds for visualization
            for plot_speed in plot_speeds:
                if np.abs(v_inj - plot_speed) < 1e-4:
                    trajectories[plot_speed] = {
                        "x": xs, "y": ys, "r1": r1s, "r2": r2s, "outcome": outcome, "return_alt": return_alt_km, "passed_behind_moon": passed_behind_moon
                    }
        
        # 3. Print Summary Table of Representative Cases
        print("\nTrajectory Sweep Results Summary (sampled speeds):")
        print(f"{'V_inj (km/s)':<12} | {'Outcome':<15} | {'Min Selene (km)':<15} | {'Pass Behind?':<12} | {'Return Alt (km)':<15} | {'C Drift':<10}")
        print("-" * 92)
        
        # Print a selection of rows from the sweep to show the transition
        indices_to_show = np.linspace(0, len(results) - 1, 15, dtype=int)
        for idx in indices_to_show:
            r = results[idx]
            ret_alt_str = f"{r['return_alt']:.1f}" if not np.isnan(r['return_alt']) else "N/A"
            print(f"{r['v_inj']:12.4f} | {r['outcome']:15} | {r['d_min_moon']:15.1f} | {str(r['passed_behind_moon']):12} | {ret_alt_str:>15} | {r['C_drift']:.1e}")
        
        # 4. Search for the "Free-Return Corridor"
        print("\nSearching for Free-Return Corridor:")
        valid_returns = [
            r for r in results 
            if r['outcome'] in ["completed", "earth_collision"]
            and r['passed_behind_moon'] 
            and r['d_min_moon'] > R_M  # Did not crash into Moon
            and not np.isnan(r['return_alt'])
        ]
        
        if len(valid_returns) == 0:
            print("  [WARNING] No trajectories met the strict free-return criteria in this sweep!")
        else:
            print(f"  Found {len(valid_returns)} trajectories that flyby the Moon and return to Earth.")
            
            # Successful free-returns that do not crash into Earth's surface but pass close
            # Let's say return altitude is between 0 and 10,000 km
            successful_free_returns = [
                r for r in valid_returns 
                if 0.0 <= r['return_alt'] <= 10000.0
            ]
            
            # Let's also look at direct re-entries (altitude < 0, meaning they hit Earth)
            reentry_free_returns = [
                r for r in valid_returns 
                if r['return_alt'] < 0.0
            ]
            
            if len(successful_free_returns) > 0:
                print(f"\n  Successful Free-Return Corridor (Return Altitude 0 to 10,000 km):")
                print(f"    TLI Speed Range: {successful_free_returns[0]['v_inj']:.4f} to {successful_free_returns[-1]['v_inj']:.4f} km/s")
                best_ret = min(successful_free_returns, key=lambda x: x['return_alt'])
                print(f"    Best altitude return: TLI speed = {best_ret['v_inj']:.4f} km/s, Return Altitude = {best_ret['return_alt']:.1f} km, closest lunar approach = {best_ret['d_min_moon']:.1f} km")
            else:
                print("\n  No successful non-collision returns (altitude 0 to 10,000 km) found.")
                
            if len(reentry_free_returns) > 0:
                print(f"  Earth Re-entry/Impact Corridor (Return Altitude < 0 km):")
                print(f"    TLI Speed Range: {reentry_free_returns[0]['v_inj']:.4f} to {reentry_free_returns[-1]['v_inj']:.4f} km/s")
                best_reentry = max(reentry_free_returns, key=lambda x: x['return_alt'])  # Closest to 0 km (grazing impact)
                print(f"    Best grazing re-entry: TLI speed = {best_reentry['v_inj']:.4f} km/s, Return Altitude = {best_reentry['return_alt']:.1f} km (under Earth's surface), closest lunar approach = {best_reentry['d_min_moon']:.1f} km")
                
        # 5. Generate Figures
        print("\nGenerating figures...")
        
        # Plot 1: Trajectories in Rotating Frame
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111)
        
        # Plot Earth and Moon
        earth_circle = plt.Circle((-MU, 0), R_E_ND, color='blue', alpha=0.3, label='Earth')
        moon_circle = plt.Circle((1.0 - MU, 0), R_M_ND, color='gray', alpha=0.6, label='Moon')
        ax.add_patch(earth_circle)
        ax.add_patch(moon_circle)
        
        # Plot orbits/trajectories
        for speed, traj in trajectories.items():
            outcome_label = traj['outcome']
            if outcome_label == "completed" and traj['passed_behind_moon']:
                if traj['return_alt'] < 0:
                    label = f"TLI {speed:.2f} km/s (Re-entry)"
                    color = "orange"
                else:
                    label = f"TLI {speed:.2f} km/s (Free-Return: Alt {traj['return_alt']:.0f} km)"
                    color = "green"
            elif outcome_label == "earth_collision":
                label = f"TLI {speed:.2f} km/s (Earth Collision)"
                color = "red"
            elif outcome_label == "moon_collision":
                label = f"TLI {speed:.2f} km/s (Moon Collision)"
                color = "purple"
            else: # escape
                label = f"TLI {speed:.2f} km/s (Escape)"
                color = "blue"
                
            ax.plot(traj['x'], traj['y'], label=label, color=color, linewidth=1.5)
            
        # Draw Moon orbit (radius = 1)
        theta = np.linspace(0, 2*np.pi, 200)
        ax.plot(np.cos(theta) - MU, np.sin(theta), 'k--', alpha=0.2, label='Moon Orbit')
        
        ax.set_xlabel('Rotating X (non-dimensional)')
        ax.set_ylabel('Rotating Y (non-dimensional)')
        ax.set_title('TLI Trajectories in Earth-Moon Rotating Frame (CR3BP)')
        ax.set_xlim(-0.2, 1.2)
        ax.set_ylim(-0.6, 0.6)
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend(loc='upper right')
        ax.set_aspect('equal')
        
        plt.tight_layout()
        plot_path_1 = FIG_DIR / f"{SCRIPT_NAME}_trajectories.png"
        plt.savefig(plot_path_1, dpi=300)
        plt.close()
        print(f"  Saved rotating frame trajectories plot to {plot_path_1}")
        
        # Plot 2: Return Altitude vs TLI Speed
        v_sweeps = [r['v_inj'] for r in results]
        outcomes = [r['outcome'] for r in results]
        return_alts = [r['return_alt'] for r in results]
        lunar_approaches = [r['d_min_moon'] for r in results]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), sharex=True)
        
        # Plot return altitude
        ax1.plot(v_sweeps, return_alts, 'g-', linewidth=2, label='Post-Flyby Return Altitude')
        ax1.axhline(0, color='r', linestyle='--', alpha=0.5, label='Earth Surface')
        ax1.axhline(10000, color='gray', linestyle=':', alpha=0.5, label='Upper Return Corridor Limit')
        ax1.set_ylabel('Return Altitude (km)')
        ax1.set_title('Post-Flyby Return Altitude and Selenocentric Distance vs. TLI Injection Velocity')
        ax1.grid(True, linestyle=':', alpha=0.6)
        ax1.legend(loc='upper left')
        
        # Plot closest lunar approach
        ax2.plot(v_sweeps, lunar_approaches, 'b-', linewidth=2, label='Closest Lunar Approach')
        ax2.axhline(R_M, color='purple', linestyle='--', alpha=0.5, label='Moon Surface')
        ax2.set_xlabel('TLI Injection Velocity (km/s)')
        ax2.set_ylabel('Closest Selene Distance (km)')
        ax2.grid(True, linestyle=':', alpha=0.6)
        ax2.legend(loc='upper left')
        
        plt.tight_layout()
        plot_path_2 = FIG_DIR / f"{SCRIPT_NAME}_metrics.png"
        plt.savefig(plot_path_2, dpi=300)
        plt.close()
        print(f"  Saved metrics sweep plot to {plot_path_2}")
        
        # Validate Jacobi constant conservation
        max_drift = max([r['C_drift'] for r in results])
        print(f"\nIntegration Quality Check:")
        print(f"  Maximum Jacobi constant drift across all runs: {max_drift:.2e}")
        assert max_drift < 1e-6, f"Integration drift {max_drift:.2e} is unacceptably high!"
        print("  Conservation check passed! The numerical integration is highly reliable.")
        print()
        
        print("="*60)
        print("=== COMPLETE ===")
        print("="*60)

if __name__ == "__main__":
    main()


# The pasted run output that used to live here has been removed. Results belong in
# results/logs/, which the logging helpers write automatically, and the interpretation
# belongs in analysis/. A transcript copied into the script it describes goes stale the
# first time the script changes, and its Windows paths made this file emit a syntax
# warning on every parse.
r"""
=== RUN OUTPUT ===
============================================================
Script: script_01_trajectory_sweep
Timestamp: 2026-06-25T09:59:10.490031
Hypothesis: Discovering the free-return trajectory band in the Earth-Moon CR3BP
============================================================

System Parameters:
  Earth GM: 398600.44 km^3/s^2
  Moon GM: 4902.80 km^3/s^2
  Earth-Moon Distance: 384400.0 km
  Mass ratio mu: 0.0121505840
  LEO Parking Altitude: 200.0 km
  LEO Radius in ND units: 0.017094 (6571.00 km)
  Non-dimensional Velocity Unit: 1.024547 km/s
  Non-dimensional Time Unit: 4.3425 days

Circular Parking Orbit Baseline (LEO):
  Inertial Circular Speed: 7.7885 km/s (ND: 7.601886)
  Rotating Circular Speed: 7.7710 km/s (ND: 7.584791)

Running sweep over 301 TLI injection speeds from 10.850 to 11.150 km/s...

Trajectory Sweep Results Summary (sampled speeds):
V_inj (km/s) | Outcome         | Min Selene (km) | Pass Behind? | Return Alt (km) | C Drift   
--------------------------------------------------------------------------------------------
     10.8500 | earth_collision |        242452.0 | False        |           285.3 | 1.9e-10
     10.8710 | earth_collision |        198464.2 | False        |           494.3 | 8.3e-11
     10.8920 | earth_collision |        129834.2 | False        |            63.4 | 1.9e-10
     10.9140 | completed       |         28302.8 | False        |          2077.1 | 2.6e-10
     10.9350 | earth_collision |         39439.3 | True         |           335.1 | 1.9e-10
     10.9570 | completed       |         86607.6 | True         |        450865.3 | 5.6e-11
     10.9780 | escape          |        111016.6 | True         |        456820.7 | 5.6e-11
     11.0000 | escape          |        125365.0 | True         |        452560.9 | 5.6e-11
     11.0210 | escape          |        133079.7 | True         |        445412.5 | 6.1e-11
     11.0420 | escape          |        137353.0 | True         |        437836.1 | 6.6e-11
     11.0640 | escape          |        139548.9 | True         |        430543.7 | 7.1e-11
     11.0850 | escape          |        140247.2 | True         |        424594.5 | 7.6e-11
     11.1070 | escape          |        140013.0 | True         |        419094.7 | 8.1e-11
     11.1280 | escape          |        139160.4 | True         |        414709.7 | 8.5e-11
     11.1500 | escape          |        137810.6 | True         |        411186.9 | 9.8e-11

Searching for Free-Return Corridor:
  Found 37 trajectories that flyby the Moon and return to Earth.

  Successful Free-Return Corridor (Return Altitude 0 to 10,000 km):
    TLI Speed Range: 10.9270 to 10.9360 km/s
    Best altitude return: TLI speed = 10.9300 km/s, Return Altitude = 118.0 km, closest lunar approach = 23938.3 km

Generating figures...
  Saved rotating frame trajectories plot to .\lunar\lunar_free_return\results\figures\script_01_trajectory_sweep_trajectories.png
  Saved metrics sweep plot to .\lunar\lunar_free_return\results\figures\script_01_trajectory_sweep_metrics.png

Integration Quality Check:
  Maximum Jacobi constant drift across all runs: 6.32e-10
  Conservation check passed! The numerical integration is highly reliable.

============================================================
=== COMPLETE ===
============================================================
"""
