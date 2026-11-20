# Dockweed drill: vergelijking van alle versies (v1 t/m v10)

Bron: de `README.md` en `RATIONALE.md` van elke versie. Cijfers met "(repo)" staan in de documentatie. Cijfers met
"(schatting)" zijn mijn eigen indicatie, omdat de repo alleen voor v2, v3 en v4 een prijslijst heeft. Prijzen zijn
indicatief, incl. btw, niet gecontroleerd bij leveranciers.

## 1. Wat is het en wat blijft gelijk

Een portaal achter de Bruut OpenAgbot (rijdt achteruit tijdens het werk). Een frees Ø 180 maalt deraap van een
ridderzuring (hoogte ~150 mm) kapot in een pot/blik Ø 219–250. Camera + LED, 48 V uit de robot.
Wat per versie verandert: **X-as** (links-rechts, 1000 mm), **Z-as** (op-neer), **spindelaandrijving** en **frame**.

## 2. Overzicht in één tabel

| Versie | X-as (zijwaarts) | Z-as (op/neer) | Spindel / aandrijving | Massa | Planten/u | Zwakste punt |
| --- | --- | --- | --- | --- | --- | --- |
| **v1** | 2 alu-profielen 40×80 + HGR15-rail | rail + kogelomloopspindel | Ø35, BLDC 1,5 kW, 1500 tpm | 88,6 kg | 153 | rails gevoelig voor vuil, veel kleine precisie-onderdelen |
| **v2** | 2 PTO-buizen (glijhulzen) | HGR15 + SFU1610 + rem | idem v1 | 96 kg | 153 | glijfrictie ~190 N, lassen van ribben, PTO-maten onzeker |
| **v3** | PTO-buizen | mast 100×100 op 8 V-rollen, tandheugel + worm | idem, BLDC | 95 kg | 153 | rollen op afgeronde hoek van koker niet getest; hoogte 1,95 m |
| **v4** | PTO-buizen | **aanhangwagen-steunpoot** (drop-leg jack) | 800 W motor, ketting 38T→12T, Ø20 in 2×UCP204 | 106 kg | 138 | 2,6 mm speling frees, trage Z (40 mm/s), jack niet voor 150 slagen/u |
| **v5** | PTO-buizen | jack | 800 W direct op as via klauwkoppeling, **500 tpm** | 102 kg | 138 | 500 tpm: geen maaien, grover frezen |
| **v6** | PTO-buizen tussen zijplaten (40×40 frame) | **2 PTO-buizen + Linak LA36** | Ø30 in 2×UCP206, koppeling 28 | 123 kg | 150* | LA36 duty 70 % i.p.v. toegestaan 20 % |
| **v7** | **geen X-as**: robot stuurt naar plant | 2 ronde buizen Ø50×4 in kunststof lagerhuizen + LA36 | als v6 | **100 kg** | 165 (b2b), 139 bij 2 m, 113 bij 5 m | robot moet ±40 mm nauwkeurig stoppen, nog geen X |
| **v8** | **2 ronde buizen Ø50×4** + 3 lagerhuizen | als v7 | als v6 | 127 kg | 165 / 139 / 113 | 240 kg op achteras, voor maar 13 %, X-buisdoorbuiging 1–1,65 mm |
| **v9 simple** | 4 mm gebogen U-sporen 25 mm + 2 skatewielen per kant | idem, sporen vast op X-slede | als v6 | 117,6 kg | = v8 | berekeningen nog voorlopig, wielflens glijdt (slijtage) |
| **v9 advanced** | 2× UPE100, 8 wielblokken, 32 skatewielen | UPE100 + LA36 | als v6 | **170 kg** | = v8 | voor-as slechts 8 % gewicht, frees 4,4–9,7 mm speling, tegengewicht verplicht |
| **v10** | als v8 + **motor vast** rechts | **HGR20-rails + 4 HGH20CA wagens**, slede = U-plaat | als v6 | 131 kg | = v8 | rails gevoelig voor vuil, rail-balk moet vlak zijn |

\* v6: 150/u alleen als de LA36 het aankan; bij 20 % duty maximaal 43 planten/u (repo).

## 3. Per versie: verbeteringen, voordelen, nadelen

### v1: alu-profiel + rail (referentie)
- **Voordelen:** rollende wrijving ~16 N, geen speling, lichtste X-as (14,6 kg), geen lassen aan de X-as.
- **Nadelen:** HGR-rails vuilgevoelig (spatkap + vetten), doorbuiging alu 0,85 mm.
- **Onderdelen:** online (profiel, rails), niet bij de landbouwdealer.

