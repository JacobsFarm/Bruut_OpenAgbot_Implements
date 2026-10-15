# Heavy-duty electric motors

**Status: idea, not worked out yet.** Category: Power & Drive.

## What it does

Electric motors such as the Ego Power+ or Greenworks units to drive implements that need real power, replacing small petrol engines.

## Concept (first thoughts)

A standard interface plate for battery-powered garden-tool motors (their battery or the robot's bus via adapter), with a belt or shaft output to an implement. Gives a ready, cheap drive where a bought motor is easier than a custom 48 V BLDC.

## Reuse from existing implements

Motor plates and V-belt drives of the around-pole mower and the weed picker.

## Open questions

- Which motors: brands, power, output shaft type
- Supply: own battery or the robot's 48 V
- Interface plate and quick-change mounting
- Protection against dust and water

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the attachments list of the website (functionality's.json).
