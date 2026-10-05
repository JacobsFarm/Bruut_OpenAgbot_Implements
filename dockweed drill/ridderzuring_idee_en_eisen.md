# Ridderzuringfrees ("vermorzelaar") voor de AgBot / OpenAgbot "Bruut"

Aanbouwdeel dat **plant voor plant** ridderzuring kapotmaalt: een CNC-portaal met een X-as (links-rechts) en een Z-as (op-neer). Daaraan hangt een snellopende frees die de wortelkop en de bovenste penwortel fijnmaalt. Een pot eromheen houdt de grond op zijn plek. Een tweede opzetstuk maait de plant bovengronds af. Volledig elektrisch (48 V), gemaakt met makkelijk verkrijgbare onderdelen. Het concept is nagebouwd op **Robot Ruud** (WUR / Joost Samsom).

| Bestand | Inhoud |
|---|---|
| `ridderzuring_ontwerp.py` | Parametrisch FreeCAD-script (alle maten in `P = dict(...)` bovenaan) met rekenwerk en export |
| `ridderzuringfrees.FCStd` | FreeCAD-model, getoond met de frees 150 mm diep. Groepen: Bok, X_as, Z_as, Spil, Pot, Gereedschap, Camera, Elektra |
| `ridderzuringfrees.step` | STEP-export, zonder de referentie-robot en de omgeving |
| `dxf/*.dxf` | Snijcontouren (laser/plasma) van 15 plaatdelen |
| `render_*.png` | Aanzichten: werkstand, rijstand, maaien en detail van de frees in de grond |

Opnieuw opbouwen in FreeCAD (Python-console):

```python
exec(open(r"F:/veldrobot/aanbouwdelen/Design ridderzuring boor/Design/ridderzuring_ontwerp.py", encoding="utf-8").read())
maak_renders()     # optioneel: alle plaatjes opnieuw (rijstand, maaien, details)
```

Een andere stand bekijken: `build(x_slede=-300, z_frees=280)` (rijstand) of `build(gereedschap="maai", z_frees=30)`.

---

## 1. Wat we leren van Robot Ruud, het gesprek met Joost en het BRUUT-concept

### Do's

| Do | Bron | Hoe in dit ontwerp |
|---|---|---|
| **Hoog toerental**, werkt als een staafmixer en niet als een boor. Te langzaam geeft grove wortelstukken, die weer uitlopen ("dan gaat hij zich juist vermeerderen") | Joost | 1500 rpm (14 m/s tipsnelheid), regelbaar tot 3000. Langzaam insteken (25 mm/s) geeft plakjes van **0,25 mm** |
| Gat van **~18 cm**, diepte **~15 cm**. De zode groeit snel dicht, inzaaien is niet nodig en koeien krabben de kleine gaten niet open | Joost, WUR-artikel | Frees Ø180, standaard 150 mm diep, max. 200 mm |
| Plant **boven én onder de grond** versnipperen | Joost | Frees gaat door rozet, wortelkop en penwortel heen. De pot houdt alles op zijn plek |
| Bij een **pol** met veel zuring: per keer een paar planten eruit, later terugkomen. Niet 2 m² zwart maken | Joost | Software: maximaal aantal behandelingen per m² per ronde |
| **Kap + kunstlicht** voor de camera werkt beter dan alleen software-correctie | Joost | LED-lichtbalk naast de camera. 's Nachts werken kan, eventueel een schortje als lichtkap |
| **Elektrisch**: precies te sturen en te meten (encoder, stroom) | Joost | Closed-loop stappenmotoren, VESC op de spil |
| **Modulair**, simpel, eerst 60–80 % werkend krijgen | Joost / jij | Bok met klemmen, gereedschap met 4 bouten, alle maten parametrisch |
| Regrowth zit alleen in het **bovenste deel van de penwortel** | Onderzoek (zie bronnen) | Minimaal ~10 cm, liever 15 cm. 20 cm als het echt weg moet |

### Don'ts

