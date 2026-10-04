# Toediener voor vloeibare meststof (renure): FreeCAD-model

Los werktuig voor de Bruut OpenAgbot: 5 injectie-elementen (schijf + mes + buisje) op 200 mm, één loopwiel dat
een 5-kanaals rollenpomp aandrijft, en een elektrisch geheven parallellogram dat in het werk zweeft (langgat).
Waarom het zo ontworpen is, staat in [ONDERBOUWING.md](ONDERBOUWING.md).

![overzicht](previews/1_iso_rear_right.png)

![animatie: achter de robot over een hobbelige strook](previews/animation_strip_ground_following.gif)

## Bestanden

| Bestand | Inhoud |
| --- | --- |
| `Liquid_Fertilizer_Applicator.FCStd` | het model in werkstand (gegenereerd, niet met de hand aanpassen) |
| `lfa_params.py` | alle maten, inclusief de robot-interface |
| `lfa_parts.py` | één functie per onderdeel, geeft een `Part`-shape |
| `build_lfa.py` | boomstructuur, kleuren, heffen, botscontrole, massa, afbeeldingen |
| `lfa_calc.py` | dosering, veer, neerdruk, zweefstand, actuator, asbelasting (puur Python) |
| `animate_lfa.py` | animatie: robot + toediener over een hobbelige strook, bodemvolging per frame |
| `make_gif_lfa.py` | frames naar GIF met bijschrift en paneel "bodemvolging" (Pillow, zit in FreeCAD) |
| `run_in_freecad.py` | macro: openen in FreeCAD en uitvoeren (F6) bouwt het model opnieuw |
| `previews/` | afbeeldingen en de GIF |

## Assen

Gelijk aan het robotmodel: x = rechts, y = rijrichting (voor = +y), z = omhoog, grond = z 0, mm.
y = 0 is het hart van de achterste onderbalk van de robot, dus robot-y = werktuig-y − 575.
Rijen op x = −400, −200, 0, 200, 400; loopwiel op x = 312.

## Opnieuw bouwen en gebruiken

In de Python-console van FreeCAD (map in `sys.path`, of via `run_in_freecad.py`):

```python
import build_lfa
build_lfa.build()                       # werkstand, slaat het FCStd op
build_lfa.build(lift=140, save_path=None, show_robot=True)   # geheven, met robotreferentie
build_lfa.check_interference()          # lijst met overlappende onderdelen (moet leeg zijn)
build_lfa.mass_properties()             # massa en zwaartepunten
build_lfa.render_all()                  # alle afbeeldingen in previews/ en opslaan in werkstand
```

```python
import lfa_calc
lfa_calc.report()                       # kerngetallen
lfa_calc.dose_table()                   # dosering per kettingwiel/slang
```

## Animatie

Bouwt een apart document `LFA_on_robot_animation`: het robotmodel uit `agbot design` (die bestanden worden niet
aangepast), de toediener erachter en een golvend maaiveld met bulten, kuilen en een richel.

Per frame:
- de robot rust op zijn vier wielen;
- de balk zweeft tot de grond zijn gewicht draagt;
- elk element en het loopwiel zoeken hun eigen armhoek;
- veerpoten, slangen en sleuven bewegen mee.

```python
import animate_lfa
animate_lfa.build()                     # document opbouwen
animate_lfa.play()                      # live afspelen, animate_lfa.stop()
animate_lfa.summary()                   # bereik balk, veerweg, mesdiepte, aanslagen
animate_lfa.render_frames(r"C:\temp\lfa_frames", 0, 30)   # in stukken van ~30 frames renderen
import make_gif_lfa
make_gif_lfa.main(r"C:\temp\lfa_frames", r"previews\animation_strip_ground_following.gif")
```

Rijplan, terrein en camera staan bovenaan `animate_lfa.py` (`SPEED`, `BUMPS`, `RIDGES`, `CAM_HIGH`, `CAM_LOW`).

## Boomstructuur

```
liquid_fertilizer_applicator
  headstock_robot_mount        aanbouwbok (vast aan de robot)
  parallel_linkage             4 stangen (draaien om de voorste pennen)
  lift_actuator                huis (op het achterframe) + stang (pen in het langgat van de bok)
  toolbar_assembly_moves_with_lift   (Placement = hefbeweging)
    toolbar, achterframe
    ground_wheel_drive_and_pump
      ground_wheel_arm_swing   (draait om de pompas)
    injection_unit_1..5
      unit_n_swing_arm         (draait om het draaipunt)
    outlet_hoses
robot_reference_NOT_PART_OF_DESIGN   (verborgen; achterbalk, bovenbalken, achterwielen)
```

## Geschat, niet gemeten

Robotgewicht en zwaartepunt (`lfa_calc.ROBOT`), veerconstante 4 N/mm, neerdruk loopwiel 150 N, vulgraad van de
pomp 0,85, rolomtrek van het loopwiel 1,19 m, benodigde neerdruk in de zode. Zie ONDERBOUWING § 6 en § 7.
In de animatie rust de robot star op vier wielen (vlak door de wielpunten) en is de balk in krachtenevenwicht
(gewicht = grondkrachten); dynamica en slip zijn niet meegenomen.
