# Air-assisted orchard sprayer - rationale

## Small fans instead of one big axial fan

A tractor orchard sprayer has a O800-900 axial fan of 10-30 kW. The robot's battery (1.9 kWh) and drive cannot carry
that. Six 48 V axial fans O300 (~200 W each) give ~10 000 m3/h together: with the "replace the air in the canopy band"
rule (air = speed x canopy height x half the row spacing) that is enough for a 1.5 m canopy band at 3 m row spacing up
to 0.63 m/s. So this is a sprayer for low trees, vines, soft fruit and hedges, at a slow speed. Separate fans per
height also make the sections: a fan and its nozzles switch together.

## Tower behind the robot, pods beside the mast

The fans must blow sideways from a narrow column in the middle of the alley; the robot's body is in the way between
0.2 and 0.75 m height, so the column stands behind the rear axle (y -880). The pods sit beside the mast with an 80 mm
intake gap (air comes in from the robot side, goes out to the trees). Diagonal stays from the mast to the upper beams
were tried on paper: they cross the pods' swept circle, and the mast moment is small (99 Nm at 0.3 g), so the mast is
a cantilever on the cross beam with a front gusset.

## Mounting under the lower beams

Arms at x +-225 use the lower-beam grid holes (y -425 and -575) and stay between the spot sprayer's sub plate
(x +-200) and the rear wheel brackets (x 261). The bolts also pass the control box base plate, which gets 4 extra
holes. The tank, pump, filter, regulator and control box are the spot sprayer's, imported unchanged; the pump is its
7 bar version (hollow-cone nozzles need 5-10 bar).

## Canopy sensing

A 2D lidar per side scans a vertical plane 225 mm ahead of the nozzles. It gives the canopy height and density per
section; the controller opens a section when the lidar saw leaves in its height band, 0.36 s later at working speed
(4 x the valve latency). With ~30 % gaps (young trees, missing trees, row ends) that saves ~95 l/ha.

## Balance

The tower moves the centre of gravity back: 64-68 % on the rear axle. The front wheels still carry 85-140 kg, enough
to steer. The full tank sits in the middle, so filling or emptying hardly changes the balance.

## Estimated, not measured

- Fan air volume at the working point (1700 m3/h), electrical power (200 W) and mass (4.5 kg per pod)
- Nozzle output 0.3 l/min at 7 bar; pump power at 7 bar (150 W)
- Drive power with a full tank at 0.6 m/s (300 W)
- Canopy band 0.6-2.1 m, row spacing 3 m, 30 % gaps, air factor 1
- Valve latency 0.08 s
- Masses of the motors, lidars, manifold and control box
