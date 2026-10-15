# Pheromone trap service

**Status: idea, not worked out yet.** Category: Weed & Crop Protection.

## What it does

Visits insect traps and pheromone dispensers at the field edge: checks them with a camera, counts catches and swaps dispensers on schedule.

## Concept (first thoughts)

A small arm or an XYZ stage that opens a trap, photographs the catch and replaces the lure. The robot stops at stored trap positions.

## Reuse from existing implements

XYZ stage and camera ideas of the field marker; trap positions kept like the marker's point list.

## Open questions

- Trap types and how they open
- Catch counting by image
- Lure storage and replacement by the robot
- Frequency of visits

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
