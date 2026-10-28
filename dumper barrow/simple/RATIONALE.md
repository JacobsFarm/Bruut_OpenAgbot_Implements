# Dumper barrow (simple): why it is built this way

## A tipping skip, not a loose bin

- Most farm transport with a wheelbarrow ends with tipping: soil, gravel, compost, wood chips, weeds and prunings.
  The [crate carrier](../../crate%20carrier/simple/) already shows the deck and the follow-me; the dumper adds a bin
  that tips backwards, so the robot unloads without help.
- The bin (2 mm steel, 353 l, 900 wide) sits on the upper beams like the crate deck: from the rear end of the robot to
  y 360, 45 mm short of the front steering stacks. The rear lip slopes out 30 degrees: it ends behind the rear wheels and
  the load slides off it clear of the tyres.

## Hinge and actuators

- The subframe (2 rails 40 x 40 at x +-270, inside the bearer bolts) hinges on a bearer at the rear end of the upper
  beams (y -620, clear of the rear unit frame bolts) and rests on rubber pads on the front bearer.
- Two 24 V 3000 N actuators (stroke 300, retracted 450) push on a cross tube under the bin from lugs in front of the
  middle bearer. The lugs hang in front of the bearer so the actuators, steep at full tip, stay clear of it: tipped to
  48 degrees the actuators are at 740 of their 750 mm. With 150 kg in the bin each needs at most ~2.1 kN.
- The full bin rises in ~36 s. The combined cg stays 220..245 mm in front of the rear axle at full tip with the load
  still in: the robot does not tip backwards even if a sticky load hangs.

## Payload

- 150 kg is the payload taken for the top of the robot (estimated, as the other top implements). Wet soil or gravel
  fill only ~100 l of the 353 l; compost 250 l; wood chips (106 kg) and green waste (53 kg) fill the bin to the rim.
- Fully loaded the robot weighs 382 kg, 39 % on the front axle; a 10 % slope leaves a margin of 1.26 on the hub motors.

## Capacity

A 100 m trip with 5 min of loading by hand, 30 s to dump: ~950 kg of soil per hour, ~13 Wh per trip.

## Estimated, not measured

- Payload 150 kg on top, robot mass 160 kg and cg (0, 0, 380)
- Bulk densities of the loads; loading time 5 min, 100 m trips at 1.0 / 1.5 m/s
- Actuator speed 8 mm/s at load, masses of the actuators
