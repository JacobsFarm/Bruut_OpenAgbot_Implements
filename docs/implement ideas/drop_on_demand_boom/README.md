# Drop-on-demand boom (coarse droplets)

**Status: idea, not worked out yet.** Category: Soil Cultivation & Weed Control.

## What it does

Boom with individually controlled injectors that fire single coarse droplets on demand at low pressure. Every droplet is placed straight onto the weed, which practically eliminates drift and cuts chemical usage to a fraction of a conventional spray pass.

## Concept (first thoughts)

Same carrier as the spot sprayer (camera mast in front, boom behind), but with drop-on-demand valves instead of PWM flat-fan nozzles. Droplets are fired at the detected plant position, so the boom needs a finer position resolution along the boom than 250 mm.

## Reuse from existing implements

Camera mast, tank, pump, folding boom and control box of the spot sprayer (spotspray unit/boom).

## Open questions

- Injector type, droplet size and firing rate
- Injector pitch along the boom
- Aiming accuracy at 0.5 m/s: time from camera to droplet
- Product types and viscosity the injectors can handle

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the attachments list of the website (functionality's.json).
