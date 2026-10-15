# UV-C light for mildew control

**Status: idea, not worked out yet.** Category: Weed & Crop Protection.

## What it does

Drives UV-C lamps along the rows, shining between and over the plants at night, to suppress powdery mildew and other fungal diseases without chemicals.

## Concept (first thoughts)

A lamp bar with UV-C tubes or LED modules in a hood close to the crop, with reflectors that shine into the canopy from the sides and from below. The hood shields people and animals; the lamps switch off the moment the robot stops, and interlocks stop them when the hood is lifted or a person is detected. Dose is set by driving speed, so speed and lamp power give a fixed dose per square metre.

## Reuse from existing implements

Hood and heat-shield thinking of the weeds burner; 48 V supply and control box; row units with gauge wheels of the in-row weeder for height above the crop.

## Open questions

- UV-C dose per pass against mildew species and crop (strawberry, cucumber, grape ...)
- Lamp type: UV-C tubes versus LED, and lifetime
- Hood height over the canopy and side reflectors
- Safety: eye and skin protection, interlocks, night-only operation
- Effects on beneficial insects and on the crop (leaf burn)

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
