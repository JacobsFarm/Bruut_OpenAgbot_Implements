# Asparagus harvester

**Status: idea, not worked out yet.** Category: Transport & General.

## What it does

Finds white asparagus spears that push up through the ridge, cuts them below the surface and lifts them out. Seen on the AVL Compact S9000 and the Inaho harvesting robot.

## Concept (first thoughts)

A module that straddles one ridge, with a camera or a sensor that detects spear tips breaking the plastic or soil, a narrow cutting and gripping tool on a vertical axis that goes into the ridge, and a crate on the robot. The robot creeps along the ridge.

## Reuse from existing implements

Vertical axis and drill head layout of the dockweed drill; camera hood of the potato disease scout; crate carrier deck for the harvested spears.

## Open questions

- Detecting spears before they reach the light
- Cut depth and closing the ridge again
- Cycle time per spear versus the robot's speed
- Working under the plastic film

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the robot catalogue (F:/side_projecten/Agbots_website): a function that other robots do and the Bruut has no implement or idea for yet.
