# Spot sprayer with a folding 3.75 m boom: design rationale

11 October 2026. Model: `Spot_Sprayer_Boom.FCStd` (FreeCAD 1.1, generated with `build_ssp.py`). The figures come from
the model, from `ssp_calc.py` and from the animation (`animate_ssp.summary()`). Where something is assumed or
estimated, this is stated.

![the spot sprayer on the robot](previews/1_work_iso_on_robot.png)

---

## 1. Assignment

- A spray boom and a tank for spot spraying, on the standard Bruut OpenAgbot.
- A camera at the front that watches the strip ahead; the boom behind it.
- Boom 3.75 m with nozzles every 25 cm: a centre section and on the left and the right an element of 1.25 m that
  folds in and out **in the field**.
- The tank on the robot.

## 2. The design in brief

1. **Camera mast** at the front: plate under the two front lower beams (8 × M10), square tube 50 × 50 × 3 in front of
   the beams, two braces to the inner front beam. Camera on two tilt arms, 1.48 m high, 55° down. The robot's GNSS
   antenna on top.
2. **Tank** 120 l (PE) on a cradle of two cross tubes on the upper beams, two straps.
3. **Rear subframe:** one plate under the two rear lower beams (8 × M10) with two welded hanger webs and clamp plates
   for the boom; pump, filter and regulator hang under the plate, between the webs. Control box on top of the rear
   beams, behind the tank.
4. **Boom:** centre section (steel 40 × 40 × 2, 1.25 m, 5 nozzles) bolted to the clamp plates 105 mm behind the
   rear tyres; two aluminium wings (40 × 40 × 3, 1.25 m, 5 nozzles each) on a hinge with its axis along the driving
   direction, 25 mm above the tube. One 24 V linear actuator per wing.
5. **Wet boom:** stainless 1/2" pipe under the carrier tubes, 15 clamp-on nozzle bodies with a PWM solenoid valve each,
   40° flat-fan tips. Across each hinge the liquid goes through a swivel on the hinge axis.

| Characteristic | Value |
| --- | --- |
| Working width | 3.75 m, 15 nozzles at 250 mm |
| Detection → nozzle | 2.65 s at 1 m/s |
| Fold 0 → 90° | 3.2 s, max 449 N on a 1000 N actuator |
| Mass (model, tank empty) | 91 kg |
| Parts, roughly | ≈ €3,580 |

## 3. Camera at the front, boom at the rear

The assignment puts the camera in front. That is also the right place: the further the camera looks ahead of the
nozzles, the more time there is to detect, to decide and to open the valve, and the more frames a plant is seen in.

| Option | For | Against |
| --- | --- | --- |
| **Camera on a mast at the front, boom at the rear** (chosen) | 2.65 s and 2.6–5.6 m between seeing and spraying: no hurry for the computer, ≈ 60 looks per plant; the boom does not hang in the image; the robot's front is free | Plants are run over by the robot's own wheels before they are sprayed (only in the two tyre tracks); odometry must carry the position over 3–6 m |
| Boom at the front, camera just ahead of it | Short distance, little odometry error | Boom and mast in front of the steering stacks, the boom must clear the steering sweep; a 3.75 m boom in front makes the robot's front heavy and hard to see past; little time for detection |
| One camera per section on the boom (as large sprayers do) | Each camera looks straight down at a small strip, high resolution, no perspective | 3–5 cameras and their computing; the camera looks only ~0.5 m ahead of the nozzle: ≈ 0.5 s at 1 m/s; the cameras on the wings fold away with them |

A wheel track is 100 mm wide and the docks in grassland are much bigger; a flattened plant still gets its spot
(the spot is 50 mm larger than the plant on each side).

## 4. One wide-angle camera, high on a mast

The image must be at least as wide as the boom (3.75 m). A single camera can do that if it hangs high and has a wide
lens. Perspective helps: further ahead the image is wider but coarser. The usable band is where the image is at least
3.75 m wide **and** finer than 3 mm per pixel (a dock leaf is 50–300 mm; 3 mm/px is plenty for a detector):

- 2/3" sensor, 2448 × 2048 px, 3.45 µm, lens f = 4 mm → 93° × 83°;
- 1.48 m high (mast top at 1.56 m, below the GNSS antenna), pitched 55° down;
- the image is 3.75 m wide from 1.81 m ahead of the robot centre; 3 mm/px is reached at 4.78 m: a band of 3 m, at
  1 m/s and 20 frames/s ≈ 60 frames per plant. On the optical axis the resolution is 1.6 mm/px.

| y from the robot centre (`ssp_calc.camera(pitch=...)`) | Pitch 45° | **Pitch 55°** | Pitch 65° |
| --- | --- | --- | --- |
| Image as wide as the boom from | 1.86 m | **1.81 m** | 1.86 m |
| Band ends at | 4.27 m (3 mm/px) | **4.78 m (3 mm/px)** | 4.23 m (top edge of the image) |
| Frames per plant at 1 m/s | 48 | **59** | 47 |
| Top edge of the image on the ground | 24.7 m: half the image is useless far away | **7.0 m** | 4.2 m |
| Bottom edge of the image on the ground | 0.92 m | **0.66 m (under the camera)** | 0.39 m (behind the camera) |

