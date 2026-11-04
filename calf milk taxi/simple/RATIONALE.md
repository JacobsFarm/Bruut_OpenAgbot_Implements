# Calf milk taxi (simple): rationale

## Warm milk from the kitchen, not heated on board

Heating 80 l of milk from 10 to 40 °C takes ~2.6 kWh: more than the robot's whole battery. So the milk is mixed and
warmed in the calf milk kitchen (where there is mains power and hot water), and the tank only has to keep it warm.
40 mm PU keeps the loss at ~35 W: the milk cools ~0.4 K per hour, a round takes ~20 minutes. The 300 W heating mat is
for holding the temperature on a long route or a cold night, not for warming up.

## Peristaltic pump

The dose (2-4 l per calf, set per calf) is counted in pump turns; there is no flow meter or valve that could foul.
Only the food tube touches the milk, it is self-priming (the tank outlet is low but the pump is higher than the tank
bottom) and it stops dead (no drip after the dose). The tube is the wear part and is changed at a fixed interval;
±5 % per dose is better than a farmer with a measuring jug.

## Swing arm, not a fixed nozzle

The buckets hang on the outside of the hutch fences, about 0.9 m from the robot centre and 0.75 m high. A fixed
nozzle that far out would make the robot 1 m wider on one side all the time. The arm swings out only at a stop and
parks along −y inside the outline; it swings through the rear-right quadrant, away from the front steering stacks.
The hose runs up inside the post and through the hollow shaft of the gearmotor to a rotary union, so it does not
twist.

## RFID and camera at the tip

The tag on the bucket holder gives the calf's number, so the dose comes from the herd management system (more milk
in week 2-5, weaning steps), and a wrong stop cannot feed the wrong calf. The camera is the safety check: no bucket,
no milk.

## Tank in the middle

Full, the taxi adds 162 kg, more than the robot itself. On the robot's centre it loads both axles evenly (84 / 78 kg).
The centre of gravity of the taxi is at ~1.0 m: on the flat barn floor and yard this is fine; the route keeps it off
steep ramps.

## Hygiene

Milk residues spoil fast. After each round the robot docks at the kitchen: the tank is rinsed, then hot water with
detergent is pumped through the tank, pump, hoses and nozzle (the nozzle into a return cup), then rinsed again. The
tank has no corners (round, conical bottom, outlet at the lowest point) and the stirrer comes out with the lid.
