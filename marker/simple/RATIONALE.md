# Field marker (simple): design rationale

10 October 2026. Model: `Field_Marker.FCStd` (FreeCAD 1.1, generated with `build_mrk.py`). The figures come from
the model, from `mrk_calc.py` and from the animation (`animate_mrk.summary()`). Where something is assumed or
estimated, this is stated.

![the marker on the robot](previews/1_work_iso_on_robot.png)

---

## 1. Assignment

- Mark points in the field at exact GPS positions: pile and post positions, drill points, planting positions.
- It must be able to mark exactly, possibly on an X axis.
- Robust, simple and easy to make, with parts that are as easy to get as possible.
- For the standard agbot; the concept and the other functions are in the [marker README](../README.md).

## 2. The design in brief

1. **Stage** behind the rear wheels, from three bought linear modules: X belt module (stroke 800), Y and Z the same
   ball-screw module (SFU1605, strokes 200 and 300). Three identical NEMA 23 closed-loop motors.
2. **Mount:** two identical welded hangers under the two rear lower beams (4 × M10 each, through the hole grid). The
   base of the X module bolts to their flanges with T-slot nuts.
3. **XY bracket** (welded steel): adapter plate on the X carriage, a vertical Y plate to which the Y module is bolted
   on its side, two gussets. The Z module stands on the Y carriage via an aluminium adapter plate.
4. **Paint head** (hangs on 2 pins, 2 star knobs): bent aluminium plate, upside-down marking-spray can in a PVC 75 drain
   pipe, servo pushes the can onto its nozzle, sprung PVC 110 shroud with an M12 sensor (touch-off).
5. **Mast** on top of the Z adapter: second GNSS antenna exactly above the nozzle, receiver + IMU box next to it.
6. **Control box** on the rear lower beams: 3 stepper drivers, controller, DC-DC 48 → 36 V.

| Characteristic | Value |
| --- | --- |
| Capture window of the nozzle | 800 × 200 mm, x −400 … +400, y −800 … −1000 |
| Mass (model) | 35 kg |
| Accuracy 95 % (estimated) | ≈ 21 mm RTK, ≈ 8 mm total station |
| Capacity at 3 m spacing | ≈ 215 points/h |
| Parts, roughly | ≈ €1,450 |

## 3. Why a stage, and not steer the robot onto the point

The robot has hub motors with tractor tyres. On grass or loose soil it stops within a few centimetres at best, and
creeping a few millimetres back and forth is not reliable (slip, cogging of the hub motor, the robot rocks). Steering
sideways onto a point is not possible at all without driving a curve.

With a stage, robot positioning and marking accuracy are separate problems:

- the robot only has to get the point **into the window** (±400 mm across, ±100 mm along): easy for any path follower;
- the stage is a CNC axis with an encoder: it goes to a set point within a millimetre, every time;
- the stage also corrects the robot's own cross-track error, so the robot does not need to drive exactly on the line.

That is the "X axis" from the assignment; Y is added because the stopping error along the driving direction is
just as large as the error across it.

## 4. Why bought linear modules

| Option | For | Against |
| --- | --- | --- |
| **Ready-made linear modules** (chosen) | One order, bolt together. Rails, carriage, belt/screw, bearings, motor mount and cover strip are already aligned and sealed. Every CNC/automation shop sells them in any stroke | Brand dimensions differ a little: the adapter plates are the only parts that depend on it |
| 40 × 80 profile + HGR15 rails + belt (like the dockweed drill) | Cheaper per metre, stronger | Two rails per axis to align, belt tensioners, end plates, motor mounts, covers: many parts, a lot of fiddling, open to dirt |
| Electric linear actuators (IP65) | Very robust and cheap | No position accuracy (or a poor potentiometer), slow (20–50 mm/s), no closed loop |
| Sliding gate rail with rollers | Indestructible | Heavy, play, not accurate to the millimetre |

