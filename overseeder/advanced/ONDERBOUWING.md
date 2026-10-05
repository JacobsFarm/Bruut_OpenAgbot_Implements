# Doorzaaimachine, geavanceerde versie: onderbouwing

5 oktober 2026. Model: `Overseeder_Advanced.FCStd` (FreeCAD 1.1, gegenereerd met `build_ova.py`).
Getallen komen uit het model, `ova_calc.py` en `ova_ground.py`. Waar iets aangenomen of geschat is, staat dat erbij.

Deze versie bouwt voort op de [geavanceerde toediener](../../liquid%20fertilezer%20applicator/advanved/ONDERBOUWING.md).
De [eenvoudige versie](../simple/ONDERBOUWING.md) bouwt voort op de eenvoudige toediener versie 2. Het onderzoek en
de eisen staan in [../inspiration/README_onderzoek_doorzaaien.md](../inspiration/README_onderzoek_doorzaaien.md) en
in § 1 en § 12 van de eenvoudige versie; die worden hier niet herhaald.

![overzicht achter-rechts](previews/1_iso_rear_right.png)

---

## 1. Wat er van de geavanceerde toediener overblijft

| | Geavanceerde toediener | **Geavanceerde doorzaaier** |
| --- | --- | --- |
| Aanbouwbok, 2 × M10 per kant door het gatenraster | ja | **zelfde**, stangen op x = ±125 (tussen element 4/5 en 5/6 door) |
| Parallellogram 260 mm, balk blijft evenwijdig aan de robot | ja | **zelfde** |
| Actuator omgedraaid, stang in een langgat: balk zweeft in werkstand | ja, ±70 mm | **zelfde**; bovenste pen 6 mm hoger (§ 7) |
| Element: één draaipunt, vorkarm, schijf Ø 300 × 3 tussen de vorkplaten | ja | **zelfde**, vorkplaten 5 mm, schijf 200 mm achter het draaipunt (was 240) |
| Diepteringen aan beide kanten van de schijf | Ø 220 → 40 mm | **Ø 270 → 15 mm**, wisselringen 5–25 mm |
| Achter de schijf, in het vlak van de schijf | mes 8 mm + RVS-buisje | **gebogen zaaikouter 16 mm** met zaadbuis, punt op 12 mm |
| Veerpoot | 140 mm achter het draaipunt, 133 N | **70 mm achter het draaipunt, 440 N** (§ 4) |
| Dichtdrukken | – (ruimte gehouden) | **aandrukrol in een gaffel met torsieveer** |
| Neerdruk | eigen gewicht balk | **gewicht + 2 gasveren in het langgat** (robotgewicht) |
| Dosering | loopwiel met spikes → ketting → 5-kanaals slangenpomp op de balk | **luchtzaaier op de robot**: zaadbak, 2 nokkenrollen met motor, 12 V-ventilator, 8 slangen |
| Rijen | 5 op 200 mm | **8 op 125 mm** |

Waarom geen loopwiel: het loopwiel van de toediener zit achter op de balk. Daar weegt elke kilo het zwaarst op de
vooras als de robot heft (§ 8). De robot kent zijn snelheid (RTK-GNSS en wielen), dus de doseermotoren kunnen die
volgen zonder loopwiel.

## 2. Wat er beter is dan de eenvoudige versie

