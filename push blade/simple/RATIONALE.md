# Push blade (simple): why it is built this way

## Front, not mid-mounted

Mid-mounted (between the wheels) the blade would have to pass the steering sweep of the front forks and the
hub motors, and the frame is only 40 mm beams there. In front, a blade can be wider than the tyres (so the tyres drive on
cleared floor), the operator sees it and the same front toolbar serves other front tools (broom, rake). The price is a
long overhang: in transport the rear axle keeps only ~15 % of the weight (see below).

## Front toolbar under the front lower beams

Same idea and same tube (80 x 80 x 4) as the rear toolbar of the disc brushes: two hangers with a 10 mm top plate,
2 x M10 per beam in the 50 mm hole grid at x = +-175 / +-225, and two 6 mm webs that wrap the toolbar. The hangers stay
at x 150..250, inside the wheel bracket top plates (x 261) and outside the steering stack. The toolbar sits at y 780..860,
z 450..530: in front of the steering sweep of the front tyres (front of the tyre at most y ~721 at 30 degrees) and above
the tyre top (z 430).

## Lift arms, king pin and angle lock

- Two arms 60 x 40 x 3 on O20 pins in forks under the toolbar. One weldment (arms + cross tube 60 x 60 + round head
  plate + actuator lug), so it is one cut-and-weld job and has no loose joints.
- Blade angle +-25 degrees in 12.5 degree steps about an M30 king pin with a PE washer between the two 12 mm round
  plates; a O16 lock pin at the rear of the head plate goes into one of five holes in the swivel plate. Angling by hand is
  enough for a robot that drives the same route every day; a second actuator can be added later on the same plates.
- At 25 degrees the effective width is 997 mm, still wider than the tyres (850 over the tyres).

## Lift actuator and float

- 24 V linear actuator, 1500 N, stroke 100 (via a 48/24 V converter). The base clevis sits on a small mast on top
  of the toolbar, the rod end on a tall lug on the carrier: that gives a lever arm of 164..180 mm about the pivot.
  Lifting the lift group (56 kg) needs ~1190 N, 80 % of the rating. A shorter lug or a lower base cost lever arm and push
  the force past the actuator rating, so the lug is tall on purpose.
- Pin-to-pin length is 268 mm (transport, 18 degrees, edge 159 mm up) to 333 mm (4 degrees below level: hollow in the
  floor); actuator range 260..360.
- The rod pin runs in a 40 mm slot: on a floor the blade floats on its rubber edge and follows bumps without the
  actuator. For grading soil the actuator holds the blade at a set height instead (`held` in `pbl_calc`).

## Blade

- 1100 x 450, 3 mm moldboard on radius 700: vertical at the bottom (cuts and scrapes), curls 133 mm forward at the
  top (rolls the material and keeps it from going over the top).
- Rubber edge 110 x 15 bolted behind the moldboard with a clamp bar and 6 x M10 carriage bolts, 40 mm below the
  steel: quiet and kind to concrete and feed alley coatings. For soil it is replaced by a steel edge (same holes).
- End plates keep feed in front of the blade when pushing straight.

## Forces (pbl_calc)

| | concrete dry | concrete with manure | grass | loose soil (held) |
| --- | --- | --- | --- | --- |
| grip of the tyres (N) | 1142 | 666 | 856 | 935 |
| net push force, continuous (N) | 801 (motors) | 348 (grip) | 481 (grip) | 702 (grip) |

- Motors: 4 x 55 Nm / 0.20 m = 1100 N continuous, 1948 N peak. On a dry floor the motors limit, on wet or dirty floors
  the grip.
- A floating blade rubs with ~44 kg on the floor: 261 N of edge friction. If that is too much on a long run, let the
  actuator carry part of it (stop with the pin halfway the slot).
- A full blade of silage (34 kg) needs 150 N, slurry (139 kg) 340 N, wet snow (55 kg) 82 N: all within reach. Loose
  soil: a full blade (194 kg) is too much; grading 20 mm deep the pile reaches its limit (119 kg) after ~3.9 m, so
  grade in short passes or angle the blade so the soil runs off the end.
- Axle loads: in transport front 202 kg / rear 36 kg (15 %); in work (floating) 123 / 71 kg. 20..40 kg ballast on the
  rear toolbar or rear beams helps for steep yards.

## Estimated, not measured

- Robot mass 160 kg and its centre of gravity midway between the axles
- Tyre grip coefficients (0.60 dry concrete, 0.35 with manure, 0.45 grass, 0.40 loose soil) and rolling resistance
- Rubber edge on concrete: friction 0.6
- Material densities, angle of repose, friction on the floor; cutting resistance of loose soil 30 kPa
- Actuator: 2.6 kg, 10 mm/s at 1000 N; motor + controller efficiency 0.75
- Pile longer than 0.6 m flows round the blade ends
