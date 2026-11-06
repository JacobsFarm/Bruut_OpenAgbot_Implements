# Why the IBC trailer with two liquids is what it is

## The 2-IBC trailer, one liquid per IBC

The trailer of `../ibc_trailer` already carries two IBCs; for the precision applicator V4 the front IBC holds liquid
A and the rear one liquid B. Frame, axle, tyres, drawbar and parking gear stay as they are (`sit_params.cfg(2)`).
What changes is everything the liquid passes through: two suction lines (no common header), two pumps, two discharge
hoses, two drop pipes and nozzles.

## Two pumps in one deeper control box

The station's control box already holds the pump, battery, controller, RTK receiver and radio. A second pump with its
own flow meter and motorised valve fits behind the first when the box is 260 mm deeper (660 instead of 400); one
controller, battery and radio serve both. The box moves 125 mm to the right so that port A lies right of the mast and
port B left of it: the two discharge hoses then go straight to their own half of the mast and never cross. The
suction lines run side by side under the floor (A at x 0 as on the 1-IBC trailer, B 120 mm to the left) through
holes in every cross member ahead of their IBC.

## Two nozzles across the arm

As on the mobile refiller: the funnels of the working robot are 455 mm apart across the robot and the arm reaches
across it, so the two drop pipes sit 455 apart on the arm, A (near) at 1422.5 and B at 1877.5 from the mast; the
working robot's centre line stays at the reach of the 1-IBC trailer (1650: half width 888 + 250 gap + 500).
The hoses run on the back of the arm (towards the control box); A crosses over B at the mast top and takes the outer
lane, B the inner one.

## A lifting arm, so it can also fill the mobile refiller

The mobile refiller with two IBCs has its fill funnels on top, at z 2060, 700 mm above the funnels of the working
robot. Rather than a second arm, the arm rides on a sleeve on a round mast (Ø114) and an electric linear actuator
(stroke 706) lifts it: low, the nozzle tips are at 1460 for the working robot; high, at 2166 for the refiller. The
refiller stops beside the trailer exactly where the working robot stops (same reach, its fill funnels at its local
y −70 instead of the working robot's 170), so the same RTK docking point and the same arm angle serve both. The hoses
from the pumps end at 1600 on the mast; above that a slack loop on each side takes up the 706 mm of lift.

At 40 mm/s the lift takes 18 s each way, small against the pumping: filling 2 × 500 l at 120 l/min per pump takes
4 minutes.

## Mass

Two IBCs with 800 l each: 1920 kg of liquid, trailer 446 kg, control box with two pumps 150 kg, mast and arm 179 kg
(round mast 2.9 m, sleeve, actuator). The 11.5/80-15.3 tyres of the 2-IBC trailer carry 2 × 1700 kg (estimated); the
nose load moves forward a little with the heavier mast and box.
