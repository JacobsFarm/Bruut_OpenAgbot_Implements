# Grass meter / crop scanner (simple): why it is built this way

## Two ways to measure grass at once

- **Compressed height (plate meter)** is what farmers and advisors calibrate to dry matter: a plate of 0.1 m2 at
  ~5 kg/m2 on the sward, the height in cm times a factor plus an offset (here 140 x h + 500 kg DM/ha, to be
  calibrated per farm and season). A towed or sledge plate measures continuously instead of one drop per step.
- **NDVI (red / near-infrared)** shows cover and vitality, independent of height: patchy N, clover share, dung
  patches, frost or drought damage. Active sensors with their own light work in sun, cloud and at night, so the robot
  can map in the evening or at night when it has nothing else to do. This covers the *NIR sensor* idea.
- A down-looking lidar adds uncompressed canopy height along the same track; the camera stores a photo every 1.5 m
  for checking odd readings.

## Plate under the robot, sensors in front

- The plate rides between the axles, where there are no tyres (y -235..235) and the grass has not yet been driven on
  by the rear wheels; the front wheels run in their own tracks at x +-375, the plate at x 0 measures the middle.
- A parallelogram of two arm pairs (350 long) keeps the plate level from 0 to 200 mm compressed height; the angle
  sensor on the upper pivot (12 bit) resolves 0.3..0.5 mm. A small 24 V actuator with a slotted rod eye lifts the
  plate to 250 mm for driving and turning; in work the eye lets the plate float.
- The boom sits on the front outer lower beam on two flat brackets (4 x M10 in the hole grid), 830..870 forward and
  at z 600..640: above the tyres (top z 480), so it stays 181 mm from the front tyres with the wheels steered 30
  degrees, and clear of the GNSS dome. The NDVI sensors look down at 0.56 m from x +-550: two strips 0.46 m wide just
  outside the wheel tracks.

## Capacity

At 1.5 m/s on transects 10 m apart (100 m long, 15 s per turn) the robot maps ~4.4 ha per hour: a plate reading every
150 mm (6700 per ha), NDVI every 150 mm, lidar every 75 mm. The kit uses ~25 W, the driving ~215 W: ~8 h and ~35 ha
per battery charge. It weighs 22 kg, so it can stay on the robot together with most other implements (not with the
push blade, which uses the same space in front, or the soil sampler / aerator between the axles).

## Estimated, not measured

- Robot mass 160 kg; lugged tyre envelope O530 x 100 from the model
- Dry matter factors 140 x h(cm) + 500 kg DM/ha (ryegrass / clover; calibrate per farm)
- Plate mass on the sward 0.5 kg (the arms counterbalanced by a spring), NDVI field of view 45 degrees across
- Sensor masses and power (25 W), NDVI repeatability 0.02
- Transect spacing 10 m, field length 100 m, 15 s per turn, rolling resistance 0.06
