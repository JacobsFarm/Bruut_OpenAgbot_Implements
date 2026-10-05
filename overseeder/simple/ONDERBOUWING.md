# Doorzaaimachine, eenvoudige versie: onderbouwing

5 oktober 2026. Model: `Overseeder.FCStd` (FreeCAD 1.1, gegenereerd met `build_ovs.py`).
Getallen komen uit het model, `ovs_calc.py` en `ovs_ground.py`. Waar iets aangenomen of geschat is, staat dat erbij.
Het onderzoek waar dit ontwerp op steunt staat in [../inspiration/README_onderzoek_doorzaaien.md](../inspiration/README_onderzoek_doorzaaien.md).
De [geavanceerde versie](../advanced/ONDERBOUWING.md) bouwt voort op de geavanceerde toediener.

![overzicht achter-rechts](previews/1_iso_rear_right.png)

---

## 1. Eisen

Van de gebruiker:
- het zaad **in** de grond leggen, niet erop strooien;
- **1 m werkbreedte**, met modules breder te maken;
- **bodemvolging**;
- de zode **snijden**;
- uitgaan van de toediener voor vloeibare mest, met een dosering voor zaad in plaats van vloeistof;
- **zo weinig mogelijk trekkracht**.

Uit het onderzoek (zie de inspiratiemap):

| Eis | Waarom | Bron |
| --- | --- | --- |
| Sleuf **dichtdrukken** is een hoofdfunctie | 418 tegen 84 kiemplanten/m² met en zonder dichtgedrukte sleuf | WUR-rapport 1354 |
| Zaaidiepte **0,5–2 cm**, klaver 0,5–1 cm | dieper zaad komt slecht op | WUR, Super-G, Arkansas |
| Dosering van **2 kg/ha** (witte klaver) tot **40 kg/ha** (raaigras), klein zaad apart | klaverzaad ontmengt in een grote bak met graszaad | Teagasc, Super-G |
| Zaaien in een sleuf wint vooral bij **droogte en dikke zode** | breedwerpig strooien is bij goed weer even goed | Virginia Tech, Arkansas, Super-G |
| **Rijen kunnen uitzetten** (strokenzaaien) | klaver in stroken op 25 % van het perceel: −75 % kosten | Arkansas FSA2159 |
| Dosering gekoppeld aan **rijsnelheid** | vaste kg/ha bij wisselende snelheid | Vredo, Evers, Einböck |

Wat de machine **niet** oplost: concurrentie van de oude zode en vocht zijn belangrijker dan de machine. Kort maaien of
grazen (≤ 4–5 cm), eerst wiedeggen en zaaien in vochtige grond eind augustus–september blijven nodig (§ 12).

## 2. Werkprincipe: één scheve schijf per rij

| Principe | Zaad in de grond | Trekkracht | Neerdruk nodig | Diepte | Oordeel voor een robot van 150 kg |
| --- | --- | --- | --- | --- | --- |
| Tandenzaaier + strooier | nee, erop en ingeharkt | middel | weinig | onnauwkeurig | valt af: zaad ligt erop |
| Dubbele schijf (Vredo) | ja | middel | veel: 2 schijven per rij | goed | te zwaar |
| Omgekeerde T (Aitchison) | ja | hoog: tand 25 mm door de grond | middel | goed | te veel trekkracht |
| **Eén vlakke schijf onder 7°, schoen in de schaduw** | **ja** | **laag** | **1 schijf per rij** | **goed met dieptering** | **gekozen** |

Zo werkt het element:
- **Snijden.** Een dunne, vlakke schijf Ø 300 × 3 staat 7° scheef op de rijrichting en snijdt 15 mm diep. De ene kant (+x) duwt de grond een paar mm opzij. Aan de andere kant (−x, de schaduwkant) blijft een open V-sleuf over. Zo werken ook de enkelschijfzaaiers van John Deere (750) en de Moore Unidrill.
- **Zaad leggen.** Een smalle zaaischoen (12 mm) loopt in die schaduw tegen de schijf aan. Het zaad valt door de zaadbuis en de schoen op de bodem van de sleuf, op ca. 12 mm.
  - De schoen hoeft geen grond te verplaatsen, dus hij geeft bijna geen trekkracht. Dat is het verschil met een mes of een omgekeerde-T-tand.
