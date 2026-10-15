# Solar panels

**Status: idea, not worked out yet.** Category: Power & Drive.

## What it does

Integrated panels to extend battery life and provide sustainable power during operation.

## Concept (first thoughts)

Panels on a flat or slightly tilted roof frame above the top plate, wired through a solar charge controller to the 48 V bus. The roof is also a mounting plane for antennas and cameras, so the GNSS antenna position must stay clear.

## Reuse from existing implements

Top-plate pattern of the robot; antenna positions of the other implements.

## Open questions

- Panel area that fits the robot's width
- Energy yield per day versus consumption
- Shadow of implements, mast and antenna
- Wind load and mounting

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the attachments list of the website (functionality's.json).
