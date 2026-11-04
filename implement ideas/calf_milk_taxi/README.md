# Calf milk taxi

**Status: idea, not worked out yet.** Category: Livestock & Farm.

## What it does

Brings warm milk to the calves in their hutches or pens and doses each calf's portion, so the farmer does not have to carry buckets. Inspired by the automatic calf feeders such as the Lely Calm.

## Concept (first thoughts)

An insulated milk tank with a heater and a stirrer on the upper beams, a pump and a dosing nozzle on a short arm at the side. The robot drives along the hutches on a stored route and stops at each one to dose the set amount into the bucket.

## Reuse from existing implements

Tank and pump of the liquid fertilizer applicator; flow dosing of the mobile refiller; stop-and-dose positioning of the field marker.

## Open questions

- Hygiene: cleaning the tank, pump and hoses after every round
- Keeping the milk at drinking temperature
- Dose per calf and identifying the calf or hutch
- Mixing milk powder on board or filling from a calf milk kitchen

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the robot catalogue (F:/side_projecten/Agbots_website): a function that other robots do and the Bruut has no implement or idea for yet.
