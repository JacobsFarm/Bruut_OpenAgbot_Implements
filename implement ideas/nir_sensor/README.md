# NIR sensor (NDVI & crop status)

**Status: idea, not worked out yet.** Category: Measuring & Sensors.

## What it does

Near-infrared sensor that measures the NDVI of the crop while driving. From the difference between reflected red and near-infrared light the robot reads biomass, ground cover and crop vitality, and builds live task maps for variable-rate fertilisation. Because the sensor moves close over the crop instead of looking down from a satellite, the readings stay reliable under cloud cover and also register small spots and gaps.

## Concept (first thoughts)

Two-band (red and near-infrared) sensor or a multispectral camera on a mast above the crop, with active illumination or a reference panel against sun angle. NDVI is logged per GNSS position and turned into a task map.

## Reuse from existing implements

Mast and mounting of the spot sprayer camera; task-map output feeds the fertilizer spreader and liquid applicator.

## Open questions

- Active versus passive sensor, sensor height
- Sun-angle and shadow correction
- Calibration of NDVI to nitrogen need
- Task-map format and update rate

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the attachments list of the website (functionality's.json).
