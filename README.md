# Bruut Implements

Implement (attachment) designs for the **AgOpenBot Bruut**, an open-source agricultural field robot. Designs are parametric and built in FreeCAD, mostly through Python scripts.

## Implements

| Folder | Description |
|---|---|
| `Design ridderzuring boor/` | Dock (broad-leaved dock) removal drill/mill, with renders, animations, DXF and STEP files |
| `liquid fertilezer applicator/` | Liquid fertilizer applicator in three variants, each with calculations, parametric model, previews and a ground-following animation: `advanved/` (disc + knife units on spring arms, ground-wheel-driven 5-channel peristaltic pump, parallel linkage), `simple/` (fixed knives, two wheelbarrow gauge wheels, single-pivot frame, 12 V pump with orifice plates; about €600 in parts) and `simple_v2/` (as `simple/`, with a cutting disc in front of each knife; about €900 in parts) |
| `overseeder/` | Overseeder (grassland slit seeder) in two variants. Both are 1 m modules with 8 rows at 125 mm and coupling flanges. They cut a 15 mm slot, place seed about 12 mm deep and close the slot with a sprung press wheel. Each row follows the ground on its own spring-loaded arm with the depth band on the disc. Gas springs add robot weight as downforce. Each variant has calculations, a ground-following comparison and previews. `simple/` is built on `simple_v2`: angled single disc with a seed boot in its shadow and a two-compartment gravity hopper on the lift frame; about €1,675 in parts. `advanced/` is built on the advanced applicator: parallel linkage, a straight disc held on both sides with depth bands on both sides, a curved seed coulter and a press-wheel yoke, plus an air seeder (hopper, electric metering, 12 V fan) mounted above the robot's rear axle; about €2,280 in parts |
| `trencher/` | Trencher attachment, with renders and STEP export |
| `feed pusher auger/` | Feed pusher auger (simple and advanced variants) |
| `around_pole_mower/` | Mower for working around poles (notes only) |
| `mower unit/` | General mower unit (notes only) |

Each folder holds its own requirements and notes (`*_idee_en_eisen.md`, `README.md` or `info.txt`).

## Working with the designs

- Models are stored as `.FCStd` (FreeCAD) with `.step` exports where available.
- The `*.py` scripts generate the models parametrically; adjust the parameter files (e.g. `*_params.py`) and rebuild in FreeCAD.
- Requires [FreeCAD](https://www.freecad.org/).

## Notes

- `inspiration/` folders and `agbot design/` (the base robot model) are excluded from the repository via `.gitignore`.
- Some documentation is written in Dutch.
