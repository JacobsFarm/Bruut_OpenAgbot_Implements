# Rationale: cauliflower root-crown applicator (simple)

## Two rows under the robot

The track is 750 mm, so the inner faces of the tyres are at x ±325. With 40 cm rows, two rows at x ±200 fit between
the wheels. The tyres then run in the inter-row on each side, 125 mm from the nearest stem. Neighbouring rows at
x ±600 stay outside the robot. Four rows would need nozzles beside and outside the wheels, through the leaves of the
outer rows. That is left for a later variant.

## Toolbar between the axles, units in the middle

Between the tyres (|y| < 285) there is nothing below the chassis, so the row units can be up to 600 mm high there. The
upper beams have M10 holes only at |y| 275 .. 625, so the toolbar hangs from the first hole at y 275. The tank cradle
moved to y 325 to make room. Two through-bolts carry the toolbar: one row unit of about 11 kg on a 375 mm span is light
work for a 50 x 50 x 3 tube. The parallelogram trails backwards to y 0, which keeps the units in the middle of the
robot, about 285 mm away from both axles. The skids stay clear of the tyres, also at 30° steering lock (≥ 115 mm).

## Parallelogram and skids, not a gauge wheel

The nozzle has to stay at a constant height above the soil next to the stem, not above the robot frame. Each
parallelogram follows its own row independently over 140 mm of travel and keeps the nozzles vertical. The skids run on
the bare soil 160 mm on each side of the stem, the same place a gauge wheel would run. Skids do not clog with mud or
leaves, have no bearings, and lift leaves at their upturned noses. The unit weighs 8.2 kg, which gives 2.7 kPa on the
soil: enough to follow the ground on loose soil and too little to leave a track. A down-pressure spring between the
bracket and the lower arm can be added if the units bounce.

## Arch at 410 mm

Mid-season plants are 250 to 350 mm high, and the idea says light contact with the structure is acceptable. The arch
underside is 60 mm above a 350 mm plant, so taller leaves brush along the flat tube. The arms and pins are higher still
(z 490 .. 600) and stay clear of the crop.

## Leaf lifters and drop nozzles

At 40 cm spacing the leaves of neighbouring plants touch, and the lower leaves cover the stem base. The lifter tip runs
low (z 30) and 70 mm from the stem, so the plant passes between the two tips. The rod rises backwards and outwards, so
the leaves slide up and away from the stem. The nozzles sit 70 mm behind the lifters (y -46), where the leaves are
still lifted. The drop tubes are thin (D8) and vertical, so they pass between leaves.

## Pulses: 1.6 mm, 2 bar, 77 ms

The idea asks for 50 .. 100 ms bursts. A 1.6 mm solid-stream orifice at 2 bar gives about 26 ml/s, so 2 ml per side
takes 77 ms. At 0.5 m/s the dose then lands on a 38 mm strip along the row, which is the 3 .. 5 cm target zone. A solid
stream (not a fan) drifts less, does not wet the leaves, and keeps the 30° aim. Low pressure means large drops and
little splash. The shroud, 10 mm past the tip, stops soil splashing back onto the orifice.

## Pump plus accumulator

The mean use is only 0.6 l/min. When both rows fire at the same moment, the four valves need 105 ml/s for 77 ms,
which is more than the pump's 75 ml/s. The 0.5 l accumulator covers the 2.3 ml shortfall, so the pressure (and so the
dose) hardly drops during a pulse. The pressure regulator with bypass keeps the pressure at 2 bar. The pressure sensor
on the regulator block lets the controller correct the pulse length for the measured pressure (dose = q(p) · t).

## Crown sensor plus odometry

The idea gives several triggers. A downward distance sensor (ToF or ultrasonic) in front of each unit finds the crown,
the highest point of a cauliflower, which sits right over the stem. The hub-motor odometry then counts the 381 mm to the
nozzles, so the timing does not depend on speed. With a 50 Hz sensor the uncertainty is about 10 mm at 0.5 m/s. Odometry
alone (every 40 cm) drifts with wheel slip and with uneven planting, so it only fills in when the sensor misses a plant.
A camera would also work, but costs more for the same result.

## Tank 60 l, on top

At 250 l/ha, 60 l treats 0.24 ha (3 km of row) in about 100 minutes. That is a reasonable time between refills, and a
full tank weighs 60 kg. The tank sits centrally above the wheelbase (centre y -25) as the idea asks, so the axle loads
stay close to even: 149 kg front and 126 kg rear when full. Gravity feed was not used because the units float and the
pulses need a constant pressure.

## Pump plate on the rear lower beams

The space behind the tank on the rear lower beams is free and dry, and close to the tank outlet. Four M10 bolts
through the existing holes at x ±275 hold the plate. The plate stays 20 mm from the frame bolts of the rear wheel units.
