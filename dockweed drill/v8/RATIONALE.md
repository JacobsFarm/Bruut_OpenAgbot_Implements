# Dockweed drill v8: why it is designed this way

The brief: "a v8 with the Z axis of v7 and the left-right axis of v6, but with round tubes instead of the PTO tubes".
So v8 keeps the process, spindle and Z part of v7 ([../v7/RATIONALE.md](../v7/RATIONALE.md): 2 round tubes Ø 50 × 4
in plain-bush housings, Linak LA36 in the middle, 800 W gearmotor directly on a Ø 30 spindle, can Ø 219) and the
layout of the v6 X axis ([../v6/RATIONALE.md](../v6/RATIONALE.md): tubes bolted between side plates, cross beams over
the full width, omega belt drive with the stepper on the slide, cable chain). The robot drives straight again.

## 1. Round X tubes: the same tube and housing as the Z axis

- **Tube Ø 50 × 4, E355, cold drawn (EN 10305-1)**, the same as the Z tubes. Over a span of 1446 mm between the side
  plates it bends 1.0 mm down and 1.65 mm in v with the slide in the middle, simply supported (0.24 / 0.41 mm if the
  side plates clamp it). The v6 PTO tubes did 0.75 / 1.31 mm over 1376 mm: about the same, the round tube is a bit
  longer here. The forces in v come for one half from the weight of the slide hanging behind the tubes and for the
  other half from the 600 N Z force on the spindle behind them.
- **The same plain-bush housings** as the Z axis (drylin type for Ø 50 with an iglidur bush, wipers and grease
  nipple), turned so the shaft runs along x. One tube type, one housing type and one bush type for the whole machine:
  fewer parts to buy, and spare bushes fit both axes.
- **3 housings, not 4:** 2 on the upper tube at x ±120 and 1 in the middle of the lower tube, with slotted holes in z
  in the slide. That is 3 points, as with the v6 sleeves: the slide cannot be over-constrained when the tubes are not
  exactly parallel. The upper housings carry 490 N each (weight + tipping + Z force), 0.14 MPa on the bush.
- **No lemon profile, no reamed sleeves, no grease on bare steel.** A round precision tube is a stock item and the
  plain bush runs on it as delivered. The tube cannot turn in a bush, but it does not need to: the slide hangs on two
  tubes, so it cannot tip about x.
- **Ends as v6:** a round plug Ø 42 × 25 welded in each tube end with 2 × M10 tapped; the bolts go from outside
  through the 12 mm side plate. A tube comes out with 4 bolts. Weld the plugs square, then drill and tap with the side
  plate as a jig (same open point as v6).
- **Friction:** μ 0.15 in the bushes gives 366 N against 895 N belt force (NEMA 23, 3 Nm, 5:1, pulley 20 T): about
  7 m/s² left to accelerate 76 kg. The X axis is not the slow part of the cycle.

## 2. The v7 mount plate became the X slide

- The Z part of v7 bolted to a fixed 10 mm steel mount plate. In v8 that plate is the **X slide**: the X housings on
  the front (robot side), the 4 Z housings, the LA36 top bracket, the X motor and the spiral-cable bracket on the back.
  The v-stack is: cross beams (v 48..88), 8 mm gap, X housing (v 96..170), slide (v 170..182), Z housings behind it.
  The spindle comes 20 mm further back than in v6 (robot y −954 against −934), because the round-tube housing is
  deeper than the v6 sleeve pad.
- **Aluminium 12 mm** instead of 10 mm steel: about 6 kg instead of 13, because it now moves in x. The M8 of the
  housings go into Helicoil inserts. The X housing bolts come from the front, the Z housing bolts from the back; their
  holes are at least about 20 mm apart, so both sets can be through holes.
- **Width 410 mm (v6: 300):** the Z tubes now stand at x ±90 (v6: ±64), so the X motor had to go outside the right Z
  tube, at x 152, between the two Z housings in height (the gearbox and motor are at z 893..953, the housings at
  725..795 and 1025..1095). The spiral cable stays at x 175, on a bracket just above the motor.
- **Side plates 1470 apart (v6: 1400):** with the slide at x +500 the idler on the right is at x 699; the belt clamps
  start at x 703. The implement is 35 mm wider per side than v6.

## 3. What stayed from v6 and v7

- From v6: headstock with 2 uprights 40 × 40 × 3, cross beams 40 × 40 × 3 over the full width welded to the side
  plates and bolted to the uprights with 1 × M12 per crossing (cantilever 473 mm: 0.5 mm down, 1.4 mm in v, 78 MPa),
  HTD5M belt clamped on the side plates, omega around the pulley and 2 idlers, NEMA 23 closed-loop + 5:1, cable chain,
  limit switch, end stop, electrics box, fixed camera at 1.9 m.
- From v7: Z part complete (tubes, housings, yoke, clamp plate, LA36, spindle bracket, UCP 206, jaw coupling, motor,
  can, cutter), the LA36 heating rule and its result: OK from about 19 s per plant.
- Cycle: with the X slide moving while the robot drives (as the animation does) the cycle is the same as v7, 21.8 s
  once stopped; 165 plants/h back to back. If X only moves after the stop, 24.0 s.

## 4. What it costs

- **Mass 127 kg** (v6 122.9, v7 99.9). 76 kg moves in x (v6 74.5). The two X tubes weigh 13 kg over the longer
  span; the aluminium slide saves about 7 kg against the steel plate of v7.
- **Axle load:** the front axle carries 37 kg when driving (13 %), 59 kg with the battery forward. With the slide at
  x ±500 the lightest front wheel drops to 11 kg when driving (v6: 12 kg). The same advice as v6: battery forward,
  or a counterweight at the front.
- **Width 1470 mm** over the side plates, plus the bolt heads.

## 5. Open points (v8)

1. Buy the X and Z housings and the tubes; check the housing dimensions and set `xg_house*`, `xg_hc`, `zg_house*`,
   `zg_hc`. Check the bush friction (μ 0.15 assumed) on both axes.
2. X tube plugs: weld them square, then drill and tap M10 with the side plate as a jig, so both tube ends line up and
   the tubes come out parallel (the 3-point slide forgives some error in z, not in v).
3. Measure the X tube deflection with the slide in the middle (1.0 / 1.65 mm calculated); add a middle support or a
   Ø 60 tube if the cutter wanders too much.
4. Helicoil M8 in the 12 mm aluminium slide: check the pull-out against the housing bolt torque, or use a 10 mm steel
   slide (+7 kg moving).
5. All open points of v7 for the Z part and the LA36 (bench test the real cycle, ask Linak about duty and life), and
   of v6 (motor type plate, 500 rpm in real soil).
