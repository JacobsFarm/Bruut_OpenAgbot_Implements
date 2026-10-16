# Triple sickle bar mower: design rationale

Why the mower looks the way it does, and where the numbers come from. Usage, parts list and files are in the
[README](README.md); the concept is in the [concept README](../README.md).

## 1. Assignment

A triple sickle bar mower for the Bruut OpenAgbot: one bar **on the front** of the robot and two **in the middle of
the robot frame**, with a cut width of **1.25 m in front and 1 m on each side, 3.25 m in total**.

## 2. The design in brief

Three double-knife cutter bars, all the same module (bar, two knives, crank gearbox, 48 V BLDC motor), only the
length differs. The front bar hangs on a parallel linkage under the front beams (as the weed picker) with a float link
and a roll pin. The wings hang on a mid frame that is bolted under the outer top beams, each on a hinge at its inner
shoe; an actuator per wing folds it up for transport and lets it float while working. The knife drive of each wing
sits at its outer end, of the front bar on the right.

## 3. Options

| Choice | Options | Chosen, because |
| --- | --- | --- |
| Knife | single knife with guards (finger bar), **double knife** without guards | double knife: half the power, cuts at low knife speed, the opposite knives cancel the inertia forces (< 20 N left instead of 550–670 N, § 7): the light robot does not shake. Less trouble with stones and molehills than fingers |
| Drive | wobble box, **2 cranks 180° apart**, hydraulic | 2 cranks with con-rods: simple, can be made from 2 spur gears 1:1; the BLDC driver sets the speed |
| Wing position | behind the robot, **between the axles** | asked; it also keeps the robot short and puts the wing weight next to the robot's centre of gravity. The wheels do not run on the wing strips |
| Wing mount | on the wheel brackets, **mid frame under the top beams** | the top beams have grid holes from y ± 275, the lower beams only at the axles; a frame with a cross tube at y 0 spreads the loads over 8 bolts and carries both hinges and both actuators |
| Wing drive end | inner end, **outer end** | the wing folds about a hinge at its inner shoe. Anything above the bar at the inner end swings down when folding (a gearbox there would hit the ground at 90°). At the outer end the motor ends up on top, above the robot (z ≈ 1.45 m) |
| Folding | cable and winch, slewing drive, **linear actuator + lever** | a 4000 N actuator from a post in the middle on a 150 mm lever: monotonic over 0–90°, 384–611 mm pin to pin, same type of part as the front lift. The slot of its anchor gives the float for free |
| Front float | rigid, **parallel linkage + float link + roll pin** | keeps the bar level when lifting, follows bumps (float link) and side slopes (roll pin ± 6°) |

## 4. Dimensions

- **Cut widths exactly as asked: 1250 + 2 × 1000 = 3250 mm, no overlap.** The wing knives start at x ± 625, where the
  front knife ends. Driving straight that leaves no strip; when the robot steers, a strip can stay standing at the
  inside of the turn. Making the wings 50–100 mm longer (or moving the hinges 50 mm in) gives an overlap; it is one
  parameter (`x_wing0` / `wing_L`).
- **Front bar in front of the wheels:** the knife at y 1020, 305 mm in front of the tyres (front edge y 715). The
  front strip (x ± 625) is wider than the robot over the tyres (± 425), so the wheels run on the cut strip.
- **Wings at y 140:** the knife line just in front of the middle; the inner shoe and the hinge between y −120 and 200,
  well clear of the wheels (tyres from |y| 285).
- **Hinge at (± 560, z 160):** low, so the folded wing stands close to the robot (x 645–720) and the transport width
  stays at 1.44 m for the wings; the front bar (1.59 m with its drive end) sets the transport width.
- **Knives: pitch = stroke = 50 mm** (metric sections, 25 per 1.25 m, 20 per 1.0 m), 600 rpm: mean knife speed
  1.0 m/s, relative 3.1 m/s peak; at 1 m/s driving 50 mm of travel per stroke.
- **Cut height 60 mm** on shoes (skids); the shoes are pressed from 5 mm plate.

## 5. Front bar

- Mount plate, robot lugs and pins are those of the weed picker (8 × M10 under the two front lower beams). Links
  440 mm, head pivots at y 820: −30° in work, +10° lifted 300 mm.
- The head frame carries a roll pin M30 along y at z 230; the bar frame (cross tube RHS 60 × 40 + 2 arm plates on the
  stiffener) turns on it. Stops at ± 6° (rubber buffers, not modelled).
