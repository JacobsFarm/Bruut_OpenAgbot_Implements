# Charging dock (simple): why it is built this way

## Contacts, not inductive

- An inductive pad needs the receiver coil within ~50 mm of the ground pad. The robot's belly is at 619 mm, so the coil
  would hang low on a bracket, in the crop and the mud, and lose 10..15 % more than copper. Two sprung copper contacts
  at 54 V and ~17 A lose 0.3 W. The *wireless* part of the idea is left for later; this is the contact dock.
- Safety: the bars are dead until the robot's pilot pin closes the circuit and the BMS answers (CAN or a simple
  enable line); then the charger switches on. Low voltage (54 V DC max) and the bars face away from people walking by.

## Where the contacts are

- On the robot: a 6 mm bracket on the front face of the front outer lower beam (one top flange, 2 x M10 in the hole
  grid, notched round the GNSS mount), a PE carrier with 2 copper pads on springs and a pilot pin. 3.9 kg, it can stay
  on the robot with most implements (not with the push blade or the grass meter boom, which use the same beam face).
- On the station: an arm that reaches back from the post between the front wheels, above the tyres (top z 480) and
  under the beams, with a PE head, 2 wide copper bars and a V-funnel. With the wheels steered 30 degrees nothing of the
  station comes closer than 33 mm to the wheel units, also on the last 300 mm of the approach.

## Catching the robot

- RTK plus a camera on a marker on the funnel bring the robot to within ~60 mm sideways and 3 degrees. The funnel mouth
  catches 75 mm, the throat leaves 15 mm play, and the bars are 150 wide against 60 mm pads, so a centred pad stays
  on the bar. The last 0.5 m is driven at 0.15 m/s; the pad springs (2 x 4 N/mm, 15 mm travel) give ~60 N per pad.

## Charging and duty

- 48 V 1 kW CC/CV charger (IP65) on the post under a roof: the robot's ~1.9 kWh usable from 20 to 100 % in ~2 h, with
  the two battery pack pods ~7 h. The share of the day the robot can work does not depend on the battery size, only on
  the charger power: ~76 % with the grass meter, ~48 % with the inter-row hoe, ~41 % with the compost spreader. A
  larger charger (2 kW) is the way to more working hours, the pods give longer runs between charges.

## Estimated, not measured

- Robot usable battery 1.9 kWh, battery pack 2 x 2.56 kWh x 0.9
- Charger efficiency 0.92, CV share 12 % of the energy at ~35 % power
- Contact resistance 0.5 mOhm per pair, spring rate 4 N/mm
- Average power of the implements in work (grass meter 239 W, inter-row hoe 800 W, compost spreader 1100 W)
- Positioning accuracy 60 mm / 3 degrees with RTK and the camera marker
