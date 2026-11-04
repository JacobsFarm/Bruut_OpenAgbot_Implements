# Security patrol (simple) - rationale

- **Mast height 2 m (head at 2.23 m).** High enough to look over a standing person, a fence and most of the crop, and
  to see the ground between the sheds; low enough to pass under barn doors (2.5 m) and to keep the centre of gravity at
  z 700, so the side tilt limit stays at 28 degrees (the robot alone ~35).
- **Behind the robot centre (y -300).** Far from the steering stacks, out of the sky view of the GNSS antenna at the
  front (y 575), and the extra mass evens the axle loads (102 / 96 kg).
- **Base plate over all 4 upper beams, 2 bolt rows.** The grid holes of the upper beams are at |y| 275..625 step 50
  (not at 300); 8 M10 in 2 rows give a wide foot. The mast is 60 x 60 x 3: 73 Nm at 20 m/s wind is only 6 N/mm2, the
  section is chosen for stiffness (a steady image while driving), not strength.
- **Thermal plus zoom camera on one pan/tilt head.** The thermal camera finds people and animals in the dark at
  hundreds of metres (Johnson criteria, 0.48 mrad); the zoom camera with IR light then gives a picture a person can
  recognise. Both look the same way, so one head is enough.
- **4 fixed wide cameras.** While the head looks at one thing, motion anywhere around the robot is still seen
  (~32 m detection range, 40 degrees overlap).
- **Stop-and-sweep route.** A thermal sweep while standing still (14 s) avoids motion blur and false alarms from the
  robot's own movement; a viewpoint every 80 m keeps a 2 km round under 50 minutes.
- **Horns and beacon.** Same horn as the speech speaker, front and rear: a recorded or live warning is more effective
  than a siren; the beacon shows that the robot is working (and is visible to people on the yard).
- **Privacy.** Cameras filming only the own premises and fields; the software can blur public roads and neighbours'
  plots (to be set per farm, see the rules for camera surveillance).
