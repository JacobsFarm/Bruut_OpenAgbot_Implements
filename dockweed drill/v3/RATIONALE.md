# Dockweed drill v3: why it is designed this way

v3 keeps everything from v2 ([../v2/RATIONALE.md](../v2/RATIONALE.md): process, requirements, mounting on the
robot, X axis on PTO tubes, cycle, control) and changes three things, from the brief "a different up/down axis, be
creative and somewhat cheaper, and a can like Robot Ruud's".

## 1. Z axis: a mast with the spindle inside (drill-press principle)

**v2:** Z tube 120 × 60 with 2 HGR15 rails on risers, 4 carriages, ball screw SFU1610 with BK12/BF12, coupling and
a NEMA 23 **with brake**; the orange spindle bracket (5 plates, 2 × UCF207) hangs on the back of the Z tube. That is
the most expensive and most dirt-sensitive part of v2 (rails and ball screw half a metre above a milling cutter).

**v3:** the mast itself is the guide, the spindle housing and the cable duct.

| Part | v3 | Why |
| --- | --- | --- |
| Guide | Square tube 100 × 100 × 3 with **V-groove rollers on the 4 corners**, 2 cages of 4 rollers (z 920 and 1170) | The tube corners are the rails: nothing to buy, align or keep clean. 4 rollers per level fix x, y and rotation. Dirt rolls off the corners; sealed 6202 bearings are cheap and everywhere |
| Why the corners are free | Nothing is attached to the sides of the mast along its stroke: the bearing cartridge is under the mast, the motor on top | In v2 the spindle bracket on the back of the Z tube would block rollers on the rear corners |
| Spindle | Shaft Ø 35 in a cartridge (tube Ø 100 with 2 × 6207) under the mast; motor on top, drive tube Ø 40 × 3 in the mast with 2 jaw couplings | No bracket plates; the mast protects the drive and the cables |
| Drive | Rack M2 on the front of the mast + pinion z20 on a worm gearbox NMRV030 i = 30 + NEMA 23 | A single-start worm at i = 30 is self-locking: the mast stays put without power, so no brake motor. 2060 N at plunge speed, 825 N at rapid; software limit 600 N as before |
| Roller loads | lower cage 1540 N, upper 1240 N at 300 N side force on the cutter (lever 1030 mm), ≈ 1090 N per roller | 6202: C0 3750 N, factor ≈ 3.4 |
| Mast stiffness | 0.28 mm under 300 N side force | similar to v2 |

The spindle shaft overhang (lower bearing to cutting level) is 369 mm (v2: 356): 0.45 mm and 26 MPa at 300 N,
critical speed ≈ 4900 rpm. The drive tube hangs between the 2 couplings: first critical speed ≈ 10,500 rpm.

Because the guide is the mast itself, the spindle sits **in the centre of the Z axis** instead of 75 mm behind a
bracket: it moved 67 mm closer to the robot (y −865 instead of −932). The lever on the X guide gets shorter (Y
deflection of the PTO tubes 0.68 instead of 0.96 mm).

**The price of this choice:** the machine is taller. Mast plus motor reach ≈ 1.95 m in driving position (v2 ≈ 1.8 m),
because the cartridge, the can and the stroke all sit under the lower cage. Fine on grassland; watch gates and low
branches.

Alternatives considered:

| Alternative | Why not |
| --- | --- |
| Swing arm (an arc does the up/down movement) | Cheapest, but the cutter moves sideways along the arc during the plunge (≈ 14 mm over 180 mm with a 600 mm arm): the can would be dragged over the sward |
| Linear actuator 1500 N | Simple and self-locking, but ≈ 30 mm/s: +10 s per plant |
| Tube-in-tube with plastic strips | Robust and cheap, but play and friction; the spindle bracket would still need its own plates |
| Belt hoist instead of a rack | Needs end clamps and tension on a moving mast; the rack is simpler and stiffer |

## 2. The can (like Robot Ruud)

Ruud uses a straight steel can around the cutter (see `inspiration/robot ruud.png`). v3 does the same: a piece of
**steel pipe DN200 (219.1 × 3.6), 180 mm high**, with a 5 mm lid, hanging on 2 rods Ø 16 in PE bushes on the mast
bottom plate. It replaces the stainless pot, the rubber rim and the splash flap of v2:

- cheaper (pipe offcut + a laser-cut lid), sturdier, weldable, can be galvanised;
- higher (180 instead of 150 mm), so it catches stones itself; the splash flap is no longer needed;
- heavier (6.4 instead of 4.2 kg), so it presses harder on the sward and holds the soil better, still far below
  the 600 N Z force limit;
- inside Ø 212 around the Ø 180 cutter.

The can rises relative to the cutter when it lands on the sward (up to 230 mm at 200 mm depth). The cartridge sits
so that the lid and the shaft seal stay 7 mm below it at maximum depth.

## 3. Camera fixed and high (like Robot Ruud)

Ruud has its camera on a high boom. v3 puts an aluminium mast (40 × 40 × 3) on the right upright with an arm at
2.1 m. The camera looks down on the whole 1 m strip behind the spindle line, and can find the next plant while the
cutter works. The X slide no longer carries a camera arm and LED bar (lighter, fewer moving cables). Joost's tip
still applies: in bright sun a light hood or apron under the camera helps.

## 4. Mass and cost

| | v2 | v3 |
| --- | --- | --- |
| Implement | 96.4 kg | 95.0 kg |
| Z moving (carriage or mast + spindle + motor) | 44.0 kg | 35.0 kg |
| X moving | 61.9 kg | 57.2 kg |
| Pot / can | 4.2 kg | 6.4 kg |

Cost of the parts that change (indicative, 2026, incl. VAT, not verified):

| v2 | € | v3 | € |
| --- | --- | --- | --- |
| 2 × HGR15 850 + 4 carriages, risers | 60–80 | Tube 100 × 100 × 3, 1 m | 15–25 |
| SFU1610 + BK12/BF12 + nut housing + coupling | 45–70 | 8 V-groove rollers 6202 + M10 axles, 2 alu cage plates | 40–60 |
| NEMA 23 with brake + driver | 90–120 | NEMA 23 + driver, worm gearbox NMRV030 i30, pinion, rack M2 | 110–150 |
| Spindle bracket (5 laser plates) + 2 × UCF207 | 80–110 | Bearing cartridge (tube + 2 × 6207, turning) + 2 jaw couplings + drive tube | 70–100 |
| Stainless pot, rubber rim, splash flap | 30–60 | Steel pipe DN200 offcut + lid | 15–25 |
| Camera arm + LED on the slide | in v2 total | Alu mast, arm, crossbar | 20–30 |
| **Total** | **305–440** | | **270–390** |

So v3 is roughly € 30–90 cheaper on these parts, and simpler to build and keep clean. The rest of the parts list is
as in v2.

## 5. Open points (v3)

1. **Test one roller cage** on a piece of the tube: rolling on the corner radius, wear, preload (eccentric axles).
2. Worm gearbox: check self-locking at the real lead angle, and the backlash of rack and pinion (closed-loop helps).
3. Height 1.95–2.1 m: check transport, gates and the sway of the camera mast (a diagonal strut is easy to add).
4. Bearing cartridge: bore and seals to be detailed with the turner; balance of the drive tube at 3000 rpm.
5. All open points of v2 (measure the PTO tubes, weigh the robot, process trial first).
