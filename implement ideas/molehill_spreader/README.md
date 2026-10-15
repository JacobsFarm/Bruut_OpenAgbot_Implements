# Molehill spreader

**Status: idea, not worked out yet.** Category: Crop & Soil.

## What it does

Spreads molehills flat in grassland before mowing or overseeding, so the mower stays clean and the sward closes again.

## Concept (first thoughts)

A drag chain or a light roller bar behind the robot (or a low rotating brush), floating on a parallelogram. A camera or the mole mapper tells where hills are, so the unit can be raised elsewhere.

## Reuse from existing implements

Disc-brush drive and toolbar of the disc brushes; floating lift frame of the overseeder.

## Open questions

- Drag chain, harrow or brush
- Soil and stones in the hills: damage to the mower after all?
- Switch on only above hills (camera) or always

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