### v2: PTO-buizen als X-as
- **Verbetering t.o.v. v1:** vuil-/roestbestendig, goedkoop, bij elke landbouwdealer.
- **Voordelen:** stijver (0,45 mm), 3 korte hulzen met sleufgaten voorkomen klemmen. Compleet kostenoverzicht.
- **Nadelen:** glijwrijving ~190 N, 0,5–1 mm speling normaal, lassen (ribben, pads), PTO-maten zijn nog niet gemeten
  (Sparex 1B/2A uit adverteerlijsten). Z-as met kogelomloop + rem + rail is veel onderdelen.
- **Prijs (repo):** totaal ≈ **€ 1.200–1.900**. Grootste posten: BLDC + VESC € 250–450, staal/laser € 150–250.

### v3: mast als Z-as + stalen blik
- **Verbetering:** Z-as als "boormachine-mast", geen rails of kogelomloop. Blik van DN200-buis i.p.v. RVS pot, vaste
  hoge camera.
- **Voordelen:** goedkoper (Z ≈ € 270–390 vs € 305–440), zelfremmend, stijf (0,28 mm), spindel 67 mm dichter bij robot.
- **Nadelen:** 8 V-rollen op koker-hoeken niet getest, 1,95 m hoog, 60 mm vrij van achterband (kleinste).

### v4: aanhangwagen-steunpoot + voorraadonderdelen
- **Verbetering:** hele Z-as (geleiding, spindel, tandwiel, afdichting) = één goedkoop standaardonderdeel (€ 70–110).
  Voorraad-onderdelen: 800 W-motor + UCP204.
- **Voordelen:** eenvoudigste Z-as, weerbestendig, zelfremmend, ± € 40 goedkoper dan v2.
- **Nadelen:** 10 % lagere capaciteit (138/u), **2,6 mm** speling frees, Ø20 as buigt 2,35 mm, kritisch toerental
  69 % van frees. Jack is gemaakt voor honderden slagen per jaar, hier 150 per uur: elk seizoen vervangen.
  12T-tandwiel met 20 mm gat niet in de lijst.

### v5: motor direct op de as
- **Verbetering:** geen ketting, tandwielen of kettingkast.
- **Voordelen:** 4 kg lichter, minder onderdelen, geen kettingonderhoud.
- **Nadelen:** frees nu **500 tpm** (v4: 1500): grover (0,75 mm/tand), 15 Nm, maaien kan niet meer, regroei-risico.
  Motor staat hoog (1,11 m). Geen eigen animatie. Het procesrisico (te trage frees) is door Joost juist als fout genoemd.

### v6: 40×40 frame, Ø30 as, PTO-Z met Linak
- **Verbetering:** lichter frame (40×40), PTO-buizen met 4 bouten los te halen, Ø30 massief in UCP206 (1,09 mm i.p.v.
  2,35 mm), LA36 geeft 1700 N met marge 3,1.
- **Voordelen:** stijver spindel, onderhoudsarm, goede toegankelijkheid.
- **Nadelen:** **zwaarste PTO-versie (123 kg)**, LA36 duty 70 % bij toegestaan 20 % (oververhit; vervangen door
  servo-cilinder voor echt werk), voor-as 39 kg, lichtste wiel 12 kg. LA36 kost veel (zie prijs).

### v7: geen X-as, alleen Z (ontwerp van de Z-module)
- **Verbetering:** grootste en duurste deel (X-as, slede, riem, ketting, motor) weg. Ronde precisiebuis Ø50×4 (E355)
  in gekochte kunststoflagerhuizen. Alles 64 mm dichter bij robot, 23 kg lichter, voor-as 49 kg, frees 250 mm van band.
- **Voordelen:** **simpelst en goedkoopst**, 100 kg, cyclus 21,8 s, 18,5× veiligheid hoofdbouten.
- **Nadelen:** robot moet zijdelings sturen (1,3–1,8 m voor 250 mm), stuurmotor-snelheid tot 43°/s onbekend,
  nauwkeurigheid ±40 mm niet getest; bij 5 m plantafstand nog 113/u. Is ook bedoeld als Z-deel voor een latere X-as.

### v8: Z van v7 + X van v6 met ronde buizen
- **Verbetering:** X-as terug maar met **één buistype, één lagerhuis, één lager** voor beide assen (geen PTO-citroenprofiel,
  geen gerijmde hulzen, geen vet op blank staal). Slede is de v7-montageplaat.
