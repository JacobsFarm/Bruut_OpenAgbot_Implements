# Three-point hitch

**Status: idea, not worked out yet.** Category: Transport & General.

## What it does

Standard lifting system for attaching various agricultural implements.

## Concept (first thoughts)

A scaled-down (category 0 or 1) three-point linkage with lift arms, driven by a linear actuator or hydraulic cylinder. It would let standard compact-tractor implements hang on the robot instead of making each lift frame by hand.

## Reuse from existing implements

Lift frame with actuator and slotted hole of the liquid fertilizer applicator and overseeder.

## Open questions

- Category 0 or 1, lifting force and stroke
- Rear versus front mounting
- Weight limit imposed by the robot's axle loads
- Electric versus hydraulic lift

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the attachments list of the website (functionality's.json).
