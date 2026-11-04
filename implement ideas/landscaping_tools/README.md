# Hedge trimmer, edger and leaf blower

**Status: idea, not worked out yet.** Category: Transport & General.

## What it does

Trims hedges, cuts lawn edges along paths and blows leaves into a windrow, without a gardener walking along. Seen on the Electric Sheep Verdie.

## Concept (first thoughts)

A side arm with two axes that carries a hedge trimmer bar, swapped for an edger disc at ground level, and a separate blower nozzle at the front. The robot follows the hedge or path edge with a camera or a stored RTK line.

## Reuse from existing implements

Arm and swing-out of the around-pole fence mower; following a line of plants of the windbreak and tree-row inspector; garden-tool motors of the heavy-duty electric motors; broom sweeper for picking up the windrow.

## Open questions

- Arm reach and height for hedges
- Detecting the hedge face and the path edge
- Safety of the trimmer bar near people
- Blower power and noise

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the robot catalogue (F:/side_projecten/Agbots_website): a function that other robots do and the Bruut has no implement or idea for yet.
