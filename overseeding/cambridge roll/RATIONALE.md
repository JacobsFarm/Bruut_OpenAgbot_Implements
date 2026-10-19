# Cambridge roll, simple: why it is built like this

## Trailed, not mounted

A roller has to follow the ground over its whole width and carries weight that belongs on the ground, not on the
robot. Trailed on a ball it rests on the roll and on the ball only (a statically determinate support): it follows
hollows and bumps by itself and the robot only carries 10 kg of it. A mounted roller would need a parallel linkage,
a float and a lift actuator, and its weight would unload the front wheels.

## Tow hitch with a 50 mm ball

The cheapest coupling that allows yaw, pitch and roll at the same time is a car tow ball with a bought coupling head
(about € 15 + € 30). A pin hitch with a drawbar eye needs a vertical pin and play for pitch and roll, and a clevis on
the trailer side. The ball is bolted with one M20 stud through a square tube, so it can be swapped for another size or
a pin later.

- The top plate uses 4 holes of the 50 mm grid under both rear lower beams (x ±175, y −575 and −425): the same
  sandwich as the other rear implements, 86 mm clear of the wheel brackets (x 261).
- Ball at y −830: the coupling head has a rounded nose of Ø90 around the ball and reaches y −785, 70 mm behind the
  rear tyres (−715). The drawbar points backwards from the ball, so even at 90° articulation nothing comes near the
  tyres (26 mm from the braces to the hitch bar at 90°).
- Ball centre at z 330: the drawbars (60 × 60) are then nearly level with the frames of the roll and the seeder
  (cross beams at z 300 … 340). The hitch bar is 205 mm above the ground: enough on a lawn and over a ridge.

## Rings

- **Cambridge rings, not a smooth drum**: the ridges press the soil in narrow bands and leave a ribbed surface; seed
  that lands in the grooves is covered and kept moist, and water does not run off. Each ring turns on its own on the
  shaft, so in a turn the outer rings run faster than the inner ones and the sward is not torn (a drum scrubs).
- **Ø280, 50 mm wide, 20 rings = 1 m**: small enough for the robot (draft and turning), still large enough to roll over
  a molehill. Generic spare-part rings of this size exist; the profile here is a generic one with a 6 mm web and rim
  and a ridge of 24 mm. Volume by Pappus: 6.65 kg per ring, 133 kg for the roll.
- **Line load 169 kg/m**: garden lawn rollers weigh 60 … 150 kg per metre; agricultural Cambridge rollers 300 … 700 kg/m.
  A seedbed for grass repair wants firm, not compacted soil; 150 … 200 kg/m with a ridge pressure of 60 … 200 kPa
  (sinkage 15 … 5 mm) is in the right range. More weight is possible with a ballast tray on the arms, but the draft
  grows with it.
- **Shaft Ø40**: the rings carry their own weight directly to the ground; the shaft only carries the frame (350 N):
  8.6 MPa bending, far below the limit. Ø40 is the bore of the rings and of a standard UCFL208, so no turning is needed.

## Frame

- Side plates (10 mm laser cut) with the bearings on the outside: the shaft can be pulled out sideways to change rings
  without taking the frame apart.
- Arms and cross beam of 40 × 40 × 3 on top of the side plates, 20 mm above the ring tips: the frame is low (z 340)
  and the arms leave the whole space in front of the roll free. That is where the seeder unit hangs in the
  combination; the stand-alone roll has a short frame (cross beam 250 mm in front of the axle).
- Drawbar 60 × 60 × 4 with two braces: the drawbar takes the pull (≤ 400 N) and the side forces in turns; the braces
  stop the cross beam from twisting.
- Parking leg on a lug above the braces, stowed along the drawbar: when the roll is unhitched the coupling stays at
  ball height. Its position is measured from the front of the drawbar, so the same leg fits every drawbar length.

## Draft and the robot

Draft = rolling resistance × weight on the roll (+ slope × whole trailer):

| Surface | f | Level | Up 5° |
| --- | --- | --- | --- |
| firm lawn | 0.06 | 100 N | 250 N |
| moist lawn | 0.09 | 150 N | 300 N |
| loose seedbed | 0.15 | 250 N | 400 N |

The robot can pull µ × (robot + ball load) minus its own rolling resistance: 580 N on wet grass, 900 N on dry grass
(level), 450 … 770 N up 5°. That leaves a margin everywhere except a loose seedbed up a slope on wet grass (400 vs
450 N), which is the edge of what this roll is for. Extra drive power at 0.5 m/s: 50 … 200 W.

## Not done (yet)

- Scraper bar for sticky soil (an angle iron on the arms behind the rings).
- Ballast tray.
- Lights or a reflector for road use (not needed on a lawn).
