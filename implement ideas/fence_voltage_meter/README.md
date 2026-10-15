# Fence voltage meter

**Status: idea, not worked out yet.** Category: Measuring & Sensors.

## What it does

Measures the voltage and current of the electric fence while driving along it and maps where the voltage drops.

## Concept (first thoughts)

A contactless sensor (capacitive or inductive) on the arm near the wire, with a GPS log per metre. Can ride on the fence mower arm.

## Reuse from existing implements

Arm and post-following geometry of the around-pole fence mower.

## Open questions

- Contactless versus contact sensing
- Calibration to a known voltage
- Reporting threshold and alarms

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
