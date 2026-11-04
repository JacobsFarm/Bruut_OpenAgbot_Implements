# Power harrow / rotary tiller

**Status: idea, not worked out yet.** Category: Crop & Soil.

## What it does

Driven tines or blades work the top soil into a seedbed, or loosen the soil between vines and trees. Seen on vineyard and orchard robots (Slopehelper power harrow, Pellenc RX-20, Naïo Ted) and small electric tractors.

## Concept (first thoughts)

A narrow rear-mounted rotor with vertical tines (power harrow) or L-blades (rotary tiller) and a crumbler roller that sets the depth, driven by a geared electric motor. Lifted by a linear actuator like the grassland harrow. Works in strips, so the power stays within what the robot can supply.

## Reuse from existing implements

Rear mount and lift of the grassland harrow; gearmotor and chain drive of the dockweed drill; power supply from the battery pack or hybrid range extender.

## Open questions

- Working width versus available power and traction
- Rotor speed, tine type and working depth
- Draft and reaction forces on a light robot
- Stones: overload protection of the rotor

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the robot catalogue (F:/side_projecten/Agbots_website): a function that other robots do and the Bruut has no implement or idea for yet.
