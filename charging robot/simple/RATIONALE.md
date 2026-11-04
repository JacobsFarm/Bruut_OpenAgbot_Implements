# Charging robot (simple) - rationale

- **A standard robot, not a new vehicle.** The charger is a Bruut with a deck: same wheels, steering, software and
  spare parts. When it is not charging, the deck comes off and the robot works.
- **Conductive contacts, the dock's head.** The working robots already get the charging dock's bracket; with the same
  head behind the charger they cannot tell a mobile charger from the fixed dock. Copper bars and sprung pads carry
  28 A with 0.4 W loss; wireless charging would lose ~10 % and needs exact alignment.
- **Battery-pack pods.** The same exchangeable pods as the battery pack: one design, one charger at the shed, and pods
  can be moved between the charger and a working robot. 4 pods (86 kg) keep the charger at 295 kg, 75 kg per tyre:
  a fifth pod would fit but brings the deck to its edge and the robot to 320 kg.
- **DC/DC instead of pod-to-robot parallel.** Both packs are 48 V LiFePO4 at a different state of charge; a DC/DC
  in CC/CV gives a controlled current (1.5 kW, ~73 min for 80 %) and the same charge curve as the dock.
- **Docked 1550 mm behind.** The steered front wheels of the working robot stay clear of the charger's rear wheels
  (checked at +-30 degrees), and the arm stays short (290 mm) and stiff.
- **Deck bars at y -625 / -275 / 275.** In the grid holes of the upper beams and clear of the frame bolts of the wheel
  units (y +-425 / +-575 stick up to z 705), so the deck plate lies flat at z 707.
- **When it pays.** For heavy tools (hoe, harrow: 1.2-1.5 h per charge) the charger adds ~3 h of work a day and saves
  the trips to the shed; for light sensors (grass meter: 6.4 h per charge) the gain is small.
