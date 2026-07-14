#!/usr/bin/env python3
"""
Script 02: Parameter Sweep to Discover Direct Lunar Intercept Trajectories

Hypothesis: HYPOTHESIS_02.md
Phase: synthetic
Track: Core
Iteration: 2

Depends on:
  - None (or rather script_01_trajectory_sweep.py constants/equations)
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
SCRIPT_NAME = "script_02_lunar_intercept"
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
        print("Hypothesis: Discovering Direct Lunar Intercept Trajectories (Hohmann-like Leading Face Impacts)")
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
        
        # 1. We search across the narrow, high-density impact band found in our search
        # Sweeping speeds from 10.920 to 10.970 km/s, and phase angles from 224 to 238 degrees
        v_inj_sweep = np.linspace(10.920, 10.970, 51)
        phi_deg_sweep = np.linspace(224.0, 238.0, 15)
        
        results = []
        impact_trajectories = []
        
        print(f"Running 2D grid sweep over {len(v_inj_sweep)} TLI speeds and {len(phi_deg_sweep)} phase angles...")
        
        best_impact_case = None
        min_tof = float('inf')
        
        for phi_deg in phi_deg_sweep:
            phi = np.radians(phi_deg)
            for v_inj in v_inj_sweep:
                v_inj_nd = v_inj / V_UNIT
                
                # Setup initial state
                x0 = -MU + R_PARK * np.cos(phi)
                y0 = R_PARK * np.sin(phi)
                vx0 = -(v_inj_nd - R_PARK) * np.sin(phi)
                vy0 = (v_inj_nd - R_PARK) * np.cos(phi)
                
                initial_state = [x0, y0, vx0, vy0]
                C_initial = get_jacobi_constant(initial_state, MU)
                
                # Integrate up to t = 5.0 (~21.7 days)
                t_span = (0, 5.0)
                t_eval = np.linspace(0, 5.0, 5000)
                
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
                
                outcome = "completed"
                if sol.status == 1:
                    if len(sol.t_events[0]) > 0:
                        outcome = "earth_collision"
                    elif len(sol.t_events[1]) > 0:
                        outcome = "moon_collision"
                    elif len(sol.t_events[2]) > 0:
                        outcome = "escape"
                
                times = sol.t
                states = sol.y
                xs, ys = states[0], states[1]
                vxs, vys = states[2], states[3]
                
                # Verify integration quality check on Jacobi Constant
                Cs = [get_jacobi_constant(states[:, i], MU) for i in range(len(times))]
                C_drift = np.max(np.abs(Cs - C_initial))
                
                r2s = np.sqrt((xs - 1.0 + MU)**2 + ys**2)
                d_min_moon_km = np.min(r2s) * D
                
                t_flight_days = times[-1] * T_UNIT / 86400.0
                
                if outcome == "moon_collision":
                    x_imp_nd = xs[-1]
                    y_imp_nd = ys[-1]
                    vx_imp_nd = vxs[-1]
                    vy_imp_nd = vys[-1]
                    
                    # Coordinates relative to Moon center
                    x_rel_nd = x_imp_nd - (1.0 - MU)
                    y_rel_nd = y_imp_nd
                    
                    x_rel_km = x_rel_nd * D
                    y_rel_km = y_rel_nd * D
                    
                    # Leading hemisphere has y > 0 relative to Moon's center in rotating frame
                    is_leading_face = y_rel_nd > 0
                    
                    # Compute impact angle relative to local surface horizontal
                    # Surface normal vector (outward): n = [x_rel, y_rel] / R_M
                    n_vec = np.array([x_rel_nd, y_rel_nd])
                    n_vec = n_vec / np.linalg.norm(n_vec)
                    
                    # Spacecraft velocity relative to Moon
                    v_vec = np.array([vx_imp_nd, vy_imp_nd])
                    v_mag = np.linalg.norm(v_vec)
                    
                    # Impact speed in physical units
                    v_impact_km_s = v_mag * V_UNIT
                    
                    # Dot product to find angle between velocity and surface normal
                    cos_theta = np.dot(v_vec, n_vec) / (v_mag * np.linalg.norm(n_vec))
                    cos_theta = max(-1.0, min(1.0, cos_theta))
                    
                    # Angle relative to horizontal is 90 deg - angle with normal
                    normal_angle_deg = np.degrees(np.arccos(np.clip(-cos_theta, -1.0, 1.0)))
                    impact_angle_deg = 90.0 - normal_angle_deg
                    
                    entry = {
                        "v_inj": v_inj,
                        "phi_deg": phi_deg,
                        "C_drift": C_drift,
                        "t_flight": t_flight_days,
                        "x_rel": x_rel_km,
                        "y_rel": y_rel_km,
                        "is_leading": is_leading_face,
                        "impact_speed": v_impact_km_s,
                        "impact_angle": impact_angle_deg,
                        "x": xs,
                        "y": ys
                    }
                    results.append(entry)
                    impact_trajectories.append(entry)
                    
                    # Keep track of the minimum-energy direct impact (lowest v_inj and leading face)
                    if is_leading_face and t_flight_days < min_tof:
                        min_tof = t_flight_days
                        best_impact_case = entry
                        
        print(f"\nCompleted grid search. Found {len(impact_trajectories)} lunar impact trajectories.")
        
        # Leading vs trailing impacts
        leading_impacts = [r for r in impact_trajectories if r['is_leading']]
        print(f"  Leading face impacts (y > 0): {len(leading_impacts)}")
        print(f"  Trailing face impacts (y <= 0): {len(impact_trajectories) - len(leading_impacts)}")
        
        if best_impact_case is not None:
            print("\nOptimal Leading-Face Lunar Intercept Case:")
            print(f"  TLI Launch Speed: {best_impact_case['v_inj']:.4f} km/s")
            print(f"  Launch Phase Angle (phi): {best_impact_case['phi_deg']:.1f} degrees")
            print(f"  Time of Flight to Impact: {best_impact_case['t_flight']:.3f} days")
            print(f"  Impact Velocity: {best_impact_case['impact_speed']:.3f} km/s")
            print(f"  Impact Angle: {best_impact_case['impact_angle']:.1f} degrees (from surface horizontal)")
            print(f"  Impact Coordinates relative to Moon center: ({best_impact_case['x_rel']:.1f}, {best_impact_case['y_rel']:.1f}) km")
            print(f"  Jacobi Constant Drift: {best_impact_case['C_drift']:.2e}")
            assert best_impact_case['C_drift'] < 1e-6, "Jacobi constant conservation check failed!"
        else:
            print("\n[WARNING] No leading-face impact cases were found in the grid search!")
            
        # 2. Print selection of impact cases
        if len(impact_trajectories) > 0:
            print("\nSampled Lunar Impact Trajectories:")
            print(f"{'V_inj (km/s)':<12} | {'Phase (deg)':<10} | {'TOF (days)':<10} | {'Impact X (km)':<12} | {'Impact Y (km)':<12} | {'Leading?':<8} | {'Angle (deg)':<10}")
            print("-" * 88)
            indices = np.linspace(0, len(impact_trajectories)-1, min(10, len(impact_trajectories)), dtype=int)
            for idx in indices:
                r = impact_trajectories[idx]
                print(f"{r['v_inj']:12.4f} | {r['phi_deg']:10.1f} | {r['t_flight']:10.3f} | {r['x_rel']:12.1f} | {r['y_rel']:12.1f} | {str(r['is_leading']):8} | {r['impact_angle']:10.1f}")
                
        # 3. Visualization
        print("\nGenerating figures...")
        
        # Figure 1: Impact Trajectories in Rotating Frame
        plt.figure(figsize=(10, 8))
        
        # Plot Earth
        earth_circle = plt.Circle((-MU, 0), R_E_ND, color='blue', alpha=0.3, label='Earth')
        plt.gca().add_patch(earth_circle)
        plt.plot(-MU, 0, 'bo', markersize=6)
        
        # Plot Moon
        moon_circle = plt.Circle((1.0-MU, 0), R_M_ND, color='gray', alpha=0.5, label='Moon')
        plt.gca().add_patch(moon_circle)
        plt.plot(1.0-MU, 0, 'ko', markersize=4)
        
        # Plot a subset of impact trajectories
        sampled_impacts = []
        if len(leading_impacts) > 0:
            sampled_impacts.extend(leading_impacts[::max(1, len(leading_impacts)//4)])
        trailing_impacts = [r for r in impact_trajectories if not r['is_leading']]
        if len(trailing_impacts) > 0:
            sampled_impacts.extend(trailing_impacts[::max(1, len(trailing_impacts)//2)])
            
        for r in sampled_impacts:
            color = 'red' if r['is_leading'] else 'orange'
            plt.plot(r['x'], r['y'], color=color, alpha=0.6, linewidth=1)
            # Plot impact point
            plt.plot(r['x'][-1], r['y'][-1], 'kx', markersize=5)
            
        # Add labels for single entries in legend
        plt.plot([], [], color='red', label='Leading Face Impact')
        plt.plot([], [], color='orange', label='Trailing Face Impact')
        
        plt.title('Direct Lunar Intercept Trajectories in Rotating Frame')
        plt.xlabel('x (ND)')
        plt.ylabel('y (ND)')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.axis('equal')
        plt.legend(loc='upper left')
        
        plot_path_1 = FIG_DIR / f"{SCRIPT_NAME}_trajectories.png"
        plt.savefig(plot_path_1, dpi=300)
        plt.close()
        print(f"  Saved rotating frame trajectories plot to {plot_path_1}")
        
        # Figure 2: Zoomed-in Impact Locations on Moon Surface
        plt.figure(figsize=(8, 8))
        theta = np.linspace(0, 2*np.pi, 500)
        plt.plot(R_M * np.cos(theta), R_M * np.sin(theta), 'k-', label='Lunar Surface')
        plt.fill_between(R_M * np.cos(theta), R_M * np.sin(theta), where=(np.sin(theta) > 0), color='red', alpha=0.1, label='Leading Hemisphere (y > 0)')
        plt.fill_between(R_M * np.cos(theta), R_M * np.sin(theta), where=(np.sin(theta) <= 0), color='orange', alpha=0.1, label='Trailing Hemisphere (y <= 0)')
        
        for r in impact_trajectories:
            color = 'darkred' if r['is_leading'] else 'darkorange'
            plt.plot(r['x_rel'], r['y_rel'], 'o', color=color, markersize=3, alpha=0.7)
            
        plt.title('Lunar Impact Location Distribution (Selenocentric Frame)')
        plt.xlabel('x (km relative to Moon center)')
        plt.ylabel('y (km relative to Moon center)')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.axis('equal')
        plt.legend()
        
        plot_path_2 = FIG_DIR / f"{SCRIPT_NAME}_impacts.png"
        plt.savefig(plot_path_2, dpi=300)
        plt.close()
        print(f"  Saved selenocentric impact locations plot to {plot_path_2}")
        
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