- The actuator (4000 N, 150 mm) sits on the diagonal with a float link of 105 mm with a 60 mm slot. In work it is set
  for 40 mm below the ground: the bar rests on its shoes (512 N), can drop 40 mm and rise 141 mm. Holding force
  1.6–1.7 kN. The rear eye stays 45 mm from pin A at the end of the slot (with 90 mm it touched the lug).

## 6. Wings

- **Mid frame:** 2 rails RHS 40 × 40 × 3 under the outer top beams (x ± 425), bolted with M10 through the grid holes
  at y ± 275 / ± 325; under them a cross tube RHS 80 × 60 × 4 at y 0 (x ± 610). At each end 2 hanger plates 12 × 100
  down to the hinge, closed to a box above z 360 by 2 webs (the actuator and the lever pass below it). In the middle a
  post of 2 plates 8 mm with a 50 mm slot per wing actuator.
- **Hinge:** M30 through the hanger plates and the hinge tube on the inner shoe; the wing lever (2 plates 8 mm) has
  its pin 150 mm from the hinge, 45° up and out.
- **Actuator:** from the post (x ± 20 … 70, z 266) to the lever. 611 mm in work, 384 mm folded, so 250 mm stroke and
  375 closed. Force over the fold: 2.6 kN at the start (lever arm 106 mm), 1.4 kN at 45°, 0.1 kN at 90°.
- **Float:** in work the anchor pin sits 15 mm in from the outer end of its slot. The wing can drop 8.7° and rise 17°
  (outer end ≈ 190 mm down, 370 mm up) before the actuator takes it.

## 7. Knife drive

- Each knife peaks at 260–345 N (mass 2.7–3.5 kg × 100 m/s²). Opposite knives cancel to < 20 N (the lower knife is
  heavier by its head extension). A single knife of the same length would push the bar with 550–670 N at 10 Hz.
- Mean crank torque 10 Nm (front), peak ≈ 25 Nm; at the motor 2.3 Nm through 5:1.

## 8. Power, speed and capacity

- Idle 120 W per metre of knife (friction of knives and gearbox), cutting 400 J/m² in a dense sward (3 t DM/ha).
  At 1 m/s: front 650 W, wings 520 W at the crank; 2.2 kW electric for mowing.
- Driving with 690 N draft (cutting 195 N, shoe friction 495 N) + 300 W: 3.4 kW in total, 71 A at 48 V.
- The front motor (1000 W) limits the speed: 1.5 m/s in thin grass, 1.3 m/s at 3 t, 1.0 m/s at 4 t DM/ha.
- 1.0 ha/h at 1 m/s; the 2.4 kWh battery lasts ≈ 0.6 h → ≈ 0.6 ha per charge. For more area: a second battery pack,
  or a lower knife speed in thin grass (idle power falls with it).

## 9. Robot loads

- 210 kg, of which 163 kg (front bar with head frame and both wings) rests on the shoes in work. The robot carries
  85 kg: axle loads 147 / 98 kg.
- In transport all of it is on the robot: 372 kg, 72 % on the front axle (267 kg of the 500 kg spec). A counterweight
  on the rear beams is not needed for the axle, but it improves steering grip in transport.
- Traction: the draft (≈ 0.7 kN) needs about 30 % of the weight on the wheels (2.4 kN in work) as tractive force:
  fine on dry grass, marginal on wet grass.

## 10. Strength

- Wing bar at the hinge while lifting (× 2 dynamic): 510 Nm on flat 80 × 8 + RHS 50 × 30 × 3: 103 MPa (S355).
- A shoe hitting a molehill or a stone at the wing tip (1 kN backwards, estimated): 42 MPa in the hanger plates across,
  and a torque of 1.07 kNm about the hinge that the two hanger plates take as ± 11.6 kN in their plane: 116 MPa with
  100 mm wide plates (181 MPa with 80 mm, so they were widened). A breakaway (shear bolt or spring catch that lets
  the wing swing back) is the next improvement for stony fields.

## 11. Open points

- Overlap between the strips (§ 4).
- Swath handling: the cut grass lies where it fell; the front swath passes under the robot (619 mm free) and the
  wheels run on it. Swath boards behind the wing ends would keep the wheel tracks free for the next pass.
- Breakaway on the wings, rubber roll stops on the front bar, guards over the con-rods (not modelled).
- Measure the cutting power and the knife inertia on a real bar and update `idle_W_m`, `e_cut`.
