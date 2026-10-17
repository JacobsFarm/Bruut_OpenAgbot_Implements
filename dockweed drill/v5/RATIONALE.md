# Dockweed drill v5: why it is designed this way

v5 keeps everything from v4 ([../v4/RATIONALE.md](../v4/RATIONALE.md): jack as the Z axis, PTO-tube X axis, can,
camera, spindle Ø 20 in 2 × UCP 204 with a tube 42.4 × 4 over the overhang). Only the spindle drive changes: the
800 W gearmotor in stock sits **directly above the spindle** with a **flexible jaw coupling**, no chain.

## 1. Layout

- **Motor on the spindle axis**, shaft down. The gearmotor has a foot parallel to its shaft (64 mm from the axis),
  so it is bolted to a **standing motor plate** (10 mm, in the v-z plane) at x +64..+74, welded on the top plate of
  the spindle bracket and braced with **2 gussets** (6 mm) in front of and behind the motor.
- Foot on **+x**, because the other sides are taken: −x is the spiral cable (x −95), the front (−v) is the outer tube
  of the jack (the motor plate would hit it when the inner tube slides up into it), the rear (+v) would put the
  motor off the spindle axis.
- The holes for the motor foot in the plate are slots in z (±3 mm): the motor is aligned on the coupling and then
  clamped. Radial offset and angle are taken up by the spider of the coupling (size 24: ≈ 0.2 mm, 1°), so the
  plate must be drilled true to the bearing plate.
- **Jaw coupling size 24** (GR / ROTEX type, spider 92 Sh A), hubs Ø 19 (motor, key 6) and Ø 20 (spindle, key 6),
  7 mm above the top plate. Size 19 (10 Nm) is too small: the motor gives 15.3 Nm nominal and ≈ 30 Nm at peak
  current. Size 24: 35 Nm nominal, 70 Nm max.
- The spindle shaft now ends in the lower hub (top 30 mm above the top plate) instead of carrying a sprocket.

## 2. What it costs: 500 rpm at the cutter

Without the chain the cutter turns at the motor speed. The gearmotor gives 500 rpm (listing), so:

| | v5 direct | v4 chain 3.17 : 1 |
| --- | --- | --- |
| Cutter | 500 rpm, tip speed 4.7 m/s | 1500 rpm, 14.1 m/s |
| Torque at the cutter | 15.3 Nm (30 Nm peak) | 4.7 Nm (9.4 Nm peak) |
| Chip per tooth | 0.75 mm | 0.25 mm |
| Mower | 500 rpm: blades do not cut | 1500 rpm |
| Critical speed of the spindle | cutter at 23 % | 69 % |

- **Good:** three times more torque at the cutter, so a stone or a thick root stalls it less easily; the spindle runs
  far below its critical speed; no chain to tension, oil or guard; fewer parts (−3.7 kg); shorter build.
- **Bad:** the cutter works more like a slow auger than a high-speed crusher. The roots are cut into thicker slices
  (0.75 mm per tooth at 25 mm/s plunge) and the soil is mixed less finely. Whether that is good enough for dock roots
  must be tried; if not, plunge slower (10 mm/s gives 0.3 mm per tooth, at the cost of cycle time) or go back to the
  chain of v4. The power needed is roughly the same (energy per volume of soil).
- **Mowing** with the hinged-blade disc is not possible at 500 rpm. Leave mowing to another implement, or use the
  v4 chain drive.
- **Height:** the motor top is 1.11 m above the ground in the driving position (v4: 0.81 m), still well below the
  jack head (1.76 m).
- **Mass:** 102.2 kg implement, 35.1 kg on the Z axis (v4: 38.8 kg): lifting needs 345 N against 450 N at rapid,
  a little more margin than v4.

## 3. Open points (v5)

1. Read the type plate of the motor (rpm, voltage) and measure the foot (width, hole distance across); set
   `motor_*`. If the motor turns faster than 500 rpm, the comparison above shifts in favour of v5.
2. Choose the jaw coupling (size 24, bores 19 and 20 with keyways) and check `jaw_*`.
3. Try the cutter at 500 rpm in real soil with dock roots: hole quality, root slices, current.
4. All open points of v4.
