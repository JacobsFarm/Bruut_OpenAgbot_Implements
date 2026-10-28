# UV-C mildew light (simple): why it is built this way

## UV-C at night instead of fungicide

- Low doses of UV-C (254 nm, ~100..400 J/m2 per pass, twice a week) suppress powdery mildew on strawberries,
  cucurbits, roses and grapes. Given at night the fungus cannot repair the damage with blue light, so the dose can stay
  low enough not to harm the crop. A robot is a good carrier: the work is slow, repetitive and at night.

## A hood between the axles

- The robot straddles the bed; between the axles there are no tyres, so a hood can reach down into the crop there.
  The steered front tyres come to y ~297 (x ~200) and the rear tyres start at y -235: the hood is 440 long (y +-220)
  and 580 wide (x +-290, inside the tyres at 325). With the front wheels steered 30 degrees it stays 25 mm from the
  tyres (lugged model tyre).
- Aluminium 2 mm, anodised: reflects UV-C well (~65 % of the lamp output reaches the canopy plane, estimated). Rubber
  side skirts to z 150 and brush curtains front and rear keep the light in; the crop passes through the brushes.
- It hangs on 4 slotted flats from 2 bearers on the upper beams: the hood height can be set +-75 mm for the crop.

## Lamps

- 6 compact UV-C tubes (PL-L 55 W class: ~17 W UV-C each, 535 long) across the bed, 290 mm above a 300 mm canopy,
  behind wire guards; electronic ballasts and an interlock relay in a box on the rear bearer. The lamps only burn
  with the hood down (tilt switch) and the robot moving; at a stop they switch off, so no plant gets a double dose and
  nobody looks into a lamp.
- 102 W of UV-C over 0.225 m2 gives ~300 W/m2; a plant is under the lamps for 0.39 m of travel. 200 J/m2 then needs
  0.58 m/s; the robot sets its speed from the dose wanted (100 J/m2: 1.15 m/s, 400 J/m2: 0.29 m/s).

## Capacity

At 200 J/m2: ~1020 m2 per hour, 489 W (lamps 367 W), ~3.9 h per battery charge: ~4000 m2 or ~69 beds of 100 m. A
night of 8 h with the [charging dock](../../charging%20dock/simple/) covers about a hectare of strawberry beds twice a
week.

## Estimated, not measured

- UV-C efficiency of the tubes 0.31, ballast efficiency 0.9, share reaching the canopy 0.65
- Effective doses (100..400 J/m2) from literature; to verify per crop and variety (leaf burn above the safe dose)
- Robot mass 160 kg, rolling resistance 0.06, base drive power 40 W, 30 s per bed end
- Masses of the lamps, ballasts and brushes
