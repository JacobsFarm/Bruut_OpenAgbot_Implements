# Air-assisted orchard sprayer

**Status: idea, not worked out yet.** Category: Spraying, Fertilizing & Irrigation.

## What it does

Sprays the canopy of fruit trees, vines or hedges with an air stream that carries the droplets into the leaves, and switches nozzles off where there is no canopy. Seen on GUSS, LJ-Tech S500Pro, MQ Agritech M200 and Smart Apply.

## Concept (first thoughts)

A tank on the upper beams, an axial fan at the rear with a ring of nozzles, or two vertical towers with cross-flow fans. A lidar or camera measures the canopy per height section and switches each nozzle section on and off.

## Reuse from existing implements

Tank, pump and control box of the spot sprayer; nozzle switching of the drop-on-demand boom; canopy sensing of the windbreak and tree-row inspector.

## Open questions

- Fan power and air volume versus battery
- Tank size versus mass and the robot's payload
- Drift: tower or tunnel version, canopy sensing
- Height of the trees to reach

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the robot catalogue (F:/side_projecten/Agbots_website): a function that other robots do and the Bruut has no implement or idea for yet.
