# Asparagus harvester - rationale

## Straddling one ridge

The track (750 mm, tyre inner faces at x +-325) fits one ridge of 600 mm base: the wheels run in the furrows and the
ridge top (z 400) passes 179 mm under the belly rails. The robot is light (~205 kg with the module), so it does not
press the ridge sides in.

## A tall Z axis through the robot

The tool must go 220 mm into the ridge and come out above it: a stroke far longer than the space under the belly.
At y 0 nothing blocks the vertical between x +-300 (the lower beams are at |y| 405-595, the upper beams at |x| 305-445),
so the Z profile stands up through the robot to 1.45 m and its lower end stays 30 mm above the ridge. The X axis
(+-120 mm) covers the ridge top width (260 mm).

## Cycle and capacity

Between spears the tool only lifts 250 mm over the ridge (3.5 s per spear); every ~15 spears it goes to the top and
empties its bin into the crate. With ~3 spears per metre per day the robot does ~270 m/h: ~21 h for a hectare. That is
the honest limit of a single tool: a field needs several robots or a second tool head on the same gantry. Harvest runs
day and night (LED light in the hood), so ~0.5-1 ha per robot is realistic.

## Plastic film (open)

White asparagus is grown under film. This model works on an open ridge: the film must be folded back for the run, or
a next variant lifts it with front rollers over a guide sheet. The Z axis would then need a gap in the film's path;
that is not solved here.

## Estimated, not measured

- Spears per metre per harvest day (3), spear mass (25 g)
- Axis speeds (Z 0.5 m/s, X 0.3 m/s), grip and cut time 1.2 s, travel time between spears
- Power (250 W for drive, axes and computer)
- Crate packing (45 %)
- Detection of tips before they reach the light (camera + line laser): not tested
