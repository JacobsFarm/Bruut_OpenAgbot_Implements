# Bedding rake (simple): why it is built this way

## Grooming the cubicles from the alley

- Cows dig holes in the rear half of the cubicle bed and drag bedding into the alley; a bed that is loosened and levelled
  every day stays drier and needs less fresh bedding. The robot already drives along these alleys (feed pushing,
  [sawdust spreading](../../sawdust%20spreader/simple/)), so a groomer on a side arm fits the same rounds.
- The barn is drawn with the model (curb 200 high, beds 2.3 m, cantilever divider loops every 1.2 m with the bottom
  rail 380 above the bed and the rear 330 mm of the bed open): the arm has to reach over the curb and stay under the
  loops while the robot drives on.

## Arm and rotor

- The rotor axis lies along the bed (across the alley): 970 long, it covers the bed from 100 to 1070 mm behind the curb,
  the part where the cow lies. The tines (O7 spring wire, tip O240, 180 rpm, 2.3 m/s) turn in the plane of travel:
  they loosen the bedding and spread it evenly between the dividers. A first layout with the axis along the alley
  covered only a 240 mm strip.
- The arm runs from a pivot above the robot's beams steeply down to an elbow just past the curb, then out over the bed
  at z 470..520: the top of the arm stays 90 mm under the divider loops; check_poses passes the loops along the arm.
  Two hangers carry the rotor bearings; a 48 V 400 W gearmotor sits on the outer end.
- The pivot is above the beams (z 760) so the crank plate on the arm can swing over the beams: a 24 V 1500 N actuator
  lies across the robot top from a lug on a bearer to the crank pin (160 mm above the pivot) and swings the arm up to
  40 degrees at the row end (the rotor rises ~550 mm, over the curb). It holds the arm with ~1140 N in work.

## Load on the robot

- The rake weighs 37 kg, its cg 884 mm right of the centre: the robot's cg moves 167 mm to the right, side tip angle
  27 degrees towards the cubicles: fine on a flat barn floor, but the arm should be lifted on slopes and when turning
  fast.
- The rotor pushes the robot along the alley with ~134 N (the tines dig in), against 774 N of grip.

## Capacity

At 0.3 m/s a cubicle takes 4 s; with 60 s per row end, ~655 cubicles per hour, ~325 W: one battery charge does ~3800
cubicles. The robot can groom a 200-cow barn in under 20 minutes.

## Estimated, not measured

- Rotor power 250 W per m of rotor in loose sawdust or chopped straw plus 60 W idle
- Barn dimensions (curb 200, bed 2.3 m, divider loop bottom 380 above the bed, rear end 330 mm from the curb): measure
  per barn, the arm length and height follow from them
- Robot mass 160 kg, cg height 380 mm; side grip coefficient 0.4 on wet concrete
- Gearmotor and actuator masses
