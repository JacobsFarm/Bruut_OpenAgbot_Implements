# Dockweed drill v2: why it is designed this way

Implement that grinds up broad-leaved dock plant by plant: a CNC gantry (X + Z) behind the Bruut OpenAgbot, with a
fast cutter and a pot that keeps the soil in place. The concept was modelled on **Robot Ruud** (WUR / Joost Samsom).
v1 ([../v1/RATIONALE.md](../v1/RATIONALE.md)) is the same machine with an X axis of aluminium profiles and HGR15
rails. This document describes the current design (v2); § 7 lists what changed from the first scripts.

Key figures come from `dwd2_calc.report()` and `build_dwd2.mass_properties()`; estimated values are marked.

---

## 1. What we learn from Robot Ruud, Joost and the BRUUT concept

### Do's

| Do | Source | How in this design |
| --- | --- | --- |
| **High speed**: it works like a hand blender, not like a drill. Too slow gives coarse root pieces that sprout again | Joost | 1500 rpm (14 m/s tip speed), up to 3000. Plunging slowly (25 mm/s) gives slices of **0.25 mm** |
| Hole of **~18 cm**, depth **~15 cm**. The sward closes quickly, no re-seeding, cows do not scratch the holes open | Joost, WUR | Cutter Ø 180, standard 150 mm deep, max. 200 mm |
| Shred the plant **above and below ground** | Joost | Cutter goes through rosette, root crown and taproot; the pot keeps it all in place |
| With a **clump**: take out a few plants per round, come back later | Joost | Software: maximum treatments per m² per round |
| **Hood + artificial light** for the camera | Joost | LED bar next to the camera on the X slide |
| **Electric**: precise control and measuring (encoder, current) | Joost | Closed-loop steppers, VESC on the spindle |
| **Modular**, simple, first get 60–80 % working | Joost | Headstock on the hole grid, tool with 4 bolts, all dimensions parametric |
| Regrowth comes only from the **upper part of the taproot** | Research | At least ~10 cm, preferably 15 cm, 20 cm if it really has to go |

### Don'ts

| Don't | Why |
| --- | --- |
| Hydraulics in the field | A burst hose means oil in the land; motor, pumps and valve block cost Ruud approx. € 25,000 |
| Turning too slowly (hydraulic motor, a few hundred rpm) | Coarse pieces that sprout again |
| Blank mandate for the builder | The second Ruud became 3–4× more expensive than budgeted |
| Heavy machines on soft ground | Ground pressure: hence the attention to mass (§ 5) |
| Milling a clump bare in one go | Drying out and weeds |

### From the BRUUT.STP concept (inspiration folder)

| | BRUUT.STP | This design | Why |
| --- | --- | --- | --- |
| Construction | 2 horizontal guides + Z slide, motor on top | Same | Good CNC principle |
| X guide | PTO-shaft profile tubes | **v2: PTO tubes**, but with 3 short sleeves and slotted holes | Not over-constrained (§ 3.2); v1 used HGR15 rails |
| Cutter shaft | Ø 15, ~210 mm free below the bearing | Ø 35 in 2 × UCF207 | Ø 15 bends ±3 mm at 300 N and sees ±190 MPa alternating stress: fatigue and vibration |
| Cutter | 3 small blades, Ø ~110 | Cross cutter Ø 180, 4 teeth + centring point | Joost: 18 cm; MEV Ampferfräse: 180 mm |
| Pot | none | Pot Ø 250 resting on the sward | Soil stays in place; protection |

---

## 2. Requirements

### Functional
| # | Requirement | Value |
| --- | --- | --- |
| F1 | Hole diameter | Ø 180 mm |
| F2 | Depth | 0–200 mm, standard 150, measured from the **actual ground** (pot sensor) |
| F3 | Speed | 1000–2000 rpm pulverising (1500 standard), up to 3000 rpm mowing |
| F4 | Working width X | 1000 mm stroke, positioning ±2 mm |
| F5 | Z stroke | 480 mm: driving position 280 above ground to 200 deep |
| F6 | Soil | stays in the hole; no flung stones or clods |
| F7 | Second tool | mowing disc, above ground or "scalping" just above it |
| F8 | Capacity | ≈ 20–25 s per plant, ≈ 150–170 plants per hour |

