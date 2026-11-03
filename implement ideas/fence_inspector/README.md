# Fence inspector

**Status: idea, not worked out yet.** Category: Livestock & Farm.

## What it does

Drives along the fence, measures the voltage of the electric fence per metre, reports breaks, shorts and where the voltage drops, and straightens leaning posts.

## Concept (first thoughts)

A contactless (capacitive or inductive) or contact sensor on an arm along the wire to measure voltage and current with a GPS log per metre, a camera for posts and a simple push or pull tool for leaning posts. Reports the position of every fault. The sensor can also ride on the fence mower arm.

## Reuse from existing implements

Around-pole fence mower arm and post-following geometry.

## Open questions

- Contactless versus contact sensing, calibration to a known voltage
- How to straighten a post without damage
- Fault classification: break, short, vegetation
- Reporting to the farmer: map, push message, alarm threshold

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
