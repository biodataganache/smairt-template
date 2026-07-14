import numpy as np
from scipy.integrate import solve_ivp

D = 384400.0          # Earth-Moon distance (km)
R_E = 6371.0          # Earth radius (km)
R_M = 1737.4          # Moon radius (km)
GM_EARTH = 398600.44
GM_MOON = 4902.80
GM_TOTAL = GM_EARTH + GM_MOON
MU = GM_MOON / GM_TOTAL  # Mass ratio

L_UNIT = D                      # length unit (km)
V_UNIT = np.sqrt(GM_TOTAL / D)  # velocity unit (km/s)
T_UNIT = np.sqrt(D**3 / GM_TOTAL) # time unit (seconds)
R_E_ND = R_E / L_UNIT
R_M_ND = R_M / L_UNIT

LEO_ALTITUDE = 200.0            # km
R_PARK = (R_E + LEO_ALTITUDE) / L_UNIT

def cr3bp_equations(t, state, mu):
    x, y, vx, vy = state
    r1 = np.sqrt((x + mu)**2 + y**2)
    r2 = np.sqrt((x - 1.0 + mu)**2 + y**2)
    r1 = max(r1, 1e-6)
    r2 = max(r2, 1e-6)
    ax_g = -(1.0 - mu) * (x + mu) / r1**3 - mu * (x - 1.0 + mu) / r2**3
    ay_g = -(1.0 - mu) * y / r1**3 - mu * y / r2**3
    ax = 2.0 * vy + x + ax_g
    ay = -2.0 * vx + y + ay_g
    return [vx, vy, ax, ay]

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

# Coarse 2D search
v_inj_sweep = np.linspace(10.85, 11.15, 61)
phi_deg_sweep = np.linspace(0.0, 360.0, 73)

min_distance = float('inf')
best_v = None
best_phi = None
hits = []

print("Starting coarse search...")
for phi_deg in phi_deg_sweep:
    phi = np.radians(phi_deg)
    for v_inj in v_inj_sweep:
        v_inj_nd = v_inj / V_UNIT
        x0 = -MU + R_PARK * np.cos(phi)
        y0 = R_PARK * np.sin(phi)
        vx0 = -(v_inj_nd - R_PARK) * np.sin(phi)
        vy0 = (v_inj_nd - R_PARK) * np.cos(phi)
        
        sol = solve_ivp(
            fun=cr3bp_equations,
            t_span=(0, 2.5),
            y0=[x0, y0, vx0, vy0],
            args=(MU,),
            method='DOP853',
            rtol=1e-10,
            atol=1e-10,
            events=(earth_collision_event, moon_collision_event)
        )
        
        # Check if moon collision happened
        if sol.status == 1 and len(sol.t_events[1]) > 0:
            impact_y = sol.y_events[1][0][1]
            print(f"HIT! v={v_inj:.4f} km/s, phi={phi_deg:.1f} deg, impact y={impact_y*D:.1f} km, TOF={sol.t[-1]*T_UNIT/86400.0:.2f} days")
            hits.append((v_inj, phi_deg, impact_y, sol.t[-1]*T_UNIT/86400.0))
        else:
            xs, ys = sol.y[0], sol.y[1]
            r2s = np.sqrt((xs - 1.0 + MU)**2 + ys**2)
            d_min = np.min(r2s) * D
            if d_min < min_distance:
                min_distance = d_min
                best_v = v_inj
                best_phi = phi_deg

print(f"Best non-hitting approach: {min_distance:.1f} km at v={best_v:.4f}, phi={best_phi:.1f}")
print(f"Total hits found: {len(hits)}")