### Robot and mounting
| # | Requirement |
| --- | --- |
| R1 | 48 V from the robot battery |
| R2 | No drilling or welding on the robot: M10 on the **50 mm hole grid** of the rear lower beam |
| R3 | Behind the **rear axle** (fixed wheels, no steering stack); the robot drives backwards while weeding |
| R4 | Robot stands still while milling; driving only with Z at the top (interlock) |
| R5 | Down force ≤ 600 N, so the rear wheels keep load (§ 5) |

### Construction and maintenance
| # | Requirement |
| --- | --- |
| B1 | Laser/plasma plate parts (DXF), straight lines and arcs |
| B2 | Standard purchased parts: PTO tubes, HGR15 (Z), SFU1610, NEMA 23, UCF207, HTD-5M, BLDC + VESC |
| B3 | Tool change with **4 × M10**; wear parts (teeth) of Hardox |
| B4 | Overload (stone, root) must not break anything: current limits on spindle and axes |

### Safety
| # | Requirement |
| --- | --- |
| V1 | Spindle only runs with the pot on or just above the ground |
| V2 | Robot emergency stop = 48 V of the implement off (contactor); VESC brakes, Z motor holds on its brake |
| V3 | People > 5 m (autonomous). Mowing with the pot raised: rubber splash flap around the pot |

---

## 3. Construction and choices

### 3.1 Mounting on the robot (headstock)

The robot's rear lower beam (`rear_outer`, 40 × 40 × 2, y = −575, z 619–659) has M10 holes every 50 mm along x.
x = ±325/±425 are taken by the frame bolts of the wheel units and x = ±375 lies above the wooden block, so the free
holes are **x = ±225 and ±275**. Per side: a top plate on the beam and a clamp plate under it (4 × M10 through the
beam), a back plate against the rear face of the beam, an upright 50 × 50 × 3 (up to z 1110) and a gusset. A cross
tube 40 × 40 × 3 ties the uprights together and carries the E-box. Uprights at **x = ±250** (inside the rear tyres).

The pitching moment of the implement is taken by the bolts (tension) and the back plate (pressure on the beam).
With 2 g shock while driving: ≈ 2100 N per bolt, M10 8.8 proof load 33.7 kN, factor ≈ 16.

Why behind the **rear** axle: the front wheels have the steering stack (NEMA34 up to z 1032) and sweep; the rear
wheels are fixed. All four wheels are hub motors, so traction does not decide the side (the old scripts assumed a
2WD robot with driven and steered axles). The robot drives backwards while weeding: gantry first, camera on the X
slide sees the plant before the spindle.

### 3.2 X axis on PTO-shaft tubes (v2)

- **Fixed:** 2 inner tubes (lemon profile 49 × 39.5 × 4.5, L 1400) at z 760 and 1060. Each rests on 2 support
  ribs (10 mm, welded to the back of the tube) with a flange plate bolted to the uprights (4 × M10). End plates
  (steel 12 mm) tie the tubes together.
- **Moving:** 3 sleeves of the matching outer tube (57.5 × 48 × 4): 2 × 100 mm on the upper tube (220 apart),
  1 × 140 mm on the lower tube. A pad (8 mm) on each sleeve, bolted to the X slide (4 × M8).
- **Slot:** the robot side of every sleeve and scraper is sawn open (14 mm) so it passes the support ribs.
- **Not over-constrained:** slotted holes (±8 mm in z) for the lower sleeve. The lemon profile locks rotation, so one
  tube already guides; the second only adds stiffness.
- **Dirt:** rubber scrapers on both ends, one grease nipple per sleeve, the plastic strips of the PTO shaft inside.
- **Drive:** HTD-5M belt 15 mm with steel cord between the tubes, omega drive on the slide (pulley 20T + 2 idlers),
  NEMA 23 closed-loop + 5:1. Belt clamps at x ±670–685, outside the idler travel (the first scripts had the idlers
  hit the right clamp at x = +500). Inductive limit switch left, rubber stop right.