- **Voordelen:** standaardonderdelen (precisiebuis, drylin/iglidur huis), simpel te vervangen, 21,8 s per plant met X tijdens rijden.
- **Nadelen:** 127 kg, voor-as 13 % (37 kg), lichtste wiel 11 kg, X-buisdoorbuiging 1,0 / 1,65 mm, X-motor op de slede
  (beweegt mee met kabel), 78 MPa in dwarsbalken.

### v9 simple: 4 mm U-sporen met skatewielen
- **Verbetering:** alles in 4 mm staal, wielen op één M8-bout, eenvoudigste montage, **117,6 kg** (lichtste met X-as).
- **Voordelen:** spindel 86 mm dichter bij robot, voor-as 47 kg (17,5 %), goedkope onderdelen (skatewielen, buigwerk).
- **Nadelen:** rekenwerk nog voorlopig, wielzijde glijdt langs flens (slijtage nog niet berekend), 3 mm speling tot
  robot (X-as), 25 mm U moet na buigen 25 mm blijven.

### v9 advanced: UPE100 + 8 wielblokken
- **Verbetering:** alles rolt, geen glijdende delen, instelbare blokken, stijve profielen (0,2 mm X-doorbuiging).
- **Voordelen:** makkelijk afstellen (sleufgaten), motor vast rechts (kabel beweegt niet), vlakke X-frame-constructie.
- **Nadelen:** **170 kg** (+43 kg t.o.v. v8), voor-as **26 kg (8 %)**: robot kan niet betrouwbaar sturen, lichtste wiel
  6,8 kg, **tegengewicht van 30–40 kg verplicht**, frees 4,4–9,7 mm speling (zachte wielen), 32 wielen = veel
  onderdelen, 1570 mm breed.

### v10: v8 + vaste X-motor + lineaire geleiding in Z
- **Verbetering:** HGR20-rails vast op de X-slede, wagens meelopend met de slede (arm 430 mm constant), motor vast
  rechts als v9 (kabel beweegt niet, slede 380 mm i.p.v. 410), LA36 minder belast (push 241 N, 60 % duty).
- **Voordelen:** **stijfste Z**: frees 1,8 mm bij 300 N (v8: 2,4, v9 adv: 9,7), wrijving 26 N i.p.v. 380 N, kleinste
  LA36-verwarming (13,1 A²), L10 1,9 miljoen km, zelfde 131 kg-klasse als v8, geen extra tegengewicht.
- **Nadelen:** HGR-rails zijn vuilgevoelig (dubbele afdichting + schraper nodig), rail-balken moeten vlak (900 mm), M5-draad in 4 mm wand,
  4,2 kg zwaarder dan v8 (131,2 vs 127,0 kg), HIWIN-maten uit catalogus (andere merken wijken af).

## 4. Prijs, complexiteit, montage en onderdelen per versie

Prijs: v2/v3/v4 uit de repo, rest is mijn schatting (afgeleid van v2-lijst + marktprijzen LA36 ≈ € 400–600,
HGR20-set ≈ € 150–250, UPE100 ≈ € 40–70 per profiel, skatewiel 80 mm 90A ≈ € 5–10 per stuk).

