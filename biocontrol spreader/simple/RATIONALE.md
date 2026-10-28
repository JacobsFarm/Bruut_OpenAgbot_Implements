# Biological-control spreader (simple): why it is built this way

## What it spreads

- Predatory mites (*Amblyseius cucumeris*, *A. swirskii*) come in bran or vermiculite, ~50,000 per litre; parasitic
  wasps come as mummies in sawdust. They are spread at 1..100 per m2 over the crop, weekly or after a pest count. By
  hand that is slow and uneven; a blower on the robot puts a constant dose per metre of row, also at night.

## Hoppers, metering, air

- 2 PE hoppers (7.9 l each, cylinder O200 on a 60 degree cone) above the 2 rows of the bed (x +-187.5), with a slow
  agitator so the bran does not bridge and the mites stay spread through it.
- Under each cone a metering wheel (NEMA17, ~4 ml per revolution) drops the carrier into a venturi; a 24 V 60 W
  centrifugal fan on the bearer blows ~8 l/s per hose at ~8 m/s: enough to carry bran, gentle on the mites (no
  impeller in the product path). The hoses end in deflector cones 450 mm above the ground that spread a band of
  ~0.3..0.4 m over each row.
- The dose follows the driving speed: 2 ml/m2 of cucumeris at 0.5 m/s needs only ~5.6 rpm of the wheel, so the same
  unit doses wasp mummies (0.25 ml/m2) as well.

## On the robot

- One bearer across the upper beams at y -60, the hoppers just in front of it on arms and rings, the driver box under
  the bearer between the beams. Everything is between the axles and inside the wheel tracks: no conflict with the
  steered front wheels. 18 kg; it can stay on the robot with the grass meter or the UV-C light.

## Capacity

0.75 m of bed per pass at 0.5 m/s: ~1350 m2 per hour. A fill of 2 x 7.9 l covers ~0.8 ha with cucumeris
(2 ml/m2), ~1.6 ha with swirskii, ~6 ha with wasp mummies. ~160 W in all: ~12 h on a battery charge.

## Estimated, not measured

- Organisms per litre and doses per m2 (label values of common products)
- Metering wheel volume 4 ml per revolution, air speed 8 m/s, band width 0.75 m per pass
- Fan 60 W, metering 15 W per unit, robot mass 160 kg, rolling resistance 0.06
- Survival of the mites in the air stream (to test with a sample on sticky cards)
