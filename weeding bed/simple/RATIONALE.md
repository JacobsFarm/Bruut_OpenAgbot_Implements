# Weeding bed - rationale

## Beside the robot, not over it

A worker lying prone needs his chest about 0.5-0.6 m above the ground to reach the soil (arm ~650 mm). The robot's
upper beams are at 0.7 m and the space between the wheels is taken by the steering stacks, so the bed cannot be under
or on the robot. Two beds hang beside it, one per side, outside the front steering sweep (x 534 at 30 degrees): two
workers balance each other, and each lies over a row that the robot's wheels do not run on.

## C-frames instead of cross tubes over the bed

A first version had the cross tubes running out to the outer rail: they crossed 110 mm above the board, over the
worker's back. Now each cross tube ends at x 620 in a hanger down to a cross arm under the bed (C-frame). The moment
of the bed is taken by the welded corners (40 x 40 x 4, top gusset); with 135 kg per side, factor 2, each corner sees
~230 Nm (~45 MPa). The cross tube at the outer upper beam is the highest stressed point (69 MPa, `cross_tube()`).

## Front stubs

The upper beams have vertical holes at |y| 275..625 only. The front pair uses y 375 and 625; the fixed steering plates
are at y 405..595, so both clear. At y 625 the GNSS dome (x +-75, y 500..650) is in the middle: there are two stubs
from x 260, each on its own two beams (the bolts 100 mm apart take the moment: 3.5 kN tension, ample for M10 8.8).

## Board, chest wedge and face rest

550 mm wide (between the hanger and the outer rail), long enough for a 1.85 m person from y -1050 to 1000. The chest
wedge lifts the shoulders 40 mm, the face rest has an oval opening so the neck stays straight and the eyes look down
at the crop in front of the hands (y ~1100, ahead of the front tyres). Synthetic leather over foam: washable.

## Hold-to-run and parking stands

The robot creeps only while every worker on board holds the run button; releasing it stops the robot. That is the
same rule as a weeding bed with a tractor drive, and it lets slower workers set the pace. The speed knob sets
100-400 m/h. The empty bed (339 kg with the robot) tips when a worker steps on the outer edge with a dynamic load of
110 kg: restoring 127 kgm vs 89 kgm, factor 1.44. So the stands go down before anyone gets on or off; a limit switch
on each stand blocks driving while it is down.

## Mass

178 kg is more than the robot itself. Rails 40 x 40 x 2 and aluminium canopy posts would save ~15 kg; the bed is
meant for flat fields at creep speed, where the wheel loads (144 kg per front wheel with 2 workers) are the limit to
watch, not the stability (32 degrees sideways with 2 workers, 18 with 1).

## Estimated, not measured

- Worker mass (85 kg) and prone centre of gravity (y 100, z 680)
- Drive power at creep speed with 2 workers (120 W) and electronics (40 W)
- Worked strip per worker (0.5 m) and speed range 100-400 m/h
- Dynamic factors (2 for the frame, 110 kg for a worker getting on)
- Hub motor and tyre load rating at ~145 kg per wheel (robot data missing)
- Foam and canopy densities
