# Dockweed drill v1: why it is designed this way

Process, requirements, Z axis, spindle, pot, cycle, mounting on the robot, wheel loads, control, costs and sources
are the same for v1 and v2 and are described in [../v2/RATIONALE.md](../v2/RATIONALE.md). This document covers what
is specific to v1: the X axis on aluminium profiles with HGR15 rails. The original v1 requirements document is in
`legacy/dockweed_requirements.md`.

## 1. X axis on profiles and rails

| Choice | v1 | Alternatives considered |
| --- | --- | --- |
| X guide | 2 aluminium profiles 40 × 80 (slot 8) at z 760 and 1060, each with an HGR15 rail; 4 carriages HGH15CA on the slide (2 per rail, ±90 mm) | SBR16 (chrome shafts, forgiving, heavier); gate rail with roller carriages (cheap and robust, +15 kg); V-slot (too weak); PTO tubes (v2) |
| Fixing | M8 + T-nut through the uprights into the front slot | Brackets (more parts) |
| End plates | Aluminium 10 mm on the profile ends; belt clamps outside them | Steel (heavier) |
| X drive | HTD-5M 15 mm steel cord, omega drive on the slide, NEMA 23 + 5:1 | Chain 08B (rust, oil), rack and pinion |

Why not PTO tubes as in the BRUUT concept (the reasoning of the first v1): two parallel sliding pairs are
over-constrained and jam, and steel slides on steel with dirt. v2 solves the first point with 3 short sleeves and
slotted holes; the second with scrapers and grease.

| | v1 (profiles + HGR15) | v2 (PTO tubes) |
| --- | --- | --- |
| Mass X axis + X carriage | 25.0 kg | 33.0 kg |
| Deflection in z at x ±500 under the moving mass | 0.85 mm (aluminium, weak axis) | 0.45 mm |
| Deflection in y at 600 N Z force | 0.53 mm | 0.96 mm |
| Friction | ≈ 16 N (rolling) | ≈ 190 N (sliding) |
| Accuracy and play | high, no play | 0.5–1 mm play is normal |
| Dirt and rust | HGR rails are sensitive: splash guard above the upper profile, grease regularly | made for dirt |
| Availability | online (profile, rails) | any agricultural dealer |
| Welding | none on the X axis | ribs on the tubes, pads on the sleeves |

## 2. What changed from the original v1 script (dockweed_design.py)

| Change | Why |
| --- | --- |
| Standard layout (`dwd1_params/parts/build/calc`, animation, GIF), English names, robot coordinates | Same as the other implements (AGENTS.md) |
| Mounted behind the rear lower beam of the real robot model, on the hole grid (x ±225/±275), uprights at ±250 | The original assumed cross beams with clamps at y −20/−470, a 700 mm wheelbase and 2WD |
| Wheel loads for the 4WD robot (1000 mm wheelbase) | See ../v2/RATIONALE.md § 5 |
| Spiral cable to the Z slide added (anchored at z 850 on the slide), camera mast at +x | Open point 7 of the original |
| Pot splash flap added | Open point 9 of the original |
| E-box on a cross tube between the uprights | The original E-box sat on the left upright |
| Plunge stroke 30 + 150 mm in cycle and G-code | The pot touches 30 mm before the cutter reaches the ground |

## 3. Estimated values specific to v1

Profile catalogue values (2.8 kg/m, I = 14.3 cm⁴ weak axis, 45.6 cm⁴ strong axis), HGR15 rail stiffness (15 × 15
steel), rolling friction μ 0.005 + 2 N seal drag per carriage.