- **Diepte.** Een PE-ring Ø 270 aan de +x kant van de schijf rolt op het maaiveld, precies waar gesneden wordt. Diepte = (schijf − ring) / 2 = 15 mm.
  - Een ander diepte vraagt een andere ring: Ø 290 / 280 / 270 / 260 / 250 geeft 5 / 10 / 15 / 20 / 25 mm.
  - In de eerste versie regelde de aandrukrol de diepte, 265 mm achter de schijf. Over bulten en molshopen gaf dat sd 11,5 mm: slechter dan de starre balk van de toediener. Met de ring op de schijf is het sd 1,4 mm (§ 7).
- **Dichtdrukken.** Een massief rubber rol Ø 200 × 40 zit op een eigen rolarm met een torsieveer (ca. 35 N). De rol drukt de sleuf dicht en volgt het maaiveld los van de diepte.
- **Bodemvolging per rij.** Elk element hangt aan een eigen sleeparm. Een zachte drukveer (4 N/mm, ca. 375 N voorgespannen) zit op een veerpoot tussen arm en balk.

![element van opzij](previews/9_unit_side.png)

![schoen en schijven van onderen](previews/7_boot_detail_from_below.png)

## 3. Wat er van de toediener overblijft

Basis is de [eenvoudige toediener versie 2](../../liquid%20fertilezer%20applicator/simple_v2/ONDERBOUWING.md).

| | Toediener simple_v2 | **Doorzaaier** |
| --- | --- | --- |
| Bok op de robotbalk, draaipunt (−70, 200), bouten M10 in het gatenraster | ja | **zelfde**; armen op x = ±62,5 (tussen de elementen door), langgatplaten lager en hoger doorgetrokken |
| Hefraam met balk 60×60×4 | balk star, 2 dieptewielen | **balk met koppelflenzen, geen dieptewielen**: elk element volgt zelf de grond |
| Actuator met langgat | 1500 N, slag 200, hefraam zweeft op zijn gewicht | **3000 N, slag 150; 2 gasveren duwen het hefraam omlaag** (§ 5) |
| Snijden | schijf Ø 300 × 4, 45 mm diep | schijf Ø 300 × 3, **15 mm**, 7° scheef |
| In de sleuf | mes + RVS-buisje, vloeistof op 27 mm | **zaaischoen + zaadbuis, zaad op ca. 12 mm** |
| Dichtdrukken | – | **aandrukrol per rij** |
| Dosering | 12 V-membraanpomp, drukregelaar, doseerplaatjes | **zaadbak 41 + 18 l, 2 nokkenrollen, 2 wormwielmotoren met encoder** |
| Rijen | 5 op 200 mm | **8 op 125 mm** |
| Massa werktuig / hefraam | 101 / 70 kg | **136 / 104 kg** (lege bak) |

## 4. Het element in maten

| Onderdeel | Uitvoering |
| --- | --- |
| Houder | klemplaat 76 × 8 onder de balk, 2 beugelbouten M12, 2 wangen 40 × 6 naar het draaipunt, veertoren met ankerplaat |
| Sleeparm | koker 30 × 30 × 3, draaibus Ø 30 op bout M16, draaipunt 150 mm onder de balk en 150 mm boven de grond (laag: de trekkracht drukt de arm weinig omhoog) |
| Schijf | vlakke kouterschijf Ø 300 × 3, gehard, op lagernaaf (2 × 6203-2RS) en asbout M20 door een schuin afgezaagde bus (7°) |
| Dieptering | PE-HD Ø 270 / 200 × 15, 4 bouten M8 door de schijf |
| Zaaischoen | slijtvast staal 12 mm, gelast aan de zaadbuis RVS 20 × 1,5; onderkant 3 mm boven de onderkant van de schijf |
| Aandrukrol | massief rubber Ø 200 × 40, rolarm strip 36 × 8 op bout M12, torsieveer; slag −40/+30° |
| Veerpoot | stang M12 met oog, drukveer draad 4 / Ø 41 / 12 windingen (ca. 4 N/mm), stelmoer onder de schotel, stopmoer boven de ankerplaat (arm zakt max. 12°) |
| Zaadslang | PVC-spiraalslang 20/26 van de uitloop naar de zaadbuis, minstens 55° helling |
| Massa | element 9,5 kg, waarvan de sleeparm met alles wat meedraait 6,7 kg |

