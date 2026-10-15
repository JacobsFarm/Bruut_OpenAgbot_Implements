# Irrigation pump (direct pump)

**Status: idea, not worked out yet.** Category: Spraying, Fertilizing & Irrigation.

## What it does

Pumping water from ditches for local irrigation or crop spraying (website: Irrigation Pump). In the repo this is the not-yet-worked-out variant "direct pump" of the irrigation implement: pump on the robot, water from a tank, a ditch or a hydrant.

## Concept (first thoughts)

Instead of a petrol pump staying at the ditch, a pump on the robot feeds a hose or a short boom directly. Water comes from a tank on a trailer or a hydrant at the field edge.

## Reuse from existing implements

Reel, pinch rollers and outlets of irrigation/stationary + roller; the mobile refiller for tank supply.

## Open questions

- Pump mass on the robot versus pump at the ditch
- Hose or boom as distributor
- Water supply: tank, hydrant or ditch
- Comparison of energy and capacity with the stationary-pump variant

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the attachments list of the website (functionality's.json).
