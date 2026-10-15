# Swarm operation (multiple robots per field)

**Status: idea, not worked out yet.** Category: Cooperation & Swarm Operation.

## What it does

Several Bruut units work the same field as one swarm. The job is split into sections, the robots divide the passes among themselves and keep each other informed of position, progress and battery state, so they never overlap or cross. Capacity scales simply with the number of units instead of with machine size, work continues when one unit drops out, and the light platforms keep soil compaction low.

## Concept (first thoughts)

Mostly software: a job planner that splits the field into passes, shared position and progress messages over a radio link, collision avoidance by reserved corridors, and hand-over of a pass when one unit drops out. The mobile refiller already works with a working robot, which is a two-unit special case.

## Reuse from existing implements

The pass pattern of the mobile refiller (simple) and the headland-turn animations of the agbot slim.

## Open questions

- Communication link and message set
- Pass allocation and re-allocation
- Collision and crossing rules
- Charging and refilling logistics for many units

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the attachments list of the website (functionality's.json).
