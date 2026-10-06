# Simple liquid fertilizer applicator (renure): FreeCAD model

A cheap, robust variant of the applicator in [`../advanced`](../advanced/README.md), for the Bruut OpenAgbot.
- 5 fixed injection knives at 200 mm, each with a stainless steel tube behind it.
- Two wheelbarrow wheels hold the depth.
- A lift frame with a single low pivot floats while working; one cheap linear actuator lifts it.
- A 12 V diaphragm pump with a fixed pressure regulator and orifice plates does the dosing.
- Only flat bar, tube and standard off-the-shelf parts; about € 600 in materials.

Ground following is slightly worse than with the advanced variant, and the dose depends on the driving speed. Why it is
designed this way and what you give up is explained in [RATIONALE.md](RATIONALE.md).

**Version 2** adds a cutting disc in front of the knife in each row: [`../simple_v2`](../simple_v2/README.md).

![overview](previews/1_iso_rear_right.png)

![animation: behind the robot over a bumpy strip](previews/animation_strip_ground_following.gif)

## Files

| File | Contents |
| --- | --- |
| `Liquid_Fertilizer_Applicator_Simple.FCStd` | the model in working position (generated, do not edit by hand) |
| `lfs_params.py` | all dimensions, including the robot interface |
| `lfs_kin.py` | kinematics: pivot, slotted hole, floating range, lift angle, knife (pure Python) |
| `lfs_parts.py` | one function per part, returns a `Part` shape |
| `build_lfs.py` | model tree, colors, lifting, interference check, mass, images |
| `lfs_calc.py` | dosing, forces on the lift frame, shear bolt, lifting, axle load, cost (pure Python) |
| `lfs_ground.py` | ground following over the bumpy strip, same ground as the advanced variant (pure Python) |
| `plot_ground.py` | comparison chart of ground following, simple vs advanced (matplotlib) |
| `ground_advanced_reference.json` | knife depth per frame of the advanced variant (from `../advanced/animate_lfa.py`) |
| `animate_lfs.py` | animation: robot + applicator over the strip |
| `make_gif_lfs.py` | frames to GIF with a caption and a "knife depth per row" panel (Pillow, included with FreeCAD) |
| `run_in_freecad.py` | macro: open in FreeCAD and run (F6) to rebuild the model |
| `previews/` | images, the comparison chart and the GIF |

All module names start with `lfs_`, so that they do not clash with the `lfa_` modules of the advanced variant in the
same FreeCAD session.

## Axes

Same as the robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
- y = 0 is the centre of the robot's rear lower beam, so robot y = implement y − 575.
- Rows at x = −400, −200, 0, 200, 400; depth wheels at x = ±300.
- Pivot of the lift frame at (y, z) = (−70, 200).
- Lift angle `psi` in degrees; + = rear up.

## Rebuilding and using

In FreeCAD's Python console (folder in `sys.path`, or via `run_in_freecad.py`):

```python
import build_lfs, lfs_kin
build_lfs.build()                                   # working position, saves the FCStd
build_lfs.build(psi=lfs_kin.lift_angle(), save_path=None, show_robot=True)   # lifted, with the robot reference
build_lfs.check_interference()                      # list of overlapping parts (must be empty)
build_lfs.mass_properties()                         # mass and centres of gravity
build_lfs.render_all()                              # images 1 to 11 in previews/ and save in working position
```

Without FreeCAD (any Python 3; `plot_ground.py` needs matplotlib):

```bash
python lfs_calc.py
```

```bash
python lfs_ground.py
```

```bash
python plot_ground.py
```

- `lfs_calc.py` gives the key figures and the dosing table.
- `lfs_ground.py` gives the range of the knife depth, the floating angle and the stops.
- `plot_ground.py` creates `previews/12_ground_following_comparison.png`.

## Animation

Builds a separate document `LFS_on_robot_animation` with:
- the robot model from `agbot design` (those files are not modified);
- the applicator behind it;
- the same wavy ground as in the advanced animation.

```python
import animate_lfs
animate_lfs.build()                     # build the document
animate_lfs.play()                      # play live, animate_lfs.stop()
animate_lfs.check_fit()                 # overlap with the real robot model (must be empty)
animate_lfs.render_frames(r"C:\temp\lfs_frames", 0, 60)   # render in chunks of ~60 frames
import make_gif_lfs
make_gif_lfs.main(r"C:\temp\lfs_frames", r"previews\animation_strip_ground_following.gif")
```

Driving plan, actuator speed and ground are at the top of `lfs_ground.py`: `SPEED`, `ACT_SPEED`, `BUMPS`, `RIDGES`.

## Model tree

```
liquid_fertilizer_applicator_simple
  headstock_robot_mount          headstock (fixed): top plate, clamp strip, 4 cheeks, slotted-hole plates, bolts
  dosing_unit_on_headstock       pump, filter + camlock, pressure regulator + gauge, manifold, connecting hoses
  lift_actuator                  housing (pin on the lift frame) + rod (eye in the slotted hole) + 2 pins
  outlet_hoses_flex_with_lift    5 hoses from the manifold to the nozzle holders
  swing_frame_moves_with_lift    (Placement = rotation about the pivot bolts)
    toolbar, frame_arms, cross_tube_with_actuator_lugs
    injection_knife_1..5         holder, U-bolts, knife, pivot and shear bolt, tube, P-clips, nozzle holder
    gauge_wheel_left / right     clamp plate, U-bolts, sleeve, stem, adjusting pin, fork, axle, wheel
robot_reference_NOT_PART_OF_DESIGN   (hidden; rear beams, upper beams, rear wheels)
```

## Estimated, not measured

- **Draft force per knife**: 125 N, heavy sward 250 N.
- **Downward force on the knife tip**: 30 % of the draft force.
- **Discharge coefficient of the orifice plates**: 0.65 (to be calibrated).
- **Robot weight and centre of gravity**: `lfs_calc.ROBOT`, same as the advanced variant.
- **Robot traction**: μ = 0.5.
- **Actuator speed and prices**: typical values from datasheets and web shops.

See RATIONALE § 5 to § 8.

Ground following is calculated quasi-statically:
- the robot rests rigidly on four wheels;
- the lift frame rests on the highest depth wheel;
- dynamics, slip and floating up under draft force are not in the animation. Floating up is in `lfs_calc`.
