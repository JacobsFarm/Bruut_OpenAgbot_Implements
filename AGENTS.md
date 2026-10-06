# AGENTS.md - implements for the Bruut OpenAgbot

Short guide for an AI agent that creates or modifies implements (tools, brackets, hoods). Each implement is a
parametric FreeCAD model generated from Python scripts, with calculations and an animation on the robot.
The robot itself is in `agbots/` and is only read here.

## Link with FreeCAD

- FreeCAD **1.1**, GUI open, operated via the **FreeCAD MCP addon** (tools `mcp__freecad__*`, mainly `execute_code`).
- `execute_code` does not remember variables between calls: put code in files and `import`/`exec` those.
  Use `sys.dont_write_bytecode = True` (no `__pycache__`).
- Put the implement's folder in `sys.path` and build via `run_in_freecad.py` (reloads the modules and builds).
- First check with `list_documents` which documents are open.

## Folders

```
agbots/agbot design/       robot Bruut_OpenAgbot (standard), see README.md there
agbots/agbot design big/   robot XL (Quinder 16", 60 mm beams)
agbots/agbot comparison/   comparison of the two robots
<implement>/advanced|simple/   per implement a folder per variant (liquid fertilizer applicator, overseeder,
                               feed pusher auger, ...), see below
<implement>/inspiration/   source material, not in git
```

`agbots/` and `inspiration/` are in `.gitignore`. The implement reads the robot model from `agbots/agbot design`
(`AGBOT_FOLDER` in `build_*.py`) and does not modify anything there.
The dockweed drill and the trencher are older single scripts (`*_design.py`, `*_requirements.md`) and do not follow the
layout below.

## Files per implement (single source of truth)

Prefix = short code of the implement (`fpa`, `lfa`, `ova`, ...). Not every variant has all files.

| File | Contents |
| --- | --- |
| `<p>_params.py` | all dimensions, including the robot interface (taken from `agbot_params.py`). Never hardcode dimensions |
| `<p>_parts.py` | one function per part, returns a `Part` shape in local/robot coordinates |
| `build_<p>.py` | model tree (`build()`), `COLOR`, `new_part`, `add_shape`, interference check, mass, `render_all()`, STEP export |
| `<p>_calc.py` | calculations in pure Python (capacity, forces, torque, spring, axle load, ...) |
| `<p>_kin.py`, `<p>_ground.py`, `<p>_feed.py` | kinematics, ground model or process model, if the implement needs it |
| `animate_<p>.py` | animation on the robot: `build()`, `play()`, `stop()`, `summary()`, `render_all(folder)` |
| `make_gif_<p>.py` | frames to GIF with caption and force panel (different name than the robot's `make_gif.py`, because that folder is also on `sys.path`) |
| `run_in_freecad.py` | macro: reload, build, print key figures |
| `README.md`, `RATIONALE.md` | usage and files; why the dimensions and choices are what they are |
| `previews/` | images and GIFs |

- The FCStd (and STEP) is **generated**. So put a new part in `<p>_parts.py` and `build_<p>.py` and rebuild.
  Manually added objects are lost.
- All dimensions are in `<p>_params.py`; calculations (`<p>_calc.py`) and animation read the same parameters.

## Coordinates

x = right, y = driving direction (front = +y), z = up, ground = z 0. Unit mm. Origin = centre of the robot,
so the implement stands directly in robot coordinates.
Standard robot: wheel centres (+-375, +-500), axle at z 215. Wheel unit local: origin = axle centre, top plate top
z 349. The XL has different dimensions: use the parameters, not these numbers.

## Robot structure (agbots/agbot design)

```
Robot (App::Part)
  Chassis: lower_beam_* (x direction, y = +-500 +-75), upper_beam_* (y direction, x = +-375 +-50), GNSS
  RL_unit, RR_unit            rear, fixed: wheel bracket + wooden block + frame_bolts
  FL_unit, FR_unit            front: steering stack; sub-Part *_steered rotates along (Placement rotation about z)
```
Objects are named `<TAG>_<part>` (TAG = RL/RR/FL/FR). Rolling parts: `<TAG>_tire/_rim/_hub` (rotation about local x).
Beams: lower top z = `z_lower_beam_top`, upper `z_upper_beam_top` (local, +215 for world).

## Rules for implements

- Mount on the **50 mm hole grid** of the beams (M10, hole 10.4), on the pattern of the top plate, or on the
  flange holes of the wheel brackets.
- Keep clear: steering sweep of the front wheels (fork rotates up to ~30 degrees) and the zone above the front wheels
  (stepper motor, bearings, threaded rods). Robot structure: see above.
- The implement is its own `App::Part` with the parts in subgroups (e.g. Mount, Frame, Drive). The robot model
  sits next to it, hidden or visible, for checking only.
- Set color via `COLOR`, give unique `Name`/`Label` (English snake_case, like the OpenSCAD files).
- Moving parts (rotor, arm, wheel) get their own sub-Part, so that `animate_<p>.py` only sets the `Placement`.
- `Shape.rotate/translate` puts the movement in the shape Placement; `add_shape(..., pos=)` combines that correctly.
  Do not overwrite `obj.Placement` of a build object yourself; only the animation does that per frame.

## Animation

- `animate_<p>.build()` creates a **separate document** (`<name>_on_robot_animation`) with the robot (from `agbots/agbot design`,
  via `build_robot`), implement, ground (terrain, floor, fence) and possibly a process model. It does not need to be
  saved.
- Per frame: update the robot (position, steering angle, wheel rotation, possibly pitch/roll), the implement (arm, rotor) and
  the process (ground, feed, slots). Calculations come from `<p>_calc.py`, so that animation and report give the same figures.
- The camera follows the robot (`track_camera`); the poses are at the top of the script (`CAM_*`).
- Live: `play()` and `stop()`. GIF: `render_all(folder)` writes frames, then `make_gif_<p>.main(folder, "previews/....gif")`.
  `summary()` gives the range of the key figures, to check the run.
- The GIF goes in `previews/` and is shown in the README.

## Check after every change

1. No interference: `build_<p>.check_interference()` (`common()` volume between visible parts, bounding-box
   pre-filter) must be empty. For an animation also check the end positions (`check_fit()` where present).
2. Check clearance to tires and steering sweep (`clearance()`) and mass/centre of gravity (`mass_properties()`).
3. Compare parts from OpenSCAD with an STL export (`C:\Program Files\OpenSCAD\openscad.exe`, `-D toggle=false`):
   volume < 0.01 % difference.
4. Look at the result: `view.saveImage(path, w, h, "White")`, camera via `pivy` (set `cam.orientation` directly,
   no `viewTop()` right before `saveImage`). `render_all()` does this for the standard images in `previews/`.
5. Update `README.md` (files, usage) and `RATIONALE.md` (choices, estimated values).

## Estimated, not measured

Each implement's README has a list "Estimated, not measured" (e.g. robot mass, bulk density of feed, motor mass).
Keep that list up to date. For the robot: steering stack (bearings UCF205, shaft O25, plates), stepper motor + gearbox,
`steering_gap` 55, wooden blocks, antenna position, hub motor and tire (STLs are missing).
