# Dockweed drill v4: why it is designed this way

v4 keeps everything from v3 ([../v3/RATIONALE.md](../v3/RATIONALE.md): X axis on PTO tubes, Ruud-style can, fixed
high camera, mounting on the robot) and takes the idea of a **trailer jack as the Z axis**.

## 1. Which jack

| Type | Fit | Why |
| --- | --- | --- |
| Round caravan/trailer jack with jockey wheel (Ø 48–60) | ✗ | Round tubes rotate; stroke 150–250 mm; light |
| Square **side-wind drop-leg jack** (2.5" outer / 2" inner, 7000 lb, 15" stroke) | ✓ chosen | Square tubes do not rotate (anti-rotation for free), 380 mm stroke, trapezoidal screw + bevel gear in a sealed head, made for weather and dirt, crank on the side where a motor can go |
| Electric 12 V tongue jack | ✗ | Round, slow (≈ 5–10 mm/s), short stroke |

The drop-leg jack is everything a Z axis needs in one part: guide (the two tubes), screw and nut, gearbox and
housing. It costs about as much as one HGR15 rail set.

## 2. How it is built in

- The **outer tube** is bolted to the X slide with a mounting plate (8 mm, 4 × M10), from z 910 to 1670, head on
  top. The jack is mounted "upside down" from its normal use: the inner tube moves down.
- The **NEMA 23 closed-loop** sits directly on the crank shaft of the head (+x side), with a jaw coupling.
- The original foot is replaced by a **foot plate** on the inner tube. The **orange spindle bracket** (back
  plate, lower plate, standing bearing plate with 2 × UCP 204, top plate, side plates; 800 W gearmotor behind it with a chain, see section 5) is bolted to the rear face of
  the inner tube, 40 mm higher than in v2 so the higher can of v3 fits.
- **Play:** as delivered there is 1–2 mm play between the tubes. A PE bush at the bottom of the outer tube and a PE
  ring on top of the inner tube (shimmed) bring it to ≈ 0.3 mm. Overlap between bush and ring: 245 mm at
  150 mm depth.
- **Spiral cable:** from the top plate of the spindle bracket up to an arm on the jack's outer tube (x −95).

## 3. What it costs: speed and stiffness

The jack is made for hand cranking (≈ 60 rpm). A motor can turn it faster, but not without limit:

| | v4 (jack) | v2/v3 |
| --- | --- | --- |
| Rapid Z | 40 mm/s (400 crank rpm, 6 mm per turn) | 100 mm/s |
| Force | 620 N at plunge speed, 450 N at rapid (lifting 39 kg needs 380 N) | 1700–2060 N |
| Cycle | 26.1 s → 138 plants/h | 23.6 s → 153 plants/h |
| Cutter wobble at 300 N side force (150 deep) | 2.6 mm: 1.4 mm bending of the 2" inner tube (460 mm free length) + 1.3 mm play | < 0.5 mm |

- **Speed:** 2.5 s slower per plant (−10 %). The jack only moves 150 mm between driving position and ground
  (driving position 180 instead of 280), which helps. With a jack with a coarser screw (fast gear ≈ 10 mm/turn)
  the cycle comes back to v2.
- **Force:** the plunge needs 150–300 N (estimated); the software limit stays at 600 N. When lifting, 450 N against
  380 N weight leaves little margin: use the full motor current at rapid, or drop to 30 mm/s.
- **Accuracy:** ±2.6 mm at the cutter with a hard side load (stone, root). For a Ø 180 hole around a dock plant
  that is acceptable; the positioning accuracy without side load stays ±1 mm (closed-loop motor, trapezoidal screw
  without lost motion when it always approaches from above).
- **Self-locking:** trapezoidal screw efficiency ≈ 0.3 < 0.5: the inner tube stays put without power. No brake
  motor.
- **Wear:** a trailer jack is made for a few hundred strokes a year; here it does 150 per hour. Grease the screw
  every day of work and expect to replace the jack once a season (it is a cheap part). Check the temperature of the
  nut in the first trials.

## 4. Mass and cost

| | v2 | v3 | v4 |
| --- | --- | --- | --- |
| Implement | 96.4 kg | 95.0 kg | 105.9 kg (99.4 with the BLDC) |
| Z moving | 44.0 kg | 35.0 kg | 38.8 kg (32.3 with the BLDC) |

Cost of the Z axis (indicative, 2026, incl. VAT, not verified):

| v4 part | € |
| --- | --- |
| Drop-leg jack 7000 lb, side wind, 15" (2.5"/2") | 70–110 |
| NEMA 23 closed-loop + driver (no brake), jaw coupling, motor bracket | 70–95 |
| Mounting plate, foot plate (laser), PE strips, bolts | 20–25 |
| Spindle bracket (7 laser plates incl. bearing and motor plate), 2 × UCP 204 and the 800 W motor in stock; sprockets 38T + bus, 12T, 10B chain, guard | 70–100 |
| **Z axis + spindle bearing housing** | **≈ 230–330** (without the motor and bearings in stock) |
| v2: HGR15 + carriages + ball screw kit + brake motor + spindle bracket | ≈ 275–380 |
| v3: mast + 8 rollers + worm gearbox + rack + bearing cartridge | ≈ 235–335 |

The can and camera are as in v3; the spindle drive uses the 800 W gearmotor and the UCP 204 bearings in stock (section 5). So v4 costs about the same as v3 and ≈ € 40 less than v2. Its gain is not price but simplicity: the jack is one
off-the-shelf part (no rails to align, no roller cages, no turning work), the fastest to build: buy, bolt on, couple
the motor. The price is 10 % capacity and more wobble under side load.

## 5. Spindle drive: 800 W gearmotor and 2 × UCP 204 (parts in stock)

The BLDC 1500 W on top of the spindle with a jaw coupling, the Ø 35 shaft and the 2 × UCF207 are replaced by parts
that are already in stock (`parts/800 watt motor`, `parts/lagers/UCP 204`):

- **Motor:** 800 W, 48 V brushed gearmotor with a foot, **500 rpm** output (listing, check the type plate), Ø 19 h6
  shaft with key 6 × 6. It cannot sit on the spindle axis (500 rpm is too slow for the cutter), so it stands upright
  **behind the spindle** (+v, away from the robot, x 0), shaft up, foot towards the spindle on a 10 mm motor plate.
  The motor plate has two tabs that bolt into slots in the (longer) side plates: sliding it along the chain sets the
  chain tension (±6 mm).
  Behind and not beside the spindle, because the pot rods (x ±100) slide up through the side of the bracket when the
  can lands; a motor at the side was hit by the rods in the deep positions.
- **Chain:** 10B-1 (the standard size for the robot, `parts/Kettingwielen`), 38T Taper-Lock 2012 with bush 19 on the
  motor → 12T bore 20 on the spindle: 3.17 : 1 up, max. 1583 rpm, the controller runs the cutter at 1500 rpm.
  50 links, centre distance 187 mm, wrap 139° on the 12T, chain speed 5.0 m/s (drip or spray oil), pull at peak
  torque 320 N (break load 22.2 kN). A 2 mm chain guard over the top, open at the bottom.
- **Bearings:** 2 × UCP 204 pillow blocks (shaft Ø 20, bolt distance 95, shaft height 33.3). The shaft is vertical,
  so the feet bolt (M12, slots in z) against a **standing 10 mm bearing plate** between the side plates; bearing
  distance 140. The spindle axis stays at y −886, so the can, the tools and the robot clearances do not change.
- **Shaft:** Ø 20 alone is too weak for the 407 mm overhang to the cutting level (it would bend 5 mm at 300 N and
  have its critical speed below 1500 rpm). Below the lower bearing the shaft is therefore a **tube 42.4 × 4** welded
  to the spindle flange, with a plug that takes the Ø 20 shaft (welded, 30 mm). Ø 20 runs only through the bearings
  and up to the sprocket.

| | v4 now (800 W + UCP 204) | v4 before (BLDC 1500 W + UCF207) |
| --- | --- | --- |
| Cutter torque (nominal) | 4.7 Nm at 1500 rpm, 735 W; peak ×2 for a short time | 4.8 Nm, 750 W at 1500 rpm (1500 W at 3000 rpm when mowing) |
| Cut power needed (estimated, 25 mm/s plunge) | 400 / 720 / 1350 W (soft / normal / hard) | same |
| Mower | 1500 rpm, tip 18 m/s (same spindle speed) | 3000 rpm, 36 m/s |
| Deflection at 300 N side force | 2.35 mm (0.4 mm tube, 1.9 mm from the Ø 20 between the bearings) | 0.56 mm |
| Stress Ø 20 at the lower bearing | 155 MPa at 300 N (shock load, C45 ok; fatigue not for a continuous 300 N) | 28 MPa |
| Bearing loads at 300 N | 1170 / 870 N (UCP 204: C = 12.8 kN) | 1040 / 740 N (UCF207) |
| Critical speed | 2160 rpm: cutter at 69 % | 4400 rpm |
| Z moving mass | 38.8 kg | 32.3 kg |

What this costs:

- **Power:** normal soil fits the 800 W; in hard soil (1350 W) the motor runs on its peak current. Lower the plunge
  speed when the current stays high (the controller already sees it), e.g. 15 mm/s in hard ground.
- **Mowing:** with the fixed chain ratio the mowing disc runs at 1500 rpm (tip 18 m/s) instead of 3000 rpm. That cuts
  leaves with hinged blades poorly; for mowing a ratio of 38/10 or a second sprocket pair would be needed, or leave
  mowing to another implement.
- **Stiffness:** the cutter moves 2.35 mm at a hard side load (stone): with the 2.6 mm of the jack that makes ≈ 5 mm.
  For a Ø 180 hole that is still acceptable. The Ø 20 between the bearings is the weak part; a shorter bearing
  distance helps the stiffness but raises the bearing loads.
- **Z axis:** the moving mass rises from 32 to 39 kg (motor 9 kg instead of 6.5, sprockets, chain, tube): lifting
  needs 380 N, rapid gives 450 N. Little margin: drop rapid to 30 mm/s if the jack stalls.
- **Axle load:** the motor 190 mm further back takes ≈ 5 kg off the front axle when driving (43 kg instead of 48;
  70 → 65 kg with the battery forward).

## 6. Open points (v4)

1. **Buy one jack and measure it:** tubes, play, lead per crank turn (fast gear), head dimensions; set the `jack_*`
   parameters.
2. Run it with the NEMA 23 on the bench: max. crank speed without overheating, force at 250 and 400 rpm.
3. Shim the play with PE strips (or bronze/PE plates with set screws) and measure the wobble at the cutter.
4. Endurance: 1000 strokes on the bench, check the nut and the bevel gear.
5. Spindle drive: read the type plate of the 800 W motor (rpm, voltage), measure the foot (width, hole distance
   across) and set `motor_*`; order the 12T sprocket with a 20 mm bore (not in the price list, which has 16/19/30)
   or bore one out; check the critical speed with the cutter mounted (run up slowly to 1500 rpm).
6. All open points of v2/v3.
