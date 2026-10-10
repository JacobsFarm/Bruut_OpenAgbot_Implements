# Disc brushes (simple): design rationale

10 October 2026. Models: `Disc_Brushes_double_750.FCStd`, `…_double_650.FCStd`, `…_single_850.FCStd`
(FreeCAD 1.1, generated with `build_dbr.py`). The figures come from the model, from `dbr_calc.py` and from the
animation (`animate_dbr.summary()`). Where something is assumed or estimated, this is stated.

![2 × Ø750 on the robot](previews/1_double_750_iso_on_robot.png)

---

## 1. Assignment

- An implement in the `brushes` folder with two brushes of 65 or 75 cm working width.
- The two brushes side by side must be able to **spread material wide** and to **work inwards into a windrow**.
- Electrically driven.
- Also a version with **one brush of 85 cm**.
- For the standard agbot. Simple, robust, and easy for a farmer to build and maintain.

## 2. The design in brief

1. **Brush:** a standard sweeper disc brush (Ø650, Ø750 or Ø850), steel plate with PP or PP/steel-wire tufts.
   Tilted 4° forwards, so only the front touches the floor.
2. **Drive:** each brush directly on its own worm gearmotor: NMRV063 i = 30 with output flange FA, plug-in shaft
   Ø25, 48 V DC motor 550 W (IEC 71 B14). 100 rpm at full voltage, slower with PWM. Reversible.
3. **Brush unit:** clamp plate 10 mm with 4 vertical slots, 2 square U-bolts M16 around the toolbar, an M16 jack
   bolt on a tab, a head plate 10 mm with 2 gussets. The gearmotor stands on the head plate, the brush hangs under it.
4. **Toolbar:** 80 × 80 × 4, 1300 mm, welded to 2 hangers. Each hanger: a 10 mm top plate under the two rear lower
   beams (4 × M10 through the hole grid) and two 6 mm webs that wrap around the toolbar.
5. **Controller box:** IP66, 2 motor controllers 48 V / 30 A (reversible), fuse, emergency-stop relay, on the rear
   lower beams.
6. **Counterweight (optional):** the same 2 × 20 kg as the feed pusher, on the front lower beam.

| Characteristic | 2 × Ø650 | 2 × Ø750 | 1 × Ø850 |
| --- | --- | --- | --- |
| Working width | 1.30–1.50 m | 1.50–1.70 m | 0.85 m |
| Mass (model) | 104 kg | 110 kg | 75 kg |
| Brush centre | y −1110, x ±325 (spread) / ±425 (windrow) | y −1110, x ±375 / ±475 | y −1110, x 0 |
| Tip speed | 3.4 m/s at 100 rpm | 3.9 m/s | 4.0 m/s at 90 rpm |
| Power per brush (estimated) | 340 W | 460 W | 510 W |

## 3. Why disc brushes with a vertical axis

| Option | For | Against |
| --- | --- | --- |
| **Disc brush, vertical axis** (chosen) | Standard part (every sweeper uses them), Ø650/750/850 are stock sizes. Turn the motor around and the job changes: inwards = windrow, outwards = spread. No hood, no guard against flying stones needed at 100 rpm | The working width per brush is limited to its diameter |
| Roller brush, horizontal axis, at an angle | One brush can push the full width to one side | To switch between spread and windrow you need two brushes in a V that can be turned around: a frame with pivots. Throws material forwards and upwards: needs a hood |
| Brush with a bulldozer blade | Simple | Cannot spread; pushes a growing heap |

The assignment wants the same pair of brushes to spread **and** to windrow. With two disc brushes that is purely
the direction of rotation:

- **windrow:** the front of the left brush moves to the right, the front of the right brush to the left. The
  material is carried round the front of each brush into the middle. Between the brushes (200 mm gap) it is left as
  a windrow, which passes under the robot between the wheels (wheel tracks at x ±325 … ±425);
- **spread wide:** the other way round. A windrow or heap in the middle is carried round the front and thrown out
  to both sides, beyond the brushes (to about ±1.2 m in the animation).

At the point where the two brushes meet, their bristles move in the same direction in both modes, so the brushes
can touch (gap 0) without working against each other. That is why the spread setting is gap 0: otherwise a strip in
the middle is left untouched.

## 4. Design choices

### 4.1 At the back, on the side of the fixed wheels

