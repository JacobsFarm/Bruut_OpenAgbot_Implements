# Overseeder with Cambridge roll: why it is built like this

## Seed first, then roll

Seed on the surface of bare soil dries out, blows away and is eaten by birds. Rolling it in right away presses it
into contact with moist soil and leaves it in the grooves of the rings, under a thin layer of crumbs: the standard
practice for lawn repair (seed, then roll). So the seed drops in front of the roll, not behind it.

## One trailer instead of two

Two trailers behind each other (seeder on wheels, then the roll) would have two articulations, a worse reverse and
twice the drawbars, wheels and coupling heads. Hung between the arms of the roll, the seeder unit needs no wheels: the
trailer rests on the ball and the roll. The unit is the same module as the stand-alone seeder (`build_ovd.build_unit`),
bolted with four M10 to the arms: it comes off in a few minutes and goes back on its own wheels.

## Distances

- **Drop line 300 mm in front of the roll contact**: the end plates of the unit (v −170) stay 20 mm in front of the
  side plates of the roll (axle +110), and the rear of the throat is far from the rings. At 0.5 m/s the seed lies 0.6 s
  on the surface before it is rolled in.
- **Front cross beam 250 mm in front of the drop line**, low (z 300 … 340): clear of the hopper front, the mast and the
  control box above it, and under the line of sight of the camera to the analysed strip (0.4 … 1.2 m ahead).
- **Ball to roll 1.43 m**: the braces of the drawbar have to end in front of the parking leg lug (y −1255, fixed from the
  front of the drawbar). A shorter trailer would turn tighter but needs another brace layout.

## Turning

The robot steers its front wheels only (stop 30°): the smallest rear axle radius is 2.11 m. The trailer cuts inside:
at 2.25 m it articulates 47° and the roll centre runs on a radius of 1.77 m, 0.48 m inside the robot. Nothing touches up
to ±75° (`build_osr.check_poses()`), and in the turn the rings turn at their own speed, so the lawn is not torn. In the
animation the turn is on the headland (no patches); the seeder is off there anyway.

## Weight and draft

The hopper adds 35 kg (+ 17 kg seed) in front of the roll: 205 … 241 N on the ball, which also helps the traction of the
robot. The draft is that of the roll (185 N on moist lawn, 310 N on a loose patch); the seeder unit itself has no
rolling parts on the ground. Up a 5° slope on a loose patch the draft (510 N) equals what the robot can pull on wet
grass (500 N): there the robot slips. Keep this combination for (nearly) level lawns, or work up and down a slope only
when the grass is dry.

## Control and waste

The controller (in `osr_ground.py`, timing from `ovd_calc`) runs the motor while at least 2 bare cells of 50 mm lie
between `lead_off` and `lead_on` ahead of the drop line; both scale with the speed. In the animation: 6 patches, 6 on
switchings, 99.8 % of the bare cells seeded (one cell at the edge of a patch), 100 % rolled, and the two single bare
cells are ignored. With one 1 m section 63 % of the seed falls on the grass next to the narrow patches; that is the
price of one motor. Two sections would roughly halve it.

## Cost (estimated)

Roll with hitch about € 850, seeder unit without wheels and drawbar about € 330, hangers € 10: **≈ € 1,200**.
