# Biostimulant sprayer (full field)

**Status: idea, not worked out yet.** Category: Spraying, Fertilizing & Irrigation.

## What it does

Sprays biostimulants over the whole field at the right moment: compost tea, seaweed extract, or nitrogen-fixing products such as Corteva's Utrisha N (Blue N). It needs no plant-by-plant precision, but every pass is logged, so it is clear what was applied where and when.

## Concept (first thoughts)

100 to 200 l/ha is little to carry: a tank on the robot with the boom of the spot sprayer with all nozzles open. The main part is the record keeping: a log per pass with product, rate, time, weather and GPS track, to compare treated and untreated strips afterwards.

## Reuse from existing implements

Folding boom, tank and pump of the spot sprayer; tank and pump of the liquid fertilizer applicator.

## Open questions

- Nozzles and filtering for compost tea (particles, living organisms)
- Tank size versus field size
- Log format and registration
- Timing: weather and crop stage

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
