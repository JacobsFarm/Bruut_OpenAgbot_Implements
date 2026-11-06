# Why advanced V2 is built this way

Advanced V2 keeps everything of [`../advanced/`](../advanced/RATIONALE.md) that carries and guides the elements
(headstock, parallel linkage, actuator with slotted hole, floating toolbar, spring struts, swing arms, press wheel) and
changes what goes into the soil and how the liquid gets there. The reasons for the suspension are in advanced's
RATIONALE; here only what is new.

## 1. A pair of V-discs instead of one disc

The single disc of advanced cuts a slit and the knife behind it opens the slot. The twin injector in
`../inspiration/` ("Minimale bodembeschadiging door v-schijven") works the other way round: two discs cut the sward
open together and lift it a little, the liquid goes in while the sod is open, and the slot is closed right after.
That keeps the sod intact and puts the liquid at the roots without losses to the air.

Two angles per disc do that:

- **toe-in 5°** (fronts towards each other): the discs meet at the front and diverge backwards, so behind the meeting
  point there is an open V in which the knife fits;
- **camber 8°** (bottoms towards each other, tops apart): the discs run together at the bottom, and their faces push
  the soil up and outwards as they open: they lift the sod and lay it aside, instead of only cutting.

With both angles the closest point of the two rims lies in front of and under the axle (84 mm in front, 26 mm deep),
not at the bottom: the discs cut one slit there, behind it they open. The rims are 2 mm apart at that point
(`disc_meet_gap`): they do not touch, but nothing gets between them. The x position of the discs follows from that
gap (`DISC_CX`, 27.6 mm), the height from the depth bands (`disc_z`).

Larger angles open the slot wider and lift more soil, but need more draft and leave a wider slot to close. 5° and 8°
are a starting point and are single parameters (`disc_toe`, `disc_camber`); the knife, fork, hangers and bands
follow when they are changed.

## 2. Disc Ø 325 and depth bands on the outside

The precision applicator uses Ø 325 discs and puts the liquid 50 mm deep. With advanced's Ø 220 depth band on a
Ø 325 disc the discs run 50 mm deep. The band can only be on the outside of each disc (the insides meet), and on a
tilted disc its lowest point is no longer straight under the axle; `band_contact()` gives that point and the effective
radius, which both the build (lifting) and the animation (ground following, both bands, the lowest counts) use.

## 3. Hangers outside, fork plates between the discs

Each disc runs on its own hub on a stub axle along its tilted axis. The axle can not run through the middle (the knife
is there and the discs meet), so each stub axle sits in a boss welded into a hanger plate outside its disc. The hanger
plates hang from a 40 × 40 cross tube over the discs (13 mm over the highest point of the rims), and that tube is
welded to the two fork plates of the swing arm. The hanger is at x 66: the top of the tilted depth band reaches x 59.

The fork plates of advanced (x ±21.5 … 27.5) run from the pivot via the spring pin to the cross tube, and from there
down between the discs to the knife bolts and the ear of the press wheel arm. Between the discs they had too little
room (3 mm from bolt head to disc), so they moved in to ±15 … 21: the strut eye (20 wide) and the tongue (10) still fit
between them, the press wheel straps stay at ±28.5 with a washer.

## 4. Double knife from precision V3, trailing, between the discs

The knife is the double injector knife of the precision applicator (loaded, not copied): two tubes in line behind the
blade, for two liquids that may not be mixed in one tank, and the slot stays 10 mm wide. It is placed as in precision
V3: **trailing 20°** (tip back, top forward), so it slides over stones and roots and presses the soil down instead of
lifting it; and **by its outlet**: the outlet of tube A is 50 mm deep, B lies 10 mm behind and ends 4 mm further, so
it is also at 50 mm.

"Close behind the discs": the knife is moved forward along y until the blade or a tube comes within 6 mm of either disc
(`knife_origin`, bisection over a set of points on blade and tubes against both tilted discs). It then stands in the
open V, partly between the discs in the side view, just as the seed tube of a double-disc opener. The outlets are 128 mm
behind the disc axle, the tip goes 16 mm deeper than the discs and makes a small pocket under the outlets.

## 5. Press wheel right behind the knife

