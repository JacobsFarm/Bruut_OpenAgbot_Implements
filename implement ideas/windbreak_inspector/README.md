# Windbreak and tree-row inspector

**Status: idea, not worked out yet.** Category: Measuring & Sensors.

## What it does

Drives along hedgerows, windbreaks and orchard rows and logs gaps, damage, dead trees and growth with a camera.

## Concept (first thoughts)

A sideways-looking camera pair and a logging unit, producing a tree-by-tree status list with photos.

## Reuse from existing implements

Camera masts of the spot sprayer and yield estimator.

## Open questions

- Image quality in shade and at row ends
- Per-tree identification
- Status classes and reports

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
