# Sports field line marker

**Status: idea, not worked out yet.** Category: Transport & General.

## What it does

Paints the lines of sports fields (football, hockey) from a stored layout, with only a few minutes of setup. Seen on the Turf Tank Two.

## Concept (first thoughts)

A paint tank on the robot, a small pump and a spray nozzle with a shield, mounted at a known point under the robot. The robot drives the lines on RTK; the nozzle switches on and off at the ends. A field layout is placed on two measured corners, like the AB line.

## Reuse from existing implements

Paint marking and point list of the field marker; pump and nozzle of the spot sprayer; RTK antenna offset of the robot.

## Open questions

- Line accuracy at the nozzle (antenna offset, tilt)
- Paint type, nozzle and line width
- Drawing curves (centre circle, penalty arc)
- Field templates and the user interface

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the robot catalogue (F:/side_projecten/Agbots_website): a function that other robots do and the Bruut has no implement or idea for yet.
