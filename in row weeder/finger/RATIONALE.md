# In-row finger weeder, 2 rows: design rationale

15 October 2026. Model: `In_Row_Finger_Weeder.FCStd` (FreeCAD 1.1, generated with `build_irw.py`). The figures come
from the model, from `irw_calc.py` and from the process model (`irw_field.py`, `animate_irw.summary()`). Where
something is assumed or estimated, this is stated.

![the in-row weeder under the robot](previews/1_work_iso_on_robot.png)

---

## 1. Assignment

- Weed **inside** two rows of broccoli (between the plants in the row), on the standard Bruut OpenAgbot.
- Two "fingers" that go into the rows, **two stepper motors**; the arm and the mechanism are free to choose.
- A camera above the rows.

## 2. The design in brief

1. **Frame:** two rails 40 × 40 × 3 under the lower beams (x ±225, 8 × M10 through beam and rail), a toolbar
   50 × 50 × 4 across under them at y 260, just behind the steering sweep of the front wheels.
2. **Row unit (2×):** parallelogram (links 170 mm) back from the toolbar to a unit head: a deck with a flange bearing,
   a vertical shaft Ø20, a 10:1 planetary gearbox and a NEMA 23 closed-loop stepper on top. A gauge wheel Ø200 in the
   robot's wheel track sets the depth; a 24 V actuator with a slotted rod end lifts the unit.
3. **Finger:** an aluminium arm of 220 mm on the shaft, 280 mm above the soil (over the leaves), a spring-steel shank
   down to a flat knife 80 × 35 mm, 20 mm deep.
4. **Camera:** under the front inner beam, 545 mm high, 15° forward, two LED bars; control box (computer, drivers) on
   the upper beams.

| Characteristic | Value |
| --- | --- |
| Rows / plants | 2 rows 375 mm apart, plants every 450 mm |
| Swing out / in | 98 / 148 ms |
| Row line left around a plant | ≈ 200 mm of 450 |
| Seedlings in the row band hoed out (animation) | 62 % at 0.5 m/s (69 % at 0.3 m/s) |
| Mass (model) | 55 kg |
| Parts, roughly | ≈ €2,240 |

## 3. Under the belly, between the wheels

The space under the robot between y −285 and +285 (between the front and rear tyres) is free from the ground up to
the lower beams (z 619) over the full width. That is where the units are:

| Option | For | Against |
| --- | --- | --- |
| **Under the belly** (chosen) | Free space, nothing sticks out; the camera can look at the rows ahead of the knives from under the front beams; the robot's own wheels guide the units (the gauge wheels run in the wheel tracks); short, stiff frame | Shade under the robot (LED bars); the front tyres limit how far forward the toolbar may go (steering sweep from y 279) |
| Behind the robot | More room, the camera above the rows on a mast | The units swing out when the robot steers (long lever behind the rear axle); a mast and an extra frame |
| In front of the robot | The camera sees what the knife does | Inside the steering sweep; the robot drives over the hoed (loose) row band |

## 4. Why a swing arm (and not another in-row mechanism)

The assignment asks for fingers on stepper motors. Four ways to move a knife into and out of the row:

| Mechanism | For | Against |
| --- | --- | --- |
| **Swing arm on a vertical shaft, one knife** (chosen) | One rotary axis per row: a stepper with a gearbox drives it directly; the knife moves 115 mm sideways for a swing of only 31°; robust (bearing, shaft, arm), nothing slides in the dirt | The knife turns a little with the arm (27° when out) and moves 29 mm back; the arm passes over the row (here 280 mm high, over the leaves) |
| Linear slide (belt or screw) across the row | Knife stays square, pure sideways motion | Slide and belt in dust and mud, more moving mass, a second guide |
| Rotating disc with a cut-out (Robocrop type) | Continuous rotation, no reversing | The speed must be synchronised with every plant spacing; the disc works a circle, not the row band; bigger motor |
| Two blades that open and close (Robovator type) | Hoes both sides of the stem up to the plant | Two actuators per row (4 in total), hydraulics or big solenoids; more parts in the soil |

The knife covers the row band (±40 mm) when it is in; around the plant it swings to the outside of the row only.
The inside of the plant (towards the other row) keeps its safe zone too: that is the price of one knife per row.

## 5. Arm geometry and the stepper

The shaft stands 110 mm beside the row (outside, towards the robot wheel) and 190 mm in front of the knife. With an
arm of 220 mm:

- **in** at 30.0° the knife is on the row line, **out** at −1.3° the knife is 115 mm beside it, a swing of 31.3°;
- out lies just past "straight back": the draft of the soil holds the finger out by itself; in the row it pulls the
  finger towards out with 7.2 Nm at the shaft, held by 0.8 Nm at the motor (the closed-loop stepper holds 3 Nm: × 3.8);
