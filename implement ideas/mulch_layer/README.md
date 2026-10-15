# Mulch / foil layer

**Status: idea, not worked out yet.** Category: Crop & Soil.

## What it does

Lays mulch foil or paper along the rows, pressing the edges into the soil, to suppress weeds and keep moisture.

## Concept (first thoughts)

A reel on a frame behind the robot, two shaped discs that bury the edges and a press roller. Tensioning via a brake on the reel; the robot pulls straight along the RTK line.

## Reuse from existing implements

Reel and winding mechanics of the irrigation hose reel; discs and press wheels of the overseeder.

## Open questions

- Reel width and foil roll mass
- Edge covering: discs or soil throw
- Cutting and ending the foil at the headland
- Biodegradable foil: strength at the robot's pull

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
