# Fertilizer spreader (simple): why it is built this way

## Spinning disc, not row drop tubes

The robot works grassland and wide fields: a disc spreads 4..7 m from a 0.85 m wide robot, so one pass covers several
robot widths and the robot drives less. Row drop tubes are more precise but would need a boom as wide as the work.
Variable rate comes from the metering roller, not from the disc, so it stays simple.

## Hopper over and behind the rear axle

- The disc must be behind the robot (otherwise it throws into the wheels) and the granules must fall from the outlet
  onto the disc without a long flat chute (fertilizer needs walls of more than ~40 degrees). So the outlet sits behind the
  rear lower beams and the funnel walls run at 46..57 degrees.
- The hopper rides on two rails on top of the upper beams, which run back past the beam ends. That puts the full
  hopper (130 kg) at y -834: the rear axle takes almost all of it and the front keeps only 13 %. The optional front
  counterweight (2 x 20 kg, same blocks as the disc brushes) brings that to 24 %. With an empty hopper it is 33 %.
- 25 mm spacers lift the rails over the nuts of the rear wheel units (x 325 / 425, y -425 / -575); the rail bolts sit
  between them (y -625, -500, -250).

## Metering

- Fluted roller O80 x 120 with 10 flutes: 196 ml per turn at 85 % filling. At 1 m/s and 5.4 m driving width,
  100..500 kg/ha needs 17..83 rpm, within a 100 rpm gearmotor. The roller speed follows the driving speed from the
  robot (same idea as the cam rollers of the overseeder), so the dose per hectare stays the same when the robot slows
  down, and a task map changes it per zone.
- The drop point is 35 mm in front of the disc centre; moving it (slot in the chute) shifts the pattern to the sides.

## Disc and width

- Exit speed = 1.3 x tip speed (radial plus tangential, slip on the vanes). A 3.5 mm granule (1500 kg/m3) launched
  horizontally from 0.5 m with quadratic air drag lands 2.0..3.3 m from the disc centre at 500..900 rpm.
- Driving width = 50 % of the throw width for a triangular pattern with full overlap (estimated; should be checked
  with a tray test).
- Spinner power is small (74 W at 300 kg/ha, 151 W at 900 rpm): a 300 W 48 V BLDC motor runs directly from the
  robot battery.
- The guard covers the front half (15..165 degrees) so nothing hits the robot or the tyres. The two legs of the
  spinner frame stand behind the disc at x = +-345 and catch a small part of the throw to the rear corners; moving
  them further out is an option for the advanced variant.

## Estimated, not measured

- Robot mass 160 kg, centre of gravity (y 0, z 450), side tipping static only
- Fertilizer bulk density 1.0 kg/l, granule size 3.5 mm and particle density 1500 kg/m3, drag coefficient 0.44
- Exit speed factor 1.3, flute filling 0.85, overlap 50 %
- Gearmotor 0.6 kg, spinner motor 3.2 kg; PE density 0.96
