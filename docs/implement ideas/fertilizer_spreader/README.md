# Fertilizer spreader

**Status: idea, not worked out yet.** Category: Spraying, Fertilizing & Irrigation.

## What it does

Precise application and spreading of granular fertilizers.

## Concept (first thoughts)

A hopper with a metering roller and a spreading disc or a drop tube per row. Dose follows the driving speed (as with the overseeder's cam rollers) and can follow a task map from the crop scanner for variable-rate application.

## Reuse from existing implements

Metering rollers and speed-following motors of the overseeder; granular loading from the mobile refiller concept.

## Open questions

- Spreading disc versus row drop tubes
- Working width and edge spreading accuracy
- Hopper size versus robot axle load
- Variable-rate from a task map: update rate

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the attachments list of the website (functionality's.json).
