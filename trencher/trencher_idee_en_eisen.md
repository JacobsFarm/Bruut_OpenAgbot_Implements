# Geulfrees (trencher) voor AgOpenBot "Bruut"

Aanbouwdeel om in grasland of op maisland een **ondiep geultje** te frezen dat water van een plas naar de sloot afvoert. Elektrisch aangedreven en zo eenvoudig mogelijk te bouwen.

Bestanden in deze map:

| Bestand | Inhoud |
|---|---|
| `trencher_ontwerp.py` | Parametrisch FreeCAD-script (alle maten in `P = dict(...)` bovenaan) |
| `trencher_bruut.FCStd` | FreeCAD-model, getoond op 150 mm werkdiepte |
| `trencher_bruut.step` | STEP-export (zonder de referentiebalken van de robot) |
| `render_*.png` | Aanzichten |

Opnieuw opbouwen in FreeCAD (Python-console):

```python
exec(open(r"F:/veldrobot/aanbouwdelen/trencher/trencher_ontwerp.py", encoding="utf-8").read())
```

---

## 1. Eisen

### Functioneel
| # | Eis | Waarde |
|---|---|---|
| F1 | Geulbreedte | 100 – 200 mm (≈ één spadebreedte), standaard 150 mm |
| F2 | Geuldiepte | 100 – 200 mm, instelbaar |
| F3 | Geullengte per klus | typisch 10 – 20 m, van plas naar sloot |
| F4 | Ondergrond | grasland (zode met wortels), maisland/maisstoppel, natte klei en zand |
| F5 | Grondafvoer | uitgegraven grond naast de geul uitstrooien (niet terug laten vallen in de geul) |
| F6 | Geulbodem | zo glad mogelijk, zonder drempels, zodat het water blijft stromen |
| F7 | Transport | gereedschap volledig opheffen, minimaal 150 mm vrij boven maaiveld |
| F8 | Sturing | rijden langs een AB-lijn van AgOpenGPS/AgOpenBot; heffen, dalen en freesmotor aan/uit vanuit de robot |

### Robot / aanbouw
| # | Eis |
|---|---|
| R1 | Volledig elektrisch, gevoed uit het robotaccu (48 V de voorkeur, 24 V mogelijk, zie §5) |
| R2 | Monteren zonder te boren of te lassen aan het robotframe: beugelbouten om de achterbalk |
| R3 | Licht genoeg dat de robot niet achterover gaat en de voorwielen genoeg grip houden. Streefgewicht < 80 kg (eerste model ≈ 110 kg, zie §6) |
| R4 | Reactiekrachten klein houden, zodat de robot met beperkte tractie toch kan rijden |
| R5 | Met één persoon aan en af te bouwen |

### Bouw en onderhoud
| # | Eis |
|---|---|
| B1 | Plaatdelen laser- of plasmasnijden, met alleen rechte lijnen en bogen. Lassen alleen waar het niet anders kan |
| B2 | Standaard koopdelen: UCFL-flenslagers, ketting 08B-1, BLDC-motor met planetaire kast en een standaard lineaire actuator |
| B3 | Slijtdelen (messen) met 2 bouten te vervangen. De messen zijn van Hardox of een oud graafbakmes |
| B4 | Overbelasting (steen, boomwortel) mag niets breken |

### Veiligheid
| # | Eis |
|---|---|
| V1 | Schijf boven en aan de rechterkant afgeschermd met een kap. De werprichting gaat naar links en weg van de robot |
| V2 | Freesmotor draait alleen als het gereedschap omlaag staat (hoeksensor op het scharnier) |
| V3 | De noodstop van de robot schakelt ook de freesmotor af. Bij blokkeren stopt de motor op stroomgrens |
| V4 | Niemand binnen 5 m tijdens het frezen (stenen en kluiten worden weggeworpen) |

---

## 2. Gekozen principe: schoepenschijf ("mini-greppelfrees")

Bekeken alternatieven:

| Principe | Voordeel | Nadeel | Oordeel |
|---|---|---|---|
| Kettingtrencher (Ditch Witch) | nette, smalle sleuf | veel slijtende delen, groot vermogen, grond blijft op de rand liggen, duur | ✗ |
| Getrokken V-ploeg / greppelploeg | heel simpel, geen motor | vraagt veel trekkracht (> 2 kN), en die heeft de robot niet. De zode scheurt | ✗ |
| Freestrommel (smalle rotavator) | standaard messen | grond valt terug in de geul, werkt slecht in zode | ✗ |
| **Schoepenschijf met kap** | snijdt en werpt in één beweging, weinig onderdelen, kleine reactiekracht | iets meer laserwerk | **✓** |

