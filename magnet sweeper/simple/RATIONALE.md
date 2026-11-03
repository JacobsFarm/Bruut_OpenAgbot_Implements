# Magnet sweeper (simple): why it is built like this

## Flat magnet, not a roller or an electromagnet

A flat magnet face low over the ground is what commercial magnetic sweepers use: no moving parts and no power while
working, and it works the same on grass, gravel and concrete. An electromagnet of the same reach needs several hundred
watts continuously from the 48 V battery and is heavier (copper + iron); a permanent magnet only needs power for the
17 s release.

## Two rows with opposite poles

A single wide pole face (one row, all north down) gives a strong but **uniform** field: the pull on a soft-iron part
is proportional to the field *gradient*, and under a 1 m x 0.15 m face that is almost zero (the first calculation gave
0.6 T/m and no pick-up at all). Two rows with opposite poles across the driving direction close the flux between them
through the air under the box: the gradient goes to 1.3-2 T/m and the parts are pulled up. More, narrower rows give a
stronger field close to the face but less reach; 2 rows of 100 mm gave the best reach in the comparison (2 x 100,
3 x 66, 4 x 50 mm).

## NdFeB, 10 mm thick, and the skin at 20 mm

Ferrite (Br 0.4 T) of 25-40 mm reached nails at ~30-36 mm with the safety factor of 2: enough on a hard floor but not
for a nail lying in the thatch of a sward. NdFeB N35 (Br 1.17 T) of 10 mm reaches 35-56 mm. The skin is set at
20 mm over the floor (on the castors): parts on a floor are 24 mm from the magnet face, parts 15 mm into the grass
39 mm. Under the poles they are picked up; between the poles (the weakest places across the face) not always, so a
second pass shifted half a pole (50 mm) is advised on a festival field. 20 blocks 100 x 100 x 10 are ~15 kg NdFeB.

The steel back plate (15 mm) closes the flux on the back and works as a mirror; with NdFeB a 15 mm plate partly
saturates, so the model counts the magnet as 1.5x as thick, not 2x.

## Release by lifting the core

A stainless (austenitic, non-magnetic) skin lets the field through and stays smooth. Lifting the core 100 mm drops the
field at the skin from 140 to 20 mT and the pull to 0.1-0.25 x the weight of each part: everything falls off. No
scraper, no moving part outside the box, no wear. The force at the start is the core weight plus the pull on the parts
that sit right on the pole lines; with 75 nails there ~1350 N, so the 3000 N actuator (the same type as the lift
actuator of the broom) has margin for a heavier load. Guide rods, box bolts and clevis pin are stainless, so the magnet
does not pull on them.

## Empty over a flat tray, not lifted

The broom showed that a heavy head lifted on the push-blade arms tips the robot forward without ballast. The magnet
head is 99 kg on the arms, so lifting needs ballast too (4 plates for a short hop; lifted transport is not possible).
The skin is 20 mm over the floor and the skids 12 mm, so a 10 mm high PE tray fits under it: the robot drives over it
in the work pose, the castors stop in front of it, the core goes up and the iron drops in. Lifting is only for kerbs.

## Box in front of the beam

The castors of the broom swivel about y 1200 with 40 mm trail and an O125 wheel: when reversing the wheel swings up to
y ~1302. The box therefore starts at y 1310, held by 2 brackets on the beam. The box is 1100 mm wide (as the push
blade) with the magnet rows 1000 mm; the 4 guide rods stand outside the rows.

## Estimated, not measured

- Magnet model: 2D (long rows, ends not modelled), back plate as a 1.5x mirror, soft-iron parts with a demagnetizing
  factor of 0.4-0.85, saturation 1.6 MA/m; real pick-up should be tested with a few blocks on a plate
- Safety factor 2 to lift a part out of the grass, the depth of a part in the thatch (15 mm)
- Parts that touch the skin on the pole lines with a full load (75) and the load before parts fall off in front (3 kg)
- Iron per ha after a festival (4 kg), extra pick-up width beyond the ends of the rows (25 mm each side)
- Rolling resistance of the robot (0.06) and the castors (0.08) on grass, working speed 1.2 m/s
- Robot mass (160 kg) and centre of gravity, usable battery energy (1.9 kWh), electronics 40 W
- Actuator masses and speeds (3000 N versions), least rear-axle shares (10 % hop, 25 % transport)
- Not modelled: cable of the release actuator, sealing of the lid, the PE glide strip on the magnets, logging of the
  covered area (as the field marker)
