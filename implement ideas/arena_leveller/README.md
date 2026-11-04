# Riding arena leveller

**Status: idea, not worked out yet.** Category: Crop & Soil.

## What it does

Levels and loosens the footing of a horse riding arena at night, so it is ready every morning. Seen on Fraunhofer ARA (tracked arena robot).

## Concept (first thoughts)

A rear tool frame with a row of loosening tines, a levelling board and a small roller or mesh, driven over the arena in a fixed RTK or lidar pattern (indoor arenas have no RTK). The depth and board height are set by a linear actuator.

## Reuse from existing implements

Levelling board, tines and lift of the grassland harrow; push blade for moving sand back from the edges; lidar ideas of the chicken house robot for indoor navigation.

## Open questions

- Navigation in an indoor arena without RTK
- Footing types (sand, sand with fibres, wood chips) and the depth to work
- Edges and corners along the arena wall
- Watering the footing at the same time

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the robot catalogue (F:/side_projecten/Agbots_website): a function that other robots do and the Bruut has no implement or idea for yet.