The belt module is used for X because 800 mm stroke with a ball screw would whip and is slow; the belt is fast
(500 mm/s) and the X axis only has to hold its position against small side forces. Y and Z are short and use a
ball screw: stiff, accurate and strong (Z can push 1350 N, so later heads such as a flag or peg pusher fit). Y and Z
are the **same module** with a different stroke: one type of spare part.

All three motors are the **same NEMA 23 closed-loop stepper** with encoder: no lost steps go unnoticed, one spare
motor. For Y and Z they are much stronger than needed (a few hundredths of a Nm); that is accepted for the single
spare part and for heavier heads later.

## 5. Why this stack and these dimensions

**X stroke 800 (not 1100 as in the first concept).** A linear module is always longer than its stroke (carriage and
end blocks: +250 mm). With 1100 mm stroke the module would stick out ±0.7 m, much wider than the robot (850 mm over
the tyres), and the module end, not the nozzle, would hit a fence first. With 800 the module is 1050 long and stays
roughly within the robot's width; the nozzle still reaches from wheel track to wheel track, and two points 0.8 m apart
can be marked from one stop.

**Y stroke 200.** Stopping errors of ±100 mm are generous for a robot at 0.5 m/s with 0.5 m/s² braking. A longer Y
module moves everything further behind the robot (more overhang, more load on the rear axle when pressing).

**Y module on its side, Z module upright next to it.** The Y carriage then has a vertical face to which the Z module
bolts directly (via one flat adapter plate). With a flat Y module, the Z module would need an angle bracket on the Y
carriage and would stand off to one side anyway. The price is that the nozzle sits 80 mm to the right of the X
carriage centre; the X module is shifted 80 mm to the left to make the reach symmetric.

**Nozzle at y −800 … −1000.** The front-most position keeps the PVC tube, the knobs and the shroud ≥ 19 mm behind the
rear tyres (y −716) at every height. The shroud rods are not straight in front of the nozzle but at ±45° (the first
version had them in line with y: the front rod hit the tyre at axle height).

**Z stroke 300, Z module bottom at 150 mm.** Parked, the shroud is 196 mm above the ground (over grass and clods); at
the bottom it reaches 104 mm below nominal ground (a dip, the robot pitching back). The Z module itself never comes
lower than 150 mm, about as low as the hub motors.

**Hangers at x ±200.** On the grid holes x 175/225 under both rear lower beams, 16 mm clear of the wheel brackets
(x 261), the same place as the brush hangers. Both hangers are the same part.

**X motor at −x, standing up.** At +x the motor would touch the end of the right upper beam (y −650); at −x it is
outside the robot frame.

## 6. Why a spray can with a shroud

| Option | For | Against |
| --- | --- | --- |
| **Upside-down marking spray can, servo, shroud** (chosen) | The can is the standard marking product: every builders' merchant sells it, in all colours, also turf paint. No pump, no hoses, no cleaning. The servo is a €30 part | ≈ 450 dots per can (estimated): change cans on big jobs |
| Paint tank + pump + solenoid valve | Cheaper per dot, line marking possible | Pump, hoses, pressure, cleaning, nozzles that dry up: more to break; for later (advanced) |
| Pull/push solenoid on the can | Fast (fly-by) | Needs 30–40 N over 5 mm: big, hot solenoid; the servo is simpler |

The **shroud** (a piece of PVC 110 sewer pipe) solves three things at once: wind cannot blow the spray away, the dot
is round and sharp, and the nozzle is always 134 mm above the ground, whatever the robot does. Because it rests on
the ground on springs, it is also the **ground sensor**: an inductive M12 sensor sees the ring lift ≈ 5 mm. That
contact height is needed for the tilt correction (a tilted Z axis moves the tip sideways as it goes down) and gives a
ground-level measurement for free. The springs go solid after 8 mm, before the ring can touch the sensor.

The **guide tube** is PVC 75 drain pipe: the 65 mm can slides in it with 3 mm play, the nozzle cap rests on the
bottom plate, the servo lever pushes a disc on top of the can. Changing a can takes seconds and needs no tools.

The **quick change** (2 pins in keyholes + 2 star knobs) is there so other heads can be hung on the same Z carriage
later (flag, peg, punch, soil probe; see the concept README).

