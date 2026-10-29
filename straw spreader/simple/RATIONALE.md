# Straw spreader (simple) - rationale

## Bales, not loose straw

Loose straw is bulky (~30 kg/m3) and bridges in any bin; a small bale is 3 x denser, holds its shape, and one person
lifts it (13 kg) onto the slats at 880 mm. The drum only has to tear the face of the bale loose, not chop it: the
straw comes off as a loose mat that falls well through a wide chute. Long straw does not block a metering opening,
because there is none: the dose is set by how fast the floor moves the bale into the drum.

## Floor chain and drum

- The floor moves 1-3 mm/s; a 24 V gearmotor on the front shaft and the robot's speed signal set it.
- The drum turns at a fixed 250 rpm (tip 4.2 m/s): fast enough to pull straw out, slow enough not to throw it far.
  The housing keeps it inside, the chute takes it down.
- The top bale sinks onto the slats when the bottom one is used up; the drum (z 900-1220) reaches both.

## Where the straw goes

The robot straddles 2 rows; the middle inter-row (x 0) is the free one. The outlet is 160 mm wide and 300 mm above
the ground: the straw spreads to ~200 mm and lies between the rows without covering the plants. Below 400 mm the chute
stays within x +-105 (`check_rows()`).

## Dose and refilling

0.5 kg/m2 of strip is ~4 cm of loose straw, enough against weeds. That is 0.1 kg per m of strip: 2 bales cover
260 m, ~9 minutes of work. Refilling is the main work; a larger bale rack or a trailer with bales behind the robot is
the next step (advanced). Mulching with a separate machine that lays a bale at a time is the alternative.

## Weight

The chamber, drum and housing make the empty spreader ~100 kg, 64 % on the rear axle loaded; the high load (cg 705 mm)
limits side slopes to 28 degrees static. Aluminium walls and chute and a 3 mm housing keep it within that.

## Estimated, not measured

- Bale size and mass (460 x 360 x 880, 13 kg), density ~89 kg/m3
- Energy to tear straw loose (5.4 kJ/kg = 1.5 kWh/t), drum idle power (100 W), drum efficiency (0.8)
- Strip width on the ground (0.20 m) and mulch doses (0.3-0.8 kg/m2)
- Rolling resistance (0.08), robot mass (160 kg) and centre of gravity, battery energy (1.9 kWh)
- Motor masses (drum 9 kg, floor 2.5 kg)
- Not modelled: chain tensioner, slats on the return strand, bale retaining bar, guard over the floor-chain drive