| Don't | Waarom |
|---|---|
| Hydrauliek op het veld | Een gesprongen slang betekent olie in het land. Kubota, pompen en ventielblok kostten bij Ruud ±€25.000 |
| Te traag draaien (gewone hydromotor, een paar honderd toeren) | Grove stukken, en die lopen weer uit |
| Bouwer een blanco mandaat geven of alles integreren | Bij de tweede machine werd het 3–4× duurder dan begroot |
| Zware machines op zachte (veen)grond | Bodemdruk. Daarom ook letten op het gewicht van dit aanbouwdeel (§8) |
| Een pol in één keer kaal frezen | Uitdroging en onkruid |

### Wat ik van het BRUUT.STP-concept (inspiratiemap) heb overgenomen en veranderd

| | BRUUT.STP | Dit ontwerp | Waarom |
|---|---|---|---|
| Opbouw | 2 liggende geleidingen + Z-slede, motor bovenop | Zelfde idee | Goed CNC-principe |
| Geleiding | Aftakas-profielbuizen die in elkaar schuiven | HGR15-profielrails | Twee parallelle schuifparen klemmen snel (overbepaald), staal op staal met vuil |
| Freesas | Ø15 mm, ~210 mm vrij onder het lager (280 mm tot de punt) | Ø35 in 2× UCF207 | Ø15 buigt bij 300 N zijkracht ±3 mm en krijgt ±190 MPa wisselspanning. Dat breekt door vermoeiing en trilt |
| Frees | 3 kleine bladen, Ø~110 | Kruisfrees Ø180 met 4 tanden + centreerpunt | Joost: 18 cm. MEV-Ampferfräse: 180 mm |
| Pot | ontbreekt | Pot Ø250, rust met eigen gewicht op de zode | Grond blijft op zijn plek, en de pot werkt als bescherming |

---

## 2. Eisen

### Functioneel
| # | Eis | Waarde |
|---|---|---|
| F1 | Gat / werkdiameter | Ø180 mm |
| F2 | Freesdiepte | 0–200 mm instelbaar, standaard 150 mm, gemeten vanaf het **werkelijke maaiveld** (pot-sensor) |
| F3 | Toerental | 1000–2000 rpm vermorzelen (standaard 1500), tot 3000 rpm maaien |
| F4 | Werkbreedte X | 1000 mm (slag), plaatsnauwkeurigheid ±2 mm |
| F5 | Z-slag | 480 mm: rijstand 280 mm boven maaiveld tot 200 mm diep |
| F6 | Grond | blijft in het gat (pot). Geen weggeslingerde stenen of kluiten |
| F7 | Tweede functie | maaischijf voor bovengronds afmaaien of kort "scalperen" net boven de grond |
| F8 | Capaciteit | ±20 s per plant, ≈ 150–180 planten per uur |

### Robot / aanbouw
| # | Eis |
|---|---|
| R1 | 48 V uit de robotaccu |
| R2 | Monteren zonder boren of lassen aan het robotframe: **4 kruisklemmen** op 2 dwarsbalken (koker 40×40) |
| R3 | Aan de **aangedreven as** (hubmotoren). Robot rijdt tijdens het wieden met het portaal vooruit (§8) |
| R4 | Robot staat stil tijdens het frezen. Rijden mag alleen als de Z-as boven is (vergrendeling) |
| R5 | Neerwaartse kracht < 600 N, zodat de robot niet opgetild wordt |

### Bouw en onderhoud
| # | Eis |
|---|---|
| B1 | Plaatdelen laser- of plasmasnijden (DXF), alleen rechte lijnen en bogen |
| B2 | Standaard koopdelen: alu-profiel 40×80, HGR15, SFU1610, NEMA 23, UCF207, HTD-5M, BLDC + VESC |
| B3 | Gereedschap wisselen met **4 bouten M10**. Slijtdelen (tanden) van Hardox |
| B4 | Overbelasting (steen, boomwortel) mag niets breken: stroomgrens op spil en assen |

### Veiligheid
| # | Eis |
|---|---|
| V1 | Spil draait alleen als de pot op of vlak boven de grond is |
| V2 | Noodstop robot = 48 V van het aanbouwdeel eraf (magneetschakelaar). VESC remt, Z-motor valt op de rem |
| V3 | Mensen > 5 m (autonoom werken). Bij maaien met opgetilde pot: rubber flap aan de potrand |

---

## 3. Gekozen principe (en de alternatieven)

