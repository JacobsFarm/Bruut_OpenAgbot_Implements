# Doorzaaimachine (overseeder) voor de Bruut

Twee varianten van een doorzaaimachine die graszaad en klaver **in** een bestaande zode legt:
- een schijf snijdt een ondiepe sleuf van 15 mm;
- het zaad komt op ca. 12 mm;
- een aandrukrol drukt de sleuf dicht;
- 8 rijen op 125 mm = 1 m per module, met flenzen breder te koppelen;
- elke rij volgt de grond met een eigen arm, en de diepte wordt op de schijf zelf ingesteld.

| | [Eenvoudig](simple/README.md) | [Geavanceerd](advanced/README.md) |
| --- | --- | --- |
| Basis | toediener `simple_v2` | geavanceerde toediener `advanved` |
| Ophanging | hefraam om één draaipunt, actuator in een langgat | parallellogram, balk blijft evenwijdig |
| Element | sleeparm, schijf 7° scheef met naaf aan één kant, schoen in de schaduw, dieptering aan één kant | vorkarm, schijf recht en aan twee kanten gelagerd, ringen aan twee kanten, kouter in het hart van de snede |
| Aandrukrol | rolarm met torsieveer | gaffel met torsieveer |
| Zaadbak | 41 + 18 l op het hefraam, zwaartekracht | 62 + 17 l op de robot, lucht (12 V-ventilator) |
| Neerdruk | gewicht + 2 gasveren in het langgat | gewicht + 2 gasveren in het langgat |
| Trekkracht normaal | 335 N | 375 N |
| Snijdiepte binnen ±3 mm (testbaan) | 94 % | 98 % |
| Frontgewicht nodig (robot 150 kg) | ca. 42 kg | ca. 46 kg |
| Materiaal | ca. € 1675 | ca. € 2280 |

Het onderzoek waar beide op steunen (WUR, Teagasc, Super-G, Arkansas en machines) staat in `inspiration/`. Die map
zit niet in git.

![eenvoudig](simple/previews/1_iso_rear_right.png)

![geavanceerd](advanced/previews/1_iso_rear_right.png)
