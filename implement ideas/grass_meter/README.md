# Grass meter / crop scanner

**Status: idea, not worked out yet.** Category: Measuring & Sensors.

## What it does

Measuring grass and crop height and health to create task maps for nitrogen or phosphate.

## Concept (first thoughts)

A mast or boom with ultrasonic, lidar or a rising-plate meter that records height at each GNSS position, stored as a map. The map becomes a task map for the fertilizer spreader or liquid applicator.

## Reuse from existing implements

Camera mast of the spot sprayer; RTK antenna mast of the field marker; logging of the other implements.

## Open questions

- Sensor type: ultrasonic, lidar or plate meter
- Number of sensors across the working width
- Calibration to dry-matter yield
- Map format for the task maps

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the attachments list of the website (functionality's.json).