Werking:
- Een **schijf Ø600 × 10 mm** (laser) met **6 gelaste schoepen**. Op elke schoep zit een **vervangbaar mes van 10 mm**, met 2 × M12 vastgezet. De tipdiameter is **Ø700**.
- Alle messen steken **naar links** uit de schijf. De schijf vormt zo de rechterwand van de geul. Daardoor kunnen lager, kettingkast en draagplaat **rechts buiten de geul** blijven. Bij 200 mm diepte zit de naaf nog 150 mm boven maaiveld.
- De **mesbreedte bepaalt de geulbreedte**. Er komen 3 messets: 100, 150 en 200 mm.
- De schijf draait **tegenlopend**: de onderkant beweegt mee met de rijrichting. De grond wordt dus van onder naar boven gesneden en over de top gegooid. De kap stuurt de grond naar **links** weg, en een verstelbare werpklep regelt de strooibreedte.
- Doordat de schijf tegenloopt, wordt het gereedschap licht de grond in getrokken. Dat helpt de diepte vast te houden. De horizontale reactiekracht is maar ±130 N, dus de robot hoeft nauwelijks te trekken.
- De schijf is **rotatiesymmetrisch**: de hoek van de draagarm maakt niets uit voor de geulvorm. Een eenvoudige **scharnierarm** volstaat dus, een parallellogram is niet nodig.

## 3. Opbouw (zie model)

| Groep | Onderdelen |
|---|---|
| **Bok** (vast op de robot) | voorplaat 8 mm, 2 zijplaten 10 mm, bovenste dwarsbuis Ø42,4, 2 beugelbouten M12 om de achterbalk, scharnierpen Ø25, actuatorpen Ø25 |
| **Arm + draagplaat** (één laswerk) | scharnierbus Ø42,4×5, arm koker 60×60×4, draagplaat 10 mm, actuatorlippen met **sleufgat** |
| **Schijf** | schijf Ø600×10 met lichtgaten en gelaste naaf, 6 schoepen van 8 mm, 6 messen van 10 mm Hardox |
| **Aandrijving** | BLDC 48 V 1,5 kW 3000 rpm met planetaire kast i=10 (300 rpm), links op de draagplaat boven de kap. Ketting 08B-1 15T/15T in een smalle kettingkast (band 3 mm + deksel 6 mm). As Ø35, 2 × UCFL207 |
| **Kap** | 3 mm plaat, gezet in segmenten van 15°, met rechterzijwand. Links open, met verstelbare werpklep |
| **Diepte** | glijslof 70 mm breed rechts naast de geul, ter hoogte van de schijf. Houder met een gatenrij in stappen van 22 mm (~25 mm diepteverschil) |
| **Heffen** | lineaire actuator 6000 N, slag 200 mm (pen-pen ≈ 400 → 600 mm), met eindschakelaars en potmeter |
| **Elektra** | IP65-kast met BLDC-controller en actuatorrelais/-driver. Hoeksensor op het scharnier |

### Zweefstand (de belangrijkste vereenvoudiging)
Het onderste oog van de actuator zit in een **sleufgat van 40 mm**. In werkstand schuift de actuator iets verder uit dan nodig. Het gereedschap rust dan met zijn eigen gewicht op de **glijslof** en volgt het maaiveld. Er is dus geen hydrauliek of krachtregeling nodig.

## 4. Kengetallen (uit het script)

| Grootheid | Waarde |
|---|---|
| Schijftoerental | 300 rpm (via de controller regelbaar) |
| Tipsnelheid | 11 m/s (genoeg om de grond 1–3 m weg te werpen) |
| Askoppel | ≈ 44 Nm, tipkracht ≈ 125 N continu (plus vliegwieleffect van de schijf voor pieken) |
| Geuldoorsnede 150×150 | 0,0225 m³ per meter |
| Rijsnelheid tijdens frezen | 2 – 4 m/min (instelbaar in AgOpenBot) |
| Benodigd freesvermogen | ≈ 250 – 600 W bij 3 m/min (schatting met 200–500 kJ/m³ voor graszode/klei). De 1,5 kW geeft ruim reserve |
| Hap per mes | ≈ 1,7 mm, dus weinig kracht per mes en een rustige loop |
| 20 m geul | ≈ 7 minuten |
| Armhoek | werkstand ≈ −4°, geheven ≈ −30° |
| Actuatorslag nodig | ≈ 160 mm + 40 mm sleuf, dus een slag van 200 mm |
| Massa | ≈ 110 kg (eerste model, nog niet geoptimaliseerd) |

