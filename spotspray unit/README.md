# Spot sprayer for the Bruut

Sprays weeds **plant by plant** instead of the whole field. A camera in front of the robot finds the weeds; a boom
behind it opens only the nozzles above a plant, for just as long as the plant is under them. In grassland with
scattered broad-leaved dock, thistle or nettle (a few % of the area) that saves 90–95 % of the herbicide compared with
blanket spraying, and the grass and clover between the weeds are not touched.

| | Variant | Contents |
| --- | --- | --- |
| [Folding boom 3.75 m](boom/README.md) | `boom/` | FreeCAD model: camera on a mast at the front, 120 l tank on the robot, 3.75 m boom behind it with 15 PWM nozzles at 250 mm; centre section 1.25 m, two 1.25 m wings that fold up in the field with a 24 V actuator each. Calculations (camera footprint, latency, dose, fold force, axle loads), animation with docks and a fence post, parts list (≈ €3,580); why: [RATIONALE](boom/RATIONALE.md) |

![the spot sprayer on the robot](boom/previews/1_work_iso_on_robot.png)

![animation: spot spraying dock, the right wing folds for a post](boom/previews/animation_spot_spraying.gif)

## Concept

1. **See ahead.** One wide-angle global-shutter camera, 1.48 m high on a mast at the front, looks at the strip
   ahead. The image is wider than the boom from 1.8 m ahead of the robot; a plant is seen in about 60 frames.
2. **Carry the position.** The plant's position on the ground goes with wheel odometry (and the IMU / GNSS heading) to
   the boom 2.6–5.6 m further back: 2.65 s at 1 m/s, much more than the ≈ 135 ms that detection and the valve need.
3. **Spray the spot.** Every nozzle has its own PWM solenoid valve; a 40° flat fan 400 mm above the ground sprays a
   strip of 250 mm. The nozzles open 50 mm before the plant and close 50 mm after it.
4. **Fold for obstacles.** Each wing folds up in 3.2 s for a post, a tree or a gate and comes down behind it; the
   strip it misses is logged.
5. **Log.** Every spot with its position, time, nozzle and litres: a weed map of the field, and next year a check of
   where the dock came back.

## Requirements

| | |
| --- | --- |
| Robot | standard Bruut OpenAgbot, bolted to the hole grid of the beams; nothing drilled |
| Working width | 3.75 m, 15 nozzles at 250 mm; centre 1.25 m fixed, 2 wings of 1.25 m that fold in and out in the field |
| Camera | at the front, watches the whole boom width |
| Tank | on the robot |
| Speed | 1 m/s (≈ 1.1 ha/h net) |

## Options for later

| Option | What it adds |
| --- | --- |
| Air-induction tips or a shroud per nozzle | less drift on windy days |
| Two products | a second, small tank and a second wet pipe (e.g. one herbicide for dock, one for thistle) |
| Breakaway in the wings | spring-loaded joint at the hinge for an obstacle that was not on the map and not seen |
| LED flash under the camera | work at dusk and at night, independent of shadows |
| Spot fertilising / liming | the same boom with a fertiliser in place of a herbicide, on patches from a yield or soil map |
| Mobile refiller | tops up the tank in the headland turn ([mobile refiller](../mobile%20refiller/)) |
