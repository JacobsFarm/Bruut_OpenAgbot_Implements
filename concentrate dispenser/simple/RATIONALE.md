# Concentrate dispenser (simple): rationale

## Why on the feed pusher run

Pushing feed back to the fence already brings cows to the feed table every 1-3 hours. A small dose of concentrate or
a mineral on top of the freshly pushed windrow makes that visit more attractive (commercial pushers do this as an
option). The dispenser therefore rides on the same robot and the same route as the feed pusher auger V3, and does not
need its own trip.

## Where the hopper sits

The feed pusher hangs 1 m behind the rear axle and already needs 40 kg of counterweight at the front. A hopper at the
rear would add up to 69 kg behind the axle; at the front it would collide with the steering stacks and the
counterweight. In the middle (y 0) a full hopper adds the same load to both axles and changes nothing in the pusher's
balance. The upper beams have grid holes only at |y| 275 … 625, so the hopper stands on 2 cross tubes at y ±325 (the
same bolt line as the drone platform); the wheel-unit frame bolts at y ±425 / ±575 are not touched.

## Where the pellets go

The robot drives with the auger first (−y) and the auger throws the feed to +x, against the fence. The spout sits at
x 850, just outside the end plate of the pusher (x 736) and above the middle of the windrow, at y 0: everything it
drops lands on feed that has just been pushed. The pellets fall ~230 mm onto the windrow; the rubber spout keeps them
out of the wind and does not hurt a cow's head that reaches over the fence.

## Auger, not a cup wheel

A small auger doses pellets, meal and minerals alike, runs from 5 to 150 rpm without changing parts and closes the
outlet when it stops (no trickle while turning or standing). A cup wheel or a slide gate needs another setting for
every product. The auger in a tube also bridges the 600 mm from the hopper to the side of the robot, so the hopper can
stay in the middle.

## Loss-in-weight, not calibration

The output of a small auger depends on the fill (30-60 %), the pellet size and the moisture. A calibrated auger is off
by 10-20 % when the product changes. With the hopper on 4 load cells the controller sees the real mass flow over a
window of ~10 s and trims the auger speed; at 467 g per window the estimated error is ±2 %, and the herd management
system gets the real grams per round. The cells weigh the hopper, the frame and the drive; the cross tubes and the bolts
are below them. While the robot drives the signal is filtered; the controller also uses the tare taken at standstill
before and after a round.

## Hopper shape

60° side walls: pellets slide at ~30-40°, mineral meal needs ~55-60°, so both empty without a stirrer. The box part on
top adds volume without making the hopper taller (top of the lid at 1.19 m, the feed fence neck rail is at ~1.2 m).
47 l is ~2.7 rounds for 120 cows at 100 g per place; more volume would mean a taller hopper and more mass on the
robot.

## Drive

The running power of the auger is about a watt; the stepper with a 10:1 planetary is chosen for speed range and
for the starting torque when minerals have caked in the trough overnight (10 Nm at the auger). A stepper also gives
the auger speed without an encoder.
