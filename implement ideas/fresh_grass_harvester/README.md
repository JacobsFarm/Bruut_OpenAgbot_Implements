# Fresh grass harvester (zero grazing)

**Status: idea, not worked out yet.** Category: Livestock & Farm.

## What it does

Mows fresh grass in the field, loads it and brings it to the feed fence, several times a day. Seen on the Lely Exos.

## Concept (first thoughts)

A front sickle bar or disc mower, a short pick-up belt or auger that lifts the swath into a container on the robot, and an unloading floor or tipping container at the feed fence. Small loads, many trips.

## Reuse from existing implements

Sickle bar mower; belt rake for the pick-up; dumper barrow or bag trailer for the container; feed pusher route at the barn.

## Open questions

- Load per trip versus mass and the field's bearing capacity
- Pick-up of fresh, heavy grass
- Unloading at the feed fence
- Trips per day for a given number of cows

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the robot catalogue (F:/side_projecten/Agbots_website): a function that other robots do and the Bruut has no implement or idea for yet.