55° gives the longest useful band; the pitch is not critical (±10° costs ≈ 20 % of the frames).

Global shutter: at 1 m/s a rolling shutter of 30 ms smears the image by 30 mm across its height and distorts the
positions; a global-shutter sensor exposes all rows at once (with 1 ms exposure, 1 mm motion blur).

The camera sits in an IP67 housing with a window and a hood against sun and rain, on two arms with a pivot: the pitch
is set once and calibrated (the camera-to-ground transformation is measured on a checkerboard on flat ground).

## 5. The GNSS antenna moves to the top of the mast

The robot's antenna stands on the front beam at 0.74 m, 150 mm behind where the mast must be. A 50 mm tube next to an
antenna shades a wedge of the sky of about 20° wide from the horizon almost to the zenith, and gives multipath: RTK
loses satellites straight ahead. Options:

- mast to one side (x ±250): still 0.28 m from the antenna, still a wedge of ≈ 10°;
- **antenna on top of the mast** (chosen): free sky all around, above everything else on the robot. The lever arm in
  the robot's configuration changes (antenna 1.65 m high, 145 mm further forward); roll and pitch from the IMU become
  more important (2° roll = 58 mm at 1.65 m), but spot spraying does not need GNSS for the hit: the plant position
  comes from the camera, odometry carries it to the boom. GNSS is used for the map of sprayed spots and the field
  boundaries.

The mast plate has a 40 mm hole around the old antenna stud, so the stud can stay or be removed.

## 6. Folding: vertical, with an actuator, also in the field

| Option | For | Against |
| --- | --- | --- |
| **Wings fold up to vertical** (chosen) | Fast (3.2 s), needs no room beside or behind the robot, works while driving; folded width 1.61 m (less than a field gate) | Folded height 1.85 m; the cg goes up (still 28° tip angle full) |
| Wings fold forward along the robot's sides | Low cg | The wing (1.25 m) would sweep past the rear wheels and the steering stacks; the robot is only 1.43 m long; needs a second hinge or a slide |
| Wings fold back and up over the centre | Compact | Two wings of 1.25 m on a centre of 1.25 m overlap each other; a fold of 180° needs a much longer actuator stroke |
| Breakaway only, no actuator | Cheap | Cannot fold for a post on purpose; the nozzles hit the post first |

**Hinge.** The axis lies along the driving direction, 25 mm above the top of the tube, at the joint (x ±625). The
wing and centre tube have welded end plates that touch below the hinge: gravity and bumps press them together, so at
0° the wing rests on a hard stop and the actuator only lifts. Folding up opens the joint (every point below the
hinge moves outward). The fixed lugs are chamfered below the pin so the top corner of the wing can pass.

**Actuator geometry.** Lever pin on the wing 90 mm from the hinge, 45° up and out; actuator base 420 mm inside the
hinge, at the same height. Then the actuator is exactly horizontal at 0° and at 90°, and tilts only 3.6° in between.
Its length goes from 484 mm (working) to 356 mm (folded): 127 mm of the 150 mm stroke, with 6 mm left before its end
at 90° and 16 mm at 0°, so that the actuator never pulls the wing off its stop. The lever arm about the hinge is
64 mm at both ends and 90 mm at 45°.

| Fold angle | 0° | 30° | 60° | 90° |
| --- | --- | --- | --- | --- |
| Actuator length (mm) | 484 | 444 | 397 | 356 |
| Lever arm (mm) | 64 | 86 | 88 | 64 |
| Gravity torque (Nm) | 29 | 26 | 17 | 3 |
| Force (N) | 449 | 308 | 194 | 51 |

A 24 V actuator of 1000 N gives × 2.2 reserve for acceleration, friction, wind and a wet, dirty boom. At 40 mm/s a full
fold takes 3.2 s. The actuator is self-locking: when folded, the wing stays up when the power is off.

**Obstacle.** At 1 m/s the robot drives 3.2 m while the wing folds. The post must therefore be known 3.4 m before the
boom reaches it: from the field map (fence lines, trees) or from the camera, which sees up to 4.8 m ahead of the robot
centre (5.6 m ahead of the boom). For a low obstacle 60° is enough (2.2 s). The nozzles of a wing are off as soon as
it leaves 0°: the strip it misses is 4.7 m (to 60° and back) to 6.7 m (to 90° and back) and is logged; the next pass
in the other direction sprays it, or the robot slows down near posts (at 0.5 m/s the strip is half as long).

## 7. Boom section, nozzles and plumbing

