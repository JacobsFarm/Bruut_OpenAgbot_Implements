# Dockweed drill v9 simple: why it is designed this way

The brief (after [../advanced](../advanced/RATIONALE.md)): switch to the harder 90A wheels, and make a simpler design
with 2 wheels per U profile; the U profiles stay fixed on the same plate as the actuator, the plate with the drill
has 2 wheels on each side that run down in a 25 mm U profile; the same for the X axis; 4 mm steel is strong enough.
The old design became "advanced".

## 1. The track and the wheel

- A 25 mm U fits the 24 mm wheel only one way: the **tread runs on the web** and the wheel sticks out of the
  opening; the flanges hold its sides. So every wheel axle runs front to back (along v), perpendicular to the plates.
  That makes each wheel one M8 bolt through a plate, a spacer and the wheel: the simplest possible mounting.
- The wheel centre is 15 mm outside the flange tips, so the bolt head in front of the wheel stays clear of the flange.
  Where that head would hit something (the uprights, the slide) the track sits on a shim or strip.
- Bent U 4 mm, 25 × 25 inside, from flat bar or laser-cut and bent; for the X axis welded on a beam 50 × 30 × 4,
  because a 4 mm U alone sags too much over the 500 mm overhang outside the uprights.

## 2. Z axis: tracks fixed, drill plate rolls

- The 2 Z tracks are fixed on the X slide, as asked: the same plate as the LA36 top bracket. The drill plate rolls
  down in them on 2 + 2 wheels (300 mm apart). Nothing above the slide moves except the drill plate, the LA36 rod
  and the spiral cable.
- The drill plate is also the back plate of the spindle bracket, and the LA36 moved behind it. The spindle comes out
  86 mm closer to the robot than in advanced (robot y −861).
- Track length 790 mm (z 445..1235): from 10 mm above the rear tyres to just below the LA36 housing.

## 3. X axis: the same principle

- Lower track open upwards (the wheels carry the weight on its web), upper track open downwards, 2 wheels in each on
  the X slide (4 mm). The tracks sit on beams 50 × 30 × 4 with a 10 mm shim on the uprights; the beams start 3 mm
  behind the upper robot beams.
- The X drive stays as in advanced: motor fixed at the right end, belt clamped to the slide.

## 4. What still has to be checked (calculations to follow)

What the model already shows: no interference in any end position, all 8 wheels sit 0.3 mm from their web, and the
mass drops to 117.6 kg (advanced 170.1 kg, v8 127.0 kg).

What happens with the loads is the open question: the wheels roll only towards the web. Forces across the track
(front–back on X and Z: the moment of the cantilevered spindle and the Z force) are taken by the wheel side sliding
on the flange, with 1 mm play in total. To be calculated: side force per wheel, friction against the belt force
and the LA36, axial load on the 608 bearings, play at the cutter, and the stiffness of the 4 mm slide and drill plate.
