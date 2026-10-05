# Doorzaaimachine (overseeder), geavanceerde versie: FreeCAD-model

Doorzaaimachine voor de Bruut OpenAgbot, gebouwd op de
[geavanceerde toediener](../../liquid%20fertilezer%20applicator/advanved/README.md). Overgenomen van de toediener:
- de bok en het parallellogram;
- de zwevende balk met actuator en langgat;
- de vorkarmen.

Per rij:
- een schijf Ø 300 × 3 snijdt 15 mm diep, met diepteringen aan beide kanten;
- een gebogen zaaikouter direct achter de schijf legt het zaad op ca. 12 mm;
- een aandrukrol in een gaffel drukt de sleuf dicht.

Verder:
- 8 rijen op 125 mm = 1 m per module, met koppelflenzen;
- 2 gasveren in het langgat duwen de zwevende balk omlaag met robotgewicht;
- de zaadbak (62 + 17 l), de dosering en een 12 V-ventilator staan op een frame boven de achteras; de lucht blaast het zaad door 8 slangen naar de kouters;
- trekkracht ca. 375 N normaal;
- snijdiepte op de testbaan 98 % binnen ±3 mm;
- ca. € 2280 aan materiaal.

Let op:
- **ca. 45 kg frontgewicht op de robot** is nodig om te heffen;
- in harde, droge zode alleen met 4 rijen.

Zie [ONDERBOUWING.md](ONDERBOUWING.md). De eenvoudige versie staat in [../simple](../simple/README.md).

![overzicht](previews/1_iso_rear_right.png)

![bodemvolging](previews/13_ground_following.png)

## Bestanden

| Bestand | Inhoud |
| --- | --- |
| `Overseeder_Advanced.FCStd` | het model in werkstand (gegenereerd, niet met de hand aanpassen) |
| `ova_params.py` | alle maten, inclusief de robotaansluiting |
| `ova_kin.py` | kinematica: parallellogram, langgat, gasveren, arm, veerpoot, gaffel, kouter, zaadbak (puur Python) |
| `ova_parts.py` | één functie per onderdeel, geeft een `Part`-shape |
| `build_ova.py` | boomstructuur, kleuren, heffen, botscontrole, massa, afbeeldingen |
| `ova_calc.py` | dosering, neerdruk en gasveren, trekkracht, heffen, asbelasting, modulebreedtes, kosten (puur Python) |
| `ova_ground.py` | bodemvolging over de hobbelige strook; gebruikt maaiveld en robothouding van `../simple/ovs_ground.py` |
| `plot_ground_ova.py` | vergelijkingsgrafiek: geavanceerd, eenvoudig en de starre balk van simple_v2 (matplotlib) |
| `run_in_freecad.py` | macro: openen in FreeCAD en uitvoeren (F6) bouwt het model opnieuw |
| `previews/` | afbeeldingen en de grafiek |

Modulenamen beginnen met `ova_` (eenvoudige versie: `ovs_`).

## Assen

Gelijk aan het robotmodel en de toedieners: x = rechts, y = rijrichting (voor = +y), z = omhoog, grond = z 0, mm.
- y = 0 is het hart van de achterste onderbalk van de robot (robot-y = werktuig-y − 575).
- Rijen op x = −437,5 … +437,5 (stap 125).
- Balk op (y, z) = (−395, 400).
- Per element: draaipunt arm (−490, 270), hart schijf (−690, 135), as aandrukrol (−1025, 100).
- Luchtzaaier: frame op z = 870–910 tussen y = −60 en 260; zaadbak tot z = 1450.

## Opnieuw bouwen en gebruiken

In de Python-console van FreeCAD (map in `sys.path`, of via `run_in_freecad.py`):

```python
import build_ova
build_ova.build()                                   # werkstand, slaat het FCStd op
build_ova.build_lifted()                            # geheven, met robotreferentie
build_ova.build(h=-71, drop=8, chi=22, save_path=None)   # laagste zweefstand, armen en rollen omlaag
build_ova.check_interference()                      # overlappende onderdelen (moet leeg zijn)
build_ova.mass_properties()                         # massa en zwaartepunten
build_ova.render_all()                              # afbeeldingen 1 t/m 12 en opslaan in werkstand
```

- `h` = hoogte van de balk t.o.v. de werkstand (mm);
- `drop` = armhoek (graden, + = omlaag; een getal of een lijst per rij);
- `chi` = hoek van de gaffel van de aandrukrol (graden, + = omlaag).

Zonder FreeCAD (elke Python 3 met de map `../simple` ernaast; de grafiek heeft matplotlib nodig):

```bash
python ova_calc.py
```

```bash
python ova_ground.py
```

```bash
python plot_ground_ova.py
```

## Boomstructuur

```
overseeder_advanced_1m_8_rows
  headstock_robot_mount          2 bokken, wangen, dwarsbuizen, langgatplaten (doorgetrokken voor de gasveren)
  air_seeder_on_robot            draagframe, luchtkanaal met venturi's, doseerhuis, 2 motoren, zaadbak, deksel,
                                 steunplaten, ventilator, persleiding, regelkastje
  parallel_linkage               4 stangen
  lift_actuator_and_gas_springs  actuator, pen in het langgat, 2 gasveren
  toolbar_assembly_moves_with_lift   (Placement = verplaatsing van de balk)
    toolbar, achterframe, pennen
    row_unit_1..8                klemplaten, bouten, houder, veerplaat, draaipen, veerpoot, veer
      row_unit_N_swing_arm       (Placement = armhoek) vorkplaten, as, naaf, schijf, 2 ringen, kouter, bouten
        row_unit_N_press_wheel   (Placement = gaffelhoek) gaffel, as, aandrukrol
  seed_hoses_air                 8 slangen van de venturi's naar de zaadbuizen
robot_reference_NOT_PART_OF_DESIGN   (verborgen)
```

## Geschat, niet gemeten

- **Bodemkrachten**: als de eenvoudige versie; de zaaikouter neemt 15 N trekkracht (zwaar 25 N).
- **Dieptering**: inzakken 0,075 mm/N.
- **Aandrukrol**: 35 N.
- **Ventilator**: 150 W.
- **Doseerrollen**: ijken.
- **Robot**: 150 kg, zwaartepunt 500 mm voor de achteras, μ = 0,5.

Zie ONDERBOUWING § 11.
