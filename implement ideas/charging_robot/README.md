# Charging robot (mobile charger)

**Status: idea, not worked out yet.** Category: Power & Drive.

## What it does

A robot on wheels that carries a large battery and charges working robots in the field, so they do not have to return to the shed.

## Concept (first thoughts)

A support robot like the mobile refiller, with a battery pack and a charging plug on a boom or at a fixed side. The working robot docks at a stop point, or charging happens in the headland turn.

## Reuse from existing implements

Docking approach, RTK antenna above the connection and procedure of the mobile refiller; battery pack idea.

## Open questions

- Charging connector and automatic plug-in
- Charging power and time
- Battery capacity on the charger robot
- Wireless versus conductive contact

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
