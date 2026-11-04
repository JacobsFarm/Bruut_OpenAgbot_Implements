# Drone combination (simple): why it is built like this

## Platform above everything

The steering stacks reach z 1032 and the GNSS dome sits on the front beam, so a flat landing area can only be above
them: the plate is at z 1100 on 4 posts that stand between the inner and outer upper beam of each side, on cross bars
bolted into the grid holes at y +-325. 1 m square leaves ~0.3 m around a Mavic-class drone.

## Passive centring, not a mechanism

RTK plus a visual tag brings a drone down within ~0.1 m. The PE wedges along the edges catch anything up to ~0.25 m
off and slide the skids into the flat zone over the charging strips. No motors, nothing to freeze; corners are left
open for the GNSS post.

## Charging, not battery swap

A swap station (gripper, battery magazine) is the advanced variant. A 77 Wh drone battery charges in ~1 h from the
robot (4.6 % of its 1.9 kWh), which fits a day of alternate scouting (~97 ha per flight) and working. Magnets under the
strips hold the drone: 7.6 N of wind at 12 m/s (the usual flying limit) against ~15 N.

## GNSS antenna moved

An aluminium plate over the robot's antenna would block most of the sky. The antenna goes on a 150 mm post on a
platform corner, outside the landing zone, with the same RTK base.

## Estimated, not measured

- Drone mass, battery, flight time, camera field of view and pixels, landing errors
- Charging power and efficiency, magnet force (20 N), skid friction (0.5), wind area of the drone
- Masses of the GNSS post and the strips
- Not modelled: the contact adapter on the drone, cables, the data link; flight rules (operator in reach or a permit
  for automated flights) are for the user to check
