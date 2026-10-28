# Soil sampler (simple): why it is built this way

## In the middle of the robot

The push force comes from the robot weight. With the probe at (0, -60), almost on the centre of gravity, all four
wheels stay loaded and the robot does not tip or lift a wheel. 70 % of robot + sampler weight (1318 N) is used as the
limit. Behind the robot (like the field marker) the lever over the rear axle would lift the front wheels long before that.

## Gouge probe, 0-10 cm

Dutch practice for grassland is 40 cores of 0-10 cm per plot (one composite sample); arable land is 0-30 cm. A O25
gouge with a O19 core needs 0.5..0.8 kN for 0-10 cm grass and ~1 kN for 0-20 cm compact arable soil (cone resistance on
the annular tip plus side friction). 0-30 cm in dry soil approaches the 1.3 kN limit and needs a longer mast: that is the
arable variant (`depth_arable`), not drawn here.

## Ball screw instead of a linear actuator

A 24 V linear actuator with 760 mm stroke is long (retracted ~900 mm) and slow (~10 mm/s). A ball screw with a NEMA23
gives 75 mm/s, holds its position for the force check (current), and the motor stands on top of the mast. At the force
limit the screw needs 1.17 Nm; a 2.2 Nm NEMA23 gives about 1.3 Nm at 900 rpm.

## Core handling

- The ejector rod runs inside the probe and pushes the core out at the top of the stroke; the swing chute sits under the
  tip only then, and swings 90 degrees aside while the probe goes down.
- Park height 560 mm is set by the chute: it must run at >45 degrees from under the tip to the funnel over the cups.
- The carousel stands far enough back (centre y -380) that the foot passes the index cup; 10 cups of 1.3 l fit inside
  the wheel brackets (x < 261) and hold 40 cores each (1.13 l, 88 % full).

## Sprung foot

The foot touches the turf 40 mm before the tip: it senses the ground (switch on the rods) so the depth is measured from
the surface, not from the robot, and it holds the sod down when the gouge comes out.

## Estimated, not measured

- Robot mass 160 kg
- Cone resistance 1.0..3.0 MPa, side friction 20 kPa, dry bulk density 1300 kg/m3
- NEMA23 torque at 900 rpm 1.3 Nm, ball screw efficiency 0.90
- Time per core: 2 s settle, 3 s eject, 15 m driving at 1 m/s between cores
- Masses of the motors, servo and cups
