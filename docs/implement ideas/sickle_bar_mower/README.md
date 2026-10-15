# Sickle bar mower

**Status: idea, not worked out yet.** Category: Mowing.

## What it does

Mowing at various heights, including 'topping' plants above ground level.

## Concept (first thoughts)

A bought double-knife or single-knife cutter bar on a parallel linkage in front of the robot, with a 48 V motor and a crank drive. Height by an actuator, a float link lets it follow the ground. The weed picker already tops weeds with rotors; the bar gives a clean cut with low power.

## Reuse from existing implements

Parallel linkage, actuator, float link and 48 V drive of the weed picker (weed picker/mowing_deck).

## Open questions

- Bar length (robot width or wider)
- Power per metre in grass and in thick weeds
- Cut-material handling: left in swath or gathered
- Stone and molehill protection (breakaway)

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the attachments list of the website (functionality's.json).