**Carrier tube above, wet pipe below.** The square tube carries; the stainless 1/2" pipe hangs 5 mm under it on clips,
the nozzle bodies clamp onto the pipe from below. The pipe is filled and under pressure all the time (constant
pressure, the bypass regulator keeps it at 3 bar); each nozzle has its own PWM solenoid valve right above the tip, so
there is no hose between valve and tip that empties or drips. The coils point backwards, away from the clamp plates.

**Nozzle height and angle.** With 40° fans at 400 mm the fan is 291 mm wide on the ground: 41 mm overlap with the
neighbours at 250 mm spacing. A narrow fan close to the ground keeps the spot sharp and reduces drift (the classic
80°–110° fans at 500 mm would spray 0.8–1.4 m wide per nozzle: no spot resolution of 250 mm). The tube can be bolted
50 mm higher or lower on the clamp plates for tall grass or for a sharper spot.

**Spot.** The nozzles open 50 mm before the plant and close 50 mm after it; the valve time of 25 ms (25 mm at 1 m/s) is
compensated by switching early. Across, every nozzle whose 250 mm strip touches the plant plus margin opens: a Ø300
plant needs 2–3 nozzles.

**Dose.** Size 015 at 3 bar: 0.59 l/min per nozzle = 393 l/ha at 1 m/s where it sprays, the usual blanket rate for a
herbicide in water. With 5 % of the field sprayed that is ≈ 20 l/ha: 120 l covers ≈ 6 ha. The animation sprays 139 ml
on 16 m × 3.75 m with 14 docks, where blanket spraying would use 2.4 l: 94 % less.

**Pump.** A 24 V diaphragm pump of 11 l/min (9.5 l/min at 3 bar) feeds all 15 nozzles at once (8.8 l/min); in normal
spot work 2–6 are open and the rest goes back through the bypass into the tank (submerged return: no foam, and the
return keeps the liquid mixed). The pump hangs below the tank bottom: it is always flooded. Suction filter 50 mesh
before the pump; the nozzle tips have their own strainers.

**Hinge swivel.** The pipe goes across the hinge through a swivel on the hinge axis, behind the hinge pin: a hose
along the axis would also work, a hose loop across the joint would bend 90° at every fold and wear.

## 8. Tank on the robot

- 120 l (800 × 720 × 240, PE 6 mm) on the same kind of cradle as the mobile refiller and the receiver kit: two cross
  tubes on the upper beams at y −375 and 275, rubber strips, two straps. The front stays 85 mm behind the stepper
  plates of the steering.
- Full, the tank is the biggest single mass (120 kg); its centre is 40 mm behind the robot centre, the boom (24 kg)
  hangs 840 mm behind it. Axle loads full: rear 203 kg, front 169 kg (45 % front); max 102 kg per wheel of the
  500 kg the hub motor allows.
- 120 l and not more: at 5 % cover that is ≈ 6 ha, the battery lasts ≈ 4.3 ha. A bigger tank would make the robot
  heavier on wet grassland without a longer working day. Refilling: the mobile refiller can top it up.
- Two bottom fittings between the cradle tubes: suction and the bypass return. Level sensor (ultrasonic) in the lid.

## 9. Mounting on the robot

- **Rear:** one subframe plate under the rear lower beams, 8 × M10 through the hole grid (x ±125, ±175). The same bolts
  clamp the base plate of the control box on top of the beams (sandwich). The hanger webs (x ±150) lie between the pump
  in the middle and the wheel brackets (x 261); the rear mount stays 20 mm from the wooden blocks.
- **Front:** one plate under the two front lower beams, 8 × M10, tapered to ±80 mm in front of the beams, with a
  window between the beams. At 30° steering the wheel units stay 48 mm from it. The braces land on foot plates on top
  of the inner front beam, on the same bolts.
- Nothing is drilled in the robot; the two plates replace no robot parts.

## 10. Checks

- `check_interference()`: no overlap between any two of the 59 sprayer parts and with the robot (visible and hidden).
- `check_fit()`: no overlap over the fold 0–92° of both wings (wings, actuator bodies and rods against each other, the
  centre section, the mount and the robot).
- `animate_ssp.check_fit()`: no overlap in the fold angles of the animation.
- Strength (× 2.5 for bumps): aluminium wing at the hinge 14 MPa, steel centre tube at the clamp plates 40 MPa, hinge
  pin 1.6 kN, 4 MPa; the 8 subframe bolts 0.4 kN each.

## 11. Open points

- The detector: training data for dock, thistle and nettle in grass of different heights; how well it works decides
  the margin and the spot size.
- Wind: at 400 mm and size 015 drift is small, but a shroud or air-induction tips can be added for windy days.
- A breakaway in the wings (spring-loaded) for an obstacle that was not on the map and not seen.
- Lighting for work at dusk or at night (LED bar under the camera, flashed with the exposure).
- Hose loops of the swivels and the cables of the coils on the wings are not modelled.
