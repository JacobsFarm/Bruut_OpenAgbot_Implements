# Liquid fertilizer applicator (renure): FreeCAD model

Stand-alone implement for the Bruut OpenAgbot: 5 injection elements (disc + knife + tube) at 200 mm, one ground wheel
that drives a 5-channel peristaltic pump, and an electrically lifted parallel linkage that floats while working
(slotted hole).
Why it is designed this way is explained in [RATIONALE.md](RATIONALE.md).

![overview](previews/1_iso_rear_right.png)

![animation: behind the robot over a bumpy strip](previews/animation_strip_ground_following.gif)

## Files

| File | Contents |
| --- | --- |
| `Liquid_Fertilizer_Applicator.FCStd` | the model in working position (generated, do not edit by hand) |
| `lfa_params.py` | all dimensions, including the robot interface |
| `lfa_parts.py` | one function per part, returns a `Part` shape |
| `build_lfa.py` | model tree, colors, lifting, interference check, mass, images |
| `lfa_calc.py` | dosing, spring, down force, floating position, actuator, axle load (pure Python) |
| `animate_lfa.py` | animation: robot + applicator over a bumpy strip, ground following per frame |
| `make_gif_lfa.py` | frames to GIF with a caption and a "ground following" panel (Pillow, included with FreeCAD) |
| `run_in_freecad.py` | macro: open in FreeCAD and run (F6) to rebuild the model |
| `previews/` | images and the GIF |

## Axes

Same as the robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
y = 0 is the centre of the robot's rear lower beam, so robot y = implement y − 575.
Rows at x = −400, −200, 0, 200, 400; ground wheel at x = 312.

## Rebuilding and using

In FreeCAD's Python console (folder in `sys.path`, or via `run_in_freecad.py`):

```python
import build_lfa
build_lfa.build()                       # working position, saves the FCStd
build_lfa.build(lift=140, save_path=None, show_robot=True)   # lifted, with the robot reference
build_lfa.check_interference()          # list of overlapping parts (must be empty)
build_lfa.mass_properties()             # mass and centres of gravity
build_lfa.render_all()                  # all images in previews/ and save in working position
```

```python
import lfa_calc
lfa_calc.report()                       # key figures
lfa_calc.dose_table()                   # dosing per sprocket / hose
```

## Animation

Builds a separate document `LFA_on_robot_animation`: the robot model from `agbot design` (those files are not
modified), the applicator behind it and a wavy ground with bumps, pits and a ridge.

Per frame:
- the robot rests on its four wheels;
- the toolbar floats until the ground carries its weight;
- each element and the ground wheel find their own arm angle;
- spring legs, hoses and slots move along.

```python
import animate_lfa
animate_lfa.build()                     # build the document
animate_lfa.play()                      # play live, animate_lfa.stop()
animate_lfa.summary()                   # range of toolbar, spring travel, knife depth, stops
animate_lfa.render_frames(r"C:\temp\lfa_frames", 0, 30)   # render in chunks of ~30 frames
import make_gif_lfa
make_gif_lfa.main(r"C:\temp\lfa_frames", r"previews\animation_strip_ground_following.gif")
```

Driving plan, terrain and camera are at the top of `animate_lfa.py` (`SPEED`, `BUMPS`, `RIDGES`, `CAM_HIGH`, `CAM_LOW`).

## Model tree

```
liquid_fertilizer_applicator
  headstock_robot_mount        mounting headstock (fixed to the robot)
  parallel_linkage             4 rods (rotate about the front pins)
  lift_actuator                housing (on the rear frame) + rod (pin in the slotted hole of the headstock)
  toolbar_assembly_moves_with_lift   (Placement = lift movement)
    toolbar, rear frame
    ground_wheel_drive_and_pump
      ground_wheel_arm_swing   (rotates about the pump axis)
    injection_unit_1..5
      unit_n_swing_arm         (rotates about the pivot)
    outlet_hoses
robot_reference_NOT_PART_OF_DESIGN   (hidden; rear beam, upper beams, rear wheels)
```

## Estimated, not measured

Robot weight and centre of gravity (`lfa_calc.ROBOT`), spring rate 4 N/mm, ground wheel down force 150 N, pump
volumetric efficiency 0.85, ground wheel circumference 1.19 m, required down force in the sward. See RATIONALE § 6 and § 7.
In the animation the robot rests rigidly on four wheels (a plane through the wheel contact points) and the toolbar is in
force equilibrium (weight = ground forces); dynamics and slip are not included.
