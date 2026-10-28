# Grassland aerator (simple): why it is built this way

## Slitter knives, not spikes or hollow tines

A slitting knife (6 mm plate, tapering to a point) cuts a narrow slit and needs far less force than a solid spike or a
hollow tine of the same depth: ~160 N for 70 mm in moist grassland against 400..800 N for a hollow tine. A small robot
cannot press much, so the knife is the only element that reaches a useful depth with the weight it has. Hollow tines
(cores) are left for a heavier, trailed machine.

## In the middle of the robot, between the axles

- Behind the robot a pressing roller lifts the front axle (lever) and only the rear axle can give weight. Between the
  axles the reaction of the roller is shared by both axles, so the whole robot can press and steering stays normal:
  in transport 47 / 53 % front / rear.
- There is room: between the tyres (y +-285 at the steered front tyre) a star of O450 fits, and outside the wheel
  units (x > 525, the steering sweep) the side arms and hangers run past the front wheels. The roller (1.2 m) is wider
  than the track (750) and slits the wheel tracks too.

## Roller

- 8 stars at 150 mm, 6 knives each, neighbours turned half a knife pitch: the knives enter one after another (about
  1.55 knives per star in the ground at 70 mm), the roller runs smoothly and turns by itself (no drive).
- Slits 150 x 236 mm: 28 slits per m2. 1.2 m at 1.2 m/s gives ~0.41 ha/h.
- O40 shaft (hex in practice, stars slid on with spacer tubes) in 2 UCFL208 flange bearings on the side arms.

## Weight, ballast and actuator

- Needed: 8 stars x 1.55 knives x 160 N = ~1980 N. The frame with 4 ballast blocks (the 20 kg blocks of the disc brushes
  and fertilizer spreader) puts ~1790 N on the roller by itself; the actuator pushes the rest (~120 N).
- The wheels have to pull the roller: at most ~2420 N on the roller keeps a grip margin of 1.3 on grass. At the
  needed load 148 kg stays on the wheels, pull 325 N, margin 2.0, ~0.5 kW.
- Ballast stacks between the inner upper beams (x < 305), so they can rise between the beams when lifted.
- Actuator 24 V 2000 N, stroke 200, vertical from a mast on the rear bridge: retracts to lift the roller 14 degrees
  (knife tips 36 mm above the ground, ~1.3 kN), extends to press. ~13 s for the full lift; at the headland half the
  stroke is enough.

## Estimated, not measured

- Robot mass 160 kg and its centre of gravity midway between the axles
- Knife force 160 N at 70 mm (moist grassland); dry soil needs more ballast or less depth
- Pull of the knife roller 0.12 x its load; tyre grip 0.45 and rolling resistance 0.06 on grass
- Actuator 3.6 kg, 15 mm/s at 1300 N
- Free space between the axles under the upper beams: the model has no battery or electronics box there; check the
  real robot before building