De naaf, de arm en de schoen zitten allemaal aan de schaduwkant (−x). De +x kant, waar de grond opzij gaat, is vrij.
Alle 8 elementen staan dezelfde kant op. De schijven geven samen ca. 80 N zijkracht naar −x (aangenomen: 0,4 × de
trekkracht van de schijf). De robot stuurt dat weg. Wie dat niet wil, kan bij een tweede module de elementen
spiegelen.

![detail elementen](previews/6_unit_detail.png)

## 5. Neerdruk: gewicht alleen is niet genoeg

Dit is de belangrijkste les van het ontwerp. Een schijf moet de zode in gedrukt worden. Geschat (zie `ovs_calc.LOADS`):

| Per element | Normaal (vochtig, kort gegraasd) | Zwaar (droog, dichte zode) |
| --- | --- | --- |
| Schijf 15 mm de zode in | 90 N | 180 N |
| Aandrukrol (torsieveer) | 35 N | 35 N |
| Minimaal op de dieptering (anders komt de schijf niet op diepte) | 20 N | 20 N |
| Trekkracht schijf / schoen | 25 / 8 N | 45 / 15 N |

- **Het hefraam weegt 104 kg (met 20 kg zaad 124 kg), maar de bok draagt een deel.** Het zwaartepunt ligt 435 mm achter het draaipunt; de schijven en rollen liggen 470–765 mm erachter.
  - Met alleen het gewicht houdt elke schijf **26 N**; nodig is 90 N.
  - Zonder hulp zou er 89 kg ballast op de balk moeten. Die moet de robot dan ook heffen (§ 9).
- **Oplossing: robotgewicht gebruiken met 2 gasveren.** De gasveren (samen 750–1000 N, ca. 870 N in werkstand) zitten naast de langgatplaten van de bok. Ze duwen het stangoog van de actuator naar beneden, en via de actuator het hefraam.
  - Het hefraam blijft vrij zweven in het langgat (−8 tot +9°). De duwkracht is bijna constant.
  - Bij heffen trekt de actuator het oog onderin het langgat. Dan duwen de gasveren tegen de bok zelf. De actuator hoeft ze niet te overwinnen.
  - Met de gasveren houdt elke schijf **105 N** bij een lege bak.
- **Twee instellingen, elk met een eigen taak:**
  - de **gasveren** bepalen hoeveel neerdruk er is: 2 × 400 N normaal, 2 × 650 N voor de zware zode met 4 rijen;
  - de **voorspanning van de drukveren** bepaalt alleen op welke hoogte het hefraam zweeft: 310 N lege bak, 365 N volle bak; 5,8 mm moer = 10 N op de ring.

| Normaal, 8 rijen, gasveren 870 N | Lege bak | Volle bak (20 kg) |
| --- | --- | --- |
| Op de dieptering per element | 33 N | 54 N |
| Kracht per element op de grond (schijf + ring + rol) | 158 N | 179 N |
| Wat het werktuig aan de robot trekt (omhoog) | 249 N | 217 N |

| Gasveren (volle bak) | 0 | 400 N | 800 N | 1000 N | 1300 N |
| --- | --- | --- | --- | --- | --- |
| Normaal 8 rijen: kracht op de ring | −17 N (schijf niet op diepte) | 15 N | 48 N | 64 N | 89 N |
| Normaal 8 rijen: trekkracht / grip | 292 / 1003 N | 304 / 941 | 330 / 811 | 343 / 745 | 363 / 647 |

Zware zode met 8 rijen vraagt 1840 N gasveerkracht. Dan trekt het werktuig 830 N van de robot af en is de grip
kleiner dan de trekkracht (§ 6). **In zware zode dus met 4 rijen**: zet elk tweede element omhoog met de stelmoer, of
haal het eraf. Dan is 2 × 370 N genoeg.

## 6. Trekkracht

| | Toediener simple_v2 | **Doorzaaier 8 rijen** | **Doorzaaier 4 rijen** |
| --- | --- | --- | --- |
| Normaal | 461 N | **335 N** | 154 N |
| Zwaar | 875 N | 540 N | **278 N** |
| Grip robot (μ = 0,5) | ca. 950 N | 788 N (984 N met 40 kg frontgewicht) | 764 N (zwaar) |