| PTO-tube guide | Value |
| --- | --- |
| Section | 544 mm², I = 118,700 mm⁴ (bending in z) / 86,700 mm⁴ (bending in y), 2 tubes 12.0 kg |
| Overhang to the outermost sleeve | 360 mm (uprights at ±250, slide at ±500) |
| Deflection in z under the moving mass (62 kg) | 0.45 mm |
| 600 N Z force at 234 mm lever → 468 N in y per tube | 0.96 mm per tube, slide twist 0.36° |
| Friction (μ 0.15, greased) | ≈ 190 N against 895 N belt force |

The overhang is longer than in the first v2 script (uprights at ±340 there), because the free holes on the real beam
are at ±225/±275. 0.96 mm at full Z force on the outermost position is acceptable for ±2 mm; keep the Z force limit.

### 3.3 Z axis and spindle

| Choice | Chosen | Alternatives |
| --- | --- | --- |
| Z guide | Tube 120 × 60 × 3 with 2 HGR15 rails, 4 carriages on the X slide | Tube-in-tube with PE strips (robust, more play) |
| Z drive | SFU1610 + NEMA 23 closed-loop **with brake** | Linear actuator 1500 N (simple, ~30 mm/s: cycle +10 s) |
| Spindle | BLDC 48 V 1.5 kW 3000 rpm, jaw coupling, shaft Ø 35 C45 in 2 × UCF207 (160 apart) | Belt 1:2 (more torque, extra parts) |
| Cutter | Hardox cross cutter Ø 180, 2 levels, 4 teeth, centring point | Earth auger (carries soil away: not wanted) |
| Pot | Stainless Ø 250 × 150, rests with its own weight (4.2 kg) on 2 rods Ø 16 in PE bushes | Spring-loaded (no room) |

**CNC trick:** the pot sensor is the probe. `G38.2` lowers Z until the pot touches the sward: that is the ground
level. The pot then hangs 30 mm below the cutter, so the cutter plunges 30 + 150 mm from there.

```gcode
G90 G0 X420            ; spindle above the plant (also while driving)
; spindle on via VESC (CAN) 1500 rpm
G38.2 Z-300 F6000      ; lower until the pot sensor switches = ground level
G91 G1 Z-180 F1500     ; 30 mm to the ground + 150 mm deep, 25 mm/s
G4 P1                  ; 1 s dwell
G1 Z180 F3000          ; back while turning, until the pot comes loose
G90 G0 Z0              ; driving position, spindle off (VESC brakes)
```

**Spindle motor.** BLDC 48 V 1.5–2 kW ±3000 rpm with Hall sensors, keyed shaft, flange, ≥ IP54 (go-kart class,
e.g. sold as MY1020D/Kunray). Direct drive: 4.8 Nm nominal, 750 W at 1500 rpm, 1.5 kW peak (VESC 2× current). The
VESC sets the speed, limits current (electronic slip clutch), measures current (slower plunge when it rises) and
brakes. Not: brushed motor (wear, no speed measurement), RC outrunner (dirt), hub motor (too slow), 230 V tools.

### 3.4 Cables

- **X:** cable chain on the upper tube, fixed end on a bracket on the left end plate, moving end on a driver on
  the slide. Its shape follows x (`dwd2_parts.chain_shapes`).
- **Z (new):** spiral cable from a bracket on the X slide (z 850, x −95) to the top plate of the Z slide. The first
  scripts anchored it on top of the slide, where the distance shrinks to 30 mm at full depth (a coil of 26 turns
  needs ≥ 234 mm). Now 308–788 mm. The camera mast moved to +x to stay clear of it.

### 3.5 Camera and light

Industrial USB3 camera and LED bar on an arm on the X slide, 300 mm behind the spindle: it looks at the ground where
the plant arrives (robot drives backwards). If the robot's own camera is used, the arm can go (−1.5 kg).

---

## 4. Cycle and capacity

