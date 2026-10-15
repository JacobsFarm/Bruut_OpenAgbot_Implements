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
- The original foot is replaced by a **foot plate** on the inner tube. The **orange spindle bracket of v2** (back
  plate, 2 bearing plates, motor plate, side plates, 2 × UCF207, BLDC motor on top) is bolted to the rear face of
  the inner tube, 40 mm higher than in v2 so the higher can of v3 fits.
- **Play:** as delivered there is 1–2 mm play between the tubes. A PE bush at the bottom of the outer tube and a PE
  ring on top of the inner tube (shimmed) bring it to ≈ 0.3 mm. Overlap between bush and ring: 245 mm at
  150 mm depth.
- **Spiral cable:** from the motor plate of the spindle bracket up to an arm on the jack's outer tube (x −95).

## 3. What it costs: speed and stiffness

The jack is made for hand cranking (≈ 60 rpm). A motor can turn it faster, but not without limit:

| | v4 (jack) | v2/v3 |
| --- | --- | --- |
| Rapid Z | 40 mm/s (400 crank rpm, 6 mm per turn) | 100 mm/s |
| Force | 620 N at plunge speed, 450 N at rapid (lifting 32 kg needs 320 N) | 1700–2060 N |
| Cycle | 26.1 s → 138 plants/h | 23.6 s → 153 plants/h |
| Cutter wobble at 300 N side force (150 deep) | 2.6 mm: 1.4 mm bending of the 2" inner tube (460 mm free length) + 1.3 mm play | < 0.5 mm |

- **Speed:** 2.5 s slower per plant (−10 %). The jack only moves 150 mm between driving position and ground
  (driving position 180 instead of 280), which helps. With a jack with a coarser screw (fast gear ≈ 10 mm/turn)
  the cycle comes back to v2.
- **Force:** the plunge needs 150–300 N (estimated); the software limit stays at 600 N. When lifting, 450 N against
  320 N weight leaves little margin: use the full motor current at rapid, or drop to 30 mm/s.
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
| Implement | 96.4 kg | 95.0 kg | 99.4 kg |
| Z moving | 44.0 kg | 35.0 kg | 32.3 kg |

Cost of the Z axis (indicative, 2026, incl. VAT, not verified):

| v4 part | € |
| --- | --- |
| Drop-leg jack 7000 lb, side wind, 15" (2.5"/2") | 70–110 |
| NEMA 23 closed-loop + driver (no brake), jaw coupling, motor bracket | 70–95 |
| Mounting plate, foot plate (laser), PE strips, bolts | 20–25 |
| Spindle bracket (5 laser plates) + 2 × UCF207 (as v2) | 80–110 |
| **Z axis + spindle bearing housing** | **≈ 240–340** |
| v2: HGR15 + carriages + ball screw kit + brake motor + spindle bracket | ≈ 275–380 |
| v3: mast + 8 rollers + worm gearbox + rack + bearing cartridge | ≈ 235–335 |

The spindle bracket (2 × UCF207, plates) is as in v2; the can and camera as in v3. So v4 costs about the same as v3 and ≈ € 40 less than v2. Its gain is not price but simplicity: the jack is one
off-the-shelf part (no rails to align, no roller cages, no turning work), the fastest to build: buy, bolt on, couple
the motor. The price is 10 % capacity and more wobble under side load.

## 5. Open points (v4)

1. **Buy one jack and measure it:** tubes, play, lead per crank turn (fast gear), head dimensions; set the `jack_*`
   parameters.
2. Run it with the NEMA 23 on the bench: max. crank speed without overheating, force at 250 and 400 rpm.
3. Shim the play with PE strips (or bronze/PE plates with set screws) and measure the wobble at the cutter.
4. Endurance: 1000 strokes on the bench, check the nut and the bevel gear.
5. All open points of v2/v3.
