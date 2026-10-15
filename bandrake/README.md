# Belt rake (band rake) for the Bruut

A belt rake moves everything on the surface **sideways into one windrow**: a rubber belt with tine bars runs around
two drums, and on the bottom run the tines comb the surface and carry it to one end. On the Bruut it is electric and
sits in front of the robot.

| | Variant | Contents |
| --- | --- | --- |
| [Electric, 1.5 m](electric/README.md) | `electric/` | FreeCAD model: drums Ø220 1,160 mm apart, belt 260 mm with 15 tine bars (3 double spring tines each), 48 V 750 W gearmotor on the drive drum, swath board, two swivel castors on 24 V actuators (depth and headland lift), free parallelogram on the front of the robot. Calculations (belt path, working width, comb lines, tine forces, drive, side force, axle loads, windrow), animation in grassland, parts list (≈ €2,380); why: [RATIONALE](electric/RATIONALE.md) |

![the belt rake on the robot](electric/previews/1_work_iso_on_robot.png)

![animation: raking moss and thatch into one windrow](electric/previews/animation_raking_windrow.gif)

## Uses

1. **Nursery beds with small trees.** The tines comb 10 mm deep between the young trees and pull out fine weed
   seedlings with their roots; the woody trees bend the spring tines aside. Done often, it keeps the beds weed-free
   without herbicides.
2. **Grassland before overseeding.** After scarifying (or on a sward full of moss and dead grass) the rake takes out
   the litter so that the seed reaches the soil. The robot works from the outside of the field inwards with the
   windrow always on the inside: every pass carries the previous windrow along, so it ends as **one small windrow**.
3. **Hay and silage.** Small windrows of real hay or grass for silage, on plots too small or too wet for a tractor.

## Requirements

| | |
| --- | --- |
| Robot | standard Bruut OpenAgbot; mount plate under the front beams, nothing drilled |
| Drive | electric, from the robot's 48 V battery |
| Position | in front of or behind the robot (chosen: in front, see RATIONALE) |
| Width | ≈ 1.5 m (twice the robot's track) |

## Options for later

| Option | What it adds |
| --- | --- |
| Reversible belt | windrow to the left or the right: work back and forth instead of round the field |
| Swivel locks on the castors | the castors take the side force in work, unlocked for the headland |
| Cover over the top run | protection against thrown stones and for people near the robot |
| Second rake in tandem | 3 m: grassland and hay at twice the capacity (the castors carry the weight) |
| Pick-up behind | a small loader wagon or baler that picks up the windrow (another robot) |
