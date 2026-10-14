# Mobile refiller, simple (IBC): why it is built like this

The concept, all uses and the other variants are in the [mobile refiller README](../README.md). This file explains the
choices in the simple model. Numbers come from `mrs_calc.py` and the model (`build_mrs.py`); estimated values are
listed at the end of the [README](README.md#estimated-not-measured).

## 1. Simpler parts, different field pattern

The [liquid variant](../liquid/RATIONALE.md) tops up the working robot *while both drive*, in the straight reverse
of a turn with three points. That needs a slewing boom with a trolley, a spout actuator, a camera, a second RTK
receiver on the spout and a powered trailer: about €6,000 in parts and a lot of control software (the boom follows
the funnel at 10–20 Hz).

The simple variant changes the **field pattern** of the working robot instead of the machine:

| | Liquid | Simple (IBC) |
| --- | --- | --- |
| Turn of the working robot | to the neighbouring pass, with three points (forward, reverse 3.8 m, forward): 29.4 s | skips 5 passes, one U-turn of 6 m, never reversing: 17.5 s |
| Where the refiller is | beside the turn, outside: headland 6.4 m | inside the turn: headland 5.3 m |
| How the spout gets to the funnel | boom (slew + trolley) follows the funnel, spout goes down | the working robot stops its funnel under a fixed nozzle |
| Standstill per refill | ≈ 3 s | 12.7 s (22 l); 2.2 % of the round trip at 505 l/ha and 200 m |
| Tank | 268 l + trailer 246 l, special tanks | standard 1000 l IBC, swapped with pallet forks |
| Parts | ≈ €6,000 | ≈ €1,650 |

The price is about 10 s of extra standstill per refill. At normal doses that is 2–2.5 % of the working robot's time,
against 11–47 % for driving to the farm without a refiller (yard 0.2–2 km).

## 2. The skip pattern

With a working width of 1 m and a smallest turning radius of 2.1 m (rear-axle centre, see `agbots/agbot slim`), the
Bruut cannot make a U-turn to the next pass. If it skips passes, it can: the jump N must satisfy (N − 1) W ≥ 2 R,
because the turns alternate between N and N − 1 passes. With the planner radius R 2.4 m: **N = 6**.

- Order in a block of 12 passes: 1, 7, 2, 8, 3, 9, 4, 10, 5, 11, 6, 12. On the refiller headland every turn goes from
  k to k + 6 (6 m), on the far headland from k + 6 to k + 1 (5 m).
- At the end of a block (pass 12) the next pass would be 13, right beside it. So every other block is **mirrored**:
  19, 13, 20, 14, ... The block change 12 → 19 is a U-turn of 7 m, the far-headland turns in the mirrored block are
  7 m, and **on the refiller headland every turn stays 6 m**.
- A U-turn of 6 m is an arc R 2.4 m, 1.2 m straight and an arc R 2.4 m. That straight is "the straight of the turn"
  where the working robot stops.
- The middles of successive turns on the refiller headland are exactly 1 pass (1 m) apart (4, 5, 6, ... in pass
  units). That is why the refiller only has to drive **1 m per refill**, and 7 m at a block change (once every 6
  refills).
- The working robot never reverses: no reversing with the applicator lifted behind it, no stops to change direction,
  and the turn takes 17.5 s instead of 29.4 s.
- Every turn on the refiller headland is a refill opportunity: the refiller is visited every 2 passes (one round trip),
  as in the liquid variant.
- Limits: a field whose width is not a multiple of 12 m ends with a partial block (finish with turns with three points
  or a smaller pattern without refilling); irregular fields need a planner that keeps the turns on the refiller
  headland the same width.

## 3. The refiller stands inside the turn

Inside the U-turn there is a free space: the inner side of the working robot runs on R 2.4 − 0.5 = 1.9 m around the
centres of the two arcs, and on the straight its inner side is 0.5 m from the straight's centre line. The refiller
stands there, **heading along the headland**, with its arm over the straight.

- Its widest point on the straight side below 1.3 m is the camlock elbow on the IBC valve (722 mm from its centre
  line). With the centre lines **1.45 m apart** the gap to the working robot is 225 mm on the straight. The arcs stay
  further away. This was checked with outlines over the whole turn in both directions (`mrs_calc.loop_clearance`) and
  with the real shapes in the animation (`animate_mrs.check_fit`).
- The nozzle hangs above the middle of the straight. The funnel of the working robot is 465 mm in front of its rear
  axle, so it stops with the rear axle 135 mm into the straight. This works for turns to the right and to the left
  (mirrored blocks), so the refiller never has to turn around.
- The headland is not deeper than for the U-turn alone (5.3 m from the field edge); the liquid variant needs 6.4 m.
- The refiller only moves forward, 1 m at a time, straight along the headland. It moves when the working robot is
  back in the field, so it is never in the way.
- Outside the turn (as in the liquid variant) would also work, but it makes the headland about 1.1 m deeper and puts
  the refiller on the fence side.

## 4. The IBC: standard, swapped with pallet forks

- A **standard 1000 l IBC** (1200 × 1000 × 1160) is on every farm, products are delivered in them, and every
  forklift, telehandler or front loader with pallet forks can handle it. The refiller does not need to be filled: the
  empty IBC is swapped for a full one. 1000 l at 505 l/ha is 1.98 ha, or 9.2 h of work for one working robot.
- **1200 across the robot, 1000 along it.** The steering stacks with the stepper motors stand above the front wheels
  (y 405–595, up to 1032 mm high), so the IBC must stay behind y 405. With 1000 mm along the robot it fits from
  y −620 to 380 (20 mm behind the stacks with the corner guides). With 1200 mm along the robot it would have to go
  100 mm further back, and the rear wheels would carry more than 500 kg when full.
- **Low**: the pallet sits on a bed 40 mm above the upper beams (the lowest practical support), the IBC top is at
  1.90 m. The centre of gravity of a full refiller is 1.23 m high. Every centimetre counts for tipping.
- The IBC is 1.2 m wide, 0.2 m wider than the robot. It overhangs the tyres by 175 mm on each side, high above them.
- The forks come in **from the right or from behind** (4-way pallet). The mast is on the left, the front has the
  steering stacks. Corner guides 140 mm high centre the pallet when it is lowered; two ratchet straps hold it.
- The **valve faces left**, towards the mast and the working robot, so the suction hose is short and the pump stays
  below the valve.

## 5. Wheel loads, tipping and traction: the limits

A 162 kg robot carrying 1.5 t is at the edge of what the Bruut can do. The numbers:

- **Wheel loads**: 470 kg on the heaviest wheel (left rear, the mast side) with 1000 l at 1.2 kg/l. The Quinder
  datasheet allows 500 kg. With UAN (1.32 kg/l), fill to 980 l at most (`mrs_calc.max_fill_for_wheels`). The
  centre of the IBC is 120 mm behind the middle (because of the steering stacks), so the rear wheels carry 60 %.
- **Tipping**: 16.4° sideways when full (22° empty) is enough on flat headlands and farm tracks, not on side slopes.
  The IBC has no baffles: sloshing at half fill makes it worse. Drive at 0.5 m/s at most when full, accelerate gently
  (0.3 m/s²), and avoid side slopes.
- **Traction**: on wet grass the rolling resistance of the full refiller is 120 kgf, and the four hub motors give 84
  kgf continuously (21 kgf each). This is why the refiller **only makes short moves on the headland**: 1 m per refill,
  3.7 s, with the motors' peak current (up to 4 × 44 kgf). On a hard farm track (c_rr 0.03) it drives continuously
  when full, up to 2.6 % grade. Up to 630 l it drives continuously on grass. For hilly farms or long grass headlands:
  the XL robot (`agbots/agbot design big`, 16" hub motors), or let the telehandler bring the IBC to the field edge.
- The robot frame (40 × 40 × 2 beams) was not checked for 1.5 t. The three bolted cross tubes put their load on the
  upper beams within 150 mm of the lower beams; the welded one at y 0 rests in the middle of their span. A load test
  is needed before driving with a full IBC.

## 6. Pump, hose and nozzle

- **A pump is needed**: the IBC valve is at 0.94 m, the funnel of the working robot at 1.14 m. Gravity does not
  work.
- **24 V centrifugal transfer pump, 1.5"**, hanging inside the frame under the IBC. It is protected, under the valve
  (always flooded, no self-priming needed) and between the wheels. Free operating point 165 l/min; the controller
  throttles it to **120 l/min**, because the stream falls 0.1 m freely into an open funnel. About 170 W.
- **Hose up inside the mast**, out of a window at the top, a loop over the pivot, along the arm and into a PP drop pipe.
- **Fixed nozzle at 1250 mm**: 106 mm above the funnel rim (1144 mm, the highest point of the working robot). The
  working robot simply drives in under it. No spout actuator. A **drip-stop nozzle** (spring check valve, opens at
  ~0.3 bar) keeps the hose full and stops the last drops when the pump stops.
- **Arm at 2.0 m** so that the antenna on top is above the IBC (1.90 m) and sees the whole sky.

## 7. Positioning: RTK above the nozzle, no camera

- The robot's own GNSS antenna moves from the front beam (where the IBC would block half of the sky) to the **arm tip,
  straight above the nozzle**. The nozzle position is then measured, not calculated through the robot pose. The
  refiller stands still during the refill, and the working robot positions itself.
- The stream may be 128 mm off the funnel axis (Ø300 funnel). The error budget is ≈ 46 mm (2σ): antenna RTK, tilt
  of the robot (IMU), the working robot's GNSS and heading, its stopping position. There is enough margin without a
  camera. Both robots must use the same RTK base.
- No flow without: the working robot reports "stopped", both positions agree within 50 mm (0.5 s check), and the work
  tank is not full. The level sensor in the work tank stops the pump; a float valve in the funnel is the mechanical
  backup.

## 8. Mast and arm

- **Mast 80 × 80 × 4** beside the IBC, in the middle of its length. It stands on a stub of the welded cross tube at
  y 0, with two gussets to the side rail. There are no beam holes at |y| < 275, so this cross tube is welded into the
  bed and not bolted.
- **Arm 60 × 60 × 3** pivots on a Ø30 pin on the mast top and is locked with a pin in two positions: out (0°) and
  folded back along the IBC (90°) for transport. Folded, the refiller is 1.41 m wide instead of 2.17 m.
- The loads are small: 56 Nm at the mast foot, 0.35 mm deflection at the tip.

## 9. Bed

- **60 × 40 × 3 tube lying flat**: 40 mm high, the lowest practical support. Cross tubes 58 MPa, side rails 23 MPa
  with a dynamic factor of 2 (S235).
- **Cross tubes at y −525, −275 and 325**, bolted with 4 × M10 each through the upper-beam holes. The holes at
  y ±425 and ±575 are taken by the bolts of the wheel units and the steering stacks. The bolt heads sit **inside the
  tube** on the bottom wall (access holes on top), so nothing sticks up under the pallet.
- **Side rails under the pallet edges**: the pallet bears on its perimeter whatever direction its runners run.
- 12 × M10 carry braking and sloshing (0.5 g) at 514 N each in shear. The corner guides and the straps keep the IBC
  in place.

## 10. Not chosen / later

- **Gravity**: an IBC higher on the robot (valve above 1.2 m) would make the pump unnecessary, but it raises the centre
  of gravity by about 0.25 m (tipping from 16° to about 14°).
- **Two IBCs** or a bigger tank: beyond the wheel load and traction limits of the standard robot. The XL robot could
  carry more.
- **Camera on the nozzle**: not needed for the funnel tolerance. A cheap camera can be added as a second check for crop
  protection products.
- **IBC stirrer or circulation** for suspensions (the pump can circulate back into the IBC through a valve).
- **Level sensor in the IBC cap**, and a flow meter for litres per working robot and per field (in the parts list as an
  option).
- **Refilling while driving** (as in the liquid variant): it would need a following boom again. The standstill of the
  simple variant is small at normal doses.
