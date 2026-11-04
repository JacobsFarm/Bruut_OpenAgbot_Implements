# Precision seeder (single seed)

**Status: idea, not worked out yet.** Category: Sowing & Planting.

## What it does

Sows row crops (beet, maize, vegetables) seed by seed and records the RTK position of every seed, so a later weeding pass can hoe around each plant before it is even visible. Seen on FarmDroid FD20 and Fendt Xaver.

## Concept (first thoughts)

Two to four seeding units on a toolbar behind the robot, each with a small hopper, a vacuum or finger metering disc driven by its own stepper, a coulter and a press wheel. The controller logs each seed drop with the RTK position and time.

## Reuse from existing implements

Toolbar and parallelogram units of the inter-row hoe; metering motor and hopper of the overseeder; position logging and odometry timing of the cauliflower applicator; in-row weeder for the follow-up pass.

## Open questions

- Metering principle (vacuum, finger, cell wheel) per crop
- Accuracy of the logged seed position at the working speed
- Depth control and soil closing
- Row spacing and number of units per pass

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (`simple/`, `advanced/`) with `<p>_params.py`, `<p>_parts.py`,
`build_<p>.py`, `<p>_calc.py`, `README.md` and `RATIONALE.md`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of `implement ideas/` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

Source: the robot catalogue (F:/side_projecten/Agbots_website): a function that other robots do and the Bruut has no implement or idea for yet.