| Phase | s |
| --- | --- |
| X to the plant (1/3 of the stroke) | 2.2 (can run while driving) |
| Z down until the pot touches | 2.8 |
| Plunge 180 mm at 25 mm/s | 7.2 |
| Dwell | 1.0 |
| Rise while turning (2× faster) | 3.6 |
| Z up to driving position | 2.8 |
| Robot stop / position / start | 4.0 |
| **Total** | **23.6 s → 153 plants/h** (168 when X moves while driving) |

Energy ≈ 2.8 Wh per plant (spindle + axes): 1000 plants ≈ 3 kWh. Cutting power 0.4–1.4 kW during the plunge
(specific energy 0.5–2 MJ/m³, **estimated**). For comparison: MEV Ampferfräse with tractor and driver, 50–200
holes/hour at 10 kW.

---

## 5. Mass and the robot's wheel loads (important)

| Group | kg |
| --- | --- |
| Z carriage + spindle bracket + spindle + motor | 41.5 |
| X axis (tubes, flanges, ribs, end plates, belt) | 19.3 |
| X carriage (sleeves, slide, motor, camera) | 13.7 |
| Headstock | 8.4 |
| Electrics | 5.9 |
| Pot / cutter / cables | 4.2 / 2.5 / 0.9 |
| **Total** | **96.4 kg**, centre of gravity y −784 (190 mm behind the beam), z 700 |

The implement hangs ≈ 280 mm behind the rear axle. Robot 150 kg with its centre of gravity midway (**estimated**):

| Situation | front axle | rear axle |
| --- | --- | --- |
| Robot alone | 75 kg | 75 kg |
| With the implement, driving position | **48 kg** | 199 kg |
| Same, battery (≈ 45 kg) 500 mm forward: robot cg +150 mm | 70 kg | 176 kg |
| Milling at x = 500, 300 N thrust | 62 kg | 149 kg |

- The front (steering) wheels get light: about 24 kg per wheel, 16 kg on one side with the slide at x ±500 (23 kg with the battery forward).
  Traction is no problem (4 hub motors), but steering gets poor and the robot pitches on bumps.
- **Therefore:** put the battery (or a second battery as useful counterweight) at the front of the robot; drive
  slowly with the gantry first; keep Z at the top while driving.
- The cutter thrust lifts the rear: max. ≈ 1050 N (x 0) / 920 N (x ±500) before the lightest wheel has 20 kg left.
  Limit the Z force to 600 N.
- Weigh the robot (scales under the wheels) and set `robot_kg`, `robot_cg_y` in `dwd2_params.py`.

Lighter (±10 kg): aluminium spindle bracket (−4 kg), X stroke 800 (−2 kg), robot camera instead of our own
(−1.5 kg), aluminium end plates and 6 mm ribs (−2 kg).

---

## 6. Control and electrical

- **48 V** from the robot via a 63 A fuse and a contactor in the emergency stop loop.
- **Spindle:** VESC 75/100 via CAN (same code as `VESC/`, `vesc_can.py`). ±15 A at 716 W, peaks 30–60 A; 10 mm².
- **X and Z:** NEMA 23 closed-loop 3 Nm. A "48 V" battery is 54–58 V when full while many NEMA 23 drivers go to
  ±50 V: use a DC/DC 48 → 36/24 V or 80 V drivers.
- **Controller:** ESP32 with FluidNC (e.g. MKS DLC32), G-code from the Jetson. Homing with inductive sensors
  (X-min, Z-top), probe input = pot sensor.
- **Interlocks:** spindle only below a safe Z; robot only drives with Z home; stepper alarm → spindle off, 50 mm up,
  retry; after 3× skip and log the position.
- **Log:** RTK position of every treated plant, to come back after 6–8 weeks and count regrowth.

---

## 7. What changed from the first scripts (dockweed_design_v2.py)

