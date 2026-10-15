# Soil moisture sensor placer

**Status: idea, not worked out yet.** Category: Measuring & Sensors.

## What it does

Places wireless soil moisture sensors at set GPS points, reads them out and picks them up again.

## Concept (first thoughts)

A drop tube or probe that pushes a sensor into the soil, with a small magazine of sensors. A reader on the robot collects values by radio on each visit.

## Reuse from existing implements

XYZ stage and ground sensing of the field marker; irrigation hose reel for timing of the water.

## Open questions

- Sensor type, battery life and radio protocol
- Pick-up of sensors: magnet or tether
- Number of points per field

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
