# Precision applicator + roller pump on the Bruut OpenAgbot

The two parts of the precision liquid applicator put together on the standard robot (`agbots/agbot design`):

- the **roller pump** (`../roller_pump/`, 5 sections, one per row) on two 40 × 40 cross tubes over the robot's
  upper beams, outlets towards the rear;
- the **applicator** (`../applicator/`, 5 discs + injector knives at 200 mm) behind the rear wheels on its
  **parallel linkage with an electric actuator**, clamped on the rear lower beam;
- five **hoses** (8 × 12), pump channel *i* to knife *i*, over the rear beam and the headstock, down behind the
  knives onto the bent tube ends. They bend along when the applicator is lifted.

No tank yet: the 1" manifold of the pump is still open at the front.

![overview](previews/1_iso_rear_right.png)

![animation](previews/animation_inject_strip.gif)

## Files

| File | Contents |
| --- | --- |
| `Precision_Applicator_on_robot.FCStd/.step` | the combination in working position (generated, do not edit by hand) |
| `cmb_params.py` | placement of the pump, pump mount, hose route (robot coordinates) |
| `cmb_parts.py` | pump mount tubes, hose ends at pump and knife, hose path (centripetal Catmull-Rom, no loops) |
| `build_cmb.py` | loads the robot, pump and applicator from their folders, builds the tree, `set_lift()`, `check_fit()`, `check_lift()`, clearances, axle loads, images, STEP |
| `animate_cmb.py` | animation: lower, inject a strip with the pump following the speed, lift; `play()`, `stop()`, `summary()`, `render_all(folder)` |
| `make_gif_cmb.py` | frames to GIF with caption and a "knife depth / pump speed" panel |
| `run_in_freecad.py` | macro: run in FreeCAD (F6) to rebuild and print the key figures |
| `previews/` | images and the GIF |

Nothing is copied: `build_cmb.setup_path()` puts `agbots/agbot design`, `roller_pump`, `applicator` and
`applicator/parts/injector_knife` on `sys.path`. Change a part in its own folder and rebuild here.

## Model tree

```
Robot (App::Part, agbot design)
  Chassis, RL/RR/FL/FR_unit          robot
  Pump_mount                         pump_mount_tubes
  Roller_pump                        from build_rp (5 sections), Rotor turns
  pa_Precision_applicator            from build_pa, all names with "pa_"; pa_Implement moves when lifting
  Hoses                              hose_0 ... hose_4
```

## Axes

Robot coordinates: x = right, y = driving direction (front = +y), z = up, ground = z 0, origin = robot centre.
Pump: pump y 0 at robot y −390, on z 739 (top of the mount tubes). Applicator: shaft at robot y −1000
(425 behind the rear lower beam).

## Key figures

| | |
| --- | --- |
| Clearance to the rear tyres | discs 132.5, front cross tube 96.4, side shields 94.9 mm |
| Headstock to rear wheel unit | 151 mm |
| Interference | none in working position (robot, pump, applicator, mount, hoses); lifted 150: hoses free of the applicator and of each other; applicator moving parts checked at −40, 0, 75, 150 in `../applicator` |
| Hoses | 1306 … 1488 mm, 77 mm slack gained when lifted (they never stretch) |
| Added mass | applicator 59.0 kg (centre of gravity at robot y −938), pump about 16 kg |
| Axle loads | with the applicator lifted: rear axle +99 kg, front axle −24 kg (lighter) |
| Animation | 9.5 s, 5.25 m; lowering 1.75 s; pump 45 rpm at 0.75 m/s = 500 l/ha (10.2 ml per metre per row); 131 ml in 2.56 m |

## Animation

The robot stands with the applicator lifted, drives off while the actuator lowers it (discs and knives enter the
soil, a slot appears behind each knife), injects with the pump running in step with the speed (blue strip = liquid),
lifts again at the end of the strip and stops. Panel: knife depth and pump speed against time.

## Usage

```python
import build_cmb
build_cmb.build()                 # rebuild and save
build_cmb.set_lift(150)           # applicator lifted, hoses follow
build_cmb.check_fit()             # overlap between robot, pump, applicator, mount and hoses (takes ~20 min)
build_cmb.clearance()
```

```python
import animate_cmb
animate_cmb.build()
animate_cmb.play()                # animate_cmb.stop()
animate_cmb.summary()
animate_cmb.render_all(r"C:\temp\cmb_frames")
import make_gif_cmb; make_gif_cmb.main(r"C:\temp\cmb_frames", r"previews\animation_inject_strip.gif")
```

Long runs (`check_fit`, `render_all`) take longer than the MCP time-out: start them with `QtCore.QTimer.singleShot`
and write the result to a file.
