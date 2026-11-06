# Why the two work tanks are what they are

## Two tanks instead of two jerrycans

The 20 l jerrycans of V3 were enough to show the two liquids, but at 500 l/ha per liquid they last 0.04 ha (400 m of
pass): the robot would need a refill every other pass. A refiller in the turn (`mobile refiller/simple_two_ibc`) tops up
both liquids once per turn, so a work tank only needs to cover two passes plus a reserve; on 200 m passes that is
about 20 l per liquid. 78 l per liquid covers a turn even on 400 m passes, and gives room for a refill only every
other turn or for the station on the headland.

The space is the box between the pump manifold (inlets end at y −170) and the front stepper-motor plates (y 405),
over the upper beams (outer face x ±445): 880 × 420 mm. Splitting it into two tanks of 425 mm with a 30 mm gap keeps
each liquid straight in front of its own manifold inlet (A right, B left, as V3), so the supply hoses stay the short
S-bends of V3. 480 mm high gives 78 l each; higher would raise the centre of gravity and the funnel rim further
(the nozzle height of every refiller follows the rim).

## Funnels 455 mm apart

Each funnel sits in the middle of its own tank, so the two are 455 mm apart across the robot. A refiller only has to
carry two nozzles on its arm at the same spacing: the arm of the mobile refiller and of the trailer points across the
working robot (it stands beside it), so both funnels lie under the arm in one stop and both pumps run at the same
time. Funnels behind each other (along y) would need a second arm or two stops.

The rim height (1354) follows from the tank height; the nozzles of the two-liquid refillers end 106 mm above it
(z 1460), as on the other refillers, so the stream falls ~0.1 m into an open funnel at 120 l/min.

## Mass and balance

With V3's jerrycans the front axle lost 7 kg when the applicator was lifted (cans full). The tanks sit in front of
the middle of the robot (cg y 170), so full they add 105 kg to the front axle; empty, the front loses 27 kg when the
applicator is lifted: a small change against the weight of the robot itself. The refill
in every turn keeps the tanks well above empty, so in practice the front axle is always loaded.
