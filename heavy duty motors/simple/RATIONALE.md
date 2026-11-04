# Heavy-duty electric motors (simple) - rationale

## Why bought garden-tool motors

Battery lawnmower motors of the big brands deliver ~2 kW from a sealed, cooled, brushless unit with a keyed shaft, made
in large numbers: cheaper and better protected than a custom motor of the same power, and spare parts are in every
garden shop. They replace small petrol engines on mowers, brush cutters, augers and blowers.

## Own controller on the 48 V bus

The tools' own electronics talk to their batteries; running the bare motor needs its own controller. A generic BLDC
controller (75 V class, sensor or sensorless) on the robot's 48 V bus gives one energy source for driving and the
implement, and 2.4 kWh instead of 0.28 kWh in a tool battery. On 48 V instead of 56 V the motor turns ~15 % slower,
which for a mower blade is still fast enough (78.5 m/s). The tool battery in a clip remains an option for short jobs.

## Interface plate and quick change

One plate for all motors and one adapter ring per brand: the implements only need the dovetail receiver. The plate
slides in and is locked with one pin, so a farmer with one motor can move it between a mower, an auger and a blower.

## Demonstrator: mid-mower deck

The "mower unit" folder had notes only; a 530 mm deck under the belly is the simplest strong user of a 2 kW motor.
It hangs from the belly rails of the drop-on-demand boom between the wheels (inside the steering sweep), with 3
cutting heights by holes in the hangers, and side discharge to the right.

## Estimated, not measured

- Motor: continuous power (2 kW), speed under load (3300 rpm), efficiency (88 %), mass (4.2 kg)
- Mowing power (2 kW per m width at 1 m/s in dense grass), blade windage (250 W), drive power (300 W)
- Controller efficiency (96 %), tool battery energy (280 Wh)
- Robot mass and battery (2.4 kWh), field efficiency (80 %)
- Not modelled: the brand-specific ring patterns, the blade adapter of each brand, the controller's sensors and wiring
