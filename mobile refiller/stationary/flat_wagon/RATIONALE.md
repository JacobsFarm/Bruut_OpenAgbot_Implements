# Flat wagon station: why it is built like this

Numbers from `sfw_calc.py` and the model (`build_sfw.py`). Estimated values are listed in the [README](README.md).

## 1. Why a standard wagon

Most farms have a bale wagon or a flat trailer that stands idle in the growing season. With six IBCs it holds a whole
field's worth of liquid (11.9 ha at 505 l/ha, 55 h of work for one working robot, or a day for several robots), and
it is filled at the yard with a forklift or telehandler, IBC by IBC. The refill kit is designed so the wagon needs
**no welding**: two holes in the deck (header down, discharge up) and two hangers clamped or bolted to the main beams.

## 2. IBCs in rows of two, valves to the rear, header in the middle

- Two IBCs across with the 1000 side across: 2 × 1000 + 280 mm gap = 2.28 m on a 2.48 m deck. The **280 mm gap in
  the middle** carries the suction header; each valve has a short hose to it in the 500 mm gap between the rows.
- All valves point to the rear (towards the pump) and stay reachable from the side of the wagon.
- All IBCs are connected to one header: they empty together (communicating vessels), each can be closed with its own
  valve, e.g. to keep one IBC with a different product or to swap an empty one while the others keep working.
- The rows are **centred between the axles**: 3 rows put 5.1 t on each axle. With the rows packed from the rear
  (first try) the rear axle carried 63 % of the load.
- 3 rows are the limit for the assumed tyres (2,564 of ≈ 2,575 kg per tyre); 4 rows (12.7 t) need a heavier wagon.

## 3. Control box under the deck

On the deck the pump would stand at the height of the IBC bottoms and lose its prime when the IBCs run low. Under
the deck, hung from the main beams behind the rear axle, the pump axis is 0.8 m below the bottoms of the bottles:
always flooded, out of the way of the forklift, and in the shade. The door faces the rear.

## 4. Mast on the rear left corner, arm above the IBCs

A mast in the middle would need a 2 m arm to reach past the 2.48 m deck, and that arm could not be folded for
transport (it would stick out 1.6 m behind the wagon, or over the IBCs with the drop pipe hanging between them). On
the corner (x −1160) the arm is only 840 mm long: the nozzle is 2.0 m left of the centre line, 760 mm beyond the
deck edge. For transport it folds forwards along the left edge, outside the IBCs, with the nozzle 20 mm above the
deck (the nozzle tip is therefore at 1270 mm, 126 mm above the funnel rim instead of 106).

The arm sits at 2.46 m, **above the IBC tops (2.43 m)**, so that the RTK antenna (2.60 m) sees the whole sky and is
not shadowed by six IBCs full of liquid. The skid that carries the mast stands on the deck and is lashed to the
border profile; two struts brace the mast.

The station serves the left side only: park the wagon with its left side to the headland lane. A mirrored skid on the
right corner is a parameter change (`mast_xy`).

## 5. The docking place

The working robot stops beside the rear left corner, with most of its length behind the wagon: its front is 280 mm
behind the rear tyre, its inner side 260 mm from the deck edge (the tyres stay under the deck). The rear lights and
the plate are on the rear border, above the robot's working height.
