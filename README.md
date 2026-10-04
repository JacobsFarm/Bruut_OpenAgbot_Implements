# Bruut Implements

Implement (attachment) designs for the **AgOpenBot Bruut**, an open-source agricultural field robot. Designs are parametric and built in FreeCAD, mostly through Python scripts.

## Implements

| Folder | Description |
|---|---|
| `Design ridderzuring boor/` | Dock (broad-leaved dock) removal drill/mill, with renders, animations, DXF and STEP files |
| `liquid fertilezer applicator/` | Liquid fertilizer applicator, with calculations, parametric model and previews |
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