## 7. Why the antenna on a mast above the nozzle

`mrk_calc.accuracy()`:

| Source (1σ) | Antenna above the nozzle (chosen) | Robot's own antenna (front beam) |
| --- | --- | --- |
| RTK position | 10 mm | 10 mm |
| Tilt, IMU ±0.1° × lever height | 1.7 mm (985 mm) | ≈ 1.3 mm |
| Heading ±0.5° × horizontal lever | 0 mm (coaxial) | 13 mm (1475 mm lever) |
| Stage | 1 mm | 1 mm |
| Dot on the ground | 3 mm | 3 mm |
| **Total, 95 %** | **≈ 21 mm** | **≈ 34 mm** |

With the robot's antenna 1.5 m away from the nozzle, every 0.5° of heading error moves the dot 13 mm, and at
standstill a single antenna does not know its heading well. With the antenna on the nozzle axis the heading drops
out; the robot's antenna and the mast antenna together still give a heading (moving baseline, ≈ 1.5 m) for driving.
The mast moves with X and Y but not with Z, so its height is constant.

Tilt matters: without correction 3° of roll moves the dot 52 mm. An inclinometer at standstill (±0.1°) is cheap
and is part of the design, in the receiver box on the Z adapter (rigid with the mast).

With a **robotic total station** the same mast carries a 360° prism instead of (or under) the antenna: ≈ 8 mm at 95 %,
for building corners, or under trees and next to buildings where GNSS is not good enough.

## 8. Robot and loads

- **Axle loads** (robot 161.5 kg, marker 35 kg at y −734): rear 109 kg, front 88 kg (45 % front). The marker hardly
  changes the balance; no counterweight needed.
- **Press force:** a force down at the nozzle (y −1000) unloads the rear axle by 1.5 × that force. At 356 N the rear
  axle keeps half its load, at 712 N the rear wheels lift. The Z driver is limited to 300 N. The paint head only
  needs ≈ 30 N (the shroud springs).
- **Hangers:** the weight behind the beams tips the top plate about the rear bolts: 320 N per rear M10 with × 2 for
  shocks (proof load 46 kN). The X module overhangs 416 mm beyond the hanger: 4.4 MPa, 0.04 mm.
- **Drives:** X needs 55 N (17.5 kg at 2 m/s² + friction), 0.88 Nm on a 20-tooth HTD-5M pulley: 1.4 × reserve at the
  1.2 Nm a 2.2 Nm stepper still has at 300 rpm. Y and Z need hardly anything on a 5 mm lead screw.
- **Z without power:** a ball screw runs back. The Z slide (3.1 kg) needs 0.022 Nm to turn the motor; the detent
  torque (≈ 0.06 Nm, estimated) holds it, but on a bumpy field a Z motor with brake is the robust choice.
- **Cycle:** 16.8 s per point at 3 m spacing, of which 7 s driving and 4 s standing still to measure. The stage itself
  is fast (0.7 s); the measurement and the slow last 40 mm of Z determine the time. ≈ 215 points per hour.

## 9. What is estimated, and what is left out

Estimated (see the README for the full list): robot mass and centre of gravity; masses and dimensions of the bought
modules; GNSS, IMU and heading accuracy; paint per can and spray angle; carriage friction; settle and measure time.

Not modelled: cables and drag chains, home switches, the bolts of the modules and plates, the thread of the
antenna adapter, the welds. The drag chain for X goes on top of the X module, for Y along the Y module.

Open points for a first prototype:

- Check the module dimensions with the chosen supplier and adjust `xm_*` / `sm_*` in `mrk_params.py`; the adapter
  plates follow.
- Measure the real dot size and paint use with the chosen marking spray; adjust `spray_angle`, `can_line_m`.
- Measure how long the RTK solution needs at standstill to be stable (`settle_s`, `measure_s`): that is the biggest
  part of the time per point after driving.
- Weigh the robot (two scales under the axles) and update `ROBOT` in `mrk_calc.py`.
