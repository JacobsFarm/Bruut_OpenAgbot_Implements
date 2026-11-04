# Power harrow / rotary tiller - rationale

## Rotary tiller rather than a vertical-tine power harrow

A power harrow's vertical rotors give no forward force, so the robot has to pull the whole draft. A horizontal rotor
turning forward (down-cut) does the opposite: the blades push the soil back and the robot forward. For a 161 kg robot
with ~900 N of grip that is the deciding point. The idea's "power harrow" name is kept for the folder.

## Narrow and shallow

Tilling energy scales with the soil volume per second. 700 mm x 60 mm at 0.1-0.2 m/s is 4-8 l/s; at 60-150 kJ/m3
that is 0.5-0.65 kW at the rotor, within a 1.5 kW 48 V gearmotor and ~1.6 h per battery charge. Deeper or wider
tilling needs the hybrid range extender or another robot. The rotor width fits between the hitch's gauge wheels
(x +-565), so the wheels run on firm soil beside the strip and set the depth.

## Blades and speed

4 L-blades per flange at 250 rpm give a bite of 6-12 mm per blade: a fine seedbed. Flanges are turned 22.5 degrees
apart so only one blade enters at a time (smoother torque). The tips are bent alternately left and right so each
flange covers ~180 mm.

## In the three-point hitch

The hitch, its frame and gauge wheels are reused unchanged. The housing hangs on two 10 mm brackets from the toolbar
over the hood top, the rotor axis is 220 mm behind the toolbar and 115 mm above the ground (60 mm deep).

## Balance when lifted

94 kg with its cg 1.55 m behind the robot centre is too much for the hitch's standard 40 kg ballast: the front axle
would keep 6 % of the weight. 92 kg front ballast brings it to 20 %. Plates were thinned (side plates 5 mm, hood
2 mm, a webbed motor stand) from 108 kg. A belly-mounted tiller between the wheels would need no ballast; it would
lose the hitch's gauge wheels and be limited to ~460 mm width.

## Estimated, not measured

- Specific tilling energy 60-150 kJ/m3 for a shallow tiller (soil dependent)
- Gearmotor rating (1.5 kW), mass (9 kg), gearbox and chain efficiencies
- Share of the blade force that pushes the robot forward (0.3)
- Robot drive power with the tiller (250 W), tyre grip coefficient 0.5
- Front share needed to steer (20 %, from the three-point hitch)
