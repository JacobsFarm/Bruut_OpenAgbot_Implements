# Pheromone trap service (simple) - rationale

- **A trap made for the robot.** Opening a standard delta trap, peeling a sticky card and clipping a lure takes hands.
  A drawer that slides out with a handle frame turns all of it into 2 straight moves (out, back) and a hook, which a
  linear actuator and the Z axis of a mast can do. The card is photographed in the drawer, so it never has to be
  handled; a full card is changed by a person on the work list.
- **Lure in a push-through clip.** A new capsule pushed into the clip from above pushes the old one out below: no
  gripper, one plunger. The revolver of 12 covers a round of 40 traps with a 4-week lure (~10 swaps).
- **Fence-inspector mast reused.** Same mast, lead screw, stepper and carriage, so the Z range (drawer 0.2..1.0 m)
  and the parts are proven; only the arm is fixed (the trap position is known) and gets a guide and actuator.
  The fin base plate bolts at y +-300, between the grid holes of the upper beams; this implement has its own plate
  with 8 bolts in the holes at y +-275 / +-325.
- **Hook from below + Z up.** The hook finger goes in under the handle bar, the carriage lifts 15 mm and the
  upturned tip is behind the bar: no extra gripper axis, and it lets go by moving down.
- **Camera on a post, 55 degrees down.** It sees the whole pulled-out card (560 x 420 mm field) without moving; 7 px/mm
  counts moths and flies. Thrips (1.2 mm) need a closer camera or a macro lens in a later variant.
- **Post line 1.54 m to the right.** The head stays 1.0 m from the robot centre when retracted, so the robot can drive
  along the traps on the field edge without touching them, and the reach of 220 mm closes the gap at a stop.
