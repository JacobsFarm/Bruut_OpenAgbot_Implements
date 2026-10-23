# Solar canopy: FreeCAD model

A roof of **2 solar panels** (1000 x 1650 mm, 320 Wp each, `n_panels` can be set to 3) on a steel tube frame above the
Bruut OpenAgbot. The canopy is wider and longer than the robot (2040 x 1650 mm, 595 mm overhang per side), charges
the battery through an MPPT charge controller and carries the GNSS antenna. Generated from Python (`sol_params.py`
is the single source of truth), in robot coordinates (x right, y front, z up, ground z 0).

![iso](previews/1_iso.png)

- **Base:** same as the hybrid: 2 long tubes 50x50x3 across the width (y = ±350), 8 x M10 on the upper beams, plus 2
  stringers along y (x = ±375, only |y| < 380, clear of the steering stacks).
- **Canopy frame:** 4 posts 40x40x3, 2 top rails along y, 2 cross members along x (the panels are bolted on them with
  M8), 4 diagonal struts D25 to the overhanging ends and 4 diagonal braces in driving direction.
- **Panels:** underside at z 1530, top at z 1565. Aluminium frame, glass laminate, cell grid, junction box.
- **Electronics:** MPPT box on the rear long tube. The GNSS antenna of the robot would sit under the panels, so it is
  hidden in this model and moved to a mast on the roof (passes through the gap between the panels).
- Clear of the steering stacks (25 mm to the stepper plate), no interference with the robot.

## Files

| File | Contents |
| --- | --- |
| `sol_params.py` | all dimensions and estimated figures |
| `sol_parts.py` | one function per part (robot coordinates) |
| `build_sol.py` | model tree, `check_interference()`, `clearance()`, `mass_properties()`, `render_all()`, STEP export |
| `sol_calc.py` | yield, battery runtime, wind load, tipping, frame stress (pure Python) |
| `run_in_freecad.py` | macro: reload, build, print the key figures |
| `run_checks.py` | same, started with a Qt timer; result in `_out.json` (for the 2 minute MCP timeout) |
| `RATIONALE.md` | why it is like this |

Run in FreeCAD: `exec(open(r"F:\veldrobot\aanbouwdelen\solar\run_in_freecad.py", encoding="utf-8").read())`.
There is no animation (static add-on). Do not use `execute_code_async` for the build: it deadlocks FreeCAD's GUI.

## Key figures (current build)

- 3.3 m2, 640 Wp; about 384 W at the battery with a clear sky, about 480 kWh per year (flat, NL).
- Per day: 2.3 kWh in June, 1.2 in March, 0.2 in December. Light task (900 W, 8 h = 7.2 kWh) is covered for about
  32 % in June; heavy task about 13 %.
- 2.4 kWh battery (usable 1.9 kWh): at 900 W it lasts 2.1 h without and 3.7 h with solar at noon.
- Mass about 91 kg (frame 55, panels 34, electronics 2), centre of gravity z 1309 mm; robot + canopy tips over at
  about 29 degrees static. Against a 20 m/s gust on the roof the safety factor is about 1.8.
- Interference: none. Cross member stress 4 MPa, strut buckling safety > 100.

## Estimated, not measured

Panel size, power, mass and cell layout (generic 60-cell class), derate 0.75, monthly sun hours, MPPT size and mass,
GNSS mast and mass, robot mass (150 kg) and centre of gravity (z 450), loads of light and heavy task, wind
coefficients (uplift 1.0, side 0.3), weld and bolt details of the frame.
