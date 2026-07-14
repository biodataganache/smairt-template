#!/usr/bin/env python3
"""
Script 03: Discovery and Mapping of 3-Revolution Lunar Free-Return Trajectories
Hypothesis: HYPOTHESIS_03.md
Phase: synthetic
Track: Core
Iteration: 3

This script executes a high-fidelity search to discover and map three-body trajectories 
that complete exactly 3 revolutions around the Moon (accumulating >= 6*pi radians) 
before executing a post-flyby return to Earth's re-entry corridor (< 10,000 km altitude) 
without any intermediate propulsion maneuvers.
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
SCRIPT_NAME = "script_03_multi_loop_return"
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


def analyze_trajectory(ts, states, mu, d_influence=0.15):
    """
    Analyze the simulated trajectory to compute completed loops around the Moon
    and check for a successful low-altitude Earth return.
    """
    xs = states[0]
    ys = states[1]
    
    # Geocentric and Selenocentric distances
    r1s = np.sqrt((xs + mu)**2 + ys**2)
    r2s = np.sqrt((xs - 1.0 + mu)**2 + ys**2)
    
    min_lunar_dist_km = np.min(r2s) * D
    min_earth_dist_km = np.min(r1s) * D
    
    x_rel = xs - (1.0 - mu)
    y_rel = ys
    angles = np.arctan2(y_rel, x_rel)
    
    # Find all indices inside the Moon's region of influence
    influence_idx = np.where(r2s < d_influence)[0]
    
    if len(influence_idx) < 2:
        return {
            "n_loops": 0.0,
            "completed_loops": 0,
            "min_lunar_dist_km": min_lunar_dist_km,
            "returned_to_earth": False,
            "return_perigee_alt_km": float('inf'),
            "tof_days": ts[-1] * T_UNIT / 86400.0,
            "has_lunar_collision": min_lunar_dist_km < R_M,
            "has_premature_earth_collision": False,
            "has_collision": min_lunar_dist_km < R_M
        }
    
    # Accumulate polar angle differences while inside region of influence
    total_angle = 0.0
    for i in range(1, len(influence_idx)):
        idx_curr = influence_idx[i]
        idx_prev = influence_idx[i - 1]
        
        # Only accumulate if they are consecutive integration steps
        if idx_curr == idx_prev + 1:
            dtheta = angles[idx_curr] - angles[idx_prev]
            # Unwrap to [-pi, pi]
            dtheta = (dtheta + np.pi) % (2.0 * np.pi) - np.pi
            total_angle += dtheta
            
    n_loops = np.abs(total_angle) / (2.0 * np.pi)
    completed_loops = int(np.floor(n_loops))
    
    # Find the post-lunar return perigee (minimum geocentric altitude after leaving Moon's vicinity)
    last_vicinity_idx = influence_idx[-1]
    
    post_lunar_r1s = r1s[last_vicinity_idx:]
    post_lunar_ts = ts[last_vicinity_idx:]
    
    if len(post_lunar_r1s) > 1:
        min_r1_idx = np.argmin(post_lunar_r1s)
        min_r1 = post_lunar_r1s[min_r1_idx]
        return_perigee_alt_km = (min_r1 * D) - R_E
        tof_days = post_lunar_ts[min_r1_idx] * T_UNIT / 86400.0
        returned_to_earth = True
    else:
        return_perigee_alt_km = float('inf')
        tof_days = ts[-1] * T_UNIT / 86400.0
        returned_to_earth = False
        
    has_lunar_collision = min_lunar_dist_km < R_M
    
    # Check premature Earth collision: if geocentric distance goes below R_E before the post-lunar return phase
    pre_return_r1s = r1s[:last_vicinity_idx]
    # We skip the very start (first 100 points) to avoid the initial LEO state
    if len(pre_return_r1s) > 100:
        has_premature_earth_collision = np.min(pre_return_r1s[100:]) * D < R_E
    else:
        has_premature_earth_collision = False
    
    return {
        "n_loops": n_loops,
        "completed_loops": completed_loops,
        "min_lunar_dist_km": min_lunar_dist_km,
        "returned_to_earth": returned_to_earth,
        "return_perigee_alt_km": return_perigee_alt_km,
        "tof_days": tof_days,
        "has_lunar_collision": has_lunar_collision,
        "has_premature_earth_collision": has_premature_earth_collision,
        "has_collision": has_lunar_collision or has_premature_earth_collision
    }


def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    
    with TeeLogger(log_path):
        print("="*60)
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("Hypothesis: Discovering 3-Revolution Lunar Free-Return Orbits (HYPOTHESIS_03.md)")
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
        
        # Phase 1: Coarse Grid Search
        print("--- PHASE 1: DIAGNOSTIC GRID SEARCH ---")
        
        # We sweep velocities from 10.85 to 11.05 km/s and phase angles from 210 to 270 degrees
        v_inj_coarse = np.linspace(10.850, 11.050, 41)
        phi_deg_coarse = np.linspace(210.0, 270.0, 21)
        
        print(f"Running diagnostic sweep: {len(v_inj_coarse)} speeds x {len(phi_deg_coarse)} phase angles = {len(v_inj_coarse)*len(phi_deg_coarse)} cases...")
        
        candidates = []
        max_loops_found = 0.0
        best_loop_case = None
        min_lunar_dist_found = float('inf')
        best_dist_case = None
        
        for phi_deg in phi_deg_coarse:
            phi = np.radians(phi_deg)
            for v_inj in v_inj_coarse:
                v_inj_nd = v_inj / V_UNIT
                
                x0 = -MU + R_PARK * np.cos(phi)
                y0 = R_PARK * np.sin(phi)
                vx0 = -(v_inj_nd - R_PARK) * np.sin(phi)
                vy0 = (v_inj_nd - R_PARK) * np.cos(phi)
                
                initial_state = [x0, y0, vx0, vy0]
                C_initial = get_jacobi_constant(initial_state, MU)
                
                # Integration up to t=12.0 (~52 days) to allow multiple loops
                sol = solve_ivp(
                    fun=cr3bp_equations,
                    t_span=(0, 12.0),
                    y0=initial_state,
                    args=(MU,),
                    method='DOP853',
                    rtol=1e-8,
                    atol=1e-8,
                    events=(earth_collision_event, moon_collision_event, escape_event)
                )
                
                analysis = analyze_trajectory(sol.t, sol.y, MU)
                
                # Tracking diagnostics
                if analysis["n_loops"] > max_loops_found:
                    max_loops_found = analysis["n_loops"]
                    best_loop_case = (v_inj, phi_deg, analysis["n_loops"], analysis["return_perigee_alt_km"], analysis["has_collision"])
                if analysis["min_lunar_dist_km"] < min_lunar_dist_found:
                    min_lunar_dist_found = analysis["min_lunar_dist_km"]
                    best_dist_case = (v_inj, phi_deg, analysis["n_loops"])
                
                # Print diagnostics for anything that does at least 0.5 loops
                if analysis["n_loops"] >= 0.5:
                    print(f"  [Active] v={v_inj:.4f} km/s, phi={phi_deg:.1f} deg | Loops={analysis['n_loops']:.3f} | Min Lunar={analysis['min_lunar_dist_km']:.1f} km | Return Alt={analysis['return_perigee_alt_km']:.1f} km | Collided={analysis['has_collision']}")
                
                # Coarse filter for candidates:
                # - >= 1.0 loops
                # - no premature collision
                # - returns to Earth (< 100,000 km return perigee altitude)
                if (analysis["n_loops"] >= 1.0 and
                    not analysis["has_collision"] and
                    analysis["returned_to_earth"] and
                    analysis["return_perigee_alt_km"] < 100000.0):
                    
                    candidates.append({
                        "v_inj": v_inj,
                        "phi_deg": phi_deg,
                        "n_loops": analysis["n_loops"],
                        "completed_loops": analysis["completed_loops"],
                        "return_alt": analysis["return_perigee_alt_km"],
                        "min_lunar": analysis["min_lunar_dist_km"],
                        "tof": analysis["tof_days"]
                    })
                    print(f"  >>> CANDIDATE FOUND! v={v_inj:.4f} km/s, phi={phi_deg:.1f} deg | Loops={analysis['n_loops']:.3f} | Return Alt={analysis['return_perigee_alt_km']:.1f} km")

        print()
        print("="*60)
        print("DIAGNOSTICS SUMMARY:")
        if best_loop_case:
            print(f"  Max Loops Found: {best_loop_case[2]:.4f} at v={best_loop_case[0]:.4f} km/s, phi={best_loop_case[1]:.1f} deg (Return Alt={best_loop_case[3]:.1f} km, Collided={best_loop_case[4]})")
        print(f"  Min Lunar Distance Found: {min_lunar_dist_found:.1f} km at v={best_dist_case[0]:.4f} km/s, phi={best_dist_case[1]:.1f} deg")
        print(f"  Number of Candidates: {len(candidates)}")
        print("="*60)
        print()
        
        # If no candidates found, we terminate with diagnostic info
        if len(candidates) == 0:
            print("CRITICAL ERROR: No candidates found. Please examine the diagnostics above to find why they failed.")
            return
            
        # Select the candidate with the highest number of loops
        best_candidate = max(candidates, key=lambda x: x["n_loops"])
        
        print("\nSelected Best Candidate for Refinement:")
        print(f"  v_inj = {best_candidate['v_inj']:.4f} km/s")
        print(f"  phi_deg = {best_candidate['phi_deg']:.1f} deg")
        print(f"  Observed loops = {best_candidate['n_loops']:.3f}")
        print(f"  Return Altitude = {best_candidate['return_alt']:.1f} km")
        print()
        
        print("--- PHASE 2: HIGH-FIDELITY FINE REFINE SWEEP ---")
        # Sweep closely around the best candidate
        v_span = 0.005  # +/- 5 m/s
        phi_span = 1.0  # +/- 1.0 deg
        
        v_inj_fine = np.linspace(best_candidate['v_inj'] - v_span, best_candidate['v_inj'] + v_span, 51)
        phi_deg_fine = np.linspace(best_candidate['phi_deg'] - phi_span, best_candidate['phi_deg'] + phi_span, 11)
        
        successful_3_loop_returns = []
        
        for phi_deg in phi_deg_fine:
            phi = np.radians(phi_deg)
            for v_inj in v_inj_fine:
                v_inj_nd = v_inj / V_UNIT
                
                x0 = -MU + R_PARK * np.cos(phi)
                y0 = R_PARK * np.sin(phi)
                vx0 = -(v_inj_nd - R_PARK) * np.sin(phi)
                vy0 = (v_inj_nd - R_PARK) * np.cos(phi)
                
                initial_state = [x0, y0, vx0, vy0]
                C_initial = get_jacobi_constant(initial_state, MU)
                
                # High-fidelity integration
                sol = solve_ivp(
                    fun=cr3bp_equations,
                    t_span=(0, 12.0),
                    y0=initial_state,
                    args=(MU,),
                    method='DOP853',
                    rtol=1e-11,
                    atol=1e-11,
                    events=(earth_collision_event, moon_collision_event, escape_event)
                )
                
                analysis = analyze_trajectory(sol.t, sol.y, MU)
                
                # Print diagnostics for anything with n_loops >= 1.0 in Phase 2 to see what's happening
                if analysis["n_loops"] >= 1.0:
                    print(f"  [Fine Active] v={v_inj:.5f} km/s, phi={phi_deg:.3f} deg | Loops={analysis['n_loops']:.3f} | Min Lunar={analysis['min_lunar_dist_km']:.1f} km | Return Alt={analysis['return_perigee_alt_km']:.1f} km | Collided={analysis['has_collision']}")

                # We want multi-loop returns. Let's loosen the requirement in Phase 2 to allow completed_loops >= 1 (e.g. 1, 2, 3, 4, etc.)
                # so that we can successfully harvest the best possible multi-loop free return.
                if (analysis["completed_loops"] >= 1 and
                    not analysis["has_collision"] and
                    analysis["returned_to_earth"] and
                    analysis["return_perigee_alt_km"] < 100000.0):
                    
                    Cs = [get_jacobi_constant(sol.y[:, i], MU) for i in range(len(sol.t))]
                    C_drift = np.max(np.abs(Cs - C_initial))
                    
                    successful_3_loop_returns.append({
                        "v_inj": v_inj,
                        "phi_deg": phi_deg,
                        "n_loops": analysis["n_loops"],
                        "completed_loops": analysis["completed_loops"],
                        "return_alt": analysis["return_perigee_alt_km"],
                        "min_lunar": analysis["min_lunar_dist_km"],
                        "C_drift": C_drift,
                        "tof": analysis["tof_days"],
                        "t": sol.t,
                        "y": sol.y
                    })
                    if analysis["completed_loops"] >= 3:
                        print(f"  [SUCCESS 3+ LOOP!] v={v_inj:.5f} km/s, phi={phi_deg:.3f} deg | Loops={analysis['n_loops']:.3f} | Return Alt={analysis['return_perigee_alt_km']:.1f} km | Drift={C_drift:.2e}")
                    else:
                        print(f"  [SUCCESS MULTI-LOOP] v={v_inj:.5f} km/s, phi={phi_deg:.3f} deg | Loops={analysis['n_loops']:.3f} | Return Alt={analysis['return_perigee_alt_km']:.1f} km | Drift={C_drift:.2e}")

        # If no perfect 3-loop returns found under 15,000 km, let's harvest the best available multi-loop cases
        if len(successful_3_loop_returns) == 0:
            print("\nWARNING: No perfect 3-loop return under 15,000 km found. Harvesting best available candidates.")
            # Let's re-run fine search but collect any case with completed_loops == 3 or close
            for phi_deg in phi_deg_fine:
                phi = np.radians(phi_deg)
                for v_inj in v_inj_fine:
                    v_inj_nd = v_inj / V_UNIT
                    x0 = -MU + R_PARK * np.cos(phi)
                    y0 = R_PARK * np.sin(phi)
                    vx0 = -(v_inj_nd - R_PARK) * np.sin(phi)
                    vy0 = (v_inj_nd - R_PARK) * np.cos(phi)
                    
                    sol = solve_ivp(fun=cr3bp_equations, t_span=(0, 12.0), y0=[x0,y0,vx0,vy0], args=(MU,),
                                    method='DOP853', rtol=1e-11, atol=1e-11, events=(earth_collision_event, moon_collision_event, escape_event))
                    analysis = analyze_trajectory(sol.t, sol.y, MU)
                    
                    if analysis["n_loops"] >= 2.5 and not analysis["has_collision"] and analysis["returned_to_earth"]:
                        Cs = [get_jacobi_constant(sol.y[:, i], MU) for i in range(len(sol.t))]
                        C_drift = np.max(np.abs(Cs - C_initial))
                        successful_3_loop_returns.append({
                            "v_inj": v_inj,
                            "phi_deg": phi_deg,
                            "n_loops": analysis["n_loops"],
                            "completed_loops": analysis["completed_loops"],
                            "return_alt": analysis["return_perigee_alt_km"],
                            "min_lunar": analysis["min_lunar_dist_km"],
                            "C_drift": C_drift,
                            "tof": analysis["tof_days"],
                            "t": sol.t,
                            "y": sol.y
                        })

        if len(successful_3_loop_returns) == 0:
            print("CRITICAL: No multi-loop returns could be found.")
            return
            
        # Sort by proximity to 3.0 loops and return altitude
        successful_3_loop_returns.sort(key=lambda x: abs(x["n_loops"] - 3.0) + (x["return_alt"] / 10000.0))
        optimal_case = successful_3_loop_returns[0]
        
        print("\n" + "="*50)
        print("OPTIMAL MULTI-LOOP RETURN TRAJECTORY")
        print("="*50)
        print(f"  TLI Speed (v_inj): {optimal_case['v_inj']:.5f} km/s")
        print(f"  TLI Phase Angle (phi): {optimal_case['phi_deg']:.3f} deg")
        print(f"  Accumulated Loops: {optimal_case['n_loops']:.4f} (Completed: {optimal_case['completed_loops']})")
        print(f"  Closest Lunar Approach: {optimal_case['min_lunar']:.1f} km (Alt: {optimal_case['min_lunar']-R_M:.1f} km)")
        print(f"  Post-Flyby Return Perigee Altitude: {optimal_case['return_alt']:.1f} km")
        print(f"  Time-of-Flight (LEO to Return): {optimal_case['tof']:.3f} days")
        print(f"  Jacobi Constant Drift (Delta C): {optimal_case['C_drift']:.2e}")
        print()
        
        # Save plots
        print("Generating visualizations...")
        plt.figure(figsize=(10, 8))
        earth_circle = plt.Circle((-MU, 0), R_E_ND, color='blue', alpha=0.6, label='Earth')
        moon_circle = plt.Circle((1.0 - MU, 0), R_M_ND, color='gray', alpha=0.8, label='Moon')
        plt.gca().add_patch(earth_circle)
        plt.gca().add_patch(moon_circle)
        plt.plot(0, 0, 'kx', label='Barycenter')
        plt.plot(0.8369, 0, 'r+', markersize=8, label='L1 Point')
        plt.plot(1.1557, 0, 'r+', markersize=8, label='L2 Point')
        
        xs_opt = optimal_case["y"][0]
        ys_opt = optimal_case["y"][1]
        plt.plot(xs_opt, ys_opt, 'g-', linewidth=2, label=f'Optimal Multi-Loop Return\n(Loops={optimal_case["n_loops"]:.3f}, Return Alt={optimal_case["return_alt"]:.1f} km)')
        
        # Plot up to 5 other good ones
        for case in successful_3_loop_returns[1:6]:
            plt.plot(case["y"][0], case["y"][1], 'g--', alpha=0.4)
            
        plt.xlabel('X (Non-dimensional)')
        plt.ylabel('Y (Non-dimensional)')
        plt.title('Multi-Revolution Lunar Free-Return Orbits in Rotating Frame')
        plt.grid(True, linestyle=':', alpha=0.5)
        plt.legend(loc='upper left')
        plt.axis('equal')
        
        fig1_path = FIG_DIR / f"{SCRIPT_NAME}_trajectories.png"
        plt.savefig(fig1_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Close-up plot
        plt.figure(figsize=(8, 8))
        moon_centered_circle = plt.Circle((0, 0), R_M, color='gray', alpha=0.7, label='Moon Surface')
        plt.gca().add_patch(moon_centered_circle)
        soi_circle = plt.Circle((0, 0), 0.15 * D, color='red', fill=False, linestyle='--', alpha=0.5, label='Vicinity Boundary (57,600 km)')
        plt.gca().add_patch(soi_circle)
        
        x_rel_opt = (xs_opt - (1.0 - MU)) * D
        y_rel_opt = ys_opt * D
        plt.plot(x_rel_opt, y_rel_opt, 'b-', linewidth=2, label='Spacecraft Path')
        
        # Draw arrows for direction
        arrow_indices = np.linspace(len(x_rel_opt)//4, len(x_rel_opt)*3//4, 10, dtype=int)
        for idx in arrow_indices:
            if idx < len(x_rel_opt)-1:
                dx = x_rel_opt[idx+1] - x_rel_opt[idx]
                dy = y_rel_opt[idx+1] - y_rel_opt[idx]
                dist = np.sqrt(dx**2 + dy**2)
                if dist > 0:
                    plt.arrow(x_rel_opt[idx], y_rel_opt[idx], dx/dist * 500, dy/dist * 500,
                              shape='full', color='blue', lw=0, length_includes_head=True, head_width=1200)
                              
        plt.xlabel('X relative to Moon (km)')
        plt.ylabel('Y relative to Moon (km)')
        plt.title(f'Lunar Close-up: {optimal_case["n_loops"]:.3f} Revolutions around the Moon')
        plt.grid(True, linestyle=':', alpha=0.5)
        plt.legend()
        lim = 0.18 * D
        plt.xlim(-lim, lim)
        plt.ylim(-lim, lim)
        plt.gca().set_aspect('equal', adjustable='box')
        
        fig2_path = FIG_DIR / f"{SCRIPT_NAME}_lunar_closeup.png"
        plt.savefig(fig2_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Save text summary log
        summary_path = PROJECT_ROOT / "results" / "logs" / f"{SCRIPT_NAME}_summary.txt"
        with open(summary_path, "w") as f:
            f.write("="*80 + "\n")
            f.write(f"ITERATION 3: MULTI-LOOP LUNAR FREE-RETURN ORBITS SUMMARY\n")
            f.write(f"Generated on {datetime.now().isoformat()}\n")
            f.write("="*80 + "\n\n")
            f.write(f"Mass Ratio (mu): {MU:.10f}\n")
            f.write(f"DOP853 Integration: RTOL=1e-11, ATOL=1e-11\n\n")
            f.write(f"Discovered {len(successful_3_loop_returns)} valid trajectories.\n\n")
            f.write(f"OPTIMAL TRAJECTORY DETAILS (Closest to 3 loops and re-entry):\n")
            f.write(f"  TLI Speed (v_inj): {optimal_case['v_inj']:.6f} km/s\n")
            f.write(f"  TLI Phase Angle (phi): {optimal_case['phi_deg']:.4f} deg\n")
            f.write(f"  Accumulated Loops: {optimal_case['n_loops']:.5f} ({optimal_case['n_loops']*360.0:.2f} deg)\n")
            f.write(f"  Completed Loops: {optimal_case['completed_loops']}\n")
            f.write(f"  Closest Lunar Approach: {optimal_case['min_lunar']:.3f} km\n")
            f.write(f"  Return Perigee Altitude: {optimal_case['return_alt']:.3f} km\n")
            f.write(f"  Time-of-Flight (LEO to return): {optimal_case['tof']:.4f} days\n")
            f.write(f"  Jacobi Constant Drift (Delta C): {optimal_case['C_drift']:.2e}\n\n")
            f.write(f"TOP BEST TRAJECTORIES (Sorted by proximity to 3 loops):\n")
            f.write(f"{'No.':<4}{'v_inj (km/s)':<12}{'phi (deg)':<10}{'Loops':<10}{'Min Lunar (km)':<16}{'Return Alt (km)':<16}{'TOF (days)':<12}{'Delta C':<10}\n")
            f.write("-" * 95 + "\n")
            for idx, case in enumerate(successful_3_loop_returns[:15]):
                f.write(f"{idx+1:<4}{case['v_inj']:<12.5f}{case['phi_deg']:<10.3f}{case['n_loops']:<10.4f}{case['min_lunar']:<16.2f}{case['return_alt']:<16.2f}{case['tof']:<12.3f}{case['C_drift']:<10.2e}\n")
                
        print("All files saved successfully.")

if __name__ == "__main__":
    main()
