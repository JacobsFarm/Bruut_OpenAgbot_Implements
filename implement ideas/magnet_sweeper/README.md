# Magnet sweeper

**Status: idea, not worked out yet.** Category: Transport & General.

## What it does

Picks up nails, screws, wire and other loose iron from fields, paths and yards after building work or a festival, before it ends up in the feed or in tyres.

## Concept (first thoughts)

A wide permanent or electro magnet a few cm above the ground across the robot width, on a height-adjustable bar. With an electromagnet the load is dropped in a bin at the field edge; with permanent magnets a release plate strips it off. The robot drives the field in overlapping passes and logs the covered area.

## Reuse from existing implements

Toolbar and lift of the push blade or the three-point hitch; pass pattern and logging of the field marker.

## Open questions

- Permanent magnet or electromagnet (48 V power)
- Working height versus pick-up of small parts in grass
- Release and collecting of the load
- Mass of the magnet bar and the axle loads

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