As with the feed pusher: the rear wheels are fixed, so there is room behind them, and the steering heads and their
sweep stay clear (AGENTS.md). While brushing the robot drives with the brushes first (towards −y). The brushes
then always work on material that the wheels have not yet driven over.

### 4.2 Hangers under the rear lower beams, not on the wheel bracket flanges

The feed pusher bolts to the flanges of the wheel brackets (x ±283 and ±467). For the brushes those positions are
exactly where the brush units must be able to slide (unit centres at x ±315 … ±500). So the toolbar hangs on the two
rear lower beams, at x ±200 between the wheel brackets (x 261 … 489 is the bracket):

- 4 × M10 per hanger through the grid holes at x 175 and 225, in both rear beams (y −575 and −425);
- the top plate sits under the beams; the load behind the robot tilts it about the front beam, so the 4 bolts in the
  rear beam take the tension: 1.8 kN per bolt at 2 × the static load, 25 × safe for M10 8.8;
- tighten moderately or use a crush sleeve (tube 14 × 2, 36 long) in the 40 × 2 beam, so the beam is not squeezed;
- the webs stay 16 mm from the wheel bracket flanges and leave x 161 … 239 free for the nuts.

The toolbar and the hangers are one welded frame: easy to galvanize, no bolted joints that can work loose.

### 4.3 Toolbar with U-bolts and slotted holes

Everything a farmer has to adjust is done with the same 4 nuts (24 mm spanner):

- **sideways:** the U-bolts slide along the toolbar. Gap 0 for spreading, 150–250 mm for a windrow, or one brush
  in the middle. Free positions: unit centre at |x| ≤ 85 or ≥ 315 (the U-bolts must not hit the hanger webs);
- **height:** the U-bolt legs go through 4 vertical slots, range ±60 mm. The jack bolt on the tab carries the unit
  while the nuts are loose, so it does not drop, and makes fine adjustment easy. Locked with a lock nut;
- the 4 U-bolt legs clamp with tens of kN together; the unit weighs 36–43 kg. Friction alone holds it many times
  over, the jack bolt is the positive stop.

The toolbar was raised 30 mm (z 370–450) during the design: with the toolbar at z 340 the head plate hit the nuts
of the lower U-bolt in the highest position (+60). Now all positions from −60 to +60 are free of collisions.

### 4.4 One brush position for all brushes

The centre of the brush is the same for every brush: y −1110, 255 mm behind the clamp plate. It is set by the Ø750
directly behind the rear tire: 58 mm clearance with a new brush, 28 mm in the highest position (the tire reaches
further back the higher you go). The Ø850 sits in the middle between the tires and has 111 mm. With one hole
pattern, one head plate fits every brush: no second position to get wrong, no extra holes.

The price is overhang: the brush front is 1.4–1.5 m behind the robot centre. See § 5.

### 4.5 Tilt 4° forwards

A flat disc brush touches the floor all round and pushes material back under itself. Tilted forwards, only the front
arc touches the floor; the material that is caught there is carried round the edge and released at the side. 4° is
usual for sweeper side brushes. With about 20 mm bristle deflection the contact arc is about ±75°; in the model (2 mm
deflection) it is ±23°. The tilt is welded into the head plate (the gussets are cut at 4°). More tilt: shims under
the rear gearmotor bolts.

The height of the unit is set so that the lowest point of the bristles (the front) is exactly on the floor for a new
brush: `dbr_params.head_top_z()`, checked with `build_dbr.floor_contact()` (z_min = 0 for all versions). In use the
farmer sets the brush about 20 mm lower with the jack bolt.

### 4.6 Worm gearmotor directly on the brush

- **No chain, no belt, no bearings of our own.** The brush hub sits on the plug-in shaft of the gearbox; sweeper side
  brushes are mounted the same way, directly on the (hydraulic) motor shaft.
- **NMRV063:** the most common worm gearbox there is, available from many suppliers. The worm puts the motor
  horizontal: the unit stays low (top of the motor at z ~430) and the motor sits above the brush, out of the dirt.
- **Same gearmotor left and right:** for the other side the gearbox is turned over and the FA flange is moved to the
  other face of the housing. The worm (and motor) then stays on the far side of the brush axis, away from the gussets.
- **48 V:** the robot battery is 48 V LiFePO4, the same as the hub motors. No DC-DC converter; half the current of
  24 V (max ~11 A per brush).
