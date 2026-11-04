# Chicken house robot (simple): why it is built like this

## The standard robot, not a special low one

A broiler house is an open floor of 15-20 m wide and 100 m or more long, with feeder and drinker lines hung at
adjustable height (raised for cleaning and between flocks, and at bird height in use). The standard robot (1.1 m wide,
~1.1 m high, 1.5 m at the camera) drives between the lines or under raised lines. A dedicated low robot is the
advanced variant.

## Tine rotor in the broom head

Litter turning (tilling) is a rotor with tines; the broom already has a hooded rotor of the right width with a 48 V
drive, bearings, castors and a lift. Only the bristle roller changes: 60 spring tines on the same core. The castors
set the height: the tip circle (O360) ends 10 mm above the concrete, so the tines work the 60 mm litter layer and
never scrape the floor. At 150 rpm the rotor takes ~810 W in caked litter, within the 1000 W motor. The hood keeps
litter from being thrown at the birds.

## Slow, quiet, birds walk away

At 0.3 m/s a broiler walks away (~0.5 m/s) before the head reaches it; the castors and the rubber flap of the hood
push gently. A BLDC rotor at 150 rpm and electric drive are far quieter than a tractor with a tiller.

## Sensors at bird height

Ammonia is heaviest near the litter, where the birds breathe; the sensor box hangs under the rear beam with its inlet
at 300 mm, behind the rotor (it measures the air after turning, which is the worst case). The camera post sits over
the rear axle so the 360 degree view looks over the flock.

## Estimated, not measured

- Litter resistance (4 kN/m2 of tine face, 50 mm engaged), drive efficiency (0.7)
- Bird density (18/m2), escape speed (0.5 m/s), house size
- Rolling resistance on litter (0.04), sensor power (25 W), robot mass and battery energy
- Sensor box and camera masses
- Not modelled: cables, the UWB beacons, egg pick-up (advanced variant), cleaning and disinfection between flocks
