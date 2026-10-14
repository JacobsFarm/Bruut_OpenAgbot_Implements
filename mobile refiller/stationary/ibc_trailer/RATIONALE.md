# IBC trailer station: why it is built like this

Numbers from `sit_calc.py` and the model (`build_sit.py`). Estimated values are listed in the [README](README.md).

## 1. A station instead of a refiller robot

The [simple refiller](../../simple/RATIONALE.md) needs a second Bruut that carries the IBC and moves 1 m per refill,
and a field pattern in which every turn is a U-turn. The station needs neither: it stands still and the working
robot drives to it. The price is the detour: 2–15 % of the working robot's time instead of 2–3 % (see the
[stationary README](../README.md#key-figures)). On narrow fields and at normal doses the difference is small; for
wide fields the station is moved halfway through the field, or two are used.

The trailer is the obvious carrier for farms without a three-point tractor at hand: any vehicle with a tow ball or a
pin hitch can bring it, and it can stand for days.

## 2. IBCs turned with the valve forward

On the robot (simple variant) the 1200 side of the IBC lies across. On the trailer it lies **along** the trailer:

- the trailer stays narrow: 1000 IBC + 2 × 40 rails + wheels outside = 1.71 m (1 IBC), so it fits through a field
  gate and its wheels never stand under the IBC;
- the valve points forward, towards the control box: short suction line, and the valve is not beside a wheel (with
  the valve on the side, the camlock elbow would sit right in front of the tyre);
- with two IBCs the rear one's valve sits in a 250 mm gap behind the front one: enough for the valve, the elbow and
  a hand on the lever.

Both elbows go **down through the floor** to one suction header under the floor (through holes in the cross
members). Nothing lies on the floor where people step.

## 3. Control box on the drawbar, pump below the IBC

The box sits on two cross members between the A-beams, **on** the beams (its bottom at the top of the rails), so the
beams do not obstruct the door (door to the left side). The pump axis is 38 mm below the bottom of the IBC bottle
(590 vs 628 mm; 2 IBC: 668 vs 706): the centrifugal pump stays flooded down to the last litre and needs no foot
valve or priming. The box is shifted 80 mm to the right so that both ports lie on the centre line: the suction
header comes straight from behind, the discharge hose goes straight into the mast in front.

## 4. Mast in front, one arm for both sides

The mast stands on the centre line in front of the box. With the arm pinned at 0° the nozzle is 1.65 m to the left,
at −180° 1.65 m to the right: the trailer can be parked either way round. The reach follows from the widest part
(mudguards, 857 mm from the centre line) + 250 mm gap + half the working robot, rounded up.

**Transport**: the arm cannot fold straight back: the drop pipe would hang into the IBC. It is pinned at 65° instead,
with the nozzle at x −700, beside the IBC (500) and inside the wheels (857): the trailer stays 1.71 m wide. Between
the positions the arm swings over the front (over the drawbar, at 1.25–2.0 m), never over the IBC.

## 5. Running gear and parking

- One rigid square axle under the side rails, wheels outside the frame: low deck (483 / 560 mm), so the IBC can be
  set on with a pallet fork from the side or the rear, and the centre of gravity stays low (0.95 / 1.06 m full).
- Tyres: 10.0/80-12 (1 IBC: 787 of ≈ 1030 kg) and 11.5/80-15.3 (2 IBCs: 1,456 of ≈ 1700 kg).
- The IBC group sits slightly ahead of the axle: nose load 108–153 kg, enough to keep the drawbar down when the
  trailer is towed, and low enough to lift it by hand on the jockey wheel crank.
- Parked, the trailer stands on the wheels, the jockey wheel and two drop legs at the rear: it does not tip
  backwards when the front IBC is emptied first, and it does not rock when the working robot docks.
- **Road**: a trailer over 750 kg needs brakes (overrun or hydraulic, depending on the towing vehicle and the
  country), lights and a plate. Brakes are not modelled.

## 6. Two configurations from one script

`cfg(n)` derives the deck length, the IBC positions, the deck height (from the tyre), the A-frame, the box and mast
positions and the arm reach for 1 or 2 IBCs. Everything else (box, mast, arm, hoses, checks, images) is shared.
Three IBCs in line would need a tandem axle (4.6 t) and a 6.5 m trailer: then the [flat wagon](../flat_wagon/) is
the better carrier.

## 7. The refill visit in the animation

`animate_sit.py` shows one visit with 1 IBC. The choices behind it:

- **1000 l/ha on a 200 m field**: 20 l per pass, so `stc_calc.visit()` gives 6 passes and exactly 120 l per visit
  (at 505 l/ha it would be 101 l). The flow (120 l/min) comes from `sit_calc.pump_geometry` and `stc_calc.fill_q`.
  The standstill at the nozzle is `stc_calc.refill_time`: 0.5 s check + 60 s pumping + 1 s closing = 61.5 s, the
  same value as in the report.
- **Trailer parallel to the field edge, arm out to the left towards the field**: the robot docks on the docking line
  4.2 m from the edge (where the 2.4 m turning arc from the pass ends), so it does not need any extra steering to
  line up. It slows down to 0.3 m/s for the last 2 m.
- **Turning round after the refill**: the next pass lies behind the robot. It turns round on the headland with a
  forward arc towards the field and a reverse arc back onto the docking line (no extra headland depth needed, the
  trailer stays on the other side of the line), then drives back under the arm. The nozzle hangs at 1250 mm, above
  the highest part of the working robot (funnel rim 1144 mm), so the robot can pass under it in both directions.
  The turn-round takes 21.6 s; with the slower last 2 m (≈ 3 s more than at 0.5 m/s) that is about the 25 s
  docking allowance `t_dock` in `stc_calc`.
- **Distance**: the robot leaves pass p 11.9 m from the nozzle (21 s along the headland there, 26 s back). The
  report uses the mean distance for a station in the middle of the headland instead (100 s detour for a 100 m wide
  field); the animation shows one example.
