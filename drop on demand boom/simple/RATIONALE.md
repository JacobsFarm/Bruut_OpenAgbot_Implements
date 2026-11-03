# Drop-on-demand boom (simple) - rationale

## Why a hood under the belly and not a boom behind

The idea list proposed the spot sprayer's camera mast in front and a boom behind. With drop-on-demand the drop must
land within a few mm of a weed of 15-70 mm, so the distance from the image to the injector matters:

- **Mast in front, boom behind** (spot sprayer): ~1.7 m between the camera band and the nozzles. At 0.5 % odometry
  error that is ~8 mm, plus pitch and steering between the two; and outside a hood the wind blows a 2 mm drop falling
  400 mm several cm aside.
- **Hood under the belly**: camera and injectors in one rigid box, 465 mm apart: ~2.3 mm odometry error, no wind, one
  height above the ground for both (the hood hangs between the 4 wheels, so it follows the bed like the robot does).
  The constant LED light gives the same image day and night and allows a 0.1 ms exposure (no motion blur).

The price is the width: between the wheels there is room for 0.6 m (the inner tyre faces are at x +-325, a steered
front tyre comes to x ~224 at y ~339). That fits one bed of row crops (lettuce, onion, carrots, beet) on a bed system
where the robot straddles the bed. A wider machine would be the boom behind, with its own hoods (advanced variant).

## Drops instead of a fan

- **5 ul, O2.1 mm**: large enough to fall straight and not drift, small enough that 1-7 drops cover a weed seedling.
  Typical drop-on-demand weeders use drops of a few ul to ~10 ul.
- **0.5 bar, 1 m/s exit, 80 mm fall**: impact at 1.6 m/s, Weber number ~76, below the ~100 where drops shatter and
  splash onto the crop. At 1 bar / 2.5 m/s / 100 mm the impact was 2.9 m/s (Weber 242): too hard, so the pressure and
  the height were brought down.
- **25 mm pitch, 25 mm along**: a grid of 25 x 25 mm. The smallest weed hit for sure is ~25 mm; smaller seedlings get
  the nearest drop and are hit by 50 %. 25 mm pitch is also what the O14 injector bodies allow side by side.
- **Fired 31 mm early**: the drop keeps the forward speed of the robot during its 62 ms fall, so the controller fires
  that much before the tip is over the target.
- **Crop keep-out 40 mm**: no drop is fired within the leaves of a lettuce plus 40 mm. Weeds that close to the crop
  are left for the in-row weeder; in the animation 4 of 31 weeds.

## Camera and timing

f = 3.5 mm on the 2/3" sensor of the spot-sprayer camera, 293 mm above the ground: 707 x 591 mm, so the 600 mm bed
fits across with margin and the image ends at y -121, in front of the injector line (y -205): the drops and the wet
leaves are not in the image. A weed is in view for ~15 frames at 20 fps; 2 frames to confirm, 60 ms detection and
10 ms for the driver take 0.17 s of the 0.93 s available, so the speed could go to ~2.7 m/s for the vision. The
firing rate (200 Hz at 25 mm) limits it to ~5 m/s; the robot drives 0.5 m/s in a bed.

## Liquid

At 20 weeds/m2 and 15 ul per weed, ~3 l/ha. The 120 l tank of the spot sprayer is far too big; it is filled to ~30 l
(10 ha), which keeps the axle loads low (rear 50 %). The 3 bar regulator of the spot sprayer stays (bypass return to
the tank keeps the liquid stirred); a second regulator brings it to 0.5 bar at the manifold, and an accumulator
smooths the pressure drop when many injectors fire at once (peak 0.14 l/min). A bleed valve at the far end of the
manifold lets the air out after filling; a recirculation line from there to the tank would keep suspensions mixed
(not modelled).

## Height steps

Pins in 3 holes of the posts (25 mm apart): skirt 35 / 60 / 85 mm. The middle step is for transplanted lettuce in
its first weeks (plants up to ~50 mm high under the brush strip, which bends over them). Higher crops: the high step,
or the crop is past the stage where it needs drop weeding. At the low step the brush tips are 15 mm into the soil.

## Mount

The rails are bolted with 4 x M10 each through the grid holes of the lower beams at x +-225: inside the sub plate of
the spot sprayer (x +-200) and the wheel brackets with their wooden blocks (from x 261). At the rear the bolts pass
through the control-box base plate of the spot sprayer, which gets 4 extra holes. The hood stays 29 mm from a front
tyre at full steering lock (30 degrees) and does not reach the rear tyres (from y -285).

## Estimated, not measured

- Injector: drop volume (5 ul), exit speed at 0.5 bar (1 m/s), open time (1.5 ms), max firing rate (200 Hz),
  timing jitter (1 ms), power at the weed duty cycle (3 W), mass (60 g)
- Weed density (20 per m2), weed sizes (15-70 mm), crop keep-out (40 mm), broadcast rate for comparison (200 l/ha)
- Wheel odometry error (0.5 % of the distance) and detection time (60 ms per frame, Jetson class)
- Splash limit (Weber ~100 on a leaf), no air drag on the drop
- LED power (2 x 24 W), drive power at 0.5 m/s in a bed (300 W), pump duty (25 %), field efficiency (75 %)
- Robot mass (161.5 kg) and centre of gravity, usable battery energy (1.9 kWh)
- Bulk density of the brush strip, masses of the camera, regulators, accumulator and control box
- Not modelled: wiring loom of the injectors, rivet nuts, a recirculation line, rinsing tank, injector heating in cold
