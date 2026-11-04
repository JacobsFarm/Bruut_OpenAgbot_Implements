# Fresh grass harvester - rationale

## Small loads, many trips

Fresh grass is bulky (~200 kg/m3 loose) and the robot is small: a 0.41 m3 container holds ~73 kg. With a 300 m trip
that is ~11 minutes and ~92 Wh per load, so a charge gives ~1.3 t of grass: enough for ~20 cows as their main feed,
or more as a supplement. A larger herd needs several robots (swarm) or a shorter distance.

## Sickle bar, cross auger, elevator

A sickle bar needs little power (~300 W/m) and leaves the grass whole, which suits fresh feeding. The auger behind it
gathers the swath to one side; a slatted belt lifts it into the container. The elevator runs outside the right front
wheel, because the middle of the front is taken by the GNSS dome and the steering stacks. The belt (~2 m/s) throws the
grass over a short spout: a longer spout over the container would be in the container's way when it tips.

## Tipping to the left

The container hinges on the left edge and tips 55 degrees to the left: the right side (with the elevator) stays clear,
and the robot unloads with its left side along the feed fence. The tipping frame sits 6 mm over the bolt heads of the
cross tubes.

## Balance

Cutter bar, auger and elevator put ~135 kg in front of and to the right of the robot centre. With the container over
the front, 78 % of the empty weight was on the front axle. The container moved back (y -820..80, on cross tubes at
y -625 and -375) and a 60 kg block hangs behind the rear cross tube: 57 % front empty, 51 % full. The front right
wheel carries the most (~154 kg).

## Estimated, not measured

- Bulk density of fresh cut grass in the container (200 kg/m3), grass yield 1.5 t DM/ha at 18 % DM
- Power of the sickle bar (300 W/m), auger (150 W), elevator (200 W), drive (300 W)
- Trip distance (300 m), road speed 1.5 m/s, unloading 2 min
- Fresh grass per cow per day (60 kg)
- Motor and actuator masses
