# Around-pole fence mower (simple): design rationale

Why the mower looks the way it does, and where the numbers come from. Usage, parts list and files are in the
[README](README.md); designs found online and other variants in the [concept README](../README.md).

## 1. Assignment

Mow the grass under an electric fence with the Bruut OpenAgbot: simple, cheap, robust and easy to make. Grass that
touches the bottom wire drains the fence; today this strip is done with a brushcutter or a tractor-mounted fence
mower. The robot already drives along a line with RTK; the implement has to cut under the wire and get past the
posts by itself.

## 2. The design in brief

A trailing swing arm on a vertical post behind the right rear wheel. On the arm: a 48 V motor at the root, a V-belt
inside the arm, a bought deck spindle at the tip with a disc and 4 nylon strings under a PE guard ring. A spring holds
the arm on a rest stop; a post pushes the head back and in, the head slides around it, the spring brings it back.
The arm floats on a hinge and is carried by an HDPE skid.

## 3. What others do (online, October 2026)

| Design | How it gets around a post | What we took |
| --- | --- | --- |
| Tractor fence mower, US patent 7,287,364 | swing arm on a pivot pin, spring pulls it back under the fence, a **wedge nose** guides it under the bottom rail and turns a post hit into a swing; PTO → right-angle gearbox → belt → spindle → blade | trailing swing arm + spring, belt inside the arm, the spindle at the tip |
| Kneilmann "Zaunkönig" (topagrar test) | a **star with 3 mowing heads** turns around the post as the tractor drives on; blades inside a plate plus **double nylon strings that reach past the plate** to the post; 2900–3000 rpm; head 15 cm, bottom wire ≥ 40 cm; €6,390 | head speed (≈ 3000 rpm with strings beyond a plate is proven), strings past a guard, the warning that step-in posts are not stable enough |
| Tractor fence trimmers ("trimmer type", e.g. Swisher-style, AgrAbility toolbox) | spring-loaded arm with thick cutting cords; about half the price of the blade type | **cords instead of blades**: cheaper, safe on wire and posts |
| DIY: string trimmer on a riding mower / ATV / loader | spring-loaded pivot; height from the carrier | the simple spring pivot is enough |
| Robot mowers with an edge trimmer | none, they leave a 10 cm strip at fences | the robot needs a tool that reaches under the wire |

The star (Zaunkönig) gets behind the post best but needs 3 drives and a brake; a single head on a swing arm is the
simple version and the best fit for a 48 V robot.

## 4. Why string and not a blade

- Nylon does not conduct: touching the wire does not short the fence, and cannot cut it.
- A string that hits a post bends; a blade chips the post or breaks.
- A string reaches past the guard ring, so the head can slide along the post *and* cut right up to it.
- Price: a roll of line, 4 pieces of 110 mm per change, 4 clamps. No sharpening.

The cost is power: the strings' air drag (≈ 180 W at 3667 rpm) is about a third of the shaft power. The disc carries
the clamps, so the free string is only 70 mm long (r 130 → 200) and stays stiff at 77 m/s.

## 5. Why this geometry

- **Behind the right rear wheel, trailing:** a trailing arm is stable like a castor; a leading arm digs in. Behind
  the robot nothing is in the way when the arm swings in (up to 85°, the head ends up straight behind the robot). The
  robot does not have to drive close to the fence: the body stays 279 mm from the post face.
- **Rest angle 30° behind the +x axis:** a post force backwards always swings the arm back and in (no dead point);
  head travel inwards starts immediately (dx/dψ = −L sin ψ). At 0° the head would first have to move back without
  moving in.
- **Post line 100 mm outside the head centre:** the post hits the guard 29° off head-on, so the contact force has a
  good lever about the pivot. With 40 mm the swing was 23° and the impact 250 N; with 100 mm it is 16° and ≈ 210 N,
  and the uncut area per post drops from 330 to 150 cm². The head then runs right under the wire (10 mm outside it).
