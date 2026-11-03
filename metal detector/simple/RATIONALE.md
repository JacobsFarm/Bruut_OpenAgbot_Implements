# Metal detector (simple): why it is built like this

## Pulse induction, mono loop

Pulse-induction detectors ignore most of the ground mineralisation and wet soil that confuse VLF detectors, they are
simple (one loop, one board; open designs exist) and they find all metals, iron and aluminium alike. They do not
discriminate well, but on a field every metal object is worth a GNSS point. A mono loop is the simplest and the most
sensitive in depth for its size.

## Coil 600 x 400

The signal of a small target goes as r_e^3 a^4 / (a^2 + z^2)^3: a large loop sees large targets deeper, a small loop
sees small targets better near the surface. The objects that hurt on a field after building work or an event, or in
an old field, are cans, wire, horseshoes, bolts and plough points: a 600 x 400 loop (equivalent radius 276 mm) finds
those at 150-700 mm, against 120-420 mm for a hand-held O250 coil. The price is that a single nail is too small for
it; loose nails at the surface are what the magnet sweeper picks up, so the two tools split the work.
400 mm along the driving direction gives ~10 samples per target at 1 m/s and 25 samples/s.

## Distance from the robot: GFRP boom, coil 1.2 m in front

The steel frame, wheel brackets and hub motors are one big target. A static signal is balanced out, but vibration,
steering and the motor currents make part of it change while driving (taken as 0.5 %). That part stays below 30 % of
the threshold from ~0.97 m; the coil is at 1.31 m. In front of the pivot there is no metal at all: GFRP tubes and
plates, nylon bolts, and the electronics box only on the rear cross tube. The steel brackets and the pivot pin are
small and ~1 m from the winding.

## Coil on skids, floating boom

The signal falls with the 6th power of the distance, so the coil must stay low and at a constant height: it slides on
2 PE skids (coil plane 35 mm over the ground) and the boom floats on its pivot (rod pin in a 40 mm slot). The skids
carry 6 kg: ~22 N drag on grass. At the headland the 500 N actuator lifts the boom 14 degrees (coil 235 mm up) so the
robot can turn; reversing with the coil down is not allowed (the skids only slide forward).

## Mount on the front outer lower beam

The brackets use the 50 mm grid holes at x +-125 and +-225 and stay clear of the GNSS mount at x 0, the steering sweep
of the front wheels (238 mm clearance) and the steppers above the wheels. The actuator stands outside the right bracket
so the space between the tubes stays free and the robot's GNSS dome is not shadowed.

## Position of a hit

The hit is logged at the coil centre: RTK (20 mm) plus the heading error over the 1.23 m lever arm from the antenna
(21 mm at 1 degree) plus the place of the signal peak along the coil (~100 mm). ~0.1 m is enough to stake out or to
dig. Two passes in opposite directions halve the peak offset.

## Estimated, not measured

- Detection model: dipole coupling, the reference (8 mm equivalent sphere at 200 mm with a O250 PI coil), ground noise
  2x the reference after ground balancing, and the equivalent sphere radius of each target
- Robot as an equivalent sphere of 250 mm and 0.5 % of its signal changing while driving
- PI electronics power (8 W), logger and GNSS (15 W), pulse rate and averaging
- Friction of PE skids on grass (0.35), rolling resistance of the robot (0.06)
- Robot mass (160 kg) and centre of gravity, usable battery energy (1.9 kWh)
- Actuator mass and speed (500 N type), GFRP density 1.9 kg/dm3, winding as a 12 x 12 bundle
- Not modelled: cable along the boom, nylon bushes and bolts, the PI board itself
