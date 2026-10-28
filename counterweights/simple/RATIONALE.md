# Counterweights (simple): why they are built this way

## Why a separate implement

The grassland harrow, the inter-row hoe, the three-point hitch and the fertilizer spreader all hang behind the robot and
take weight off the front axle; the push blade does the same to the rear axle. Each of them called for "the 2 x 20 kg
blocks of the disc brushes". This makes those blocks a system: the same stack front and rear, in small steps, so the
ballast can be matched to the implement.

## Plates of 11 kg

- 170 x 200 x 50 steel, 11 kg with the slots and the grip: one person lifts one from the ground onto a beam at 674 mm
  without a hoist (estimated limit for frequent lifting 15 kg). Four plates per stack, two stacks per end: 0..99 kg per
  axle end including the bases.
- Open slots from the outer edge: a plate slides onto the two M16 studs from the side, it never has to be lifted over
  the studs. A clamp bar and two knob nuts hold the stack; no tools.

## Where

- On the two lower cross beams at each end, between the GNSS dome (x +-75) and the steering plates of the front units
  (x 295): x 100..280, y 400..600. The rear is the mirror image (the rear units have no steering stack, the frame bolts
  at x 315..435 stay clear).
- Base plate 15 mm with 4 countersunk M10 into the hole grid (x 125 and 275) and O32 holes over the nuts of the push
  blade / rear toolbar hanger bolts (x 175 and 225): ballast and a toolbar fit at the same time.
- The stack top with 4 plates is at 921 mm; the GNSS dome (top 740) loses sky low to the sides with more than one plate
  front. For RTK work with a full front stack, put the antenna on the mast of the crate carrier.

## What each implement needs (front axle >= 20 %, rear axle >= 25 %)

| Implement (lifted) | Without | Plates per stack | With |
| --- | --- | --- | --- |
| Grassland harrow | front 15 % | 1 front (33 kg) | 25 % |
| Inter-row hoe | front 5 % | 2 front (55 kg) | 21 % |
| Three-point hitch + cultivator | front 19 % | 1 front (33 kg) | 29 % |
| Fertilizer spreader, full | front 13 % | 1 front (33 kg) | 22 % |
| Push blade | rear 15 % | 1 rear (33 kg) | rear 25 % |

## Estimated, not measured

- Robot mass 160 kg and its centre of gravity midway between the axles
- Least axle shares: 20 % front to steer, 25 % rear for traction with a front tool
- Single-person lift limit 15 kg
- Implement masses copied from their own models (update `IMPLEMENTS` when those change)
