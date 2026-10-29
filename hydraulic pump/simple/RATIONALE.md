# Hydraulic power pack (simple) - rationale

## Size class

The robot's battery gives ~4.8 kW peak (48 V x 100 A) and 1.9 kWh. A group-1 gear pump of 4 cc at 3000 rpm gives
11 l/min; at 150 bar that is 2.8 kW hydraulic and 3.9 kW from the battery, the most the robot can sensibly give. That is
the class of small tractor front loaders and log splitters: 19-30 kN from a 40-50 mm cylinder. Larger flow would only
empty the battery faster; larger pressure needs a bigger motor.

## Motor runs on demand

The BLDC motor only runs while a valve is switched (the controller starts it in ~0.2 s), so there is no idle loss and no
open-centre heat. At 100 bar a full charge gives ~44 minutes of pumping, which is many hours of intermittent work
(a cylinder stroke takes 1-3 s).

## Tank and heat

16 l of tank for 11 l/min is 1.5 minutes of flow, enough to settle air and carry the cylinder volume. Without a cooler
the oil reaches 60 C after ~35 minutes of 50 % duty at 100 bar; for longer continuous work (a hydraulic motor) a small
12 V fan cooler on the return line is the next step (advanced).

## Valves and couplers

Two double-acting sections cover a lift cylinder and a tilt or a motor. ISO-A 1/2" couplers are the common standard on
small tractors, so existing implements fit. The block sits at the rear edge, so the couplers screw straight into it and
the work lines need no hoses on the robot.

## Mount

On the rear half (y -280..-630) the pack puts 62 % on the rear axle, where a rear implement adds its load anyway; for a
front loader, couplers on a front bracket would be added. The bearers use the beam holes at y -325 / -475, between the
wheel-unit bolts.

## Estimated, not measured

- Pump efficiencies (volumetric 0.92, hydraulic-mechanical 0.85), motor + controller efficiency (0.90)
- Battery peak power (4.8 kW), usable energy (1.9 kWh)
- Heat loss of the tank (4.5 W/K), share of the hydraulic work lost in valves (30 %)
- Masses of the motor (9 kg), pump (1.8 kg), valve block (7 kg), controller, solenoids, couplers and hoses
- Robot mass (160 kg) and centre of gravity
- Not modelled: hose fittings, motor cable, electrical connection of the solenoids, a cooler
