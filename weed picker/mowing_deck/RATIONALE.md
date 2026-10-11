# Weed picker (mowing deck): design rationale

Why the weed picker looks the way it does, and where the numbers come from. Usage, parts list and files are in the
[README](README.md); other principles and variants in the [concept README](../README.md).

## 1. Assignment

An implement for the Bruut OpenAgbot that mows weeds such as thistles, ragwort and dock **above the grass** and then
**moves them inwards**, so the weed lies together and does not stay spread over the field. It keeps mowing while it
drives through the field, also at a cut height of 10 or 20 cm. An option without a collecting bin. Free in the
choice between a sickle bar and large swinging blades. Cheap, robust and easy to make; efficiency may be lower as long
as it works well.

## 2. The design in brief

Two rotors with free-swinging blades under one stadium-shaped hood, in front of the robot. They turn towards each
other at the front, so in the middle both sweep backwards: the chopped weed leaves through an opening at the rear of
the hood and forms one windrow between the front wheels. Each rotor is a bought lawn-tractor deck spindle with a
48 V BLDC motor straight on top. The hood hangs on a parallel linkage under the front beams; an electric actuator on
the diagonal sets the cut height (100–400 mm) and a slotted float link lets the hood ride up over humps.

## 3. Options

| Principle | Gathering | Making | Verdict |
| --- | --- | --- | --- |
| Sickle bar (double knife) | needs a reel to lay the weed back and an auger or belt to the middle | knife drive (eccentric or wobble box), guards, reel: many moving parts; bought bars are expensive | clean cut at low power, but too much machine for "simple" |
| **Twin rotor, swinging blades, centre discharge** | the rotors themselves: in the middle both sweep backwards | 2 bought spindles, 2 motors, laser-cut plates | **chosen** |
| Single large rotor | throws to one side, the windrow ends under a wheel | simplest drive | no |
| Flail mulcher | spreads the material over the full width | heavy rotor, belt | no gathering |
| Disc mower (several small discs) | windrow possible with drums | gearbox bar | too expensive |

Rear-discharge twin-blade decks on lawn tractors and twin-rotor toppers use the same flow: two rotors turning
inwards push the cut material out of a gap at the rear between them. Here the gap points under the robot, so the
material lands between the wheels.

## 4. Why in front

- The robot's beams are 619 mm above the ground and the weeds are 0.5–1.2 m high. Behind the robot (or between the
  axles) they would be pushed over by the beams and run over before they are cut; a bent stem is not cut cleanly.
- In front, the weed is cut while it still stands. The windrow then passes between the front wheels and under the
  robot; the wheels run on the cut strip (cut width 990 mm, tyres at x ± 325 … 425).
- The cost is the overhang: the rotor axes are 560 mm in front of the front axle, and the robot gets 85 % of its
  weight on the front axle (§ 8).

## 5. Why the rotors this way

- **Free-swinging blades** (topper principle): a blade that hits a stone, a molehill or a post swings back on its
  bolt instead of bending the spindle. Flat 50 × 6 with both edges ground: the same blade fits both rotors (they turn
  opposite ways), and it can be turned over. Centrifugal force 3.7 kN per blade keeps it straight out; the M16 bolt
  sees 24 MPa.
- **2 blades per rotor, Ø510:** two Ø510 circles cover 990 mm, more than the robot's 850 mm over the tyres. Fewer
  blades = less windage (§ 9).
- **2400 rpm, tip 64 m/s:** impact cutting of stiff weed stems needs much less than the 80–90 m/s of a lawn mower;
  64 m/s cuts and chops cleanly and keeps the windage at ≈ 200 W per rotor (it grows with the speed cubed). The BLDC
  drivers set the speed, so it can be changed without parts.
- **One motor per rotor, no belts:** a counter-rotating pair with one motor needs a crossed or double-V belt and an
  idler. Two motors straight on the spindles are simpler and the drivers turn them in opposite directions.
- **Overlap without timing:** blades of two rotors that overlap must be timed (belt) or they hit each other. The left
  rotor sits 24 mm higher (2 laser-cut rings of 12 mm under its spindle flange), so the blade circles can overlap by
  30 mm and leave no uncut strip in the middle. Above 100 mm the 24 mm difference in cut height does not matter.
- **Deck spindle + jaw coupling:** the spindle is made for blade impacts (2 bearings, €35); the motor bearings only
  carry the coupling. The jaw coupling's rubber spider takes the shocks and the misalignment of the standoffs.

## 6. Why the hood this way

- **Stadium shape, 35 mm outside the blade tips:** two circles joined by straight plates, laser cut in one piece;
  the skirt is rolled 3 mm sheet. The blades sweep the material along the skirt to the opening.
- **Skirt 10 mm below the blades, open only at the rear between the rotors (x ± 200):** the front skirt pushes tall
  plants over so they are fed under the deck and chopped over ≈ 0.6 m of travel (6 mm per blade pass at 0.5 m/s);
  the closed front and sides keep stones in. The opening points under the robot.
