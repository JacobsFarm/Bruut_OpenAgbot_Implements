# Drinking trough check

**Status: idea, not worked out yet.** Category: Livestock & Farm.

## What it does

Visits drinking troughs, measures the water level, tops it up and reports dirt or damage with a camera.

## Concept (first thoughts)

A mast with a level sensor, a camera and a small refill nozzle on a hose; the robot parks at stored trough positions. Water from a tank on the robot or a nearby tap.

## Reuse from existing implements

Nozzle and docking approach of the mobile refiller (simple); camera mast.

## Open questions

- Level sensing: ultrasonic or float
- Water supply and tank size
- Frost and winter use
- Cleaning: only reporting or also scrubbing

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