Wat de trekkracht laag houdt:
- **Ondiep.** 15 mm in plaats van 40–45 mm. Dit is ook de zaaidiepte uit het onderzoek.
- **Eén dunne schijf per rij**, geen tweede schijf, geen mes of tand. De schoen loopt in de schaduw van de schijf.
- **Laag draaipunt van de sleeparm** (150 mm boven de grond). De trekkracht drukt de arm weinig omhoog, dus er hoeft minder neerdruk bij.
- **Rijen uitzetten**: 4 rijen op 250 mm halveert de trekkracht. Voor klaver past dat bij strokenzaaien: klaver verspreidt zich zelf (Arkansas).
- **Wiedeggen in een aparte werkgang.** Een eg voor de schijven (zoals Evers Grass Profi) kost op 1 m al snel 200–400 N extra. Met een aparte werkgang blijft de doorzaaier binnen de grip van de robot.

## 7. Bodemvolging

![bodemvolging vergeleken](previews/13_ground_following.png)

Dezelfde hobbelige strook als bij de toedieners: golvend maaiveld, molshopen, kuilen en een richel. Ook dezelfde 80
robotposities en dezelfde robothouding op vier wielen. Gerekend met `ovs_ground.py`:
- elke arm draait tot de dieptering het maaiveld raakt;
- de rol volgt het maaiveld op zijn rolarm;
- het hefraam zweeft tot de grondkrachten gelijk zijn aan gewicht + gasveren.
- Aangenomen: de ring zakt 0,075 mm per N extra belasting in.

| Werkstand, 80 posities × rijen | Toediener simple_v2 (starre balk) | **Doorzaaier** |
| --- | --- | --- |
| Afwijking van de ingestelde snijdiepte | −35 tot +22 mm | **−4 tot +7 mm** |
| Standaardafwijking | 8,7 mm | **1,4 mm** |
| Binnen ±5 mm | 59 % | **99,5 %** |
| Snijdiepte (ingesteld 15 mm) | – | 10,9–22,3 mm, gemiddeld 14,6 |
| Schijf uit de grond / te weinig neerdruk | – | 0 / 0 |
| Hefraam | – | zweeft op alle 80 posities (−5,4 tot +6,7°), nooit tegen een aanslag |
| Aandrukrol los van de grond | – | 16 van de 640 (2,5 %), achter molshopen |

- Waar de diepte toch afwijkt, komt dat door wisselende kracht op de ring. Die kracht wisselt met de armhoek: ca. 7 N per 10 mm veerweg, van 4 tot 157 N op deze strook.
  - Een zachtere veer of een luchtveer per rij maakt dit nog vlakker.
- De aandrukrol verliest vooral contact achter molshopen. Wiedeggen vooraf haalt die weg (§ 12).
- Het verschil met de toediener komt van de **diepte-instelling op de schijf zelf** en de **arm per rij**. Bij de toediener hangen 5 schijven aan één starre balk met dieptewielen ernaast.

## 8. Dosering

Zaadbak van aluminium 2 mm, met een schuin schot in twee vakken:
- **voor 41 l gras**;
- **achter 18 l fijn zaad** (klaver, kruiden).

Elk vak heeft een eigen nokkenrol met schroefvormige groeven (continue stroom, geen klonten) en 8 uitlopen op de
rijafstand. Beide rollen lopen in hetzelfde doseerhuis en vallen per rij in dezelfde uitloop.

Twee 12 V-wormwielmotoren met encoder (70 omw/min onbelast) draaien de rollen. Het toerental volgt de rijsnelheid van
de robot (GNSS/wielen), zo blijft de dosis in kg/ha gelijk. Klaver en gras zijn apart in te stellen. Aan het
einde van de rij stopt de dosering.

| Zaad (storthoogte-dichtheid, aangenomen) | Rol | kg/ha → omw/min bij 0,75 m/s |
| --- | --- | --- |
| Engels raaigras tetraploïd (0,35 kg/l) | gras, 2,0 cm³/omw/uitloop | 15 → 12; 25 → 20; 40 → 32 |
| Engels raaigras diploïd (0,40 kg/l) | gras | 15 → 11; 25 → 18; 40 → 28 |
| Witte klaver (0,78 kg/l) | fijn, 0,15 cm³/omw/uitloop | 3 → 14; 5 → 24; 6 → 29 |
| Rode klaver (0,78 kg/l) | fijn | 10 → 48; 12 → 58; 13 → 63 (grens motor) |
| Cichorei / smalle weegbree (0,5 kg/l) | fijn | 2 → 15; 4 → 30; 6 → 45 |

