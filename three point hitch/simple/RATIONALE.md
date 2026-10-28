# Three-point hitch (simple): why it is built this way

## Category 0, at the rear, electric

- Category 0 (lower pins 5/8" = O16, lower hitch spacing 500 mm, mast height 350 mm) is the size of sub-compact
  tractors and garden tractors: there is a market of small implements (cultivators, ridgers, box blades, rakes) that
  fits the weight the robot can carry. Category 1 implements are too heavy for the axle loads (see below).
- At the rear, on the same toolbar as the grassland harrow and the inter-row hoe: one toolbar for everything that is
  pulled. The front (push blade) stays free for the counterweight or a front tool.
- Two 24 V actuators are the lift rods (no rockshaft, no hydraulics): each lower link is lifted at 60 % of its length.
  The rod eye has a 40 mm slot, so in work the lower links float and the implement follows the ground on its own gauge
  wheels; position control is possible by stopping the rods with the pin at the end of the slot.

## Geometry

- Lower links 50 x 20 flat bar, pivot under the toolbar at x +-280 (clear of the hanger webs), converging to x +-260 at
  the ball (category 0 spacing). Top link (turnbuckle) from a bracket on top of the toolbar, 453 mm.
- Lower links -5 .. +25 degrees: lower pins 181 .. 425 mm high (205 mm lift above the work height of 220).
  Top link and lower links are almost parallel, so the implement stays level within 2 degrees over the lift.
- The rods are 358 .. 475 mm pin to pin: a stroke of 150 with a retracted length of 350 fits. Their base lugs lean back
  from the top of the toolbar, so the bodies run behind it. ~20 s for the full lift at 6 mm/s; at the headland half is
  enough (shares 100 mm out of the ground).

## What the robot can carry

- The lift rods are not the limit: 2 x 3000 N lifts ~270 kg at the hitch (the cultivator needs ~310 N per rod).
- The axle load is: an implement lifted 1.4 m behind the robot centre takes weight off the front axle. With the 2 x 20 kg
  front counterweight, ~56 kg can hang in the hitch (cg 150 mm behind the lower pins) while 20 % stays on the front
  axle; without the counterweight only ~25 kg. With the 28 kg cultivator lifted: front 32 % with, 19 % without.
  That is the real rating of this hitch: light category 0 implements, or implements that run on their own wheels and
  are only lifted at the headland.

## Demo implement: small cultivator (covers the "small cultivator" idea)

- 1.0 m frame (toolbar 60 x 60, A-frame mast), 5 S-tines 32 x 10 with 100 mm duckfoot shares at 200 mm, two gauge wheels
  O250 at the ends; the outer tines loosen the wheel tracks. 28 kg.
- Draft 5 x 30 kPa x 0.1 m x 40 mm = 600 N plus rolling ~210 N, against ~1040 N grip and 1100 N motors: margin 1.29,
  ~1.1 kW at 1 m/s, ~0.29 ha/h.
  Deeper (55 mm) the margin drops to ~1.0: in light soil 40 mm is the limit for 5 tines; take 3 tines for deeper work.

## Estimated, not measured

- Robot mass 160 kg and its centre of gravity midway between the axles; least front axle share 20 % to steer
- Tyre grip 0.45, rolling resistance 0.08 on cultivated soil
- Draft of a duckfoot tine 30 kPa x share width x depth (light soil)
- cg of a general implement 150 mm behind the lower pins
- Actuators 3.4 kg, 6 mm/s at 2000 N
