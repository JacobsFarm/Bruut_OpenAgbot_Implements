# Bag trailer (simple): why it is built this way

## A trailer, not more on the robot

- The top of the robot is rated at ~150 kg (estimated). Twelve 25 kg bags of seed, fertilizer or feed (300 kg) are
  twice that, and stacked on the robot they would sit high. On a trailer the load rides low (deck at 358 mm) and only
  ~24 kg (6 %) rests on the ball.
- The 50 mm tow ball, the coupling head, the drawbar, the braces and the parking leg are those of the
  [cambridge roll](../../overseeding/cambridge%20roll/): `build_bgt` imports `build_cbr`, so the hitch is the same
  model and the trailer fits every robot that has it. The trailer frame uses the roll frame's arm section (40 x 40 at
  x +-515..555, z 300..340) so the cbr braces meet it where they meet the roll frame.

## Frame, deck, wheels

- 2 side rails and 4 cross members 40 x 40 x 3, an 18 mm plywood deck 1110 x 1410, side and front boards 280 high and a
  drop tailgate: bags are taken off at the back by hand or slid off the tailgate.
- An axle tube 50 x 50 under the rails on 2 hanger plates, spindles O30 and 4.00-8 wheels (O400) outside the deck with
  mudguards. The axle is 90 mm behind the loaded cg, so the trailer stays nose-heavy also when empty (135 N).
- Yawed +-75 degrees and pitched +-8 degrees about the ball nothing touches the robot or the hitch.

## Pull and slopes (the limit)

- On flat dry grass robot and loaded trailer need ~420 N: margin 2.6 on the robot's grip. On wet grass the margin is
  1.65 on the flat, but the 4 hub motors and the robot's grip limit the slope: 3.5 degrees wet, 6.5 dry, 9.5 on
  concrete with 300 kg. On sloping fields carry half the bags.
- The trailer has no brakes. Downhill (8 degrees) the robot holds it with its own grip in all three cases, but the
  route planner should keep the speed low and avoid steeper slopes when loaded.

## Estimated, not measured

- Robot mass 160 kg; payload of 12 bags of 25 kg
- Rolling resistance of robot and trailer, grip coefficients on wet / dry grass and concrete
- Hub motors 4 x 55 Nm continuous, loaded radius 0.20 m
- Plywood density 650 kg/m3, tyre mass from a 35 % fill of the solid