| | Eenvoudig | **Geavanceerd** |
| --- | --- | --- |
| Ophanging balk | draaiend frame: hoe hoger het frame zweeft, hoe schuiner de elementen | **parallellogram**: balk blijft evenwijdig, elementgeometrie verandert niet met de zweefhoogte |
| Schijf | scheef (7°), naaf aan één kant op een schuine bus | **recht, aan twee kanten gelagerd** in de vork: geen scheve belasting op het lager, geen zijkracht |
| Diepte-instelling | één ring aan de +x kant | **ringen aan beide kanten**: diepte gelijk links en rechts van de snede, de zode wordt aan beide kanten vastgehouden |
| Zaad | schoen naast de snede (schaduwkant) | **zaaikouter in het hart van de snede**, zaad precies onder de aandrukrol |
| Aandrukrol | rolarm aan één kant | **gaffel aan twee kanten** |
| Zaadbak | 41 + 18 l op het hefraam, 470 mm achter de bok | **62 + 17 l op de robot**, boven de achteras: bijna 1,5 × zoveel zaad, zonder dat de robot het hoeft te heffen |
| Slangen | zwaartekracht, minstens 55° helling nodig | **lucht**: elke route kan, het zaad blijft niet hangen |
| Zijkracht van de schijven op de robot | ca. 80 N | **0** |
| Snijdiepte binnen ±3 mm (zelfde strook) | 94 % | **98 %** |

Wat het kost:
- **Duurder:** ca. € 2280 tegen € 1675.
- **Ventilator:** ca. 150 W extra elektrisch vermogen.
- **Hoger:** de zaadbak staat 1,45 m hoog.
- **Iets meer trekkracht:** 375 tegen 335 N, omdat de zaaikouter de snede tot 16 mm opent.
- **Frontgewicht:** ook hier ca. 45 kg (§ 8).

## 3. Het element

![element van opzij](previews/9_unit_side.png)

![zaaikouters van onderen](previews/7_coulter_detail_from_below.png)

| Onderdeel | Uitvoering |
| --- | --- |
| Houder | voor- en achterklemplaat 56 × 8 om de balk, 4 bouten M12, plaat 10 mm naar het draaipunt en de veerplaat (als de toediener) |
| Arm | 2 lasergesneden vorkplaten 5 mm, draaipen Ø 20, 100 mm onder de balk en 270 mm boven de grond |
| Schijf | vlakke kouterschijf Ø 300 × 3 op een naaf tussen de vorkplaten, as M20 aan twee kanten gesteund |
| Diepteringen | 2 × PE-HD Ø 270 / 170 × 15, tegen de schijf; diepte = (300 − ring) / 2 = 15 mm. Wisselringen Ø 290 / 280 / 260 / 250 voor 5 / 10 / 20 / 25 mm |
| Zaaikouter | 16 mm, gelast uit 2 platen slijtvast staal 3 mm met het zaadkanaal ertussen. De voorkant volgt de schijf op 5 mm, de punt zit 3 mm boven de onderkant van de schijf (zaad op ca. 12 mm). Met 2 bouten M10 tussen de vorkplaten |
| Zaadbuis | RVS 16 × 1,5, in de kouter gelast, slang 20/26 erover |
| Aandrukrol | massief rubber Ø 200 × 40 in een gaffel (2 strips 30 × 5) op 2 schouderbouten M12, torsieveer ca. 35 N; gaffel 35° omhoog, 22° omlaag |
| Veerpoot | drukveer Ø 35 × 5, c = 4 N/mm, ca. 440 N in werkstand; stelmoer = onderaanslag (arm zakt 8°) |
| Massa | element 10,9 kg, waarvan 8,0 kg meedraait met de arm |

- **Kouter direct achter de schijf.** Een mes of kouter in lijn achter een schijf kantelt met de arm mee. Hoe verder de kouter achter de schijf zit, hoe meer zijn diepte wisselt.
  - Bij de toediener zit de mespunt 125 mm achter het hart van de schijf. Daar wisselde de mesdiepte van 12 tot 64 mm bij een vaste schijfdiepte.
  - Hier zit de punt 49 mm achter het hart, en de voorkant is gebogen langs de schijf.
- **Aandrukrol op een gaffel.** De rol staat op een eigen scharnier, zodat hij los van de diepte de sleuf dichtdrukt.
  - Het scharnier en de as zijn zo gekozen dat de rol over de hele slag (−35° tot +22°) minstens 7 mm vrij blijft van de kouter.

## 4. Neerdruk: gewicht, gasveren en een kortere veerpoot

