# Laser or UV weed treatment

**Status: idea, not worked out yet.** Category: Weed & Crop Protection.

## What it does

Kills individual weeds with a laser or a focused UV beam, without chemicals and without moving the soil.

## Concept (first thoughts)

Camera finds the weeds (as in the spot sprayer), a galvo mirror aims the beam at the growing point. Needs a shroud against stray light and an interlock, and mostly works on small seedlings.

## Reuse from existing implements

Camera mast and detection of the spot sprayer; shroud and safety interlock ideas of the weeds burner.

## Open questions

- Laser class and the safety rules that follow
- Power needed per weed and dwell time
- Working width versus galvo scan area
- Cost compared with a spot sprayer

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
