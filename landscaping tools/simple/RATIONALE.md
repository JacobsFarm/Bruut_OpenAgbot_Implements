# Hedge trimmer and leaf blower (simple): rationale

## The fence inspector's mast as the carrier

A hedge is a wall next to the robot's path, like a fence: the fence inspector already has a mast at the right side
between the axles (outside the steering sweep), a carriage with 1 m of height travel, and an arm on a spring hinge that
swings back when it meets an obstacle. The trimmer only needs a tilt joint at the end of that arm.

## One bar, tilted

A side cut and a top cut need the bar in two planes: in the yz plane for the side, in the xy plane for the top.
Rotating the bar 90° about the driving direction (y) does both, and 45° cuts the chamfer on the top edge that keeps a
hedge from opening up. A double-sided bar cuts in both driving directions.

The bar stands up from the head (not down), so even at the lowest carriage position it stays 0.39 m above the ground,
and at the highest it reaches 2.37 m. The top cut is limited to the carriage height (~1.26 m); taller hedges get their
top from a person or a longer mast.

## Speed

A hedge trimmer cuts cleanly when it moves less than half a tooth pitch per stroke: at 3000 strokes per minute and
0.25 m/s that is 5 mm per stroke against 30 mm teeth. Five passes (two per side, one on top) give ~180 m of a 1.25 m
hedge per hour.

## Swing-back stop at 45°

The fence inspector's arm swings back up to 80°. With the trimmer on it, at the lowest height, that would put the head
against the rear wheel bracket. The stop is set to 45°; the controller stops the robot as soon as the hinge moves.

## Blower in front

The blower clears the path before the robot gets there, and after trimming it blows the clippings toward the hedge
foot into a windrow. A blower is loud; the robot uses it at a set time and at reduced power near houses.
