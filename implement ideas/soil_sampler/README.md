# Soil sampler

**Status: idea, not worked out yet.** Category: Crop & Soil.

## What it does

Pushes a sampling probe into the soil at GPS points and keeps each sample in a numbered tube, so a field can be sampled on a grid without a person walking it.

## Concept (first thoughts)

A probe on a Z axis with a carousel of sample tubes behind the robot. The robot stops roughly on the point, the stage positions the probe exactly (as in the field marker), pushes it in, takes the core and drops it into a tube with the GPS position logged.

## Reuse from existing implements

XYZ stage, Z axis with ground-sensing shroud and RTK antenna mast of the field marker; point list handling; soil compaction meter idea.

## Open questions

- Probe type and depth (topsoil only or a deeper profile)
- Push force versus robot weight (anchoring)
- Carousel size and cleaning of the probe between samples
- Sample label and hand-over to the lab

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
