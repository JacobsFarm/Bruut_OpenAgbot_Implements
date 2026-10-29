# Electric weeder (simple) - rationale

## Spot, not broadcast

Electric weeding of a whole band takes 30-200 kWh per ha; the robot carries ~1.9 kWh. Broadcast it would do 0.13 ha of
field per charge at best. Switching the HV on only when the camera sees a weed under the comb uses the energy on the
weeds: at 5 weeds per m2 of band, 90 % of the time the generator is off. Spot mode is what makes electric weeding fit a
small battery robot.

## Energy per weed and speed

A weed is killed when enough energy goes through stem and root; small weeds need much less (estimated: cotyledon
0.5 kJ, 4-leaf 1.5 kJ, rosette 50 mm 4 kJ). With a 3 kW generator and a comb 120 mm long, a weed gets
3 kW x 0.12 m / v: at 0.2 m/s that is 1.8 kJ, enough for 4-leaf weeds. Larger weeds need a stop (the robot can stop on
a weed) or a second pass. So the work rate is low (~100 m2 of band per hour); the robot works long hours unattended.

## Comb and earth return

Fingers of spring steel drag over the soil and the weeds and follow the surface; the PE holder insulates them from the
lift. The circuit closes through the soil to a coulter disc running in the same inter-row 0.6 m behind: the current
flows through the root zone of the weed. A disc rolls with low drag and keeps contact in dry soil better than a skid.

## Where it works

Only the free middle inter-row: the fingers and the curtains stay within x +-98, out of the crop rows (x +-187.5 +-80,
checked up to 400 mm). Weeds in the row itself need a different tool (laser, in-row weeder).

## Lift

A parallel linkage keeps the comb level; at lift -4 it follows a hollow, at 20 degrees it is 137 mm up for headlands.
The lift actuator only holds the comb; the fingers carry nothing but their own spring force.

## Safety

5 kV at 3 kW is dangerous. The HV box has an insulation monitor and a contactor; the control switches HV only with the
comb down, the robot moving, a weed detected and no person in view; the beacon shows when it is armed; the curtains
keep animals' feet away from the fingers. These are the minimum; the machine must meet local rules.

## Estimated, not measured

- Kill energy per weed stage (0.5 / 1.5 / 4 kJ), broadcast energy (60 kWh/ha of band)
- Generator output (3 kW) and efficiency (0.85), stand-by power (60 W)
- Contact length of the comb on the ground (120 mm)
- Rolling resistance (0.08), robot mass (160 kg), usable battery energy (1.9 kWh)
- HV box mass (9 kg), actuator (1.2 kg), camera (0.6 kg)
- Not modelled: HV cable from the box to the comb, the spring on the coulter arm, the lidar for person detection
