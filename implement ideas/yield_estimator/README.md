# Yield estimator

**Status: idea, not worked out yet.** Category: Measuring & Sensors.

## What it does

Counts fruits, heads or plants with a camera and logs them per GPS position, so the harvest can be estimated and planned.

## Concept (first thoughts)

Cameras on a mast or in the row, an image model that counts and sizes the crop, and a yield map per row.

## Reuse from existing implements

Global-shutter camera and detection pipeline of the in-row weeder and the spot sprayer.

## Open questions

- Crop to count (strawberry, broccoli, apple ...)
- Lighting at night versus day
- Count accuracy and counting error
- Output: map, report or plucking plan

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
