# Tray setter

**Status: idea, not worked out yet.** Category: Sowing & Planting.

## What it does

Front-mounted unit that takes seedlings out of the tray and sets them out at the right spacing.

## Concept (first thoughts)

A magazine of trays above the front beams, a gripper or pin-picker takes one seedling per cycle and plants it in a dibbled hole. Spacing by the robot's odometry; the robot stops or crawls per plant.

## Reuse from existing implements

XYZ stage idea of the field marker for positioning; camera and odometry of the in-row weeder.

## Open questions

- Tray type and plug size
- Pick-and-place mechanism and cycle time
- Planting depth and soil closing
- Tray reloading, again from a refiller?

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the attachments list of the website (functionality's.json).
