# Doorzaaimachine (overseeder), eenvoudige versie: FreeCAD-model

Doorzaaimachine voor de Bruut OpenAgbot, gebouwd op de bok en het hefraam van de
[eenvoudige toediener versie 2](../../liquid%20fertilezer%20applicator/simple_v2/README.md).

Per rij één element:
- een dunne schijf Ø 300 × 3 staat 7° scheef en snijdt een V-sleuf van 15 mm;
- een zaaischoen in de schaduw van de schijf legt het zaad op ca. 12 mm **in** de grond;
- een dieptering op de schijf houdt de diepte vast;
- een aandrukrol op een verende arm drukt de sleuf dicht.

Verder:
- 8 rijen op 125 mm = 1 m per module; modules zijn met flenzen naast elkaar te koppelen;
- elke rij volgt de grond met een eigen sleeparm en veerpoot;
- 2 gasveren duwen het zwevende hefraam omlaag met robotgewicht;
- een zaadbak met een vak voor gras (41 l) en een vak voor fijn zaad (18 l), elk met een eigen nokkenrol en motor die de rijsnelheid volgt;
- trekkracht ca. 335 N normaal, tegen 461 N voor de toediener;
- ca. € 1675 aan materiaal.

Let op:
- **ca. 40 kg frontgewicht op de robot** is nodig om de machine met een volle bak te heffen;
- in harde, droge zode alleen met 4 rijen (elk tweede element omhoog).

Zie [ONDERBOUWING.md](ONDERBOUWING.md).

![overzicht](previews/1_iso_rear_right.png)

![bodemvolging](previews/13_ground_following.png)

## Bestanden

| Bestand | Inhoud |
| --- | --- |
| `Overseeder.FCStd` | het model in werkstand (gegenereerd, niet met de hand aanpassen) |
| `ovs_params.py` | alle maten, inclusief de robotaansluiting |
| `ovs_kin.py` | kinematica: hefraam, langgat, gasveren, sleeparm, veerpoot, rolarm, schijf, zaadbak (puur Python) |
| `ovs_parts.py` | één functie per onderdeel, geeft een `Part`-shape |
| `build_ovs.py` | boomstructuur, kleuren, heffen, botscontrole, massa, afbeeldingen |
| `ovs_calc.py` | dosering, neerdruk en gasveren, trekkracht, heffen, asbelasting, modulebreedtes, kosten (puur Python) |
| `ovs_ground.py` | bodemvolging over de hobbelige strook van de toedieners (puur Python) |
| `plot_ground_ovs.py` | vergelijkingsgrafiek met simple_v2 (matplotlib) |
| `run_in_freecad.py` | macro: openen in FreeCAD en uitvoeren (F6) bouwt het model opnieuw |
| `previews/` | afbeeldingen en de grafiek |

De modulenamen beginnen met `ovs_`. Zo kunnen ze samen met de toedieners (`lfs_`, `lfs2_`, `lfa_`) in dezelfde
FreeCAD-sessie geladen worden. `ovs_ground.py` leest de strook en de 80 robotposities uit
`../../liquid fertilezer applicator/simple_v2/` voor de vergelijking. Het onderzoek staat in `../inspiration/`.

## Assen

Gelijk aan het robotmodel en de toedieners: x = rechts, y = rijrichting (voor = +y), z = omhoog, grond = z 0, mm.
- y = 0 is het hart van de achterste onderbalk van de robot (robot-y = werktuig-y − 575).
- Rijen op x = −437,5 … +437,5 (stap 125).
- Draaipunt hefraam op (y, z) = (−70, 200); balk op (−330, 330).
- Per element: draaipunt sleeparm (−330, 150), hart schijf (−540, 135), as aandrukrol (−835, 100).
- De schijf staat 7° gedraaid om z door zijn hart: de voorkant wijst naar −x.

## Opnieuw bouwen en gebruiken

In de Python-console van FreeCAD (map in `sys.path`, of via `run_in_freecad.py`):

```python
import build_ovs, ovs_kin, ovs_params as P
build_ovs.build()                                   # werkstand, slaat het FCStd op
build_ovs.build(psi=ovs_kin.lift_angle(), phi=-P.u_stop_deg, chi=P.pw_link_range[0],
                save_path=None, show_robot=True)    # geheven, met robotreferentie
build_ovs.check_interference()                      # overlappende onderdelen (moet leeg zijn)
build_ovs.mass_properties()                         # massa en zwaartepunten
build_ovs.render_all()                              # afbeeldingen 1 t/m 12 en opslaan in werkstand
```

`psi` = hefhoek van het hefraam, `phi` = hoek van de sleeparmen (een getal of een lijst per rij), `chi` = hoek van
de rolarmen. Allemaal in graden, + = omhoog.

Zonder FreeCAD (elke Python 3; `plot_ground_ovs.py` heeft matplotlib nodig, die zit ook in de Python van FreeCAD):

```bash
python ovs_calc.py
```

```bash
python ovs_ground.py
```

```bash
python plot_ground_ovs.py
```

## Boomstructuur

```
overseeder_1m_8_rows
  headstock_robot_mount          bok (vast): bovenplaat, klemstrip, 4 wangen, langgatplaten, bouten, regelkastje
  lift_actuator                  actuator 3000 N + 2 gasveren naast het langgat
  swing_frame_moves_with_lift    (Placement = rotatie om de draaibouten)
    toolbar_with_coupling_flanges, frame_arms, cross_tube, actuator_lugs_on_toolbar
    seed_hopper_and_metering     zaadbak, deksel, steunplaten, doseerhuis, 2 motoren
    row_unit_1..8                houder, beugelbouten, veerpoot, veer, zaadslang
      row_arm_N                  (Placement = armhoek) arm, schijf, naaf, dieptering, zaaischoen
        press_arm_N              (Placement = rolarmhoek) rolarm, as, aandrukrol
robot_reference_NOT_PART_OF_DESIGN   (verborgen; achterbalken, bovenbalken, achterwielen)
```

## Geschat, niet gemeten

- **Bodemkrachten per schijf**: neerdruk 90 N (zwaar 180 N), trekkracht schijf 25 N en schoen 8 N. Meet dit vóór de bouw (zie ONDERBOUWING § 13).
- **Dieptering**: inzakken 0,075 mm/N.
- **Aandrukrol**: 35 N.
- **Doseerrollen**: cm³ per omwenteling en dichtheden van het zaad (ijken met een afdraaiproef).
- **Robot**: 150 kg, zwaartepunt 500 mm voor de achteras, μ = 0,5.
- **Actuator, motoren en gasveren**: waarden uit typische datasheets.

Een animatie zoals bij de toedieners is nog niet gemaakt; de bodemvolging staat in de grafiek.