Advanced's press wheel and trailing arm are unchanged; only its pivot follows the knife: 75 mm behind the rearmost
point of knife and tubes (`pw_behind_knife`). The wheel then runs 246 mm behind the outlets, where the discs have laid
the sod aside, and presses it back onto the slot.

## 6. Spring seat 18 mm instead of 30

A swing arm with two discs, hubs, hangers and cross tube weighs 13.2 kg (advanced 8.1). The heavier arm carries more
of its own weight onto the discs, so with advanced's spring seat (30 mm up) the toolbar floated 26 mm above the design
height with the arm at 6.6°, close to its stop. With the seat 18 mm up the arm floats at 2.7°, as in advanced,
with room both ways (`lfa2_calc.float_equilibrium`).

## 7. The roller pump on the robot

The user wants the same roller pump as the precision applicator. With double knives on 5 rows that is the 10-section
pump of combined_v3: right half liquid A, left half liquid B, one shaft and one stepper motor, so both liquids follow
the driving speed with the same dose per row (a different ratio needs a different tube bore in one half). 945 mm
long and 33 kg it does not belong on the floating toolbar (advanced had a small 5-channel pump there): it would add
weight to the elements and change the floating. On the robot, in combined_v3's place with the jerrycans in front, it
is fixed and the hoses take up the lift.

combined_v3's pump height does not work with advanced's headstock: the cross tube that carries the actuator (top z 820)
is 13 mm behind the pump outlets and 70 mm above them. Under the tube the room between the headstock cheeks and
the actuator is too narrow for 10 hoses. So the pump stands 100 mm higher on four blocks and the hoses go over the tube.
The combined_v3 parts are loaded as a private copy with only the pump height changed, so combined_v3 itself does not
change.

## 8. Hoses in two layers, moving sideways together

The pump outlets lie in the order B0 … B4 A0 … A4 from left to right, the knives want A and B of each row together:
A0 … A2 cross the B hoses to the left, B3 and B4 cross the A hoses to the right. So B runs at z 836 and A at 862. Within
a layer the start order (pump) and the end order (rows) are the same; when all hoses of a layer move sideways over the
same stretch (y −70 … −400), every point is a linear blend of two sorted rows, so they never come closer than the
pump pitch (62 mm). Behind that each hose runs beside the spring strut (±26 from the row) and drops onto its tube end:
A straight up, B up and back, 61 mm apart on the knife.

The first version started the sideways move at y −20, right behind the S that lifts the A hoses: hose A1 got a bend
of R 13. Starting at −70 gives at least R 26.6 everywhere.

The hoses are built as one B-spline through control points (as advanced), not interpolated: a B-spline stays inside
its control polygon, so a clear control polygon means a clear hose. They are checked with points on the hose surface
against every part (`check_hoses`), at working height and lifted.

## 9. The price: draft and down force

Lifting and moving the sod is what the V-discs are for, and it costs force. `lfa2_draft.py` adds up the same parts for
advanced and V2 with the same (estimated) soil figures: V2 needs about 2.4 × the draft (1130 N instead of 475 N for
5 rows in normal soil) and about 275 N down force per element instead of 85 N, while floating gives 141 N on the
discs. Advanced fits within the robot's usable pull (about 516 N); V2 with 5 rows does not, and would not reach
50 mm. The design choices that can bring it back are in the README (rows, down force, disc angles); the soil figures
must be measured first.

## 10. The lift actuator is a Linak LA36

Advanced drew a generic 24 V actuator (290 mm pin to pin, 150 stroke). V2 now uses the **Linak LA36** from the
datasheet in `parts/actuator/` (repo root). The model is drawn to it: reinforced housing 148 × 76, 230 long, spindle
axis 37 above the flat side; solid back fixture (Ø 25.2, hole 13 from the end, 0°, so the hole is parallel to the
housing width) and solid rod eye (Ø 27.8, hole 13.5 from the end), both Ø 12.2 for a Ø 12 pin; outer tube 44.5.
The datasheet gives no full drawing, so how far the housing starts behind the back eye, the gearbox length, the
motor diameter, the rod diameter and where the outer tube ends are estimated from the side view.

**Length and pin positions.** With slotted or solid eyes and a stroke up to 300 the pin-to-pin length is 200 + stroke:
350 retracted, 500 extended, 60 mm longer than the old actuator. The lift needs 146 mm of stroke (working position,
actuator fully out → lifted 140 mm, slot closed). So the pins had to move apart:

