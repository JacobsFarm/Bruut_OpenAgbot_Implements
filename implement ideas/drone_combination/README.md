# Drone combination

**Status: idea, not worked out yet.** Category: Cooperation & Swarm Operation.

## What it does

The robot works together with a drone as a mobile base station. The drone flies out from the platform, maps the plot from above and passes its imagery straight to the robot, which converts it into a driving and treatment plan. The drone charges and swaps batteries on the robot, so the pair can keep scouting and working alternately for a full day without anyone coming out to the field.

## Concept (first thoughts)

A landing platform on the robot's top plate with a charging contact or battery-swap mechanism, a data link to the robot computer and a way to align the drone on landing (RTK or visual markers). The plan generation reuses the task-map pipeline of the crop scanner.

## Reuse from existing implements

Top-plate pattern; solar panel roof as an alternative platform; task-map pipeline of the grass meter and NIR sensor.

## Open questions

- Platform size and landing aid
- Charging versus battery swap
- Weather limits for flying and landing
- Regulations for autonomous flights

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the attachments list of the website (functionality's.json).
