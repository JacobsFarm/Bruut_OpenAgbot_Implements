# Riding arena leveller (simple): rationale

## Tines, board, roller: the arena groomer order

Every arena drag works in this order: tines loosen the compacted layer (hoof traffic packs the top 3-5 cm), a board
moves the loose sand from the high spots into the hoof prints, a roller or mesh firms the surface so the horse gets
grip and does not sink. The frame of the grassland harrow has exactly the positions for that: the front tine bar
carries the tines, the rear tine bar the board, and the roller hangs behind on side plates.

## Rigid tines, not spring tines

Spring tines (as on the harrow) deflect in sand and leave the compacted layer under them. Rigid flat-bar tines with a
forward lean pull themselves in and break the layer at the set depth; the reversible point is the wear part.

## The roller sets the depth

The frame rides on the roller, and the lift actuator is in its 40 mm float slot. The tine depth follows from the
height of the tines in their clamps and does not change with the robot's pitch or with soft spots, and the board
cannot dig in.

## Traction is the limit

The robot is light (161.5 kg) and arena sand gives little grip (~0.4). With 44 kg of front ballast (4 plates of the
counterweights implement) the robot can pull ~690 N, enough for 11 tines at ~35 mm plus the board and the roller. A
deeper loosening is done on successive nights (the footing is worked every night anyway). The hub torque (1100 N) is
not the limit, grip is.

## Not lifted

The leveller weighs 130 kg and its centre of gravity is 870 mm behind the rear axle. Lifting it would lift the front
wheels unless ~165 kg of ballast went on the front. So it is designed to stay on its roller: it turns on the roller in
the arena (tines in loose sand), and for the yard the tines go into the transport holes (50 mm higher). The lift
poses are kept in the model (the actuator still sets the float and can lift it with a heavy-ballast robot), but the
robot alone does not use them.

## Navigation indoors

Indoor arenas have no GNSS. A 2D lidar on a 1 m post sees the four walls over the robot; a rectangle with known size
is an easy map for scan matching (the gates and the mirror wall are features). UWB anchors in the corners are the
fallback in outdoor arenas without walls (or use RTK there). The pass pattern is fixed: straight passes 1.2 m apart and
a perimeter lap with the board along the kickboard.
