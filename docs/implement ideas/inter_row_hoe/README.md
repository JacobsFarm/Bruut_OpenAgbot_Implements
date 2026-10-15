# Single-axis inter-row hoe

**Status: idea, not worked out yet.** Category: Soil Cultivation & Weed Control.

## What it does

Hoeing unit with single-axis (left/right) guidance that stays tightly between the rows, for example in maize, so weeds are cut close to the crop without damaging it.

## Concept (first thoughts)

A hoe frame with A-blades or goosefoot shares that is shifted sideways by a linear actuator or stepper. A camera or the RTK row map gives the lateral error; the shift axis corrects it. Gauge wheels in the robot's wheel track keep the depth.

## Reuse from existing implements

Parallelogram unit with gauge wheel and camera of the in-row weeder; the X stage idea of the field marker.

## Open questions

- Lateral stroke and speed of the shift axis
- Row crop (maize, beet) and row distance to design for
- Camera-guided versus RTK-guided
- Protection against crop damage when the guidance drops out

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the attachments list of the website (functionality's.json).
