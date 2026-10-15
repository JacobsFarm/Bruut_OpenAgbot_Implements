# Mole and tunnel mapper

**Status: idea, not worked out yet.** Category: Crop & Soil.

## What it does

Finds and maps molehills (and with a probe, mole tunnels) so they can be treated or spread flat later.

## Concept (first thoughts)

A camera looking down finds fresh hills; each gets a GPS point. A probe or an acoustic sensor could later detect tunnels. The map feeds the molehill spreader or a trap placing action.

## Reuse from existing implements

Camera and detection pipeline of the spot sprayer; GPS logging of the field marker.

## Open questions

- Detection of fresh versus old hills
- Tunnel detection: is a probe or a ground-radar feasible?
- Map format and who uses it

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