| Versie | Prijs totaal | Complexiteit (onderdelen/maatwerk) | Montage | Verkrijgbaarheid onderdelen |
| --- | --- | --- | --- | --- |
| v1 | ≈ € 1.400–2.000 (schatting) | hoog: rails, kogelomloop, riem | gemiddeld, geen lassen, wel precies uitlijnen | rails/profielen online, niet bij dealer |
| v2 | **€ 1.200–1.900 (repo)** | hoog: PTO + lassen + kogelomloop + rem | zwaar: lassen met vervorming, hulzen reamen | PTO-buis bij landbouwdealer, maten onzeker |
| v3 | ≈ € 1.150–1.850 (repo, Z € 35 goedkoper) | gemiddeld: mast + rollen + worm | gemiddeld, 8 rollen + 1 kooi eerst testen | rollen 6202, NMRV030 standaard; mastkoker niet getest |
| v4 | ≈ € 1.150–1.850 (repo, ≈ € 40 onder v2) | **laag**: jack = één onderdeel | simpel (jack + plaat), ketting uitlijnen | jack, UCP204, 800 W motor: voorraad/standaard; 12T met 20 mm gat checken |
| v5 | ≈ € 1.100–1.800 (schatting) | lager: geen ketting | simpeler dan v4 | jack standaard, koppeling 24 (Ø20 beperkt) |
| v6 | ≈ € 1.700–2.500 (schatting) | gemiddeld-hoog: PTO + LA36 + converter | PTO los met 4 bouten (goed), lassen pluggen | **LA36 duur, levertijd; PTO-maat onzeker** |
| v7 | **≈ € 1.200–1.800 (schatting, goedkoopst met Z)** | **laagst**: geen X, 4 lagerhuizen + 2 buizen | **eenvoudigst**: buizen in huizen lassen als mal | precisiebuis E355 (staalhandel), drylin/iglidur huizen: standaard |
| v8 | ≈ € 1.800–2.600 (schatting) | gemiddeld: 1 buistype, 1 huistype, 1 lager | gemiddeld, 4 bouten per buis, lassen met zijplaat als mal | **alles standaard catalogus**: beste leverbaarheid |
| v9 simple | ≈ € 1.500–2.200 (schatting) | gemiddeld: gebogen U + 8 wielen | simpel (M8-bout per wiel), maar toleranties 0,5 mm per kant | skatewielen/608: goedkoop, staal gebogen op maat |
| v9 adv. | ≈ € 2.200–3.200 (schatting) | **hoogst**: 4 UPE, 8 blokken, 32 wielen | blokken instelbaar, maar zwaar en breed (170 kg) | UPE100 standaard; 32 wielen; **tegengewicht erbij** |
| v10 | ≈ € 2.000–2.900 (schatting) | gemiddeld-hoog: X-buizen + rails | gemiddeld; rail-balken vlak stellen | HIWIN HGR20/HGH20CA online; huizen standaard |

## 5. Conclusie en aanbeveling

**Beste basis om nu te bouwen: v8 (zonder X-as: v7), met de Z-geleiding van v10.**

Redenen:
1. **Spindel:** Ø30 solide in 2×UCP206 met klauwkoppeling (vanaf v6) is stijf (1,1 mm) en eenvoudig. v4/v5 (Ø20 + buis)
   zijn de zwakste schakel (2,35 mm, 155 MPa), vermijden.
2. **X-as:** de ronde Ø50×4 precisiebuis met standaard lagerhuizen (v7/v8) wint van PTO-buizen (v2–v6): maat bekend,
   standaardonderdeel, geen lassen van citroenprofiel, één type voor beide assen. Skatewielen (v9) kosten massa
   en/of stijfheid en vragen tegengewicht.
3. **X-motor vast aan het uiteinde** (v9/v10): lichtere slede (380 mm), kabel beweegt niet. Overnemen.
4. **Z-geleiding:** v10 (HGR20 op vaste rails) is veruit het stijfst (1,8 mm bij 300 N) en laat de LA36 het minst
   werken. Zijn de rails onder vuilcondities een zorg, val dan terug op de buizen van v8 (2,4 mm, goedkoper, vuilbestendiger).
5. **Z-aandrijving:** LA36 is voor veldproeven prima, maar duty 20 % is te laag voor continu werk. Plan een servo-cilinder
   of kogelomloop in dezelfde beugels (de parameters `act_*` staan er al voor).
6. **Als goedkoop/simpel begin:** **v7** (alleen Z, robot stuurt). Voeg later een X-as toe op de montageplaat.

Wat te vermijden:
- **v9 advanced**: te zwaar (170 kg, voor-as 8 %), zachte wielen geven 4–10 mm speling, veel onderdelen.
- **v4/v5**: jack te zwak voor 150 slagen/uur, Ø20-as, en bij v5 te laag toerental.
- **v1/v2**: rails of PTO-hulzen zijn achterhaald t.o.v. v8.

**Verbeteringen om verder te onderzoeken:**
1. Voor-aslast: alle X-versies (v6–v10) laten de voor-as op 13 % (of 8 % bij v9 adv.). Gewicht naar voren (accu, tegengewicht) of
   spindel dichter bij de robot zetten (v9 simple wint hier 86 mm).
2. LA36 duty: vervangen door servo-cilinder of kogelomloop (100 % duty).
3. Toerental: 500 tpm direct (v5–v10) is een proces-risico (Joost: te traag = groter stuk wortel, loopt weer uit).
   Overweeg tandwiel/riem 1:3 terug, of een BLDC (VESC) rechtstreeks.
4. Proefbouw op een bok **voor** de definitieve keuze (repo: ± € 400): regroei na 6–8 weken meten.
5. Meet echte onderdelen: PTO-buis, HGH20-rail, lagerhuizen, wielstijfheid, LA36-maten, en zet de `*_params.py` bij.
6. Combineer: v10-Z-geleiding op v7-frame (zonder X) voor de goedkoopste stijve Z-module.
