# 01_initial_question.md

## Brief Background

Artemis II will carry astronauts on a lunar **free-return** trajectory: a path
that uses only the Moon's gravity to swing the spacecraft around the far side of
the Moon and back to Earth, requiring no major return burn. If the main engine
failed after translunar injection (TLI), the spacecraft would still come home.
This is the same safety principle that brought Apollo 13 back.

This SMAIRT project reproduces a free-return trajectory in a simplified but
physically real model: the planar **Circular Restricted Three-Body Problem
(CR3BP)** for the Earth-Moon system. It is CPU-only, pure Python, and needs no
external data, which makes it ideal for a hands-on demo.

## Question

Can we find a translunar-injection burn from a low-Earth parking orbit that
produces a free-return: looping behind the Moon and returning to a low Earth
perigee (the re-entry corridor) with no further burns?

## Hypothesis

There is a narrow band of TLI burn speeds for which the trajectory passes close
behind the Moon and the post-flyby return perigee drops back near Earth. Below
the band the craft falls back without reaching the Moon; above it, the craft
escapes. The free-return lives at a sharp transition near the escape speed.

## Evidence / metrics

- Closest lunar approach (km above the Moon's surface).
- Return perigee (closest Earth approach after the lunar flyby).
- Maximum Earth distance (apogee ~ lunar distance for a true free-return).
- Jacobi-constant conservation (validates the propagator before we trust it).

## Domain Context

### The CR3BP model
- Rotating, non-dimensional frame. Mass unit = Earth+Moon; length unit =
  Earth-Moon distance (384,400 km); time chosen so mean motion n = 1.
- Earth sits at x = -mu and y = 0. The Moon sits at x = 1 - mu and y = 0, with
  mu = m_moon/(m_earth+m_moon) = 0.012150585609624.
- The Jacobi constant is the conserved "energy-like" quantity; tracking its
  drift validates the numerical integration.

### Why a free-return is special
- It is fuel-efficient and fault-tolerant: gravity does the work of turning the
  spacecraft around.
- In the rotating frame the Moon is fixed, so a successful path appears as a
  loop that reaches out to ~1.0 (lunar distance) and returns toward Earth.

### Fidelity ladder (SMAIRT data progression)
1. Synthetic: CR3BP with normalized units (fast, no dependencies).
2. Real constants: real Earth/Moon GM and distance for SI-scaled reporting
   for SI-scaled reporting.
3. (Optional) Ephemeris-based Moon position. Use this only if time permits; it is
   not required to demonstrate the free-return.

### Caveats
- Planar, circular-orbit Moon, point masses, patched into one rotating frame.
- This reproduces the *qualitative and near-quantitative* free-return geometry,
  not a mission-grade trajectory. That honesty is part of the SMAIRT method:
  state the model's limits alongside the result.

## Known constants

| Quantity | Value |
|----------|-------|
| Earth-Moon distance | 384,400 km |
| Earth radius | 6,371 km |
| Moon radius | 1,737.4 km |
| mass ratio mu | 0.012150585609624 |
| non-dim time unit | ~4.34 days |