- the lower pin (`act_b`) moved 6 mm forward to (−314, 470): the LA36 back fixture sticks out 13 mm behind its pin
  and touched the rear-frame cross tube; now it is 3 mm clear;
- the upper pin (bottom of the slot, `act_a`) moved from (5, 700) to (52, 751): 60 mm further from the lower pin and
  a little steeper (37.5° instead of 35°). Along the old line (58, 738) the rod crossed the rear robot beam when the
  toolbar floated low (15 mm overlap at −80): the longer actuator brings the rod line down over the beam. Higher up,
  the rod eye at the top of the slot runs into the cross tube that carries the slot plates. (52, 751) is the point in
  a 4 mm grid with both clearances at least 3 mm (`act_a` comment in `lfa2_params.py`).

The floating range becomes −70 … +68 mm (was −80 … +67; advanced's README says −75 … +64). Lifted, the actuator is
354.3 long, 4.3 mm before its own end stop: the lift ends on the controller, not by running into a block (the
datasheet forbids that for actuators without the integrated controller).

The model used to put the floating pin on the line from the slot bottom to the (moving) lower pin. The slot is fixed
in the headstock plates, so that is only right at the design height; with the longer LA36 the pin ended up 2 mm
beside the slot and touched the plates at −35 mm. Now `lfa2_calc.slot_pin()` puts the pin on the slot itself, at the
actuator length from the lower pin. The build, the animation and `float_range()` all use it.

**Lugs.** Both pairs of lugs are spaced for the LA36 eyes with 1 mm play per side (the datasheet asks for 0.5 … 1):
29.8 apart for the rod eye in the slot, 27.2 for the back fixture. Pins Ø 12 instead of 16. Fully retracted, the outer
tube stays 6 mm from the slot lugs (the datasheet asks for at least 2).

**Motor on top.** The parallel motor sits above the outer tube. Underneath (as advanced drew it) it hits the rear
robot beam when the toolbar is lifted, because the actuator then lies flatter and its front end comes over the beam.
Above the tube there is room up to the hoses (z 836) and the pump; the housing (76 wide) fits between the inner
cheeks (140 apart).

**Which spindle.** The force is not the same over the lift: the actuator works at a flat angle, and its length changes
0.67 mm per mm of lift just after the start and 0.98 mm when lifted. So the force is highest at the start, as soon as
the elements hang on their stops (about 32 mm up): 1530 N static for the 104 kg that moves, 1990 N with 30 % extra
for starting and friction in the pins (`ACT_DYN`). Advanced looked only at the lifted position (1460 N with the
30 %); that was too optimistic. The 24 V variants of the datasheet with that load (`lfa2_calc.actuator_variants()`):

| Spindle / gear | max load | margin | lift speed | lift time |
| --- | --- | --- | --- | --- |
| 20 mm, F 1:18 | 1700 N | 0.86 | 48.6 mm/s | 3.0 s |
| 16 mm, F 1:18 | 2000 N | 1.01 | 43.1 mm/s | 3.4 s |
| **12 mm, F 1:18** | **2600 N** | **1.31** | **34.8 mm/s** | **4.2 s** |
| 16 mm, G 1:31 | 3400 N | 1.71 | 29.2 mm/s | 5.0 s |
| 12 mm, G 1:31 | 4500 N | 2.26 | 22.9 mm/s | 6.4 s |

The 16 mm spindle would just do it (margin 1.01), so with no reserve. The 12 mm spindle with the F gear is the
lightest one with margin. It is still fast enough for a headland (4.2 s up, 3.3 s down), and it self-locks up to
3400 N, 3.3 × the holding force when lifted. In a dip (the toolbar floating 70 mm low when the lift starts) the static
force rises to 1860 N: still under 2600 N with the 30 %. Duty cycle: up and down once per 100 m row at 0.75 m/s is
about 5 %; the LA36 allows 20 % at full load. Order with the slip clutch (motor type B), so a jam does not break the
drive, and with the standard end switches.
Order code (datasheet pp. 10–12): `36 120 150 0 0 01 B 6 - 6 1 2 F 3 0350 N C S 0 0 0`.
