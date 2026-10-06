# Simple liquid fertilizer applicator version 2 (disc + knife): FreeCAD model

Version 2 of the [simple applicator](../simple/README.md), with a cutting disc in front of the knife in each row.
- A flat coulter disc Ø 300 cuts the sward 45 mm deep.
- The knife runs 14 mm behind it in the same plane, opens the cut, and the stainless steel tube places the liquid in it.
- Everything else is the same as version 1: headstock with a low pivot, floating lift frame with actuator and slotted hole, two wheelbarrow wheels as depth wheels, 12 V diaphragm pump with orifice plates.
- About € 915 in materials.

What the discs cost:
- 26 kg extra on the lift frame (70 kg);
- a 1500 N actuator;
- up to 50 kg of ballast for down force in hard sward.

See [RATIONALE.md](RATIONALE.md).

![overview](previews/1_iso_rear_right.png)

![animation: behind the robot over a bumpy strip](previews/animation_strip_ground_following.gif)

## Files

| File | Contents |
| --- | --- |
| `Liquid_Fertilizer_Applicator_Simple_v2.FCStd` | the model in working position (generated, do not edit by hand) |
| `lfs2_params.py` | all dimensions, including disc, hub, disc arm and robot interface |
| `lfs2_kin.py` | kinematics: pivot, slotted hole, floating range, lift angle, knife, knife–disc gap (pure Python) |
| `lfs2_parts.py` | one function per part, returns a `Part` shape |
| `build_lfs2.py` | model tree, colors, lifting, interference check, mass, images |
| `lfs2_calc.py` | dosing, down force and ballast, shear bolt, lifting, axle load, cost (pure Python) |
| `lfs2_ground.py` | ground following over the bumpy strip: cut, knife depth (pure Python) |
| `plot_ground2.py` | comparison chart with v1 and the advanced variant (matplotlib) |
| `ground_advanced_reference.json` / `ground_simple_v1_reference.json` | knife depth of the advanced variant and of v1 at the same positions |
| `animate_lfs2.py` | animation: robot + applicator over the strip |
| `make_gif_lfs2.py` | frames to GIF with a caption and a "knife depth and cut per row" panel |
| `run_in_freecad.py` | macro: open in FreeCAD and run (F6) to rebuild the model |
| `previews/` | images, the comparison chart and the GIF |

The module names start with `lfs2_`. This way v1 (`lfs_`), v2 and the advanced variant (`lfa_`) can be loaded in the
same FreeCAD session.

## Axes

Same as the robot model and version 1: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
- y = 0 is the centre of the robot's rear lower beam (robot y = implement y − 575).
- Rows at x = −400, −200, 0, 200, 400; depth wheels at x = ±300.
- Disc centre at (y, z) = (−320, 105); knife tip at (−461, −40); pivot of the lift frame at (−70, 200).

## Rebuilding and using

In FreeCAD's Python console (folder in `sys.path`, or via `run_in_freecad.py`):

```python
import build_lfs2, lfs2_kin
build_lfs2.build()                                  # working position, saves the FCStd
build_lfs2.build(psi=lfs2_kin.lift_angle(), save_path=None, show_robot=True)   # lifted, with the robot reference
build_lfs2.check_interference()                     # overlapping parts (must be empty)
build_lfs2.mass_properties()                        # mass and centres of gravity
build_lfs2.render_all()                             # images 1 to 11 and save in working position
```

Without FreeCAD (any Python 3; `plot_ground2.py` needs matplotlib):

```bash
python lfs2_calc.py
```

```bash
python lfs2_ground.py
```

```bash
python plot_ground2.py
```

## Animation

```python
import animate_lfs2
animate_lfs2.build()                    # build the document LFS2_on_robot_animation
animate_lfs2.play()                     # play live, animate_lfs2.stop()
animate_lfs2.check_fit()                # overlap with the real robot model (must be empty)
animate_lfs2.render_frames(r"C:\temp\lfs2_frames", 0, 60)   # render in chunks of ~60 frames
import make_gif_lfs2
make_gif_lfs2.main(r"C:\temp\lfs2_frames", r"previews\animation_strip_ground_following.gif")
```

## Model tree

```
liquid_fertilizer_applicator_simple_v2
  headstock_robot_mount          headstock (fixed): top plate, clamp strip, 4 cheeks, slotted-hole plates, bolts
  dosing_unit_on_headstock       pump, filter + camlock, pressure regulator + gauge, manifold, connecting hoses
  lift_actuator                  housing (pin on the lift frame) + rod (eye in the slotted hole) + 2 pins
  outlet_hoses_flex_with_lift    5 hoses from the manifold to the nozzle holders
  swing_frame_moves_with_lift    (Placement = rotation about the pivot bolts)
    toolbar, frame_arms, cross_tube_with_actuator_lugs
    disc_and_knife_1..5          base plate, disc arm, axle bolt, bearing hub, disc, side plates, U-bolts, knife,
                                 pivot and shear bolt, tube, P-clips, nozzle holder
    gauge_wheel_left / right     clamp plate, U-bolts, sleeve, stem, adjusting pin, fork, axle, wheel
robot_reference_NOT_PART_OF_DESIGN   (hidden; rear beams, upper beams, rear wheels)
```

## Estimated, not measured

- **Down force per disc**: 100 N, hard sward 200 N.
- **Draft force**: disc 30–50 N, knife in the cut 60–125 N.
- **Downward force on the knife tip**: 30 % of the draft force of the knife.
- **Discharge coefficient of the orifice plates**: 0.65.
- **Robot**: weight, centre of gravity and traction as in v1.
- **Actuator speed and prices**: typical values.

Ground following is calculated quasi-statically, just like in v1. Floating up through too little down force is in
`lfs2_calc`, not in the animation.