- **Rode klaver op 13 kg/ha** vraagt bij 0,75 m/s 63 omw/min, net boven de geregelde grens van 60. Rij dan iets langzamer (0,7 m/s), of gebruik een fijne rol met grotere groeven.
- **Bak vol**: 0,36 ha bij 40 kg/ha raaigras, 0,58 ha bij 25 kg/ha. Het fijne vak is goed voor ca. 2,8 ha witte klaver op 5 kg/ha.
- **Capaciteit**: 0,27 ha/h theoretisch bij 0,75 m/s.
- **IJken**: de cm³ per omwenteling en de dichtheden zijn ontwerpwaarden. Doe per zaad een afdraaiproef: motor 50 omwentelingen laten draaien, opvangen per uitloop, wegen, en de g/omw in de besturing zetten.

![doseerhuis en motoren](previews/8_metering_detail.png)

## 9. Heffen en de balans van de robot

| | Waarde |
| --- | --- |
| Actuator | 12 V, 3000 N, slag 150 (inbouw 265 / uit 415), ca. 12 mm/s (aangenomen) |
| Nodige kracht (1,5 × marge, volle bak) | 2450 N |
| Hefhoek | 19,7° |
| Vrije slag in het langgat | 44 mm, 3,7 s |
| Schijven en schoenen uit de grond | na 84 mm, 7,0 s |
| Helemaal geheven | 12,5 s; schijven 104 mm, aandrukrollen 101 mm vrij |

**De vooras wordt te licht.** Het hefraam hangt geheven bijna 0,5 m achter de achteras. Met de aanname van de
toedieners (robot 150 kg, zwaartepunt 500 mm voor de achteras):

| Vooras geheven | N |
| --- | --- |
| Volle bak | **59** |
| Lege bak | 136 |
| Volle bak + **40 kg frontgewicht** | **451** |

- **Er is ca. 40 kg frontgewicht nodig** voor 25 % van het gewicht op de vooras.
  - Gebruik bijvoorbeeld stalen platen op de voorste balk, of een tank met water voorop.
  - Het frontgewicht geeft in het werk ook meer grip: 984 in plaats van 788 N.
- **Weeg eerst de echte robot per as.** De 150 kg en het zwaartepunt zijn een aanname. Een zwaardere robot heeft minder of geen frontgewicht nodig.
- De schijven zijn al 3 mm, de zaadbak is aluminium. Lichter maken zonder in te leveren op neerdruk gaat bijna niet: de neerdruk komt nu juist van de robot via de gasveren.

![geheven met robot](previews/10_lifted_side_with_robot.png)

## 10. Breder maken met modules

Eén module is 1000 mm van flens tot flens en bevat:
- 8 elementen op 125 mm;
- een eigen zaadbak met dosering en twee motoren;
- één stekker naar de besturing.

Koppelen:
- De balk heeft aan beide kanten een flens 100 × 100 × 8 met 4 gaten M12.
- Twee modules tegen elkaar geschroefd houden de rijafstand van 125 mm over de naad: rij 8 op +437,5, rij 1 van de volgende op +562,5.
- Elk element zit met twee beugelbouten op de balk. Rijen verschuiven of uitzetten gaat dus zonder lassen.

Wat de Bruut aankan (trekkracht in N; grip ca. 790 N, met frontgewicht ca. 980 N):

| Breedte | 8 rijen/m normaal | 8 rijen/m zwaar | 4 rijen/m normaal | 4 rijen/m zwaar |
| --- | --- | --- | --- | --- |
| 1 m | 308 | 524 | 154 | 262 |
| 2 m | 616 | 1048 | 308 | 524 |
| 3 m | 924 | 1572 | 462 | 786 |