## 5. Besturing / elektrisch

- **Spanning**: 48 V heeft de voorkeur (1,5 kW is dan ≈ 31 A). Op 24 V wordt het ≈ 62 A, wat dikke kabels vraagt. Neem 24 V alleen als de Bruut niets anders heeft, en kies dan eventueel een motor van 1 kW.
- **Motorcontroller** (BLDC, bijvoorbeeld een VESC of een eenvoudige 48 V-controller met PWM-ingang): instellen op een stroomgrens als "elektronische slipkoppeling". Bij een stroompiek of blokkeren:
  1. stopt de robot met rijden,
  2. gaat het gereedschap 50 mm omhoog,
  3. doet de motor een herstart.
- **Actuator**: 12/24/48 V met ingebouwde eindschakelaars. Bij voorkeur een type met **potmeter- of Hall-terugmelding**.
- **Hoeksensor op het scharnier** (potmeter of magnetische encoder, bv. AS5600): meet de werkelijke diepte en vormt de vergrendeling "frees alleen draaien als hij omlaag staat".
- **Koppeling met AgOpenBot**: 3 uitgangen (heffen, dalen, freesmotor aan) en 2 ingangen (hoek, motorstroom). Bijvoorbeeld via de bestaande ESP32/Teensy-machinemodule ("section control" = frees aan, "hydraulic lift" = heffen/dalen).

### Fase 2: verval regelen met RTK (optioneel)
Water stroomt alleen als de geulbodem **afloopt naar de sloot**. Met de glijslof volgt de bodem het maaiveld, en dat is meestal goed genoeg. Wil je een vast verval (bijvoorbeeld 2–5 mm/m), dan kan het zo:
- de RTK-hoogte van de robot vastleggen bij de plas en bij de sloot,
- de actuator (met terugmelding) in plaats van de slof de diepte laten regelen, zodat de bodemhoogte = beginhoogte − verval × afstand,
- de glijslof dan als ondergrens/veiligheid hoger zetten.

## 6. Open punten / te controleren

1. **Maten van de achterbalk van de Bruut.** In het model staat een aanname: koker 60×60 op Z = 500–560 mm. Pas `koker_x(...)` en de beugelbouten aan na opmeten.
2. **Accuspanning en capaciteit van de Bruut** (24 of 48 V?). Hiervan hangt de motorkeuze af.
3. **Gewicht en kantelmoment.** Het gereedschap hangt ≈ 0,75 m achter de robot. Controleer de belasting op de voorwielen. Eventueel een contragewicht voorop, of de bok dichter op de achteras zetten.
4. **Gewicht omlaag** (doel < 80 kg): bokplaten van 6 mm, schijf van 8 mm met grotere lichtgaten, draagplaat met uitsparingen.
5. **Slijtvastheid van de messen** in zandgrond. Eventueel hardlassen of messen met hardmetalen tip.
6. **Stenen**: een breekbout op het kettingwiel van de schijf (M8, 8.8) als mechanische back-up voor de stroomgrens.
7. **Zode afsnijden**: optioneel een kouterschijf voor de schijf om de zode aan beide kanten in te snijden, zodat de randen netter worden.
8. **Voorafscherming**: kettinggordijn of rubber flap aan de voorkant van de kap.
9. **Kluiten en natte klei**: blijft de grond aan de schoepen kleven? Zo nodig een schraper op de kap, of de messen meer schuin zetten.
10. **Eerst testen** met een houten/MDF-mal van de schijf en een losse accuboormachine of haakse-slijpermotor, zodat je toerental en mesvorm kunt uitproberen voordat je laserdelen bestelt.

## 7. Bouwvolgorde (voorstel)

1. Achterbalk van de Bruut opmeten en de parameters in `trencher_ontwerp.py` aanpassen.
2. Laserdelen bestellen: schijf, schoepen, draagplaat, bokplaten, actuatorlippen, kapsegmenten, deksel van de kettingkast, messen.
3. Laswerk 1: schoepen op de schijf en de naaf op de schijf. Laswerk 2: scharnierbus + arm + draagplaat + lippen.
4. Bok monteren op de robot met de beugelbouten. Arm met pen ophangen. Actuator plaatsen.
5. Lagers, as, ketting en motor monteren. Kap en slof monteren.
6. Elektrisch aansluiten, met eerst de noodstop en de vergrendeling. Daarna proefdraaien zonder messen.
7. Proefgeul in grasland op 100 mm diepte. Toerental en rijsnelheid afstellen, dan dieper.