Bij een parallellogram draagt de grond **het hele gewicht van de balk**. De stangen nemen geen verticale kracht op,
anders dan het draaipunt van het hefraam bij de eenvoudige versie. Toch is het gewicht alleen niet genoeg.

| Normaal, 8 rijen (aannames als de eenvoudige versie, kouter 15 N trekkracht) | Per element |
| --- | --- |
| Gewicht balk met elementen (98,8 kg + halve slangen) | 123 N |
| Duw van de gasveren (samen 483 N langs het langgat, × 0,59 hefboom) | 36 N |
| **Totaal op de grond** | **158 N** |
| Schijf 15 mm de zode in | 90 N |
| Aandrukrol | 35 N |
| **Op de diepteringen** | **33 N** (minimaal 20) |

- **Zonder gasveren** blijft er op de ringen −2 N over: de schijven halen hun diepte net niet.
- **De gasveren** zitten naast de langgatplaten en duwen de pen van de actuator naar beneden (zelfde principe als bij de eenvoudige versie).
  - Het hefraam zweeft vrij tussen −71 en +71 mm.
  - Bij heffen ligt de pen onderin het langgat. De gasveren duwen dan tegen de bok zelf en belasten de actuator niet.
- **Zware, droge zode:** met 8 rijen zou er 1530 N gasveerkracht nodig zijn. Dan wordt de robot achter te licht en is de trekkracht groter dan de grip.
  - Gebruik dan 4 rijen: zet elk tweede element omhoog met de stelmoer, of haal het eraf.
  - Gebruik gasveren van 2 × 330 N en stijvere drukveren (zie onder). Dezelfde regel als bij de eenvoudige versie.
- **Veerpoot dichter bij het draaipunt.** Met de veerpoot van de toediener (140 mm achter het draaipunt, 230 N) wisselde de kracht op de ringen te veel met de armhoek: 7 % van de rijposities had te weinig neerdruk.
  - Op 70 mm moet de veer twee keer zo hard duwen (440 N), maar per graad armhoek verandert de kracht maar een kwart zo veel.
  - Toen bleef nog ca. 1 % over (tabel in § 6).
- **Wat de voorspanning doet:** ze bepaalt alleen op welke hoogte de balk zweeft (bij 442 N in het midden van het langgat), niet hoeveel neerdruk er is.
  - Voor zware zode met 4 rijen is ca. 740 N nodig. Dat vraagt een stijvere veer (c ≈ 6 N/mm) in plaats van alleen meer voorspanning.

## 5. Luchtzaaier op de robot

![luchtzaaier](previews/8_air_seeder_detail.png)

- **Draagframe** (koker 40 × 40 × 3) boven de achteras:
  - achter staan platen op de bovenplaten van de bok, naast de bouten;
  - voor staan kokers op de binnenste achterbalk van de robot, met M10 in het bestaande gatenraster.
  - Het frame zit boven de gasveren en de langgatplaten; ook geheven raakt niets.
- **Zaadbak** van aluminium 2 mm, met een schuin schot in twee vakken:
  - **62 l gras**: 0,54 ha bij 40 kg/ha tetraploïd raaigras;
  - **17 l fijn zaad**: ca. 2,7 ha witte klaver op 5 kg/ha.
  - Twee steunplaten dragen de trechter.
- **Dosering**: hetzelfde doseerhuis met twee nokkenrollen en twee wormwielmotoren met encoder als de eenvoudige versie. Ook de rollen, toerentallen en het ijken zijn gelijk (zie de tabel in [../simple/ONDERBOUWING.md](../simple/ONDERBOUWING.md) § 8).
  - Onder elke uitloop valt het zaad in een venturi in het luchtkanaal (PVC Ø 60).
- **Ventilator**: 12 V radiaalventilator (ca. 150 W, aangenomen) blaast door het kanaal. 8 slangen 20/26 lopen over het parallellogram naar de zaadbuizen.
  - Het zaad komt met de lucht in de zaaikouter. De lucht ontsnapt boven de grond via het open zaadkanaal achter de kouter.
  - **Proef nodig**: is de luchtsnelheid laag genoeg dat het zaad niet uit de sleuf blaast? Zet het toerental van de ventilator zo laag dat het zaad net niet in de slang blijft liggen.
