# Dockweed drill v9 advanced: why it is designed this way

(The simple variant is [../simple](../simple/RATIONALE.md).)

The brief: "a v9 based on skate wheels running in U profiles, the profile takes the side forces and the wheels
roll, for both the up/down axis and the X axis, look at ease of installation rather than the least material, and
use it with the linear actuator". The sketches in `../inspiration/` show two U profiles per axis with the openings
towards each other, a carriage with wheels in both profiles, the LA36 in the middle of the Z axis and on the X axis a
belt (or chain) round a wheel at each end with the motor at one end.

So v9 keeps everything of v8 that is not the guide: process, spindle, 800 W gearmotor on a Ø 30 spindle in
2 × UCP 206, jaw coupling, Ruud-style can, cutter, Linak LA36 as the Z drive, headstock, camera
([../../v8/RATIONALE.md](../../v8/RATIONALE.md)). The round tubes and plain-bush housings are replaced by stock steel
channels and skate wheels.

## 1. The wheel: what the user picked

- **Zandstra 80 mm 78A, set of 8 with 16 × 608ZZ** (see `../inspiration/skeeler wheels.txt`). Ø 80 × 24, bore 8 mm:
  an M8 bolt is the axle. 32 wheels are used, so **4 sets of 8**.
- The 608 bearings are not the limit: 2 × 1370 N static per wheel, 7× the 400 N we allow per wheel.
- **The PU is.** 78A is a soft "comfort" compound; on request the model now uses **90A** (E ≈ 21 MPa:
  1.3 mm at 600 N, cutter deflection 4.4 mm at 100 N instead of 7.7). The 78A text below is kept for comparison. With a thin-layer estimate (E ≈ 8 MPa from the Shore hardness,
  tread 14 mm, contact width 15 mm) a wheel compresses about **1.9 mm at 400 N** (≈ 215 N/mm). That makes the
  guide soft, not weak: see §5. The same wheel in 85A..90A is a drop-in (same block, same axles); set
  `wheel_shore` in `dwd9_params.py` and the calculation follows.

## 2. One wheel block for both axes (8 the same)

A wheel only takes load along its radius. A U profile has two kinds of running surfaces: the two **flanges**
(facing each other, 85 mm apart in a UPE 100) and the **web**. So every block carries:

- **2 flange wheels** (axle along the depth of the profile), one pressed against each flange. Two wheels, two
  flanges: no play across the profile in both directions. The axle holes are slotted (± 4 mm) so each wheel is set
  against its flange on the bench: loosen, push, tighten. That also takes up the rolling tolerance of the profile
  (UPE height ± 2 mm).
- **2 web wheels** on one M8 through two ears (double shear), rolling on the web. They take the load along the depth
  of the profile. Two side by side halve the load per wheel. The opposite profile has its own web wheels, so the
  pair of profiles holds the carriage in that direction too.
- So the "side force" of the brief is not taken by the wheel face sliding on the web: it is taken by wheels that roll
  on the web. Everything rolls, nothing slides.

The block is a 10 mm steel L: base plate just above the flange tips (with a window for the web wheels and the slots
for the flange-wheel axles), a mounting flange with 4 × M8 in slots along the depth (that sets the web wheels against
the web), and two 5 mm ears. One drawing, one set of parts, eight times. Installation per block: 4 bolts.

**Why UPE and not UNP:** UNP flanges taper 8 %; a wheel on a sloping flange is pushed sideways. UPE (EN 10365) has
parallel flanges. UPE 100 gives 85 mm between the flanges for an 80 mm wheel and 50.5 mm depth for the 24 mm wheel
plus the bolt head.

## 3. X axis

- **2 UPE 100 with the openings towards each other**, as in the sketch: the lower one open upwards (it carries the
  weight on its web), the upper one open downwards. They are welded at their ends to 2 end plates: the X frame is one
  weldment.
