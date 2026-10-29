# Irrigation pump (simple) - rationale

## Why a pump on the robot

Ditches and ponds are often where there is no power. The robot already carries 1.9 kWh and drives itself to the
water, so a 1.5 kW pump makes it a mobile pump station for a few hours: enough for 10-17 m3, 1000-1700 m2 at a 10 mm
gift. With a charging dock or solar canopy nearby it can pump all day in shifts.

## Pump

A self-priming centrifugal pump fills itself from the priming chamber, so the suction hose does not need to be filled
by hand; the foot valve keeps it full between runs. Efficiency is modest (~50 %), but it tolerates dirty ditch water,
which a piston or diaphragm pump would not. The assumed curve (32 m shut-off, 16 m3/h free flow) is typical for a 1.5 kW
1.5" pump; the operating points follow from the curve against suction lift, end head and hose friction.

## Suction side

NPSH available falls from 4.9 m at 1.5 m lift to 1.4 m at 5 m: above ~4 m lift a small self-priming pump cavitates.
The robot should drive as close to the water as the bank allows; 8 m of suction hose reaches down a 2-3 m bank.

## Reel

A reel keeps the stiff spiral hose tidy and fixed; the rotary union lets the hose stay connected while it is unrolled.
The drum is a 3 mm tube and the flanges 3 mm, so the reel stays light (the pack is ~62 kg).

## Estimated, not measured

- Pump curve (shut-off 32 m, free flow 16 m3/h), pump efficiency (0.50), motor efficiency (0.88), idle power (30 W)
- Hose friction factor (0.025) and local losses of strainer, foot valve, union and bends (k 6)
- Masses of pump (9 kg), motor (5.5 kg), wound hose (4 kg), pipes, coupling and strainer
- Usable battery energy (1.9 kWh), robot mass (160 kg)
- Not modelled: hose clamps, the motor cable, a pressure switch / dry-run sensor
