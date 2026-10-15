# Speech speaker

**Status: idea, not worked out yet.** Category: Transport & General.

## What it does

A speaker on the robot that can speak: warnings when the robot approaches, status messages for the operator, instructions in the field, and a way to speak to people near the robot.

## Concept (first thoughts)

A weatherproof loudspeaker (or a pair, front and rear) on the top plate or mast with a small amplifier, fed by the robot computer. Text-to-speech for messages such as 'robot is turning', 'tank empty' or 'battery low'; optionally a microphone and a radio link so an operator can speak through the robot. Volume follows the distance to detected people.

## Reuse from existing implements

Top-plate pattern and mast mounting of the spot sprayer and the field marker; computer and radio link of the mobile refiller.

## Open questions

- Speaker type, power and IP rating
- Languages and voice (text-to-speech engine, offline)
- Which events trigger which messages
- Noise limits near animals (cows, horses) and neighbours
- Microphone and two-way speech

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: own brainstorm, not on the website list.
