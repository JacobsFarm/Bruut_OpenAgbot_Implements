# Stone picker (simple): why it is built this way

## Under the robot, between the axles

- Between the axles (y -235..235) there are no tyres and nothing under the beams: the full width is free from the
  ground up to the beams. A picker there keeps the stones between the axles, so the axle loads hardly change when the
  basket fills (front axle 45 % empty, 41 % full) and no counterweights are needed. A front-mounted picker (push blade
  arms) with 40..50 kg of stones 1.5 m in front of the front axle would lift the rear axle off the ground.
- The rotor is 1 m wide (wider than the track, 850 over the tyres), so it also picks the strip the wheels run on. The
  basket behind it is only 488 wide: it has to pass between the rear forks (inner face x 263).

## Rotor, comb, sieve basket

- The rotor turns so that the tines move backwards at the bottom (7.9 x the driving speed at 250 rpm, tip 3.9 m/s):
  they dig 20 mm into the soil, catch the stones and flick them backwards over a comb of 12 mm bars into the basket.
  Side deflectors guide the stones from the rotor ends (x +-495) to the basket.
- The basket floor is a sieve of 12 mm bars with 25 mm gaps: soil, crumbs and small stones fall back through.
- Spring tines (O9 wire, double) give way over fixed stones and big roots instead of stalling the rotor.
- Power: raking 20 mm of topsoil, 1 m wide at 0.5 m/s, with ~30 kJ/m3 plus 120 W losses: ~525 W from a 48 V 750 W
  planetary gearmotor on the right end. Grip is no issue (margin 3.4): the rotor even pushes the robot a little.

## Parallelogram lift outside the wheel line

- The frame hangs on 4 swing links 250 mm long. They run outside the wheel line (x 546..554), on hangers under the
  outer upper beams, because between the axles that space is free and the links then pass beside, not over, the rotor
  cross tube. A rear pivot (one axis) was tried first: it lifts the rotor but hardly the rear of the basket.
- From 55 to 80 degrees the frame rises 100 mm and moves 41 mm forward, level. The links point forward, so lifting
  moves the rear of the basket away from the rear forks; the rotor stays 43 mm from the (lugged) front tyres with the
  wheels steered 30 degrees.
- One 24 V 1500 N actuator, stroke 150 (uses 336..429), almost upright from a lug on a bearer across the upper beams
  to the rear cross tube: it holds 1265 N with a full basket, 9 s to lift.

## Emptying

- At the heap the frame is lifted and a 24 V actuator behind the basket drops the sieve floor 20 degrees about its
  front hinge; the robot creeps forward and the stones roll out behind the floor, between the rear wheels, onto a heap
  the robot then leaves behind. 20 degrees is what the floor lug allows above the ground; sticky or flat stones may need
  a shake (close and open again).

## Capacity

The basket holds 40 l: ~44 kg of stones (bulk 1550 kg/m3, 70 % usable). How far that goes depends on the stones per
m2: 870 m2 at 0.05 kg/m2, 218 m2 at 0.2, 87 m2 at 0.5. With 40 s to dump and 60 m to the heap and back that is
1200..1700 m2 per hour, about 1 ha per 8 h day, 3 h per battery charge (the robot's own battery, more with the battery
pack). For a large stony field this is a cleaning-up tool for seedbeds, paddocks and lawns, not a replacement for a
tractor stone picker.

## Estimated, not measured

- Robot mass 160 kg, cg (0, 0, 380); tyre envelope O530 x 100 from the model
- Stone bulk density 1550 kg/m3, usable basket share 0.7, stones per m2 for the three cases
- Raking energy 30 kJ/m3, losses 120 W, gearmotor efficiency 0.8, comb drag 150 N
- Actuator speed 10 mm/s, masses of the gearmotor and the actuators
- Dump time 40 s, 60 m to the heap and back; that stones roll off the floor at 20 degrees
