# Precision seeder (simple): rationale

## Why log every seed

A robot that sows also knows where every plant will come up. The in-row weeder and the inter-row hoe can then work
right up to the plant from the first day, before the crop is visible to a camera, which is when weeds are easiest to
kill. That only works if the logged position is better than the hoe's safety zone (~30-50 mm): the estimate here is
~13 mm (1σ) along the row.

## Seed sensor, not the meter angle

The disc angle tells when a seed was released, but the seed then falls ~350 mm through the tube (0.12 s, 96 mm of
travel at 0.8 m/s) and that time varies. The optical sensor low in the tube sees the seed close to the furrow, so only
the last part of the fall and the bounce remain uncertain; a missed seed (empty cell) is logged as missing, a double as
double.

## Own stepper per unit

No ground wheel, no chain: the stepper turns the disc at the speed the controller wants. The spacing can change in the
field (variable seed rate), sowing starts and stops exactly at the headland line (no overlap on the point rows), and
the two units can be phased so the plants of the 2 rows stand in a grid (for cross-hoeing later).

## Vacuum disc

A vacuum disc singulates pelleted beet, maize, sunflower and many vegetable seeds by changing the disc only; a finger
meter is cheaper but limited to maize-size seed, a cell wheel damages coated seed. The blower is small (2 meters,
~100 W).

## Double disc between depth wheels

The two depth wheels beside the opener hold the seed depth within a few mm on a cloddy seedbed; the double disc cuts
through residue and leaves a clean V. The press wheel closes the V. The parallelogram lets each unit follow the ground
on its own; the hitch's frame rides on its own gauge wheels, so the robot does not carry the units in work.

## In the three-point hitch

The hitch already lifts a 1 m implement, has gauge wheels and float, and is checked against the rear tyres. The
seeder only replaces the cultivator's tines with 2 units. The limit is the front axle when the seeder is lifted at the
headland: with the hitch's 40 kg front ballast it carries 15 %, the robot needs ~20 % to steer, so 57 kg of front
ballast (or lighter units) is the condition for lifting. In work the units and the frame run on their own wheels.

## 2 rows at 500 mm

Sugar beet is sown at 45-50 cm. Two units fit between the hitch's gauge wheels and keep the implement light. Maize at
75 cm or 4 vegetable rows need a wider toolbar (and more ballast); the units are the same.
