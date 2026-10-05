# Eenvoudige toediener versie 2 (schijf + mes): FreeCAD-model

Versie 2 van de [eenvoudige toediener](../simple/README.md), met per rij een snijschijf voor het mes.
- Een vlakke kouterschijf Ø 300 snijdt de zode 45 mm diep door.
- Het mes loopt er 14 mm achter in hetzelfde vlak, zet de snede open en het RVS-buisje legt de vloeistof erin.
- Al het andere is gelijk aan versie 1: bok met laag draaipunt, zwevend hefraam met actuator en langgat, twee kruiwagenwielen als dieptewiel, 12 V-membraanpomp met doseerplaatjes.
- Ca. € 915 aan materiaal.

Wat de schijven kosten:
- 26 kg extra op het hefraam (70 kg);
- een actuator van 1500 N;
- bij harde zode tot 50 kg ballast voor neerdruk.

Zie [ONDERBOUWING.md](ONDERBOUWING.md).

![overzicht](previews/1_iso_rear_right.png)

![animatie: achter de robot over een hobbelige strook](previews/animation_strip_ground_following.gif)

## Bestanden

| Bestand | Inhoud |
| --- | --- |
| `Liquid_Fertilizer_Applicator_Simple_v2.FCStd` | het model in werkstand (gegenereerd, niet met de hand aanpassen) |
| `lfs2_params.py` | alle maten, inclusief schijf, naaf, schijfarm en robotaansluiting |
| `lfs2_kin.py` | kinematica: draaipunt, langgat, zweefbereik, hefhoek, mes, spleet mes–schijf (puur Python) |
| `lfs2_parts.py` | één functie per onderdeel, geeft een `Part`-shape |
| `build_lfs2.py` | boomstructuur, kleuren, heffen, botscontrole, massa, afbeeldingen |
| `lfs2_calc.py` | dosering, neerdruk en ballast, breekbout, heffen, asbelasting, kosten (puur Python) |
| `lfs2_ground.py` | bodemvolging over de hobbelige strook: snede, mesdiepte (puur Python) |
| `plot_ground2.py` | vergelijkingsgrafiek met v1 en de geavanceerde variant (matplotlib) |
| `ground_advanced_reference.json` / `ground_simple_v1_reference.json` | mesdiepte van de geavanceerde variant en van v1 op dezelfde posities |
| `animate_lfs2.py` | animatie: robot + toediener over de strook |
| `make_gif_lfs2.py` | frames naar GIF met bijschrift en paneel "mesdiepte en snede per rij" |
| `run_in_freecad.py` | macro: openen in FreeCAD en uitvoeren (F6) bouwt het model opnieuw |
| `previews/` | afbeeldingen, de vergelijkingsgrafiek en de GIF |

De modulenamen beginnen met `lfs2_`. Zo kunnen v1 (`lfs_`), v2 en de geavanceerde variant (`lfa_`) in dezelfde
FreeCAD-sessie geladen worden.

## Assen

Gelijk aan het robotmodel en versie 1: x = rechts, y = rijrichting (voor = +y), z = omhoog, grond = z 0, mm.
- y = 0 is het hart van de achterste onderbalk van de robot (robot-y = werktuig-y − 575).
- Rijen op x = −400, −200, 0, 200, 400; dieptewielen op x = ±300.
- Schijfhart op (y, z) = (−320, 105); mespunt op (−461, −40); draaipunt van het hefraam op (−70, 200).

## Opnieuw bouwen en gebruiken

In de Python-console van FreeCAD (map in `sys.path`, of via `run_in_freecad.py`):

```python
import build_lfs2, lfs2_kin
build_lfs2.build()                                  # werkstand, slaat het FCStd op
build_lfs2.build(psi=lfs2_kin.lift_angle(), save_path=None, show_robot=True)   # geheven, met robotreferentie
build_lfs2.check_interference()                     # overlappende onderdelen (moet leeg zijn)
build_lfs2.mass_properties()                        # massa en zwaartepunten
build_lfs2.render_all()                             # afbeeldingen 1 t/m 11 en opslaan in werkstand
```

Zonder FreeCAD (elke Python 3; `plot_ground2.py` heeft matplotlib nodig):

```bash
python lfs2_calc.py
```

```bash
python lfs2_ground.py
```

```bash
python plot_ground2.py
```

## Animatie

```python
import animate_lfs2
animate_lfs2.build()                    # document LFS2_on_robot_animation opbouwen
animate_lfs2.play()                     # live afspelen, animate_lfs2.stop()
animate_lfs2.check_fit()                # overlap met het echte robotmodel (moet leeg zijn)
animate_lfs2.render_frames(r"C:\temp\lfs2_frames", 0, 60)   # in stukken van ~60 frames renderen
import make_gif_lfs2
make_gif_lfs2.main(r"C:\temp\lfs2_frames", r"previews\animation_strip_ground_following.gif")
```

## Boomstructuur

```
liquid_fertilizer_applicator_simple_v2
  headstock_robot_mount          bok (vast): bovenplaat, klemstrip, 4 wangen, langgatplaten, bouten
  dosing_unit_on_headstock       pomp, filter + camlock, drukregelaar + manometer, verdeelblok, verbindingsslangen
  lift_actuator                  huis (pen op het hefraam) + stang (oog in het langgat) + 2 pennen
  outlet_hoses_flex_with_lift    5 slangen van het verdeelblok naar de spuitdophouders
  swing_frame_moves_with_lift    (Placement = rotatie om de draaibouten)
    toolbar, frame_arms, cross_tube_with_actuator_lugs
    disc_and_knife_1..5          bodemplaat, schijfarm, asbout, lagernaaf, schijf, zijplaten, beugelbouten, mes,
                                 draai- en breekbout, buisje, P-clips, spuitdophouder
    gauge_wheel_left / right     klemplaat, beugelbouten, huls, steel, stelpen, vork, as, wiel
robot_reference_NOT_PART_OF_DESIGN   (verborgen; achterbalken, bovenbalken, achterwielen)
```

## Geschat, niet gemeten

- **Neerdruk per schijf**: 100 N, harde zode 200 N.
- **Trekkracht**: schijf 30–50 N, mes in de snede 60–125 N.
- **Neerwaartse kracht van de mespunt**: 30 % van de trekkracht van het mes.
- **Uitstroomcoëfficiënt van de doseerplaatjes**: 0,65.
- **Robot**: gewicht, zwaartepunt en grip zoals in v1.
- **Actuatorsnelheid en prijzen**: typische waarden.

De bodemvolging is quasi-statisch gerekend, net als in v1. Opdrijven door te weinig neerdruk staat in `lfs2_calc`,
niet in de animatie.