- **Slangen tussen de elementen door**: elke slang loopt 50 mm naast zijn eigen element omhoog, op 830 mm hoogte naar voren boven bok en actuator, en buigt dan naar zijn venturi. Ze buigen mee met zweven en heffen.

## 6. Bodemvolging

![bodemvolging](previews/13_ground_following.png)

Dezelfde hobbelige strook, robothouding en 80 robotposities als bij de toedieners en de eenvoudige versie
(`ova_ground.py`):
- de balk zweeft tot de grond gewicht + gasveren draagt;
- elke arm draait tot de diepteringen links en rechts het maaiveld raken;
- de aandrukrol volgt in zijn gaffel;
- aangenomen: de ringen zakken 0,075 mm per N extra belasting in.

| Werkstand, 80 posities × rijen | Toediener simple_v2 | Doorzaaier eenvoudig | **Doorzaaier geavanceerd** |
| --- | --- | --- | --- |
| Afwijking van de ingestelde snijdiepte | −35 tot +22 mm | −4 tot +7 mm | **−4 tot +8 mm** |
| Standaardafwijking | 8,7 mm | 1,4 mm | **1,3 mm** |
| Binnen ±3 mm | 44 % | 94 % | **98 %** |
| Binnen ±5 mm | 59 % | 99,5 % | **98,8 %** |
| Te weinig neerdruk / arm op de aanslag | – | 0 / 0 | 7 / 5 van 640 |
| Aandrukrol los van de grond | – | 16 van 640 | 8 van 640 |
| Hefraam of balk | – | zweeft −5 tot +7° | zweeft −57 tot +43 mm, nooit tegen een aanslag |

- **Beide doorzaaiers houden de diepte veel beter vast dan de starre balk van de toediener.** Het verschil zit in de diepte-instelling op de schijf zelf en een arm per rij.
- **De geavanceerde houdt vaker binnen ±3 mm** (98 tegen 94 %). Dat komt door de ringen aan twee kanten en de balk die evenwijdig blijft.
- **De uitschieters zijn bij de geavanceerde iets groter** (een paar posities bij een molshoop, met de arm op de aanslag).
- **De punt van de kouter** zit 49 mm achter de schijf en volgt het maaiveld minder precies (0,7–21,6 mm, sd 2,4). Het zaad valt op de bodem van de sleuf die de schijf snijdt. Op die enkele plekken komt het daardoor iets ondieper te liggen.

## 7. Heffen en zweven

| | Waarde |
| --- | --- |
| Zweefbereik balk | −71 / +71 mm |
| Hefhoogte | 150 mm (actuator in: 290 mm) |
| Actuator | 24 V, 2500 N, slag 150, ca. 30 mm/s, IP66 |
| Nodige kracht (1,3 × marge) | 2175 N bij het begin, 1316 N geheven |
| Tijd | 1,3 s vrije slag, 5,0 s tot helemaal geheven |
| Geheven vrij van de grond | schijven 108, kouters 106, aandrukrollen 38 mm |

- **Bovenste pen 6 mm hoger dan bij de toediener.** In de laagste zweefstand (−80 mm bij de toediener) raakte de stang van de actuator de achterbalk van de robot.
  - Met de pen op z = 706 is het zweefbereik −71 / +71 mm, met 3,7 mm speling boven de balk.
- **Pen langs het langgat.** In het model schuift de pen nu echt langs het langgat, niet langs de as van de actuator (zo deed de toediener het).
  - Daardoor kwam ook naar voren dat de gasveren bij de bovenkant van het langgat te kort waren. Ze zijn nu 225 mm.
- **Botscontrole**: werkstand, geheven, en de uiterste zweefstanden met de elementen helemaal omhoog of omlaag, allemaal met de robotreferentie erbij: **0 overlap**.

![geheven met robot](previews/10_lifted_side_with_robot.png)

