# Seat, canopy and frame extension (simple) - rationale

## Seat over the rear axle

The operator (90 kg) is the heaviest part. Over the rear axle and in the middle of the track, his weight goes to the
rear wheels (traction) and the front keeps 33 % (enough to steer). A seat in front of or behind the robot would load
one axle with a long lever and lift the other. Sitting high (seat at ~1.1 m) raises the centre of gravity to 889 mm:
the static tip angle sideways is still 23 degrees, and a turn at 1.5 m/s uses only a fifth of what tips the robot.
That is why the riding speed is limited and side slopes over 10 degrees are not ridden.

## Controls and safety

A ridden robot must never drive on its own: the seat switch takes the robot out of autonomous mode and stops it when
the operator stands up, the joystick only works in manual mode, and the emergency stop on the armrest is in the
robot's hard-wired safety circuit (as the e-stops on the robot). The roll bar protects against a roll-over; the canopy
is only sun and rain protection, not a cab. A closed cab (the idea list's next step) would need a heater, wipers and
much more weight high up; it is left out.

## Side extensions only at the rear

Over the front wheels the steering stacks (bearing plates, steering hardware) and the GNSS dome take the upper-beam
holes, so a front cross tube collides with them (checked). Two long tubes at the rear (y -625 and -375, 250 mm apart)
form a stiff pair to x +-800 with a 50 mm hole grid, for marker arms, wider booms or row cleaners.

## Estimated, not measured

- Operator mass (90 kg) and seated centre of gravity
- Seat mass (18 kg), console and controls, cushion bulk
- Turn radius at 1.5 m/s (3 m), riding speed and slope rules
- Implement mass on an extension (15 kg at x 700), dynamic factor 2.5
- Robot mass (161.5 kg) and centre of gravity
- Not modelled: seat switch and wiring, the seat slide mechanism, mirrors and lights, a step to climb on
