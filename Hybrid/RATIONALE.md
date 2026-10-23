# Hybrid range extender: rationale

## Idea (from the original README)
Engine + generator keep the battery charged while driving at light load. The battery exists to deliver the peak
(traction, heavy tasks) and is topped up again on the headland at low power. On heavy work the engine may run
constantly to keep the battery at a high state of charge.

## Layout
- **Base:** 2 long tubes across the width (y = ±350, on the 50 mm grid of the upper beams) bolted with 8 × M10 x 130
  to the 4 upper beams, plus 4 short tubes along y welded on top (x = ±100, ±200). Square tube 50 x 50 x 3.
  A Ø16 spacer sleeve inside each long tube keeps the bolts from crushing the tube.
- **Train along y** (all on the centre line, one shaft line): battery (rear), controller, generator, jaw coupling,
  engine (front). Shaft height is the same for engine and generator, so the generator only needs a saddle block.
- **Keep clear:** the steering stacks above the front wheels (x > 295 for |y| > 405). The short tubes end at x = ±225,
  the minimum distance to any robot part is about 30 mm (see `clearance()`).
- **Mass:** the heavy parts sit low-ish and central; centre of gravity of the train about z 870, x 0.
  The heaviest part (engine) is at the front, the battery at the rear, so the pitch moment nearly cancels.

## Sizing (estimated, see README)
- Standard robot: 4 x 550 W = 2.2 kW continuous, peak assumed 2 x = 4.4 kW.
- Generator 3 kW electrical (engine 4.8 kW shaft, 88 % generator): covers the light task (900 W) with a 2.1 kW
  surplus and the heavy task (2.2 kW) with 0.8 kW surplus. Only above 3 kW the battery discharges.
- Battery 16S, 59 V x 40 Ah = 2.4 kWh, 80 % usable = 1.9 kWh: at the 4.4 kW peak it lasts about 81 min.
- Fuel: about 1.5 L/h at full generator output; the 3 L tank gives about 2 h. A bigger tank (jerrycan on the long
  tube overhang) is an easy extension.
- 60 V nominal matches the Quinder hub motors (60 V).

## Choices
- Permanent-magnet 3-phase alternator + rectifier instead of a mains generator: no inverter, direct to the DC bus.
- Direct jaw coupling (no belt): shortest, no tensioning, but needs alignment: the bell housing flange takes care of it.
- The frame is generated, not modeled with welds or chamfers; weld seams are not shown.

## Not modeled
Cables, fuel line, exhaust shield, throttle servo, cooling air flow, covers, rain protection.
