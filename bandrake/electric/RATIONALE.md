# Electric belt rake: design rationale

15 October 2026. Model: `Belt_Rake_Electric.FCStd` (FreeCAD 1.1, generated with `build_brk.py`). The figures come from
the model, from `brk_calc.py` and from the process model (`brk_field.py`, `animate_brk.summary()`). Where something is
assumed or estimated, this is stated.

![the belt rake on the robot](previews/1_work_iso_on_robot.png)

---

## 1. Assignment

- A belt rake (band rake, as in the inspiration photos: Brielmaier type) **in front of or behind** the robot,
  **electrically driven**.
- In crop beds: pull out fine weeds and keep the beds clean, much used in **nurseries for small trees**.
- In grassland: work **from the outside inwards** to **one small windrow**, to clean the ground for overseeding; or rake
  real hay into small windrows for silage.

## 2. The design in brief

1. **Belt loop** in the x-z plane: two drums Ø220 with their axes along the driving direction, 1,160 mm apart, a
   rubber belt 260 × 8 with 15 tine bars (3 double spring tines each). The bottom run moves to the left; a UHMW guide
   keeps it straight. Working width 1.52 m.
2. **Frame:** aluminium side plates (stadium shape, also the guards) on both sides of the belt, steel rails outside
   them carrying the four flange bearings, three cross tubes through the inside of the loop, a swath board at the
   left end.
3. **Drive:** 48 V BLDC gearmotor 750 W, 20:1, on the right drum shaft.
4. **Castors on actuators:** two swivel castors, each on a 24 V actuator, carry the rake and set the height.
5. **Mount:** plate under the front beams, free parallelogram to a rake head on a roll stub.

| Characteristic | Value |
| --- | --- |
| Working width | 1.52 m (comb), 1.41 m (rake) |
| Drive | 277 W electric in the soil (37 % of the motor) |
| Side force on the robot | 156 N (comb), 87 N (rake) |
| Mass (model) | 134 kg (rake 110, mount 24) |
| Parts, roughly | ≈ €2,380 |

## 3. In front of the robot

| Option | For | Against |
| --- | --- | --- |
| **In front** (chosen) | The robot's wheels drive on raked ground, not on the litter or the windrow; the robot pushes and the rake is always in view of the GNSS track; the delivery end is outside the robot's left wheel | It must stay out of the steering sweep (the rake starts at y 797, the tyres sweep to y 721) |
| Behind | No steering sweep | The robot first drives over the litter and presses it into the sward; the windrow would lie in the path of the next pass's wheels |

## 4. A belt rake, and how the tines move

On the bottom run the tines move sideways at belt speed u while the robot moves forward at v: in the soil they draw
lines at an angle to the travel, and every 202 mm of belt a new bar follows. With v = 0.6 m/s and u = 1.0 m/s the
robot moves 121 mm between two bars; the 6 legs of a bar (40 mm apart, 205 mm band) cover that 1.7 times: comb lines
20 mm apart on average. In grassland (1.2 / 1.5 m/s) 27 mm, 1.3 times. A belt rake moves material along the whole
width to one side with fixed tines and no cam track; it combs gently (spring tines) and puts everything in one place.

Tines straight from the bar (radial), as on the inspiration rake: on the top run they stand up, at the ends they swing
round and throw the material against the swath board.

## 5. Electric drive

| | Comb (nursery) | Rake (grassland) |
| --- | --- | --- |
| Working legs × force | 36 × 5 N | 37 × 3 N |
| Sideways force | 156 N | 87 N |
| Drum | 84 rpm, 18 Nm | 126 rpm, 10 Nm |
| Motor (20:1) | 1,675 rpm, 1.34 of 2.39 Nm | 2,513 rpm, 0.79 Nm |
| Electric | 277 W | 244 W |

A 750 W 48 V BLDC motor runs on the robot's own battery, needs no hydraulics and its speed is set per mode by the
controller (belt speed / ground speed). With 25:1 the rake mode would need 3,770 rpm: too fast, hence 20:1.

## 6. Who carries the rake: castors on actuators

The rake weighs 110 kg and its centre of gravity is 1.04 m in front of the robot centre. Hung on the robot (a normal
lift) it would leave **6 kg on the rear axle**: the robot (161.5 kg) would nearly tip forward. So the robot never
carries it:

- two **swivel castors** in front of the rake carry all of its weight (542 N each);
- each castor sits on a **24 V linear actuator** (1000 N, stroke 150): rod out 40 mm in comb mode, 65 mm in rake
  mode, 140 mm in the headland (tines 90 mm above the ground, 3.3 s). The actuators set the depth too (hall sensor);
- the **parallelogram is free**: it pushes the rake, takes its side force and keeps it level, and floats up to 130 mm
  (stop under the mount plate). The rake's weight sits 275 mm behind the castors, so the robot feels a small moment:
  front 99 / rear 87 kg.

The castors run in the robot's own wheel tracks (x ±375): in a nursery bed the robot needs free lanes for its wheels
anyway, and the castors use the same lanes.

## 7. Side force

All the tine forces push the material to the left, so the soil pushes the rake to the right: 156 N in comb mode. The
castors swivel and take nothing; the parallelogram passes it to the robot, which holds it with its tyres: 241 N on the
front tyres (50 % of their grip at μ 0.5), −85 N at the rear, a yaw moment of 163 Nm that the steering corrects. In
grassland it is half of that. Locking the castors (a swivel lock) in work would let them take part of it.

## 8. Outside to inside

The windrow always lies on the inside of the field. The next pass is one working width further in, so the windrow of
the previous pass lies inside its width and is carried along (in the animation 397 of the 433 straws of the old
windrow are picked up). With 0.1 kg/m² of litter the windrow carries 0.14 kg/m after one pass and 0.57 kg/m after four;
for real hay (1–2 kg/m²) the rake makes one windrow per pass or two passes together.

## 9. Nursery beds

- Tines 10 mm deep comb out seedlings with their roots; the young trees, woody and rooted deeper, bend the spring
  tines aside. Trees up to ≈ 180 mm pass under the bars (bar bottom at z 190).
- Lanes at x ±375 for the robot wheels and the castors.
- Thin tines (Ø4) or slower belt speed for delicate crops; test on a few metres first.

## 10. Checks

- `check_interference()` and `check_fit()` (headland lift, float stop, a bar pitch of belt movement): no overlap
  between the parts or with the robot.
- `clearance()`: rake ≥ 65 mm from the front tyres at 30° steering, mount 12 mm from the GNSS stem, control box 15 mm
  from the front steering plate.

## 11. Open points

- Tine forces (5 N per leg at 10 mm, 3 N in a sward) are estimates: measure the motor current on the first run.
- Stones in the soil: spring tines give way, but a stone can be thrown sideways; a cover over the top run and a guard
  at the delivery end are not modelled.
- Wet, sticky soil on the belt and the drums: a scraper at the drive drum.
