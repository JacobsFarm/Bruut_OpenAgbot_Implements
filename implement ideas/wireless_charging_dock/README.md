# Wireless charging dock

**Status: idea, not worked out yet.** Category: Power & Drive.

## What it does

A fixed docking station at the field edge or in the shed where the robot drives up and charges, either with contacts or wirelessly.

## Concept (first thoughts)

A drive-on plate with an inductive coil or contact bars, a guide for alignment, and an RTK-assisted approach. The robot parks over the coil.

## Reuse from existing implements

Docking alignment of the mobile refiller; solar panel idea as the power source.

## Open questions

- Wireless versus contact charging
- Power and efficiency
- Weatherproofing
- Alignment tolerance

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
