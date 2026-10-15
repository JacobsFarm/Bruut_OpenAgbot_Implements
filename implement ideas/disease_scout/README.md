# Disease and pest scout

**Status: idea, not worked out yet.** Category: Measuring & Sensors.

## What it does

Looks at the leaves close up, finds disease and pest damage early and stores a photo per plant with its position.

## Concept (first thoughts)

A camera (RGB or multispectral) on a low mast or sideways arm, with its own light so it works at night. The images feed a classification model; alerts go to the farmer. Combines well with the UV light and the biocontrol spreader.

## Reuse from existing implements

Camera and lighting of the in-row weeder; NIR sensor idea.

## Open questions

- Which diseases and crops to detect
- Training data and model
- Lighting and shading of the camera
- Spot treatment links (UV, spray)

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
