# Lime spreader (simple) - rationale

## Why a drop spreader, not a spinner

The fertilizer spreader throws granules 4-7 m with a disc. Lime is dosed at 0.5-3 t/ha, ten times fertilizer, and
ground lime is a fine powder: a disc would make a dust cloud and an uneven pattern, and drift onto crops, water or the
neighbours. Dropping it from 0.2 m inside a skirt gives an exact 1.3 m strip with no dust. The robot drives the field
anyway, so the smaller width costs time but not trouble, and the driving lines are RTK-exact (no overlap needed).

## Why the hopper in the middle

A full hopper is ~205 kg, more than the robot. Behind the rear axle (as on the fertilizer spreader) it would lift the
front wheels; centred over the robot it is shared: full, 183 / 280 kg front / rear, no ballast needed. Only the cross
auger (light) sits behind the wheels. The V-hopper goes down between the inner upper beams, which there are free of
the robot (no beams, no wheel units between y -405 and 405).

## Two augers

- **Trough auger** in the bottom of the V: meters the volume, its speed follows the driving speed (and a task map).
  Flights O100 pitch 100 at 45 % fill move 0.32 l per turn: 8-34 rpm for 500-2000 kg/ha, so a 60 rpm gearmotor has
  room up to ~3.5 t/ha.
- **Cross auger**: spreads the flow over the width. Flights from the middle to both ends push the lime along; each O20
  hole lets out about the same share while the tube is filled. Its speed is fixed (well above the trough auger), so it
  never fills up and the dose stays set by the trough auger.
- Damp ground lime bridges in a hopper: the walls are 51-57 degrees and the trough auger runs the full length, so it
  draws from the whole bottom. An agitator shaft is an option for the advanced variant.

## Weight and driving

Full, 463 kg on 4 hub motors: rolling resistance on tilled soil (~0.08) takes 363 N of the 1100 N continuous, so ~9
degrees uphill remain. Tipping sideways at 32 degrees (static) because the lime sits low between the beams.

## Estimated, not measured

- Bulk density of lime (granulated 1.15, ground dry 1.0, damp 1.25 kg/l), angle of repose
- Filling of the auger flights (45 %), material factor of the screw (4), idle power per auger (15 W)
- Even flow from the 25 outlet holes over the width (needs a test; hole size or a slide plate per section can correct it)
- Rolling resistance on tilled soil (0.08), robot mass (160 kg) and centre of gravity, usable battery energy (1.9 kWh)
- Gearmotor mass (3.5 kg each) and size
- Not modelled: slide plate under the holes, agitator, hinges and latch of the lid, fill-level sensor
