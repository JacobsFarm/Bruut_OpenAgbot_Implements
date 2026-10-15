# In-row weeder with double arms: design rationale

15 October 2026. Model: `In_Row_Double_Arm_Weeder.FCStd` (FreeCAD 1.1, generated with `build_ird.py`). The figures come
from the model, `ird_calc.py` and the process model (`ird_field.py`). This variant builds on the
[finger variant](../finger/RATIONALE.md); only what differs is explained here.

![the double-arm weeder under the robot](previews/1_work_iso_on_robot.png)

---

## 1. Assignment

An in-row weeder with **double arms that swing in and out**: per row two knives, one from each side, that close in the
row between the plants and open around each plant.

## 2. The design in brief

- Per row unit **two vertical shafts**, 110 mm on both sides of the row, each with its own flange bearing, 10:1
  planetary gearbox and NEMA 23 closed-loop stepper. The inner shaft sits 75 mm behind the outer one.
- **Knife 50 mm wide** per arm: in, the two knives together cover a row band of 95 mm (5 mm overlap in the row line);
  out, each is 75 mm beside the row on its own side.
- The lift actuator moves to the outer side of each unit (the inner motor stands where it was); the toolbar is 800 mm
  long to carry its lug.
- The rest (frame, parallelograms, gauge wheels, camera, control box) is the finger variant.

## 3. One stepper per arm, or one per row with gears

| Option | For | Against |
| --- | --- | --- |
| **One stepper per arm** (chosen) | Each knife moves on its own: the side where the stem stands off the row line waits a little longer, the other side swings early; it reuses the finger variant's drive one-to-one; if one fails, the other still hoes its half | 4 steppers, gearboxes and drivers (+ ≈ €580) |
| One stepper per row, the two shafts coupled by a gear pair (opposite rotation) | 2 steppers, the knives always symmetric | Gears of Ø220 above the row (the shafts are 220 mm apart), backlash; both knives must wait for the side that is closest to the stem |

## 4. Why the knives must not meet

When both are in, the knives overlap 5 mm in the row line. If they ran side by side they would touch in every swing.
The inner arm therefore sits 75 mm further back: the knives are 40 mm apart along the travel (75 − 35), and the inner
knife simply does its swings 0.15 s after the outer one (at 0.5 m/s). `check_fit()` checks every combination of in and
out of the two arms.

## 5. Timing by distance

The simple rule of the finger variant waits until the knife is **completely out** before its front edge comes within
65 mm (along the row) of the stem. With the stem position from the camera the controller can do better: it checks the
real distance from the knife outline to the stem during the swing and starts the swing out as late, and the swing in
as early, as a distance of 55 mm allows (with the stem ±10 mm along the row for odometry). A knife that only needs to
move 78 mm sideways profits most from this.

| Variant / rule (0.5 m/s, same field) | Row band outside the safe zones hoed | Seedlings in the band hoed out | Closest knife edge to a stem |
| --- | --- | --- | --- |
| Finger, simple rule (as built in `../finger`) | 68 % | 62 % | 57 mm |
| Finger, distance rule (test, not in `../finger`) | 86 % | 82 % | 57 mm |
| Double arms, simple rule | 71 % | 63 % | 56 mm |
| **Double arms, distance rule** (this model) | **90 %** | **82 %** | 56 mm |

The double arms gain over a single finger with the same rule: 4 % more of the band near the stem, shorter and quicker
swings (89 / 118 ms instead of 98 / 148), half the holding torque, and a result that hardly changes with speed (90 %
from 0.3 to 0.7 m/s). The **timing rule matters more than the second arm**: the distance rule is worth applying to the
finger variant too.

## 6. Arm geometry

With the shafts 110 mm beside the row and arms of 220 mm: in at 23.4° (knife centre 22.5 mm from the row line), out at
2.6° (100 mm). The knife turns 21° with the arm when it swings out; its corner is then 75 mm from the row line, so a
stem 15 mm off the line towards that knife is still 55 mm away. The draft (41 N per knife) pulls each knife towards
out, as in the finger variant; holding it in takes 3.6 Nm at the shaft, 0.4 Nm at the motor (× 7.5).

## 7. Mass and power

68 kg (13 kg more than the finger variant: two drives and arms, bigger decks). Robot + weeder 230 kg, front 130 /
rear 100 kg. Four steppers need 111 W on average (23 % of the time swinging), the knife draft 83 W; with driving
≈ 545 W: 4.4 h on the battery.

## 8. Checks

- `check_interference()` and `check_fit()`: knives in, half, out, park, one arm in and the other out (both
  combinations), lift 0 / 25 / 50 mm: no overlap between the parts or with the robot.
- `clearance()`: knives ≥ 83 mm from the rear tyres, frame bolts 12 mm from the front wheel top plates at 30°
  steering, motors 44 mm under the upper beams when lifted.

## 9. Open points

- The distance rule needs a good stem position from the camera (a few mm): a stem hidden under leaves is placed less
  accurately; the controller can then fall back to the simple rule for that plant.
- The inner arms of the two rows work in the 375 mm between the rows: the leaves of both rows touch the arms at 280 mm
  as in the finger variant.
- Four steppers in the control box: drivers, wiring and a 48 V supply of ≈ 300 W peak when all swing at once.
