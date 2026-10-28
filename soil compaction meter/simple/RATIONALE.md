# Soil compaction meter (simple): why it is built this way

## A cone penetrometer on the soil sampler's Z axis

- Soil compaction is measured as cone resistance (MPa) over depth. By hand that is slow, tiring and uneven (the push
  speed changes the reading). The robot pushes at a constant 30 mm/s (the ASABE S313 speed) and logs force and depth
  with a GNSS position, so a field gets a dense, repeatable map per depth layer.
- The mechanics are those of the [soil sampler](../../soil%20sampler/simple/): 2 bridges on the inner upper beams, a
  mast plate on the front bridge, 2 SBR20 rails, a SFU1605 ball screw and a NEMA23. The mast is longer (z 120..1150)
  for 600 mm depth, and 2 flat stays to the rear bridge take the push reaction off the bridge bolts.
- In the middle of the robot the whole weight is the reaction: 70 % of it (1320 N) is used, so the wheels stay loaded.

## Cone, rod, load cell

- ASABE small cone (30 degrees, O12.83, 1.29 cm2) on a O9.5 rod: 1320 N measures up to 10.2 MPa, far above the ~3 MPa
  where roots stop (388 N). The large cone (3.23 cm2) would reach only 4 MPa with the robot weight.
- An S-type 2 kN load cell between the holder and the rod clamp reads the force directly (no screw friction in the
  reading); 80 Hz at 30 mm/s is a reading every 0.4 mm.
- The rod has 700 mm free length: clamped at the top and guided at the ground by a PTFE bush in the foot ring, its
  buckling load (3.3 kN) is well over the push force. A guide bush on the mast was tried first, but the foot has to pass
  it on its way down.

## Foot and moisture

- The sprung foot (PE ring O140 on 2 rods) touches the ground first: that height is depth zero, so tall grass or
  ruts do not shift the profile. It also holds the sod while the rod comes out.
- Cone resistance rises strongly as soil dries, so a map is only comparable at known moisture. A capacitive probe on
  the foot ring reads the topsoil moisture at every point.

## Capacity

One profile to 600 mm takes 35 s (20 s measuring). On a 50 x 50 m grid (4 points per ha) at 1.2 m/s the robot does
~47 points per hour, ~12 ha per hour; ~2.5 Wh per point, ~750 points per battery. A denser grid (e.g. a tramline
study) is simply more points.

## Estimated, not measured

- Robot mass 160 kg; share of the weight used as push force 0.7
- NEMA23 torque 1.3 Nm at 75 mm/s, 2.0 Nm at 30 mm/s; ball screw efficiency 0.9
- Axis power 80 W while pushing, rolling resistance 0.06, settle time 3 s
- Grid density 4 points per ha
