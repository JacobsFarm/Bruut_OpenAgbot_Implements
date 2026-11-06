# Dockweed drill v7: why it is designed this way

v7 keeps the process and the spindle of v6 ([../v6/RATIONALE.md](../v6/RATIONALE.md): 800 W gearmotor directly on
a Ø 30 spindle via a jaw coupling, 500 rpm, Ruud-style can Ø 219, Linak LA36, fixed high camera). The brief: "a good
v7 with the Z axis on the Linak and no left-right axis, so only up and down", made as simple as possible to build
with easy parts.

**Status:** v7 is above all the design of the Z part; an X axis still has to be added. Sections 2 (mount plate) to 4
stay valid then, with the mount plate as the interface to the X slide. Section 1 applies until the X axis is there.
On an X axis the plate should be narrower and lighter (now 420 mm wide, 10 mm steel, about 13 kg).

## 1. No X axis: the robot steers to the plant

The X axis of v1–v6 (1000 mm stroke) was the biggest and most expensive part of the machine: two PTO tubes or rails,
a slide, a belt drive, a stepper, a cable chain and the frame to hold it all. Without it:

- **The spindle sits fixed at x 0**, 370 mm behind the rear axle (robot y −870).
- **Sideways** the robot steers on the way to the plant. When the robot stands straight, the spindle is exactly
  behind the centre of the rear axle, so the rear axle simply has to drive along a line that ends at the plant. With
  30° steering the smallest radius is 1732 mm (wheelbase 1000). An S-bend of two arcs moves the spindle:

  | Sideways | Travel needed (2 arcs) | Smooth bend | Max. heading |
  | --- | --- | --- | --- |
  | 100 mm | 0.83 m | 0.93 m | 14° |
  | 250 mm | 1.29 m | 1.46 m | 22° |
  | 500 mm | 1.79 m | 2.07 m | 31° |

- **Along the row** the robot stops with the plant under the spindle, as before.

What this costs:

- The robot must **see the plant 1–2 m ahead**. The fixed camera at 1.9 m sees that far behind the robot, or the
  plants come from a map (RTK) made on an earlier pass.
- Two plants **side by side** (closer than ~1.5 m apart along the row but far apart across it) cannot both be done in
  one pass: the robot does one and comes back for the other. In a pasture with scattered dock plants (often a minute
  between plants) the steering happens while driving and costs almost nothing.
- **Accuracy** across the row now comes from steering, not from an X axis with a closed-loop stepper. The can (Ø 219)
  around the Ø 180 cutter allows about ±40 mm around the root crown (`position_tol`). If the robot stops further off,
  it has to back up and approach again (~2 m). This is the main open point.

What it gains: **−23 kg** (99.9 instead of 122.9 kg), the spindle 64 mm closer to the robot (less load off the front
axle: front 49 kg instead of 39 kg when driving), no belt, no X motor and driver, no cable chain, and a shorter cycle
per plant (21.8 s instead of 24.0 s, no X move).

## 2. Frame: two cross beams and a mount plate

- The headstock is the same as v6: 2 uprights 40 × 40 × 3 on the hole grid of the rear lower beam (x ±225/±275).
- **2 cross beams 40 × 40 × 3** at z 760 and 1060, directly behind the uprights, 1 × M12 per crossing, 20 mm past the
  uprights. They only carry the Z frame: 0.02 mm deflection at the 600 N Z force.
- **Z mount plate**, steel 10 mm, 420 × 420 with a tab up to z 1450 for the top pin of the actuator. 4 × M10 at
  x ±180 through plate and beams (outside the bush housings, so the heads are free).

## 3. Z guide: 2 round tubes in plain bushes

From the discussion after v6: round tubes are easier than PTO tubes, and two of them side by side cannot turn, so the
lemon profile is not needed. Hollow is stiffer per kilo than solid.

| | Ø 50 × 4 tube (v7) | PTO tube (v6) | Solid Ø 40 bar |
| --- | --- | --- | --- |
| Mass | 4.5 kg/m | ≈ 4.3 kg/m | 9.9 kg/m |
| I (bending) | 154 000 mm⁴, the same in every direction | lower in the thin direction | 126 000 mm⁴ |
| Holes in plates | drilled round | lemon shape, laser | drilled round |
| Bushes | bought (iglidur / POM in a housing) | sawn from the outer tube, welded in saddles | bought |
| Wipers | standard rod wipers | made | standard |

