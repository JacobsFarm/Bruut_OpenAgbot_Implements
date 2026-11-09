# Soil scanner (simple): why it is built this way

## Source

The idea comes from an Interra Scan presentation (webinar "Aanpak veldemissies in de regio Foodvalley", November
2026; Syngenta / SoilOptix): the scanner is mounted on a Gator 60 cm above the ground, measures 4 isotopes (Cs, U,
K, Th) over a lane width of 10 m and makes ~800 data points per ha in blocks of 10 x 1.2 m. The data go to SoilOptix
(Canada) and are combined with calibration samples (Eurofins): at least 4 per field and 2 per ha. The photo shows a
black tube with blue end caps across the front of the vehicle. Vendor data of a comparable vehicle sensor (Medusa
MS-2000): CsI 2 l (90 x 310 mm), 12 kg, up to 5 Hz.

## A passive sensor on a light robot

- The sensor only counts: no contact with the soil, no draught force, no actuator. It suits the robot well: the
  robot drives the lanes on RTK, at a constant 1.2 m/s, day or night, on the same lines every year.
- 1 spectrum per second at 1.2 m/s gives exactly the 1.2 m blocks of the presentation; 10 m lanes give 833 points
  per ha.

## Height 600 mm, in front of the robot

- The calculation (`ssc_calc.footprint`) integrates the uncollided flux of a uniform soil under a detector at height
  h. At 0.6 m half the counts come from within ~1.1 m and 90 % from within ~4.6 m: a lane 10 m wide is covered
  (+-5 m) with only a little overlap. Lower (0.3 m) sees only +-2.4 m: gaps between 10 m lanes; higher (1 m) blurs
  over 7 m. So 600 mm, as on the Gator.
- In front of the front wheels: no shielding by the robot's steel, battery and hub motors under the crystal, and
  above the tyres (crystal axis z 600, tube bottom z 500, tyre top z 480) so the steering is free. Across the robot so
  the long crystal is along the lane width.
- Mounted on the front outer lower beam at x +-175: between the GNSS dome (x +-75) and the steered stack (x ~251 at
  30 degrees). The grid holes of that beam are at x +-25 + 50 k, so the bolts are at +-125 and +-225.

## Crystal and housing

- CsI(Tl) instead of NaI: more robust (not hygroscopic, less brittle), higher density, better efficiency for a small
  crystal; that is what SoilOptix uses.
- 4 l (100 x 100 x 400): count statistics decide. Sandy soils (much of the Dutch arable land) have little K, U and Th;
  with 4 l a 1.2 m block in sand still has ~29 counts in the K window (+-19 %), with 2 l +-26 %. The full-spectrum
  analysis of the processor and the calibration samples smooth that over neighbouring blocks; for a sharper map in
  sand the robot can simply drive slower (0.35 m/s for 10 %).
- The crystal is sensitive to shock and fast temperature changes: foam sleeve, rubber mounts (4 x O30) and EPDM
  liners, a guard tube in front. The photomultiplier and MCA board sit in the same sealed tube; only one cable goes
  to the processor box.

## Calibration samples with the soil sampler

The scan says where the field differs; the calibration samples tie the counts to lab values. The soil sampler in the
middle of the robot (its own bridges on the upper beams, no clash with the scanner) can take them in the same job:
after the scan the robot drives to the sample points and takes ~10 cores per point. For 18 ha: 36 samples, ~1.6 h.

## Axle load

45 kg at y ~850 moves the CG 187 mm forward: 69 % on the front axle. Acceptable on firm ground (all 4 wheels drive);
on soft soil a rear [counterweight](../../counterweights/) evens it out. A lighter bracket (6 mm plate) saves ~4 kg.

## Estimated, not measured

- Robot mass 160 kg
- Detector internals: PMT 0.8 kg, MCA board 0.35 kg, processor box 2.4 kg, foam density 50 kg/m3
- Sensitivities per litre of CsI at 0.6 m (12 cps/%K, 1.2 cps/ppm eU, 0.55 cps/ppm eTh; from portable 0.35 l NaI
  figures scaled by volume and x1.3 for CsI)
- K, U, Th contents of the soil types (sand 0.6 % / 0.8 / 2.5 ppm, loess 1.6 / 2.2 / 9, clay 2.2 / 2.8 / 11)
- Soil bulk density 1.45 g/cm3, water 0.20 g/g; the footprint model counts only uncollided gammas (scattered
  gammas widen the footprint and make the depth a bit larger, up to ~30 cm in the literature)
- Power: detector 12 W, processor + GNSS + 4G 15 W; rolling resistance 0.06, drive efficiency 0.75
- Calibration: 10 cores per sample, 9 s per core
- The pH field in the animation is synthetic
