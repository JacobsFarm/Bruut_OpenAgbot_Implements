# Fence inspector (simple): why it is built like this

## Contactless, 80 mm from the wire

A contact sensor (a fork or a wheel on the wire) has to pass every insulator and post, and it wears and catches. An
energizer pulse of several kV gives an electric field of ~10 kV/m at 80 mm; a 50 x 50 mm plate on a 1 nF integrator
turns that into ~0.25 V, an easy signal. The same pulse carries 1-15 A, which a small pickup coil sees as a few to
twenty mV. Posts and insulators stand behind the wire (x 1050 and more), the head stops at x 920, so the head never
touches them.

The field scales with 1/d, so the distance is measured with a small ToF sensor (+-4 mm): with the share of the other
wires (~8 %) the voltage is known to ~+-9 %. That is not a lab meter, but it clearly separates a good fence (5-8 kV)
from one that no longer holds cattle (under ~3 kV). The ln(2h/r) term changes 21 % from a 300 to a 1100 mm wire; the
head height is known, so it is corrected.

## What the readings tell

- Voltage gone from a point on: a break (or a gate open) just before it.
- Voltage falling slowly along the fence with current still flowing: a leak (vegetation, poor insulators).
- Current that drops at a point: the current leaves the wire there (a short to a post or the earth wire).
One reading per metre at 1 m/s is enough to point at a post span (4 m); the camera image of that span shows the cause.

## Mast between the axles on the right upper beams

The upper beams have vertical grid holes at |y| 275..625; the base plate uses y +-300 on both right upper beams. The
mast stands at y 0 and x 485: 511 mm from the front wheel steering axis, so the steering sweep (radius ~221 mm) never
reaches it, and outside the right tyres. A C-shaped carriage (open on the plate side) can slide over the full height
past the base plate.

## Lead screw, not an actuator

A 800 mm stroke actuator is long and slow to place; a Tr16 x 4 screw with a stepper gives any height to ~1 mm, holds
without power (self-locking) and takes 20 s over the full range. Following another wire is a software choice.

## Spring hinge

A branch, a gate post or a water trough next to the fence must not break the arm: it swings back on a vertical hinge
with a torsion spring (~15 N at the head) and comes back by itself. Even swung back 80 degrees at the lowest height it
stays 66 mm from the front tyre at full steering lock.

## Estimated, not measured

- Fence voltage (6 kV), the 3 kV fault threshold, pulse currents (1-15 A), pulse rise time (100 us)
- Share of the other wires in the plate signal (8 %), ToF distance error (+-4 mm)
- Mass of the head, camera and stepper; spring force of the hinge
- Rolling resistance (0.06), sensor power (20 W), robot mass and battery energy
- Not modelled: the electronics in the head, cable chain along the mast, the torsion spring, the post-straightening
  tool (a later variant)