- **Tube:** cold drawn seamless precision tube E355 (EN 10305-1), from a steel stockist. Smooth and round, no seam.
  Not galvanised (the zinc wears away under a bush); grease it.
- **Bush housings:** 4 housings with a plastic plain bush (e.g. igus drylin RJUM-06 or an SC50-type housing with an
  iglidur liner), bolted from behind with 4 × M8 into the tapped mount plate. Not ball bushings: too sensitive to dirt.
  Rubber wipers above and below each housing and a grease nipple on the back.
- **x ±90** (v6 ±64): the X gearbox that limited v6 is gone, and wider tubes resist the tilting from the spindle
  behind the actuator better. The actuator tube (±22) passes between the housings with 18 mm to spare.
- **Fixing the tubes:** they stand on the 10 mm lower yoke and pass through the 10 mm clamp plate 60 mm higher, both
  welded to the back plate of the spindle bracket. Weld them **with the tubes in the housings on the machine**: the
  housings hold them parallel, so nothing has to be aligned afterwards. Let one housing per tube float a little
  (slotted holes or 0.3 mm more clearance), so two guides that are not perfectly parallel do not jam.

Forces (300 N side force on the cutter, 600 N Z force): 585 / 435 N on the lower / upper housing per tube, plus
124 N from the spindle sitting behind the actuator. Bush pressure 0.17 MPa (iglidur allows tens of MPa). The tubes
overhang 490 mm below the lower housing at 150 deep: 1.3 mm at the cutter, 21–27 MPa. With the 1.1 mm of the spindle
shaft the cutter moves 2.4 mm under a hard side load; fine for a Ø 180 hole. Friction (μ 0.15) adds 380 N while
cutting; the LA36 has a margin of 3.2 pushing and 2.4 lifting.

## 4. The LA36 duty cycle

Per plant the actuator runs 16.8 s: down 3.0 s (2.4 A), plunge 7.2 s (5.0 A), rise 3.6 s (5.6 A), up 3.0 s (5.6 A).
The datasheet allows 20 % duty **at full load** (10.3 A). The heat in the motor goes roughly with I², so the
comparison is the mean I² over time:

| Time between plants | Duty | Mean I² | Against the allowed 21.2 A² |
| --- | --- | --- | --- |
| 21.8 s (back to back) | 77 % | 18.6 A² | 88 % |
| 60 s (typical in the field) | 28 % | 6.8 A² | **32 %** |

From about 19 s per plant the LA36 stays within its copper-loss budget. This is a rule of thumb, not a Linak figure:
idle losses, sun on the housing and the longest on-time in a row are not in it. In the controller, keep a running
I²·t over 20 minutes and pause a few seconds when it passes 21 A² (a dense patch of dock). Wear depends on the number
of strokes, so ask Linak for the expected life at 540–710 N.

## 5. What stayed from v6

Spindle bracket, Ø 30 shaft in 2 × UCP 206, jaw coupling size 28, 800 W gearmotor directly on the spindle (500 rpm),
can, camera, E-box and headstock are unchanged. The relative positions of mount plate, actuator and spindle bracket
are the same as v6's X slide, actuator and spindle bracket, so the actuator housing still clears the spindle motor
by 10 mm in the driving position. There is no mowing disc: 500 rpm is too slow for it.

## 6. Open points (v7)

1. **Steering accuracy:** test how close the robot stops to a marked point after an S-bend (target ±40 mm across the
   row), with RTK and with the camera correcting on the last metre.
2. Buy the bush housings and the tube, set `zg_house*` and `zg_hc`, and check the friction (μ 0.15 assumed).
3. Weld yoke and clamp plate with the tubes in the housings; check that the carriage slides freely over the full
   400 mm stroke.
4. LA36: bench test the real cycle (with ~600 N) for 1–2 hours and measure the housing temperature; ask Linak about
   duty and life at this load profile.
5. Animation with the robot steering to plants that are off the centre line (not made yet).
6. All open points of v6 (motor type plate, 500 rpm in real soil).
