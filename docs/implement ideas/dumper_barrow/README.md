# Dumper / power barrow

**Status: idea, not worked out yet.** Category: Transport & General.

## What it does

Motorized wheelbarrow-style bin for transporting and dumping loose materials, also usable as a carrying aid or mini dumper.

## Concept (first thoughts)

A tipping bin on the robot with an actuator, taking loads of loose material to a place and tipping them out. Tip over the front or the rear; gate for controlled discharge.

## Reuse from existing implements

Actuator, hanger and frame of the push blade; payload logic like the compost spreader.

## Open questions

- Bin volume and payload
- Tip direction and stability while tipping
- Ground pressure on soft soil

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the attachments list of the website (functionality's.json).