| Change | Why |
| --- | --- |
| Standard layout: `dwd2_params/parts/build/calc`, `animate_dwd2`, `make_gif_dwd2`, `run_in_freecad` | Same as the other implements (AGENTS.md); parts in robot coordinates, English names |
| Mounted on the **real robot model** behind the rear lower beam, on the hole grid (x ±225/±275) | The first scripts assumed cross beams at y −20/−470, a 700 mm wheelbase and 2WD; none of that matches `agbots/agbot design` |
| Uprights at ±250 (was ±340) | Free holes on the beam; overhang 360 mm, deflection recalculated |
| Axle loads for a 4WD robot with 1000 mm wheelbase, implement behind the rear axle | Real robot; front axle gets light (§ 5) |
| Belt clamps outside the idler travel | Idlers hit the right clamp at x = +500 |
| Pad bolts at ±40 in z (was ±35) | Bolt heads of the lower sleeve touched the Z carriages |
| Spiral cable anchored at z 850 on the X slide, camera mast to +x | Spiral cable could not compress at full depth; camera arm crossed it |
| Plunge stroke 30 + 150 mm in cycle and G-code | The pot touches 30 mm before the cutter reaches the ground |
| Moving sub-Parts (X carriage, Z carriage, tool, pot) and an animation on the robot | Animation and checks in all end positions |
| E-box on the cross tube, plate 3 mm | Uprights moved; lighter |

---

## 8. Parts list and cost (indicative, 2026, incl. VAT, not verified)

| Part | Qty | € approx. |
| --- | --- | --- |
| PTO inner tube lemon ≥ 1.5 m (cut to 1400) | 2 | 60–100 |
| PTO outer tube ≥ 0.4 m (2 × 100 + 1 × 140), strips, scrapers, grease nipples | 1 set | 30–50 |
| HGR15 rail + 2 carriages, 850 mm (Z) | 2 sets | 50–70 |
| SFU1610 L ≈ 950 + nut, BK12/BF12, nut housing, coupling | 1 set | 45–70 |
| NEMA 23 closed-loop 3 Nm + driver (X) / with brake (Z) | 1 + 1 | 150–200 |
| Planetary gearbox 5:1 | 1 | 35–50 |
| HTD-5M 15 mm steel cord 1.5 m + pulley 20T + 2 idlers | 1 | 25–40 |
| BLDC 48 V 1.5–2 kW 3000 rpm, Hall, keyed shaft + VESC 75/100 | 1 | 250–450 |
| 2 × UCF207, jaw coupling, shaft Ø 35 C45 (turning work) | 1 set | 70–110 |
| Pot Ø 250, rods, PE bushes, set rings, splash flap | 1 | 30–60 |
| Inductive sensors M12 (4), ESP32 FluidNC board | 1 set | 45–90 |
| E-box IP65, DC/DC, fuse, contactor, glands, cable chain, spiral cable | 1 | 100–150 |
| Camera + LED bar (if the robot camera is not used) | 1 | 50–150 |
| Steel tubes and laser parts (DXF, incl. Hardox) | — | 150–250 |
| Bolts, rivet nuts, paint | — | 50–80 |
| **Total** | | **≈ € 1,200 – 1,900** |

---

## 9. Open points

1. **Measure the PTO tubes** (section, wall, clearance), adjust `pto_*` and `sl_*`.
2. **Weigh the robot** and set the centre of gravity; decide where the battery goes (§ 5).
3. **Process trial first** (spindle bracket on a stand): 1000/1500/2000 rpm × 15/25/40 mm/s, count regrowth after
   6–8 weeks (Joost: ±20 %). This is the biggest uncertainty and costs ±€ 400.
4. Weld distortion of the ribs and pads: test piece first, check the sleeves still slide.
5. Cutter shape in wet clay/peat (sticking), stones (VESC current limit, shear pin in the flange?).
6. Hole patterns of motors and carriages on the slides: mark from the real parts (not in the DXF).
7. Software: max. plants per m² per round, log with RTK position.

## Sources

- Conversation with Joost Samsom (`inspiration/`) and WUR article "Ruud weet wel weg met ridderzuring"
  (Frits van Evert): cutter up to 15 cm, high speed, hole ~18 cm.
- MEV GmbH Ampferfräse: hole Ø 180 × 250 mm, ±10 kW hydraulic, 50–200 holes/hour.
- Regrowth of *Rumex* root fragments: https://www.researchgate.net/publication/344660399 and
  https://www.sciencedirect.com/science/article/pii/S0570178318300241
- Bruut OpenAgbot: https://github.com/JacobsFarm/Bruut_OpenAgbot and `agbots/agbot design`.
