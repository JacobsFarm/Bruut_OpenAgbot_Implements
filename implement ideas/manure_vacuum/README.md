# Manure vacuum collector

**Status: idea, not worked out yet.** Category: Livestock & Farm.

## What it does

Sucks fresh manure from a solid barn floor into a tank and empties it at a drain or pit, instead of pushing it. Seen on the Lely Discovery Collector, Hetwin Avenger Pickup, Schauer Enro Collect and JOZ Barn-E.

## Concept (first thoughts)

A low tank on the upper beams, a vacuum pump and a wide suction nozzle with a rubber squeegee at the front. The robot drives a fixed route through the barn and drives to a dump point, where a valve at the bottom of the tank opens.

## Reuse from existing implements

Nozzle and fan or pump layout of the debris vacuum; route driving and squeegee of the push blade (slurry scraping); mobile refiller docking for the dump point.

## Open questions

- Vacuum pump type that handles slurry with straw
- Tank volume versus mass and the floor's grip
- Navigation in a barn with cows (no RTK under the roof)
- Emptying point and cleaning

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the robot catalogue (F:/side_projecten/Agbots_website): a function that other robots do and the Bruut has no implement or idea for yet.