| Keuze | Gekozen | Bekeken alternatieven |
|---|---|---|
| **Kinematica** | Portaal X + Z, robot = Y (zoals Ruud) | Zwenkarm (lichter, maar geen CNC-rechthoek). Portaal tussen de assen (de spil loopt dan door de langsbalken van het frame, dus maar ±230 mm slag) |
| **X-geleiding** | 2 alu-profielen 40×80 op 300 mm met HGR15-rails | SBR16 (verchroomd, vergevingsgezind, iets zwaarder). Schuifpoortrail met rolwagens (spotgoedkoop en onverwoestbaar, maar +15 kg). V-slot (te slap) |
| **X-aandrijving** | HTD-5M tandriem 15 mm (staalkoord) met omega-aandrijving, NEMA 23 + 5:1 | Ketting 08B (roest/olie), tandheugel |
| **Z-geleiding** | Koker 120×60×3 met HGR15-rails | Koker-in-koker met PE-glijstrips (robuuster in vuil, meer wrijving en speling) |
| **Z-aandrijving** | Kogelomloopspindel SFU1610 + NEMA 23 closed-loop **met rem** | Lineaire actuator 1500 N (simpel en zelfremmend, maar ~30 mm/s: cyclus +10 s) |
| **Spil** | Direct: motor, klauwkoppeling, as Ø35 in 2× UCF207 | Riemreductie 1:2 (meer koppel bij 1500 rpm, extra delen) |
| **Frees** | Hardox-kruisfrees Ø180, 2 niveaus, 4 tanden, centreerpunt | 2 rotorkopegtanden op een eigen naaf (koopdeel, zwaar). Grondboor (voert grond af, en dat is niet de bedoeling) |
| **Pot** | Rust met eigen gewicht (≈4 kg) op 2 vrije stangen | Veerbelast (bij 230 mm slag geen ruimte voor drukveren) |
| **Montagekant** | Kop aan de **hubmotorkant** | Kop aan de gestuurde kant: aangedreven wielen houden dan ~25 kg grip (§8) |

**Een CNC-trucje:** de pot-sensor werkt als de *taster* (probe) van een CNC-frees. Met `G38.2` zakt de Z tot de pot de zode voelt. Die hoogte is het maaiveld, en daarvandaan gaat de frees precies 150 mm dieper. Hobbels en kuilen in het land maken dus niets uit.

---

## 4. Opbouw (zie model)

| Groep | Onderdelen |
|---|---|
| **Bok** (vast op de robot) | 2 draagarmen koker 40×40×3 (630 lang) op 2 dwarsbalken van de robot met **4 kruisklemmen** (platen 90×90×5 + 4× M10×100). 2 staanders 50×50×3, 2 schoren 25×25×2 |
| **X-as** | 2× alu-profiel 40×80 L=1300 (hart 760 en 1060 boven maaiveld), met M8 + T-moer aan de staanders. 2× HGR15-rail met 4 wagens HGH15CA. Kopplaten alu 10 mm. X-slede alu 10 mm 300×420. Tandriem HTD-5M 15 mm met riemklemmen buiten de kopplaten. Poelie 20T + 2 spanrollen. NEMA 23 closed-loop + planetaire kast 5:1. Inductieve eindschakelaar, rubber eindaanslag |
| **Z-as** | Z-slede koker 120×60×3, L=950, met 2 alu-risers 25×23 en 2 HGR15-rails. 4 wagens HGH15CA op de X-slede. SFU1610 met BK12/BF12, moerhuis op de X-slede. NEMA 23 closed-loop met rem bovenop de slede |
| **Spilbok** (oranje, laswerk) | Achterplaat 6 mm met blindklinkmoeren M10 op de Z-slede. Lagerplaat onder 8 mm (met armen naar de potstangen), lagerplaat boven 6 mm, motorplaat 8 mm, 2 zijplaten 5 mm met vensters |
| **Spil** | BLDC 48 V 1,5 kW 3000 rpm. Klauwkoppeling Ø65. As Ø35 C45 met gelaste flens Ø110 (4× M10 op steekcirkel 80). 2× UCF207 (lagerafstand 160) |
| **Pot** | RVS-pot Ø250×150, 2 mm wand, deksel 3 mm, rubber randstrip en asafdichting. 2 stangen Ø16 met stelringen, schuivend door PE-bussen. Inductieve sensor M12 "grondcontact" bij de stelring |
| **Gereedschap 1** | Vermorzelfrees: onderste kruis Hardox 10 mm met 4 tanden (10×18×26), bovenste kruis 45° verdraaid, kernbuis 48,3×5, flens 10 mm, centreerpunt 60 mm |
| **Gereedschap 2** | Maaischijf Ø200×4 met 3 scharnierende robotmaaiermesjes (tipcirkel Ø230), kernbuis, flens. In het model ligt hij los naast de robot |
| **Camera** | Mast en arm alu 30×30 op de X-slede (de camera beweegt mee). Industriële USB3-camera 320 mm voor de spil, LED-lichtbalk |
| **Elektra** | IP65-kast op de linker staander (VESC, 2 stappendrivers, ESP32-FluidNC, DC/DC, zekering, noodstoprelais). Kabelrups op het bovenste profiel |