- **Rear notch in the deck plate:** the plate stops 40 mm behind the deck pivots, so the bottom links stay clear of
  it at a high cut (they slope down towards the robot there).
- **Swath boards** (2 plates, 150 mm, from ± 200 to ± 160): keep the windrow narrow and 165 mm away from the tyres;
  short enough to stay outside the steering sweep of the front wheels (≥ 47 mm at ± 30°).
- **Crossbeam 50 × 40 on the deck:** stiffens the 3 mm deck between the spindles and carries the lugs.

## 7. Why the linkage and the actuator

- **Parallel linkage:** keeps the deck level over the whole range of 300 mm (± 20° on the links); the deck moves
  only 31 mm back at the ends. Links are pairs of laser-cut flat bars 40 × 6 on both sides of a 10 mm lug: double
  shear on the M16 pins, no welding on the links, and the bars can be replaced.
- **Actuator on the diagonal:** it changes the length of the diagonal from pin A (robot) to pin B (deck); no extra
  lever or cross shaft. The lever is short (the diagonal is close to the links): 300 mm of height is 104 mm of
  stroke, and holding the deck takes ≈ 1.8 kN. A 4000 N actuator is cheap and leaves margin for bumps (≈ 4 kN with
  × 2). It is slow (10 mm/s, ≈ 10 s for the full range), which is fine: the height is set per field or per weed.
- **Float link with a slot at the robot end:** the deck rests on the actuator (it can never drop below the set
  height) but a hump lifts it: pin A slides in the 60 mm slot. That is 30–175 mm of lift, depending on the height.
  The slot is at the robot end because at the deck end the free bars hit the crossbeam when the deck rises.
- **Cut height 100–400 mm:** the user's 10–20 cm is in the lower half; 300–400 mm is for very tall weed above long
  grass, and the top of the range is the transport position. The top link reaches the mount plate at 26° (cut
  428 mm), so 400 is a safe end of the range.

## 8. Robot and loads

- **82 kg**, centre of gravity 340 mm in front of the front axle. The robot then has 85 % of its weight on the front
  axle (206 kg, the hub motor spec is 500 kg per axle) and only 37 kg on the rear wheels. That is enough to drive on
  flat ground with 4WD, but for slopes and braking downhill put ≈ 45 kg on the rear beams (30 % rear), e.g. the two
  20 kg blocks of the feed pusher, or move the battery to the rear.
- **Mount:** 8 × M10 through two beams 150 apart: 642 Nm (× 2) gives ≈ 1.2 kN per bolt, against 33 kN proof load.
- **Links:** ≤ 6.4 kN in compression (weight × 2, 600 N drag, the actuator pulls the deck back): 12 MPa in the bars,
  Euler 15 kN, pins 8 MPa. The plates are thick for wear, welding and stiffness, not for strength.
- **Steering:** links and actuator are within x ± 114, the fork of a front wheel sweeps down to x 210; the deck and
  the swath boards stay ≥ 47 mm from the wheels at ± 30° steering over the whole height range.

## 9. Power, speed and capacity

- **Windage dominates when there is little weed:** 2 blades edgewise at 64 m/s cost ≈ 200 W per rotor. The
  efficiency is lower than a sickle bar's, as allowed.
- **Chopping:** 4 kJ per kg of weed above the cut (estimated: a tractor topper in a heavy weed crop takes several kJ
  per m²; here the energy is set per kg of weed so it scales with the weed, not with the area).
- **The robot drives slower in thick weed:** each motor gives ≈ 600 W at 2400 rpm. At 0.2 kg/m² (scattered weeds)
  the motors run at 70 % at 0.5 m/s; in a dense patch (1 kg/m²) the robot has to slow to 0.16 m/s. The drivers
  report the current; the robot software reduces the speed (the animation does exactly that).
- **Capacity:** 0.18 ha/h at 0.5 m/s; ≈ 1.6 h and ≈ 0.3 ha per charge. Spot topping (camera, rotors only where the
  weeds are) would roughly double the run time; listed as a variant.

## 10. What is estimated, and what is left out

Estimated (see the README list): robot mass and centre of gravity, motor, spindle and actuator data, weed masses and
the energy to chop them, the share in the windrow and its bulk density, blade drag, driving power, design loads.

Left out of the model: cables, the coupling guards, grease nipples, washers on the pins, the keys of the shafts, the
screws of the motor flanges, the bevels on the blades, a transport lock.

Not checked: the actual air and material flow under the hood (the windrow share of 85 % is an estimate, to be
checked with a prototype and adjusted with the swath boards), wrapping of long stems around the spindles, the
blades' swing back on an impact (only the energy: 361 J per blade), the deck on a side slope, and the robot's
steering with the light rear axle.