- the knife's inner edge is 75 mm from the row line when out; with stems up to 15 mm beside the line and the knife
  turned with the arm, the closest approach in the run is 57 mm (safe zone 50).

Swing time (`irw_calc.move`): time-optimal motion with 70 % of the motor's torque curve, the inertia of arm and
finger (0.049 kg m², from the model; the arm is aluminium) plus the rotor and gearbox × 10², minus the soil torque.

| Gearbox | Usable torque at the shaft | Swing in (against the draft) |
| --- | --- | --- |
| 5:1 | 8.8 Nm | the soil load (up to 16 Nm) is larger: no |
| **10:1** (chosen) | 17.6 Nm | 148 ms |
| 20:1 | 35 Nm | ≈ 200 ms (motor speed limit) |

A NEMA 23 with 10:1 is the smallest standard combination that swings in against the soil in well under 0.2 s. The
swing out is faster (98 ms) because the draft helps.

## 6. The zone around each plant, and the speed

Around every stem the knife must be fully out from 65 mm before to 65 mm after the stem (safe zone 50 + margin 15 for
odometry and the plant position). The swings themselves take distance too, so about 200 of the 450 mm row line is not
passed by the knife. In area, the run hoes 68 % of the row band outside the safe zones and kills 62 % of the seedlings
in the band (`irw_field.summary`). The speed trades capacity against coverage:

| Speed | Row line not passed per plant | Row band hoed (outside the safe zones) | Seedlings in the band hoed out | Net capacity |
| --- | --- | --- | --- | --- |
| 0.3 m/s | 174 mm | 76 % | 69 % | 0.065 ha/h |
| **0.5 m/s** (chosen) | 203 mm | 68 % | 62 % | 0.11 ha/h |
| 0.7 m/s | 232 mm | 60 % | 54 % | 0.15 ha/h |

What the knife leaves near the plant is in the shade of the broccoli leaves within a few weeks. A second pass a week
later (seedlings that were too small) or an inter-row/finger-weeder tool for the last centimetres next to the stem
completes it (see the concept README).

## 7. Knife, shank and depth

- **Flat knife 80 × 35 × 4**, sharpened front edge, 20 mm deep: cuts the seedlings under the surface and leaves the
  soil where it is (no ridging towards the plants). Replaceable, hardened.
- **Shank 30 × 8 spring steel, thin edge leading**, with a coil under the arm: gives way to a stone or a clod instead
  of bending the arm or stalling the stepper.
- **Gauge wheel in the robot's wheel track** (x ±375): firm, already compacted soil, never on the crop; three axle
  holes give a knife depth of 5 / 20 / 35 mm.
- **Parallelogram**: the knife keeps its angle when the unit follows the ground. The lift actuator's slotted rod end
  lets it float in work.

## 8. Rows 375 mm apart

With the track of 750 mm and two rows between the wheels, the wheels are in the middle of the inter-rows only when the
rows are half a track apart: 375 mm, and every next pass fits the same pattern. Broccoli at 375 × 450 mm is
5.9 plants/m², a dense but used spacing for small heads; for 500 mm rows the robot would run with one wheel close to a
row. The row positions are parameters (`row_x`); the units, gauge wheels and the camera follow them.

## 9. Camera under the robot

The camera hangs under the front inner beam, 545 mm high, tilted 15° forward. With a 6 mm lens on a 1/1.2" global
shutter sensor it sees 914 mm wide at the near edge of the image (both rows with their leaves), from y 260 to 962:
every plant is seen in 28 frames and the last look is 0.84 s before the knife arrives (detection needs ≈ 90 ms).
Under the robot it is in the shade: the two LED bars give an even light, also at dusk. Higher on a mast would see
more but the robot itself and the front wheels would be in the image.

## 10. Lift

The lift is 50 mm: the knife is then 30 mm above the soil, enough to turn on a smooth bed. More is possible only
with the rails out of the way (at 80 mm the links touch the rails, `check_fit`). The actuator only lifts; in work it
floats in its slot.

## 11. Checks

- `check_interference()` and `check_fit()` (arm in, half, out; lift 0, 25, 50 mm): no overlap between the parts or
  with the robot.
- `clearance()`: knives ≥ 78 mm from the rear tyres, the frame bolts 12 mm from the front wheel top plates at 30°
  steering, camera 91 mm from the front units.

## 12. Open points

- Soil: in crusted or heavy soil the draft can be twice the estimate; the swing in then gets slower (the stepper
  still holds the knife). Test the knife depth / speed in the real field.
- Leaves: broccoli taller than ≈ 280 mm reaches the arm; weed early (2–5 weeks after planting).
- The plant detector (broccoli vs weeds, seen from above in the shade) has to be trained; the model assumes it finds
  every plant.
- A missing plant is hoed through; a weed exactly where a plant should be is left (the detector decides).
