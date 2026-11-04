# Drinking trough check (simple): why it is built like this

## Reuse the fence-inspector mast

A head that must sit at a given height next to the robot, reach out 0.7 m and swing back while driving is exactly
what the fence inspector has: the same base plate, mast, lead screw, carriage and spring hinge, with a longer arm.
One mast kit on the robot serves both jobs; the arm with its head is the only swap.

## Ultrasonic level from above

A float or a pressure sensor would have to go into the water at every visit. An ultrasonic sensor 140 mm above the
water measures without contact to ~3 mm; animals drinking make waves, so 5 s are averaged (+-4 mm). In a 0.85 m2
trough that is ~4 l: with 30 cows drinking ~1.7 l/min, two readings a few minutes apart show whether the float valve
keeps up.

## Its own tank, but small

Topping up 100 mm takes 85 l. A 160 l tank is two such top-ups or ~1.5 h of drinking for 30 cows: enough to bridge a
broken float valve or a frozen supply pipe until the farmer comes, not to water a herd. A bigger tank would overload
the standard robot (363 kg with this one full). For real water transport the mobile refiller (IBC) is the tool.

## Tank on the left, mast on the right

The right upper beams carry the mast plate, so the tank bars bolt to the left upper beams at y +-325 and end at x 290.
The water sits left of the centre (x -95), the mast and arm right: full, the right wheels carry 48 %, empty 56 %.

## Head clear of the trough walls

The robot parks 300 mm from a 600 mm wide trough; the head (x 1120..1260) stays inside the rim (x 800..1400) with the
nozzle 70 mm above the water. The pose check confirms the arm and head never touch the trough walls.

## Estimated, not measured

- Wave error (4 mm), drinking per cow (80 l/day), trough size, visit time (4 min), route length per round (2.5 km)
- Pump flow and power, head, sensor and pump masses
- Rolling resistance (0.06), sensor power (15 W), robot mass and battery energy
- Not modelled: the hose from the pump to the head (in a cable chain on the mast), frost protection, scrubbing