- **Arm 640 mm:** reaches from the post behind the tyre (x 175) to 829 mm for the post line, with the robot well
  away from the fence.
- **Pivot post at x 175:** the 2 webs fit between the grid holes x 125 and 225 (M10 nuts outside the webs) and stay
  50 mm away from the wheel bracket (x 261).

## 6. Why the drive this way

- **Motor at the root, belt in the arm:** a motor on top of the head would make it ≈ 350 mm high. Now the part under
  the wire is 182 mm, and the heavy motor sits close to the pivot (less inertia, lower post force).
- **Deck spindle:** a lawn-tractor spindle is made for exactly this: 2 bearings, impact loads from a blade, a pulley on
  top, a blade boss below, about €35. Its 3 flange bolts also clamp the guard cover.
- **V-belt A, 110 / 90:** 3000 rpm motor → 3667 rpm head, tension with slotted motor holes (no idler), and the belt
  slips instead of breaking something if the strings wrap up.
- **48 V BLDC 750 W:** runs from the robot battery, no brushes in a wet and dusty place, the driver can limit the
  current and stop the head when the robot stops. 615 W at 0.5 m/s is 70 % of the rating; at 1 m/s it would be 110 %,
  so 0.5 m/s is the working speed (like the Zaunkönig's ≈ 2 km/h at the posts).

## 7. Why the guard, the skid and the hinge

- **Guard ring from PE pipe 315:** round, smooth, wear resistant, slides on wood (μ ≈ 0.25), insulates, and is a
  cheap offcut. A circle is its own lead-in (the patent's wedge nose).
- **Skid on the rear-inner side:** under the head is the disc, so the skid sits beside it, at the same distance from
  the hinge as the spindle (it carries the head, not a lever). On the rear-inner side (−v) it is away from the posts
  and outside the string circle.
- **Hinge with ± 5° float:** the head follows the ground on its own skid (± 49 mm); the robot does not have to. Two
  stop bars on the clevis limit the float and carry the arm when the robot drives over a hump (20 MPa in the arm,
  3 kN on the bar, × 2 for shocks).
- **Return spring on a lever, not a torsion spring:** a catalogue extension spring with an eye bolt for the preload.
  The geometry keeps the torque almost constant: 33 Nm at rest, 40 Nm at 60°, 36 Nm at 85°. At rest it holds the arm
  against 22 Nm of grass drag with a margin of 1.5.

## 8. Robot and loads

- **50 kg** behind and right of the robot: the front axle keeps 36 % and the right side carries 61 %. The right rear
  wheel gets 83 kg, well below the 500 kg per axle of the hub motors. For steering on slopes a counterweight on the
  front beam (the 2 × 20 kg blocks of the feed pusher) helps; not modelled.
- **Post force:** ≈ 210 N at first contact at 0.5 m/s (mostly the inertia of the arm), 20–30 N while sliding. Enough
  for wooden, concrete and steel posts; too much for plastic step-in posts (see README).
- **Strength:** low everywhere (arm ≤ 26 MPa, pivot post 6 MPa, hanger bolts 1.3 kN per pair against 33 kN proof
  load). The plates are 6–10 mm for wear, welding and stiffness, not for strength.

## 9. What is estimated, and what is left out

Estimated (see the README list): robot mass and centre of gravity, motor and spindle dimensions and masses, grass
cutting energy and drag, damping, friction PE on wood, spring data, fence geometry, driving power.

Left out of the model: cables (motor cable along the arm to the box), the grease nipple, the screws of the guard ring
and the cover, the slots in the skid leg and motor plate (drawn as plain plates), the key on the motor shaft, a
transport lock (a chain from the post to the arm to lift the head for driving on roads), a counterweight.

Not checked: the dynamics of the head on rough ground (only the float range), wrapping of long grass around the
spindle, a post that leans towards the robot, mowing in the other direction (the arm is built for driving forward,
fence on the right; for the left-hand side, mirror the parts).