## 8. Trekkracht en de balans van de robot

| | Waarde |
| --- | --- |
| Trekkracht normaal, 8 rijen | 375 N |
| Grip (μ = 0,5) in het werk | 1010 N |
| Zware zode, 8 rijen | 604 N, grip 703 N bij 1530 N gasveren: niet doen |
| Zware zode, 4 rijen | 302 N, grip 957 N |
| Vooras geheven, volle bak (25 kg zaad) | **31 N** |
| Vooras geheven, + 40 kg frontgewicht | 423 N |
| **Frontgewicht voor 25 % op de vooras** | **ca. 46 kg** |

- De balk met elementen weegt 99 kg en hangt geheven ruim 700 mm achter de achteras.
- **De zaadbak op de robot helpt**: 32 kg frame, bak en ventilator plus het zaad staan bijna boven de achteras. Op de balk zouden ze ca. 50 kg extra frontgewicht vragen.
- **De elementen zelf blijven het probleem**: 8 × 11 kg op 0,7 m achter de as. Een robot van 150 kg (aanname) heeft dan, net als bij de eenvoudige versie, **ca. 45 kg frontgewicht** nodig.
- **Weeg eerst de robot per as.**

## 9. Breder maken met modules

- **Wat er al op zit**:
  - de balk heeft koppelflenzen (100 × 100 × 8, 4 × M12);
  - een module is van flens tot flens 1000 mm, dus de rijafstand blijft 125 mm over de naad;
  - de elementen klemmen overal op de balk.
- **Trekkracht** (per meter): normaal 364 N met 8 rijen, 182 N met 4 rijen. Normaal kan 2 m met 8 rijen/m binnen de grip, of 3 m met 4 rijen/m.
- **Heffen**: een tweede module kan de robot niet aan de bok heffen. Voor 2–3 m krijgt elke buitenmodule een eigen steunwiel (zwenkwiel met hefactuator). De zaadbak op de robot kan dan groter, met een extra venturi per rij.

## 10. Kosten (indicatief, excl. btw, prijsniveau 2026)

| Post | € |
| --- | --- |
| Staal: bok, stangen, balk, achterframe, vorkplaten (laser), draagframe (ca. 60 kg) | 260 |
| 8 kouterschijven Ø 300 × 3 met naaf en as | 300 |
| 16 diepteringen PE Ø 270 (+ wisselsets) | 180 |
| 8 zaaikouters met zaadbuis | 160 |
| 8 aandrukrollen, gaffels, torsieveren, schouderbouten | 170 |
| 8 drukveren, veerstangen, pennen | 90 |
| Bouten, pennen, bussen | 110 |
| Actuator 2500 N | 280 |
| 2 gasveren 250 N | 50 |
| Zaadbak aluminium met deksel | 170 |
| Doseerhuis, 2 nokkenrollen, 2 motoren met encoder | 200 |
| Ventilator, luchtkanaal, 8 venturi's | 160 |
| Zaadslang (14 m) | 60 |
| Regelaars, microcontroller, kastje, kabel | 90 |
| **Totaal** | **ca. 2280** |

## 11. Geschat, niet gemeten

- **Bodemkrachten.** Dezelfde aannames als de eenvoudige versie: neerdruk per schijf 90 / 180 N. De zaaikouter neemt 15 / 25 N trekkracht.
  - Meet dit vóór de bouw met één element.
- **Inzakken van de ringen**: 0,075 mm/N.
- **Aandrukrol**: kracht 35 N en torsieveer.
- **Ventilator**: vermogen en luchtsnelheid; of het zaad in de sleuf blijft liggen.
- **Doseerrollen en dichtheden van het zaad**: ijken.
- **Robot**: 150 kg, zwaartepunt 500 mm voor de achteras, μ = 0,5.
- **Actuator en gasveren**: waarden uit typische datasheets.

De bodemvolging is quasi-statisch gerekend. Een animatie zoals bij de toedieners is nog niet gemaakt.
