# Sawdust spreader (simple): why it is built this way

## A daily stable job

- Cubicles get fresh sawdust (or chopped straw, or a lime-sawdust mix) every day or two: ~0.4..1.5 kg per cubicle,
  thrown into the back half of the bed from the alley. It is light, repetitive work along fixed routes on concrete:
  a good job for the robot between feed pushing rounds (see the [feed pusher auger](../../feed%20pusher%20auger/)).

## Bin, auger across, spinner on the right

- The bin uses the top of the robot like the compost spreader: on 2 bearers across the upper beams, front wall 25 mm
  short of the front steering stacks (104 mm from them with the wheels steered 30 degrees). Its front and rear walls
  slope at 45 degrees down to a U-trough, so sawdust slides to the auger without a moving floor: 308 l.
- An auger O150 (pitch 150) runs across the robot in the trough, driven from the left by a 24 V worm gearmotor, through
  a tube over the right upper beams into the spinner housing. Dose per cubicle = auger speed / driving speed:
  sawdust 1 kg per cubicle at 0.5 m/s needs 109 rpm; chopped straw (70 kg/m3) needs 125 rpm, just over the 120 rpm of
  the gearmotor, so the robot drives at 0.45 m/s with straw.
- The spinner disc (O320, 4 vanes, 350 rpm, tip 5.9 m/s) sits in a housing outside the right outer upper beam, low
  (z 660) and open to the right: it throws ~1.3 m from the wheel line, the length of a cubicle bed beyond the curb.
  A low tip speed keeps the dust down in the barn.

## Load and stability

- 62 kg of sawdust, 22 kg of chopped straw or 139 kg of the lime mix (heavy: 450 kg/m3, under the 150 kg payload).
- The spinner housing hangs out on the right (cg of the spreader at x 81), but the full robot still has its cg 16..24 mm
  right of the centre: side tip angle to the right 26.6 degrees with the lime mix, plenty on a flat barn floor.

## Capacity

One fill of sawdust covers ~61 cubicles (146 s of spreading); with 3 min to refill from a big bag and 60 m to the bag
and back, ~570 cubicles per hour. Energy is tiny (~13 Wh per fill): the spreader can run on the robot between other
jobs.

## Estimated, not measured

- Bulk densities (sawdust 200, chopped straw 70, lime-sawdust mix 450 kg/m3), auger filling 0.45
- Doses per cubicle, cubicle width 1.2 m
- Throw efficiency 0.5 (air drag on sawdust), power of auger (120 W) and spinner (150 W)
- Refill time 3 min, 60 m to the refill point, robot mass 160 kg and cg height 380 mm
