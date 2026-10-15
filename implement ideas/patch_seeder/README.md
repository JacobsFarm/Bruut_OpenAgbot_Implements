# Patch seeder

**Status: idea, not worked out yet.** Category: Sowing & Planting.

## What it does

Compact seeder that spreads grass seed onto bare patches in the sward, so damaged spots close up again quickly.

## Concept (first thoughts)

A small hopper with a short spreader over a scratching or raking element, switched on only above bare patches that a camera finds (as the spot sprayer finds docks). Seed is dosed per patch, not per hectare.

## Reuse from existing implements

Camera detection of the spot sprayer; seed hopper and metering of the overseeder; rake tines of the belt rake.

## Open questions

- Patch detection: bare soil in grass
- Seed dose per patch and spreading width
- Seed-to-soil contact: rake, roll or press
- Combined with the overseeder or separate?

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the attachments list of the website (functionality's.json).
