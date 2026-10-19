# Overseeder, simple drop seeder: why it is built like this

## Drop seeder, not a spinner

A spinning disc throws seed 2 … 4 m wide and the edge of the pattern is vague; it cannot seed a 0.5 m patch and stop.
A drop seeder lets the seed fall straight down over a known width, so the start and the end of a patch are sharp
(within the motor start + fall time, which the controller compensates). It is also the cheapest metering there is.

## Electric metering instead of a ground wheel

Garden drop spreaders drive the roller from a wheel. Here a 24 V worm gearmotor drives it, because the point is to
switch per patch: motor on = seed, motor off = nothing. The worm gear is self-locking and the brush strip closes the
gap to the roller, so no seed trickles out when it stops. The motor speed follows the driving speed from the robot,
so the rate per m² stays the same when the robot slows down in a turn.

## Sizes

- **1 m wide**: the same width as the roll and the robot track (rear tyres at x ±375, outer edges ±425); the passes
  match the pattern of the robot.
- **Fluted roller Ø50, 12 flutes 6 × 5 mm**: 288 ml = 101 g per revolution. 35 g/m² at 0.5 m/s needs 10 rpm; a 20 rpm
  gearmotor leaves room up to 0.96 m/s. Finer seed or a lower rate: fewer or smaller flutes (the roller is a cheap
  part to swap).
- **Seed rate 35 g/m²**: lawn repair on bare soil (30 … 50 g/m²). Overseeding a full sward uses 15 … 25 g/m²; the rate
  is a parameter.
- **Hopper 49 l**: 17 kg of seed, enough for 490 m² of bare soil, i.e. a lawn of several thousand m² with 10 % bare
  patches. Larger is possible but the unit gets top-heavy on its small wheels.
- **Drop height 180 mm** (bottom of the roller): fall time 0.19 s. Low enough for little wind drift; the rubber flaps
  shield the curtain down to 60 mm.

## Camera and timing

- The camera on the mast (z 850, 35° down) sees the ground from 0.2 to 2.5 m ahead of the drop line; the analysed
  strip is 0.4 … 1.2 m (sharp, little perspective, wide enough: 870 mm half width at 0.4 m, 500 needed).
- From the command to seed on the ground: motor start 0.15 s + fall 0.19 s = 0.34 s → at 0.5 m/s 170 mm. The controller
  switches on 220 mm before the patch (170 + 50 margin) and off 100 mm before its end (0.29 s × 0.5 m/s − 50). The
  look-ahead of 400 mm is enough up to 1.0 m/s.
- The drawbar is in the image (a 60 mm strip in the middle); the cells behind it are taken from their neighbours.

## Two small wheels behind the drop line

Wheels outside the hopper would make the trailer 1.3 m wide. Inside the hopper width, behind the throat, solid
200 × 50 wheels fit under the sloping rear wall; they run on soil that was just seeded and press it in two tracks, which
does no harm. With the ball they carry the trailer statically determinate.

## One section

A 1 m section seeds the whole strip when any part of it is bare: on narrow patches (0.3 … 0.6 m) about 60 % of the seed
lands on grass (animation of the combination: 63 %). That is still a fraction of blanket seeding: on a lawn with 10 %
bare soil spot seeding uses about 14 % of the seed. Two sections (split roller, two motors, € 40 more) would halve the
seed on grass; the controller already works per cell.

## Cost (estimated)

| Part | € |
| --- | --- |
| Hopper sheet, end plates, lid (laser cut, bent) | 90 |
| Fluted roller, shaft, 2 bearings, coupling | 80 |
| Worm gearmotor 24 V | 35 |
| Camera, small computer, motor driver, DC-DC, box | 120 |
| Wheels, axles, forks, cross bars | 60 |
| Drawbar, braces, coupling head, parking leg | 85 |
| Bolts, cable, brush strip, flaps | 30 |
| **Total** | **≈ 500** |
