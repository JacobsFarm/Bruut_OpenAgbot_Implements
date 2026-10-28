# Inter-row hoe (simple): why it is built this way

## Two inter-rows, behind the wheels

The standard robot has its wheels at x = +-375. In maize at 75 cm the robot straddles one row and its wheels run in
the two inter-rows next to it, so those are the two inter-rows the hoe works: one unit per inter-row, right behind a rear
wheel. The shares loosen the wheel track again in the same pass. A pass covers 2 x 750 = 1.5 m; the next pass straddles
the row two further on, so every inter-row is hoed once. Other row spacings: move the unit heads on the shift plate
(any x between +-300 and +-380) and change `row_spacing`, `unit_x` and the share widths; for beet at 50 cm three units
fit with a narrower goosefoot.

## Rear toolbar and lift: the grassland harrow parts

Toolbar, hangers, pivot forks and actuator mast are the grassland harrow (push blade mirrored), so the same toolbar
carries harrow or hoe. The hoe is heavier (92 kg lift group against 60 kg): with the same lever (164..184 mm) the lift
needs ~2.2 kN, so the actuator is the 3000 N version of the same size (slower: ~15 s for the full lift).
The rod pin floats in the 40 mm slot, so in work the carrier rests on the units and the units on their gauge wheels.

## Side shift: rails, ball screw, closed-loop stepper

- Two HGR15 rails on a 10 mm plate on the carrier, 4 carriages under an 8 mm shift plate, +-75 mm.
- SFU1610 (lead 10) driven by a 2 Nm closed-loop NEMA23: 80 mm/s at 480 rpm (4 x what a row wandering 40 mm over 2 m
  needs at 1 m/s), the full stroke in under 2 s. Force on the nut ~340 N (soil on the shares while shifting, accelerating
  58 kg at 1 m/s2, rail friction): 0.6 Nm, the motor has 1.2 Nm at 600 rpm (margin 2).
- A ball screw holds its position without power draw under the side load of the shares and gives a repeatable
  position for the controller, which a standard linear actuator (hall pulses, 10..40 mm/s) does not.

## Units

- Parallelogram (2 flat bar links 40 x 10 each side, 235 mm, 120 mm high) from a head on the shift plate to a post:
  the shares keep their angle while the unit follows the ground. Depth is set by the gauge wheel O250 x 80 in front of
  the shares (holes in the fork arms, not drawn).
- Goosefoot 250 mm in the middle of the inter-row, two L-blades 165 mm next to the rows with the upright wall on the row
  side (it keeps soil off the crop). Together 550 mm: 100 mm untouched each side of the row.
- Rigid shanks: young maize is hoed at 2 cm, the parallelogram takes the ground. Spring tines (S-tines) are the
  alternative for stony soil.

## Guidance

- The camera sits on the shift plate, above the middle row, looking almost straight down (80 degrees) at the share line
  (view centre y -1280, ~1.2 m wide: only the middle row in view). It measures the row position relative to the hoe
  directly, so the loop closes on what matters: offset row - shift plate -> stepper.
- Error budget against the 100 mm band: camera ~10 mm, RTK row map ~20 mm (2 sigma), drift during 80 ms latency 2 mm.
  The band is 5..10 x the error. Fallback when the camera loses the row (gaps, weeds taller than the crop): follow the
  RTK row map from sowing; when both are lost, the robot stops and lifts the hoe.

## Pull and axle load

- Cutting 25 kPa x 1.1 m x 20 mm = 550 N, rolling 214 N (loose soil, 0.08): 764 N against 938 N grip (0.45 on the robot
  weight without the units, which run on their own wheels) and 1100 N motors: margin 1.23, ~1 kW at 1 m/s.
  At 30 mm depth the margin drops below 1: hoe shallow, or slower in heavy soil, or one unit per pass.
- The lifted hoe hangs 1.16 m behind the robot centre: without ballast only 3 % stays on the front axle (steering does not
  work). The 2 x 20 kg counterweight on the front lower beams (the blocks of the disc brushes / fertilizer spreader) is
  part of this implement: 16 % on the front axle in transport.

## Estimated, not measured

- Robot mass 160 kg and its centre of gravity midway between the axles
- Tyre grip 0.45 on cultivated soil, rolling resistance 0.08
- Specific draft of a shallow sweep 25 kPa; lateral soil force while shifting 0.5 x draft
- Camera row-fit error 10 mm, RTK row map error 20 mm, latency 80 ms; row wander 40 mm over 2 m
- NEMA23 torque curve (2.0 Nm static, 1.2 Nm at 600 rpm), motor 1.4 kg, camera 0.6 kg
- Gauge wheel as one solid rubber density; actuator 3.4 kg, 6 mm/s at 2000 N