- **550 W:** the brush needs 270–410 W at the motor (49–75 % load), so there is reserve for wet or heavy material.
  The worm gear has 38 Nm nominal at the output, 1.2–2.0 × what is needed. The peak at start-up (95 Nm) is limited by
  the controller. Shaft 43 MPa and key 24 MPa at that peak.

### 4.7 Single Ø850

The Ø850 is as wide as the robot (850 mm over the tires), so one brush covers the robot's own track. It throws the
material to one side (+x or −x, chosen by the direction of rotation). Two consequences:

- **side force:** the bristles push against the floor sideways. 75 N, 112 Nm about the robot centre. The fixed rear
  wheels take it with a skew of 1.0° and the front wheels steer 1.7° against it (`dbr_calc.robot_reaction`). The
  robot's line control has to correct for that; 20 % of the grip is used;
- **wheel track:** in the animation the material lands at x +0.2 … +0.7 m, so partly in the right wheel track
  (x +0.33 … +0.43). For sweeping towards a wall, work in passes from the far side: each pass throws the material to
  where the next pass picks it up. A higher speed throws further (the slide distance goes with the square of the
  speed).

With the double brushes the side forces and moments cancel (the brushes turn against each other).

## 5. Weight on the steering wheels

The brushes hang 1.1 m behind the robot centre. With the brushes working, part of their weight rests on the floor
at the very back (contact at y −1400 … −1500), which helps. Lifted, the full weight hangs behind the rear axle:

| Front axle share | 2 × Ø650 | 2 × Ø750 | 1 × Ø850 |
| --- | --- | --- | --- |
| working | 33 % | 35 % | 40 % |
| brushes lifted | 19 % | 17 % | 28 % |
| working + counterweight | 44 % | 45 % | 51 % |
| lifted + counterweight | 31 % | 29 % | 40 % |

Minimum 20 % (agbot comparison). So: the double versions need the counterweight when driving with the brushes lifted.
The counterweight is the same as the feed pusher's (2 × 20 kg, 4 × M10 in the front lower beam). Alternative: drive
to the job with the brushes down and stopped.

## 6. Controls

- 2 motor controllers 48 V / 30 A, reversible, with current measurement; the robot controller sets direction and
  speed per brush (PWM).
- Recommended: windrow 70 rpm (gentle, the material stays together), spread 100 rpm (throws further), Ø850 90 rpm.
- Current per brush 6.5–10.7 A in the animation. A sudden rise means a blocked brush (e.g. a stone or a rope):
  the controller stops the motor (current limit) instead of a shear pin.
- Emergency stop relay in the box, connected to the robot's emergency stop.

## 7. Estimated, not measured

| Item | Value | Effect |
| --- | --- | --- |
| Robot mass and centre of gravity | 161.5 kg, y +95, z 543 (agbot comparison) | axle loads |
| Brush contact force | 150 / 180 / 200 N at ~20 mm deflection | torque, power, side force |
| Bristle friction on concrete | 0.4 (PP, wet and dirty) | torque, power |
| Effective contact radius | 0.85 R | torque |
| Material | 2 kg/m², friction 0.5 | material torque (small: < 1 Nm), windrow 3.4 kg/m |
| Material model | slip 30–60 %, contact arc ±75°, release angle 5–75° | the pictures in the animation, not calibrated |
| Gearmotor | NMRV063 i = 30 + 48 V 550 W IEC 71 B14, 13 kg, efficiency 0.72 × 0.80, dimensions approximated | mass, power |
| Brush mass | bristle ring as a solid of 0.3 kg/dm³ | brush 10–17 kg incl. hub |
| Tires | stiffness 0.12 per degree per N, grip 0.6 | skew, steering correction (Ø850) |
| Driving on concrete | 250 W | run time |
| Battery | 48 V 50 Ah, 80 % usable | run time 1.6–2.5 h |

## 8. Checks

- `build_dbr.check_interference()`: empty for all three versions, for spread and windrow, and in the lowest (−60)
  and highest (+60) position. Also in the animation document (`animate_dbr.check_fit()`).
- `build_dbr.clearance()`: brushes 58–111 mm from the rear tires (new brush), 28–93 mm in the highest position;
  hanger webs 16 mm from the wheel bracket flanges.
- `build_dbr.floor_contact()`: lowest bristle point z = 0 for every version (new brush, its own height setting).
- No parts from OpenSCAD: the robot interface (beam positions, grid holes, wheel bracket) comes from
  `agbot_params.py` and is checked against the real robot model in the interference check.
