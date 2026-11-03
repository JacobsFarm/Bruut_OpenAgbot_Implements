# Metal detector

**Status: idea, not worked out yet.** Category: Measuring & Sensors.

## What it does

Scans a field for buried or hidden metal and stores a GPS point at every hit, so the spots can be checked or cleaned later.

## Concept (first thoughts)

A pulse-induction search coil on a non-metallic boom away from the robot's steel frame and hub motors, low above the ground. Every pulse above a threshold gives a GPS point with its signal strength; the map can feed the field marker to stake out the spots, or the magnet sweeper.

## Reuse from existing implements

Front boom of the grass meter; GPS point list and staking out of the field marker.

## Open questions

- Interference from the robot's steel and motors: boom length
- Coil size and detection depth
- Threshold and false hits
- Map format

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