- **Trekkracht.** Normaal kan 2 m met 8 rijen/m, of 3 m met 4 rijen/m.
- **Heffen.** Dit is de echte grens. Al bij 1 m is frontgewicht nodig. Een tweede of derde module (elk ca. 95 kg met zaad) kan de robot niet aan de bok heffen.
- **Wat er nodig is voor 2–3 m** (niet uitgewerkt):
  - elke extra module krijgt een eigen steunwiel achter (zwenkwiel met eigen hefactuator), zodat het werktuig half gedragen wordt in plaats van aan de bok te hangen;
  - de buitenmodules scharnieren om een as in de rijrichting op de flenzen, zodat ze dwars de grond volgen;
  - een schuine trekstang naar de bok vangt hun trekkracht op.
- **Zwerm als alternatief.** Twee of drie robots met elk een module van 1 m. Dat past bij een veldrobot en vraagt geen ander werktuig.

## 11. Kosten (indicatief, excl. btw, prijsniveau 2026)

| Post | € |
| --- | --- |
| Staal (ca. 40 kg) | 120 |
| 8 kouterschijven Ø 300 × 3 | 170 |
| 8 lagernaven met asbouten M20 | 200 |
| 8 aandrukrollen, rolarmen, torsieveren | 150 |
| 8 + 16 diepteringen PE (3 maten) | 120 |
| 8 drukveren, veerstangen | 70 |
| 8 zaaischoenen + zaadbuizen | 90 |
| Beugelbouten en bouten | 75 |
| Zaadslang | 30 |
| Zaadbak aluminium met deksel | 190 |
| Doseerhuis, 2 nokkenrollen, lagers | 130 |
| 2 wormwielmotoren met encoder | 70 |
| Motorregelaars, microcontroller, kastje, kabel | 70 |
| Actuator 3000 N | 130 |
| Gasveren 2 × 400 N (+ set 650 N) | 60 |
| **Totaal** | **ca. 1675** |

Ter vergelijking: een Moore Unidrill kost nieuw € 34.500 (Nieuwe Oogst, 2022), maar is 3 m breed en vraagt een trekker.

## 12. In het veld: wat het onderzoek zegt over de werkwijze

1. **Kort maaien of grazen tot 4–5 cm** vlak voor het zaaien. Dit gaf 2 × zoveel kiemplanten (WUR).
2. **Wiedeggen in een aparte werkgang**, voor ≥ 40 % open grond en om molshopen te slechten (Super-G, WUR).
3. **Zaaien eind augustus–september** in vochtige grond, bodem ≥ 6 °C. Is het droog, dan wachten op regen. Gasveren van 2 × 650 N zijn een noodgreep.
4. **Diepte**: gras 10–15 mm (ring Ø 270–280), klaver 5–10 mm (ring Ø 280–290).
5. **Geen stikstof of drijfmest** rond het zaaien. Die helpt de oude zode, niet de zaailingen.
6. **Klaver inoculeren** of gecoat zaad gebruiken. pH ≥ 6.
7. **Vroeg maaien of grazen** zodra de oude zode 20–30 cm is. Let op muizen.

## 13. Geschat, niet gemeten

- **Bodemkrachten** (`ovs_calc.LOADS`): de neerdruk die een schijf nodig heeft (90 / 180 N), de trekkracht van schijf en schoen, de zijkracht en de rolweerstand. Dit is de grootste onzekerheid.
  - Meet het voor je bouwt: één schijf met ring op een balkje, gewichten erop, de zode in drukken op een vochtige en een droge dag. Trek hem daarna met een veerunster.
- **Inzakken van de dieptering**: 0,075 mm/N.
- **Aandrukrol**: kracht 35 N en torsieveer.
- **Doseerrollen**: cm³ per omwenteling en storthoogte-dichtheden van het zaad (ijken).
- **Motor en actuator**: toerental, snelheid en kracht uit typische datasheets.
- **Robot**: 150 kg, zwaartepunt 500 mm voor de achteras, μ = 0,5. Dit is de aanname van de toedieners.
- **Schoen in de sleuf**: of het zaad echt op de bodem van de sleuf valt, en hoe ver de sleuf dichtvalt voordat de rol komt, hangt af van vocht en grondsoort. Proef met een stukje rijbaan en uitgraven.

De bodemvolging is quasi-statisch gerekend, net als bij de toedieners. Dynamica (stuiteren van de schijf, dempen van
de gasveren) zit er niet in. Een animatie zoals bij de toedieners is nog niet gemaakt.
