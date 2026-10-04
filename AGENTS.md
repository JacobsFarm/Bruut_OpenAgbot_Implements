# AGENTS.md - FreeCAD model Bruut OpenAgbot

Korte uitleg voor een AI-agent die aanbouwdelen (accessoires, beugels, kappen) aan dit model toevoegt.

## Koppeling met FreeCAD

- FreeCAD **1.1**, GUI open, bediend via de **FreeCAD MCP-addon** (tools `mcp__freecad__*`, vooral `execute_code`).
- `execute_code` onthoudt geen variabelen tussen aanroepen: zet code in bestanden en `import`/`exec` die.
  Gebruik `sys.dont_write_bytecode = True` (geen `__pycache__`).
- Open document: `Bruut_OpenAgbot` (`freecad/Bruut_OpenAgbot.FCStd`). Controleer eerst met `list_documents`.
- Pad naar de map: `F:\Agbot\Bruut_OpenAgbot\CAD_designs\freecad`, zet die in `sys.path`.

## Bestanden (single source of truth)

- `agbot_params.py`: alle maten, zelfde namen als `config/parameters.scad`, plus stuurparameters. Nooit maten hardcoden.
- `agbot_parts.py`: een functie per onderdeel, geeft een `Part`-shape in lokale coordinaten.
- `build_agbot.py`: zet shapes in de boomstructuur (`build()`), kleuren in `COLOR`, helper `add_shape`, `new_part`.
- `animate_agbot.py`: rijden/draaien (`play()`, `stop()`, `render_all()`); `make_gif.py`: GIF.
- Het FCStd wordt **gegenereerd**. Een nieuw onderdeel dus in `agbot_parts.py` en `build_agbot.py` zetten, daarna opnieuw bouwen (`run_in_freecad.py`). Handmatig toegevoegde objecten gaan verloren.

## Coordinaten

x = rechts, y = rijrichting (voor = +y), z = omhoog, grond = z 0. Eenheid mm.
Wielmiddens (+-375, +-500), as op z 215 (`ground_to_axle`). Wielunit-lokaal: oorsprong = hart as, top plate-bovenkant z 349 (`bracket_top_z`).

## Structuur

```
Robot (App::Part)
  Chassis: lower_beam_* (x-richting, y = +-500 +-75), upper_beam_* (y-richting, x = +-375 +-50), GNSS
  RL_unit, RR_unit            achter, vast: wielbeugel + houten blok + frame_bolts
  FL_unit, FR_unit            voor: stuurstapel; sub-Part *_steered draait mee (Placement-rotatie om z)
  Optional_frame_cover        verborgen (botst met rechter stuurkop)
```
Objecten heten `<TAG>_<onderdeel>` (TAG = RL/RR/FL/FR). Rolonderdelen: `<TAG>_tire/_rim/_hub` (rotatie om lokale x).

## Regels voor aanbouwdelen

- Bevestig op het **50 mm-gatenraster** van de balken (M10, gat 10,4) of op het patroon 100 x 150 van de top plate.
- Balken: onderste top z = `z_lower_beam_top`, bovenste `z_upper_beam_top` (lokaal, +215 voor wereld). Bovenkant balken is vrij behalve voor de stuurstapel.
- Vrijhouden: stuurzwaai van de voorwielen (vork draait tot ~30 graden) en de zone boven de voorwielen (stappenmotor, lagers, draadstangen op (+-50, +-75)).
- Hang nieuwe delen aan `Chassis` (mee met de robot) en gebruik wereldcoordinaten daar. Delen die met een wiel meebewegen horen in de betreffende unit.
- Zet kleur via `COLOR`, geef unieke `Name`/`Label` (Engels snake_case, zoals de OpenSCAD-bestanden).
- `Shape.rotate/translate` zet de beweging in de shape-Placement; `add_shape(..., pos=)` combineert dat correct. Overschrijf `obj.Placement` niet zelf.

## Controle na elke wijziging

1. Geen interferentie: `common()` volume tussen zichtbare onderdelen (bounding-box voorfilter) moet 0 zijn.
2. Onderdelen uit OpenSCAD vergelijken met een STL-export (`C:\Program Files\OpenSCAD\openscad.exe`, `-D toggle=false`): volume < 0,01 % verschil.
3. Bekijk het resultaat: `view.saveImage(pad, b, h, "White")`, camera via `pivy` (`cam.orientation` direct zetten, geen `viewTop()` vlak voor `saveImage`).

## Geschat, niet gemeten

Stuurstapel (lagers UCF205, as O25, platen), stappenmotor + kast, `steering_gap` 55, houten blokken, antennepositie, hubmotor en band (STL's ontbreken). Zie `README.md`.
