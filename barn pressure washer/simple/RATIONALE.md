# Barn pressure washer (simple): rationale

## Pump in the barn, hose on the robot

A cleaning jet of 150 bar and 15 l/min carries 3.75 kW of hydraulic power; with motor and pump losses that is
~5.8 kW electric. The robot battery (1.9 kWh) would last 20 minutes, and a 6 kW motor and pump would weigh more than the
robot can carry on its top. Barns that wash pens already have a stationary high-pressure washer with a ring line and
tap points. The robot takes the HP water from a tap point through 30 m of hose on its own reel and only needs power to
drive, reel and aim (~110 W, ~18 h per charge). The water supply question of the idea (hose or tank) answers itself:
a tank of 100 l would last 7 minutes.

## Reel with a slip clutch

The reel motor keeps a small pull on the hose: when the robot drives away from the tap the clutch slips and the hose
pays out; when it comes back the reel winds it up. The hose then never lies under the wheels.

## The nozzle carrier

The fence inspector's mast and carriage give 1 m of height, and its arm reaches 0.9 m to the right; the hedge
trimmer's tilt head turns the jet from the floor to the top of the partitions. A rotating turbo nozzle (a point jet
that circles) removes dried manure much faster than a flat fan at the same flow. The reaction of the jet (43 N) acts
along the lance, back toward the mast: the tilt motor sees almost no torque, and the arm's spring hinge stays closed.

## Safety and wet barn

The jet only runs with the barn empty (a camera on the mast checks the pen), the robot stands still while washing a
section, and an IP67 cover over the robot electronics is part of the job. Navigation is the fixed route of the pens
(lidar on the pen walls, as the arena leveller).
