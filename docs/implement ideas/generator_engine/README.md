# Generator / engine

**Status: idea, not worked out yet.** Category: Power & Drive.

## What it does

Generator or combustion engine mounted between the frame as an auxiliary power source for extra electricity or mechanical power.

## Concept (first thoughts)

A small generator (range extender) on a vibration-damped frame between the beams, charging the 48 V bus. Exhaust and fuel placement are the main design problems.

## Reuse from existing implements

Frame mounting like the battery pack; the irrigation petrol pump is another engine use.

## Open questions

- Generator power class and mass
- Vibration isolation and noise
- Fuel tank and exhaust placement
- Charging strategy with the battery

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the attachments list of the website (functionality's.json).