- **No cross beams any more.** The front flange of each profile lies against the back of the 2 uprights, with
  2 × M8 countersunk (DIN 7991) per crossing: the head sits flush in the flange, away from the wheel track
  (bolt 42 mm from the web, wheel track 14..38). The channel is its own beam (weak axis 38 cm⁴ against 9 cm⁴ for the
  old 40 × 40 × 3): 0.2 mm down with the slide at x ± 500. Installation: lift the X frame onto the uprights,
  8 bolts.
- The lower profile is a gutter: 20 drain holes Ø 10 in its web, outside the wheel track.
- **Motor fixed at the right end** (sketch): NEMA 23 closed-loop + 5:1 on a bracket plate welded to the end plate,
  pulley 20T on the gearbox shaft; on the left a tension pulley on an M10 in a slot. The belt (HTD5M 15 mm) runs
  between the profiles at z 915 and is clamped to the front of the slide. The motor cable no longer moves; the slide
  carries no motor, idlers or pulley (v8 had an omega drive on the slide).
- 4 wheel blocks on the front of the slide, 2 per profile at x ± 132.

## 4. Z axis

- **2 UPE 100 standing at x ± 175**, openings towards x 0, welded on the lower yoke of the spindle bracket with a
  gusset outside each profile. They move with the spindle (as the tubes of v7/v8); the 4 wheel blocks sit on the
  back of the X slide at z 760 and 1060.
- Between the profiles there is room for the LA36 (± 38), the back plate of the spindle bracket (± 80) and the
  actuator eye bracket: the web wheels stand at |x| ≥ 95. The spindle comes out at robot y −947, 7 mm closer to the
  robot than in v8.
- No clamp plate and no top yoke: the LA36 and its top bracket sit between the profiles over the whole stroke.
  The profiles are stiff enough as two cantilevers on the welded yoke (0.5 mm at the cutter for 300 N side force).

## 5. What it costs

- **Stiffness.** The soft wheels dominate the deflection of the cutter: about **8 mm at 100 N side force** (normal
  work, estimated) and **17 mm at 300 N** (design peak), against 2.4 mm in v8. That is without preload; with the
  flange wheels set against each other both wheels of a pair carry, roughly halving it. The can (Ø 219 round a Ø 180
  cutter) and the 40 mm position tolerance absorb this; if not, use harder wheels (90A: about half again).
- **Mass 170 kg** (v8 127 kg): the 8 steel blocks (~3.7 kg each), 4 UPE profiles (50 kg) and the bigger slide.
  109 kg moves in x (v8 76).
- **Axle load:** the front axle carries only **26 kg (8 %)** when driving; the lightest front wheel drops to about
  7 kg with the slide at x ± 500. That is too light for steering and traction: battery forward and a
  [counterweight](../../../counterweights/simple/README.md) at the front are needed, not optional.
- **Width 1570 mm** over the end plates (v8 1470): the slide is 540 wide for the 2 blocks per profile.

## 6. Open points (v9)

1. Measure a real wheel: compression at 100..500 N (we assume 1.9 mm at 400 N) and compression set after a night
   under 270 N (the static load on the lower X web wheels). If it flattens, use 85A..90A.
2. Weld the X frame flat: the 2 profiles must be parallel within about ± 1 mm over 1550 (the flange wheels can be set
   ± 4 mm, the web wheels ± 5 mm). Weld the Z profiles on the yoke with the profiles in the wheel blocks as a jig.
3. Countersunk M8 in a 7.5 mm UPE flange: 4.4 mm head in 7.5 mm leaves 3.1 mm. Check the seating, or use a flat
   head with a thin washer plate on the upright side.
4. Belt length about 3.06 m (HTD5M 15 mm open length with clamp); belt stiffness and the tension slot (± 10 mm) to be
   checked with the belt you buy.
5. Lighter blocks (8 mm instead of 10 mm saves about 6 kg) if the axle load stays a problem.
6. All open points of v8 for the spindle, LA36 and can.
