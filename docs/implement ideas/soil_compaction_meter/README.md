# Soil compaction meter

**Status: idea, not worked out yet.** Category: Measuring & Sensors.

## What it does

Measuring and mapping soil density at specific data points.

## Concept (first thoughts)

A penetrometer rod pushed into the soil by an actuator at a point, force and depth logged against the GNSS position. The robot stops at each data point (like the field marker).

## Reuse from existing implements

Z axis and ground-sensing shroud of the field marker; point list from the marker's coordinate handling.

## Open questions

- Cone size and push force
- Depth range and speed
- Data points per hectare
- Calibration against a manual penetrometer

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the attachments list of the website (functionality's.json).