---

## 5. Welke 48 V-motor?

**Specificatie:** BLDC (borstelloos) **48 V, 1,5–2 kW, ±3000 rpm nominaal**, met **Hall-sensoren**, een **spie-as** (Ø14–19 mm) en flensbevestiging. Minimaal IP54. Dit is in de praktijk dezelfde klasse als de motor van de geulfrees (daar met een planetaire kast). Eén motortype voor meerdere aanbouwdelen betekent reserveonderdelen uitwisselen.

- **Direct op de spil, zonder vertraging.** Vermorzelen op 1500 rpm geeft het nominale koppel (4,8 Nm), dus ±750 W continu en ±1,5 kW kortstondig (VESC 2× stroom). Maaien gaat op volle snelheid, 3000 rpm.
- **Sturing met een VESC** (bv. Flipsky 75100), via dezelfde CAN-aansturing die al in je repo zit (`VESC/`, `vesc_can.py`).
  - toerental exact regelen,
  - **stroomgrens als elektronische slipkoppeling** (steen, dikke wortel),
  - stroom meten. Daarmee stuur je de insteeksnelheid bij: veel stroom betekent langzamer zakken.
  - actief remmen: de spil staat in < 2 s stil.
- **Waar te vinden:** "48V 1500W/2000W BLDC motor 3000 rpm hall keyed shaft". Dit zijn go-kart/e-motor-motoren (bv. typen die als *MY1020D*/*Kunray* verkocht worden). Er zijn ook industriële 110 mm-BLDC-motoren met een ronde of vierkante flens. Let op: kies een uitvoering met **spie-as**, niet alleen met een kettingwiel erop geperst. Vraag ook naar de IP-klasse.
- **Niet doen:**
  - borstelmotor (MY1020 geborsteld): kan als budgetoptie, maar borstels slijten en je hebt geen toerentalmeting,
  - open outrunner/RC-motor: vuil en water,
  - e-bike-naafmotor: te traag,
  - haakse slijper: 230 V,
  - hydromotor: zie de don'ts.
- **Te zwak in de proef?** Neem 2 kW, of zet er een riem 1:2 tussen (HTD-8M), maar dan maai je maximaal op 1500 rpm.

---

## 6. Gereedschappen en werkwijze

**Vermorzelen (gereedschap 1), cyclus per plant**
1. Camera (mee op de X-slede) en AI vinden de plant. De robot stopt met de plant onder de spillijn (RTK/odometrie).
2. `X` naar de plant. Spil op 1500 rpm.
3. `G38.2` Z omlaag tot de pot de zode raakt. Dat is het maaiveld.
4. Insteken naar 150 mm met 25 mm/s: de wortel wordt in plakjes van ±0,25 mm gesneden.
5. 1 s nadraaien, dan **draaiend omhoog** (mengt nog een keer). Pas daarna komt de pot los van de grond.
6. Ijlgang naar rijstand, spil remt. Robot rijdt door.

```gcode
G90 G0 X420            ; spil boven de plant
; spil aan via VESC (CAN) 1500 rpm
G38.2 Z-300 F3000      ; zakken tot pot-sensor schakelt = maaiveld
G91 G1 Z-150 F1500     ; 150 mm insteken, 25 mm/s
G4 P1                  ; 1 s nadraaien
G1 Z150 F3000          ; draaiend terug naar maaiveld
G90 G0 Z0              ; rijstand
; spil uit (VESC remt)
```

**Maaien / kort frezen (gereedschap 2)**
- Wisselen: 4 bouten M10 (sleutel 17), van onderen door de pot bereikbaar.
- Zakken tot de pot de grond raakt: de mesjes staan dan **30 mm** boven het maaiveld. Verder zakken (de pot schuift op) geeft een lagere snede, tot "scalperen" op 0–10 mm.
- Grote rozet of bloeistengels: op 2–3 posities naast elkaar (X verschuiven, robot iets verzetten). Doel: **bloeistengels afmaaien voor het zaad rijp is**. Eén plant kan tienduizenden zaden geven die jaren kiemkrachtig blijven.

---

## 7. Kengetallen (uit het script)

| Grootheid | Waarde |
|---|---|
| Spil vermorzelen | 1500 rpm, tipsnelheid 14 m/s, 750 W nominaal / 1,5 kW piek |
| Spil maaien | 3000 rpm, tip Ø230: 36 m/s |
| Insteek 25 mm/s | 0,25 mm per tand: plakjes die niet meer uitlopen |
| Gat Ø180×150 | 3,8 liter grond. Snij-energie 2–8 kJ, dus 0,3–1,3 kW gemiddeld over 6 s |
| Energie per plant | ≈ 2–3 Wh (spil + assen). 1000 planten ≈ 2–3 kWh |
| Z-as | SFU1610 + 3 Nm: 1700 N max. Software-grens ~600 N. Ijlgang 100 mm/s |
| X-as | 5:1 + 20T: houdkracht ~900 N, ijlgang 200 mm/s |
| Cyclus | ≈ 22 s per plant, ≈ **165 planten/uur** (MEV-Ampferfräse met trekker en bestuurder: 50–200 gaten/uur bij 10 kW) |
| Spilas Ø35 | 300 N zijkracht: 0,4 mm doorbuiging, 25 MPa. Kritisch toerental ~5000 rpm (maaien = 60 %) |
| Massa aanbouwdeel | **≈ 91 kg**: spil 23, X-as 21, Z-as 20, bok 14, elektra 5, pot 4, frees 2,5, camera 1,6 |
| Bewegende massa | X ≈ 59 kg, Z ≈ 48 kg |

---

## 8. Gewichtsverdeling robot (belangrijk!)

91 kg op ±0,4 m vóór een as, aan een robot van ±150 kg met 0,7 m wielbasis, is veel. Het script rekent het door (aanname robot 150 kg, zwaartepunt midden tussen de assen):

| Situatie | As aan portaalkant | Verre as |
|---|---|---|
| Robot zonder aanbouw | 75 kg | 75 kg |
| Portaal aan de **gestuurde** kant | 216 kg (gestuurd) | **25 kg op de hubmotoren**: geen grip, ✗ |
| Portaal aan de **hubmotorkant** | 216 kg (aangedreven) | 25 kg (gestuurd): sturen wordt licht |
| Idem + **accu aan de verre kant** | 184 kg (aangedreven) | 57 kg (gestuurd) ✓ |

**Daarom:**
- Monteer het portaal aan de **hubmotorkant** (bij jou nu de achterkant met de trekhaak).
- Laat de robot tijdens het wieden **met die kant vooruit** rijden. Dat is achterwielbesturing, en bij lage snelheid geen probleem.
- Zet de **accu aan de verre kant**. Een 2e accu daar is nuttig contragewicht: twee keer zo lang werken.
- Maximaal ±1170 N neerwaartse kracht voordat de portaal-as loskomt. Begrens de Z-kracht daarom op ±600 N.
- Pas `robot_massa` en `robot_zw_y` in het script aan zodra je de robot gewogen hebt (2 weegschalen onder de assen).
- Een **4WD**-AgBot (staat in je GitHub) lost het ook op.

Lichter maken voor versie 2 (±10 kg): spilbok in aluminium (−4 kg), X-slag 800 mm (−2 kg), camera van de robot gebruiken (−1,6 kg), kleinere klemplaten.

---

## 9. Besturing en elektrisch

- **48 V** uit de robot via zekering 63 A en een magneetschakelaar in de **noodstoplus**.
- **Spil:** VESC 75/100 via CAN naar de Jetson. Stroom ±31 A bij 1,5 kW, pieken 60 A. Kabel 10 mm², kort.
- **X en Z:** NEMA 23 closed-loop 3 Nm. ⚠️ Een "48 V"-accu is vol **54–58 V**, terwijl veel NEMA 23-drivers (HBS57/CL57T) maar tot ±50 V gaan. Twee oplossingen:
  - een **DC/DC 48→36/24 V** (±10 A) voor de drivers,
  - of drivers tot 80 V. Hetzelfde type als je HBS86H voor de stuurmotoren kan ook; controleer dan of de encoder past.
- **Controller:** ESP32 met **FluidNC** (bv. MKS DLC32, of een ESP32 met externe drivers). G-code via USB vanaf de Jetson. Homing met inductieve sensoren (X-min, Z-boven), probe-ingang = pot-sensor.
- **Vergrendelingen:**
  - spil alleen aan onder een veilige Z,
  - robot rijdt alleen als Z-home actief is,
  - stappendriver-alarm (blokkeren) betekent: spil uit, 50 mm omhoog, opnieuw proberen. Na 3× overslaan en de positie loggen.
- **Camera:** je eigen camera met YOLO-model op de Jetson, plus LED-lichtbalk 48 V (of 12 V via DC/DC). 's Nachts werken geeft constant licht. Als het overdag tegenvalt: een lichtschortje rond het camerabeeld (tip van Joost).
- **Kabels naar de Z-slede** (spilmotor, Z-motor, sensor): tweede kabelrups of een spiraalkabel langs de slede (nog niet getekend).

---

## 10. Onderdelenlijst en kosten (indicatief, 2026, incl. btw)

| Onderdeel | Aantal | Waar | € ca. |
|---|---|---|---|
| Alu-profiel 40×80 sleuf 8, 1300 mm (op maat gezaagd) | 2 | Motedis, Dold, Kanya, 123-3D | 50–70 |
| HGR15-rail + 2 wagens HGH15CA, 1300 mm | 2 sets | AliExpress, Amazon, Dold | 70–100 |
| HGR15-rail + 2 wagens, 850 mm | 2 sets | idem | 50–70 |
| SFU1610 L≈950 + moer, BK12/BF12, moerhuis, koppeling | 1 set | AliExpress | 45–70 |
| NEMA 23 closed-loop 3 Nm + driver (X) | 1 | StepperOnline, AliExpress | 60–80 |
| NEMA 23 closed-loop 3 Nm **met rem** + driver (Z) | 1 | StepperOnline | 90–120 |
| Planetaire kast NEMA 23, 5:1 | 1 | StepperOnline | 35–50 |
| HTD-5M 15 mm PU staalkoord 1,5 m + poelie 20T + 2 spanrollen | 1 | AliExpress, riemenhandel | 25–40 |
| BLDC 48 V 1,5–2 kW 3000 rpm, Hall, spie-as | 1 | zie §5 | 120–250 |
| VESC 75/100 | 1 | Flipsky, AliExpress | 130–200 |
| UCF207 + klauwkoppeling + as Ø35 C45 (en draaiwerk) | 1 set | lagerhandel, agrarisch, staalhandel | 70–110 |
| Pot: RVS-buis of pan Ø250 (of stalen buis Ø244,5), stangen Ø16, PE-bussen, stelringen | 1 | bouwmarkt, staalhandel, Action/IKEA-pan | 30–60 |
| Inductieve sensoren M12 | 4 | AliExpress, Conrad | 15–30 |
| ESP32 FluidNC-board | 1 | AliExpress | 30–60 |
| E-kast IP65, DC/DC, zekering, magneetschakelaar, wartels, kabelrups, kabel | 1 | Conrad, Kiwi, AliExpress | 100–150 |
| Camera + LED-balk (als de robotcamera niet gebruikt wordt) | 1 | — | 50–150 |
| Staal: kokers (40×40×3, 50×50×3, 25×25×2, 120×60×3) + laserdelen (DXF) incl. Hardox | — | staalhandel, lasersnijder online | 150–250 |
| Bouten, T-moeren, blindklinkmoeren, verf | — | — | 50–80 |
| **Totaal** | | | **≈ €1.300 – 1.900** |

Ter vergelijking: Ruud kostte destijds ±€25.000 alleen aan motor, pompen en ventielblok.

**Budgetversie (±€1.000):** Z met een lineaire actuator (500 mm, 1500 N, IP65, Hall) in plaats van spindel + stepper met rem. Geborstelde 48 V-motor met simpele regelaar in plaats van BLDC + VESC. Langzamer en minder terugkoppeling, maar het principe kun je er prima mee testen.

---

## 11. Open punten / te controleren

1. **Robot opmeten.** In het model staan aannames uit `parameters.scad`: koker 40×40×2, langsbalken op X = ±375, dwarsbalken op Y = −20 en −470, assen op −150 en −850, bovenkant frame 644 mm. Pas `P` aan.
2. **Robot wegen** en het zwaartepunt bepalen (§8). Daarna `robot_massa` en `robot_zw_y` aanpassen.
3. **Toerental en insteeksnelheid in de proef bepalen** (zie §12): 1000 / 1500 / 2000 rpm × 15 / 25 / 40 mm/s. Na 6–8 weken tellen hoeveel er terugkomen. Joost had ±20 %.
4. **Freesvorm**: blijft natte klei/veen aan de kruisen kleven? Zo nodig minder armen, of tanden schuiner zetten.
5. **Stenen**: stroomgrens VESC + closed-loop-alarm. Eventueel een breekpen in de flens.
6. **Afdichting X-rails**: spatkapje boven het bovenste profiel. Rails regelmatig invetten (HGR is roestgevoelig).
7. **Kabelrups/spiraalkabel** voor de Z-slede uitwerken.
8. **Gatenpatroon wagens en motoren** op X-slede en Z-slede aftekenen van de echte koopdelen (niet in de DXF).
9. **Maaien met opgetilde pot**: rubber flap aan de potrand tegen wegschietende steentjes.
10. **Software**: maximaal aantal planten per m² per ronde (pol niet kaal maken), en een logboek met RTK-positie per behandelde plant (dan kun je na 6 weken terug voor de controle).

---

## 12. Bouw- en testvolgorde (voorstel)

1. **Eerst het proces testen, zonder portaal.** Bouw de spilbok met motor, VESC, frees en pot op een houten statief of aan een kolomboor-/hefinrichting. Frees 20–30 planten met verschillende toerentallen en insteeksnelheden. Log de stroom (VESC) en markeer de plekken. Dit is het grootste onzekere punt en kost maar ±€400.
2. Robot opmeten en wegen. Parameters aanpassen en model opnieuw draaien.
3. Laserdelen bestellen (DXF-map), profielen op maat, koopdelen.
4. Bok + X-as monteren (profielen recht en evenwijdig uitlijnen: eerst één rail vast, de tweede met de wagen meelopend uitlijnen).
5. Z-as + spilbok, dan elektra: noodstop en vergrendelingen eerst. Proefdraaien zonder frees.
6. FluidNC instellen: homing, probe (pot-sensor), stroomgrenzen. G-code-cyclus met de hand testen.
7. Koppelen met de Jetson: camera → plantpositie → robot stopt → G-code. Eerst op losse planten, daarna op een perceel.
8. Na 6–8 weken: hergroei tellen en toerental/diepte bijstellen.

---

### Bronnen
- Gesprek met Joost Samsom (inspiratie/gesprek met joost samson.txt) en WUR-artikel "Ruud weet wel weg met ridderzuring" (Frits van Evert): frees tot 15 cm, hoog toerental, gat ~18 cm.
- MEV GmbH (Oostenrijk), Ampferfräse voor trekker/shovel: gat Ø180 × 250 mm, ±10 kW hydraulisch, 50–200 gaten/uur, ±80 kg (productpagina mev.co.at, via zoekmachine; de pagina gaf bij ophalen een 404)
- Regrowth van *Rumex*-wortelfragmenten (alleen het bovenste wortelgedeelte loopt uit; minimaal bovenste ~9 cm, strikt tot 20 cm verwijderen) — https://www.researchgate.net/publication/344660399 en https://www.sciencedirect.com/science/article/pii/S0570178318300241
- AgBot/OpenAgbot "Bruut": https://github.com/JacobsFarm/Bruut_OpenAgbot (`CAD_designs/config/parameters.scad`, `setup/information/Specs hardware/`)
