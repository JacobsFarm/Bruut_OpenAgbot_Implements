# Irrigation, stationary pump + hose reel: design rationale

11 October 2026. Model: `Irrigation_Hose_Reel.FCStd` (FreeCAD 1.1, generated with `build_irr.py`). The figures come
from the model, from `irr_calc.py` and from the animation (`animate_irr.summary()`). Where something is assumed or
estimated, this is stated.

![the hose reel on the robot](previews/1_full_reel_iso_on_robot.png)

---

## 1. Assignment

- Irrigate grassland autonomously with a robot, from a pump that stays at the ditch.
- The robot has a reel and drives the length of the field. Over time it comes back and winds the hose up again, so
  that one pump can serve several fields.
- The pump runs on petrol.
- Preferred principle: **flooding**, low pressure with a lot of water, not a high-pressure sprinkler.
- Chosen in the concept stage (see the [irrigation README](../README.md)): **lay-flat hose, laid out empty, water on,
  drained, wound empty by the robot**, with **outlets along the hose** (option b).

## 2. The design in brief

1. **Mount:** two cross tubes 40 × 40 × 3 on the upper beams (8 × M10 through the beam holes at y −375 and 275), the
   same as the mobile refiller.
2. **Frame:** two laser-cut side plates (6 mm, truss windows) with welded feet on the cross tubes (8 × M10). Two tie
   tubes Ø30 and the roller shafts hold them together.
3. **Reel:** core from PE pipe 315 SDR17, two aluminium flanges Ø900 × 4 mm, 6 tie rods M10 inside the core, two
   weld-on hubs on a shaft Ø25 in two UCF205 bearings. Reel axis at y −100, z 1240.
4. **Drive:** 48 V worm gearmotor (350 W, 100 rpm, 30 Nm) on a bracket with two standoffs on the left plate, chain
   08B 12 → 36 teeth.
5. **Pinch rollers** behind the robot (y −790): bottom roller fixed with the length encoder, top roller in slots,
   pressed down by two springs (2 × 150 N). A lower guide roller at z 260 brings the hose to the ground.
6. **Hose:** 150 m of 3" lay-flat PVC with 65 outlets every 2 m (the first 20 m without outlets).
7. **At the ditch** (not part of the robot model, drawn in the animation): petrol pump on a skid, suction hose with a
   strainer, a 3-way valve (pump → hose / hose → drain) and the hose coupling.

## 3. Why lay-flat hose, wound empty

| | PE hose on a reel with a swivel (classic hose reel) | **Lay-flat, wound empty (chosen)** |
| --- | --- | --- |
| Hose 150 m | 63 mm PE ≈ 160 kg empty, ≈ 470 kg full | 3" lay-flat ≈ 57 kg empty, only empty on the reel |
| Friction loss at 10 m³/h | ≈ 0.5 bar (Ø51 bore) | ≈ 0.1 bar (Ø76 bore) |
| Reel | Ø1.3 m+ (bending radius of PE), swivel, level-wind | Ø0.9 m, no swivel, one hose wide: no level-wind |
| Robot | must carry or drag the water | never carries water; the full hose (≈ 660 l) stays in the field |

The answer to "how can the hose keep giving water while it gets shorter" is: **it does not need to.** The hose lies
still at full length while the water runs. Only when it is empty does the robot wind it up. With a classic hose reel
the water flows through a swivel into the coil; with lay-flat hose that does not work (it is round when full and
cannot be wound), and the water would make the reel far too heavy for this robot (161 kg).

**Low pressure with a lot of water** suits lay-flat hose well: a big bore, little friction. At 7.4 m³/h the hose loses
only 0.21 m of head over 145 m. The whole system needs just 1.8 m at the hydrant and 3.6 m at the pump.

## 4. Outlets (option b) and the strip

- **Flooding, not spraying.** Each outlet lets the water out at the ground through a short flat tail. The water
  spreads until the wet area soaks up as much as the outlet gives: area = flow / infiltration. With 120 l/h and
  15 mm/h that is 8 m², i.e. 2 m (outlet pitch) × 4 m (strip width). The flow follows from
  `infiltration × pitch × strip_w`, not the other way round: give more and the water runs off or ponds.
- **Restrictor Ø3.5 mm** in each take-off. A small orifice gives most of the pressure drop, so friction along the
  hose hardly matters: CU 98.9 % on level ground. Smaller clogs more easily (ditch water): 0.8 mm filter at the pump.
- **Slope** is the real limit at this low pressure: ±0.5 % over the strip already gives 0.79 … 0.87 between the
  smallest and the largest outlet. On sloping fields: lay the strips across the slope, use a higher inlet pressure
  with smaller restrictors, or use pressure-compensating drippers as outlets.
- **The first 20 m (lead) have no outlets.** They run over the headland from the hydrant to the start of the strip,
  so the strips can be 4 m apart without moving the hydrant: within ±18 m about 9 strips per hydrant position.
- The real flooding principle (water flowing over the surface from the top of the field) needs a flat, even, slightly
  sloping field; outlets every 2 m give the same benefit (low pressure, no wind drift, no evaporation in the air)
  without levelling the land.

## 5. Reel and hose path

- **One hose wide.** Lay-flat hose winds on itself as a flat spiral, like a fire hose. Core Ø315 and 3.2 mm per wrap
  (hose 2.6 + outlets, estimated) give Ø843 for 150 m: 29 mm inside the Ø900 flanges. No level-wind, no traversing
  guide: the flanges are 130 mm apart for a 121 mm hose.
- **Reel on top, axis across.** The hose leaves the bottom of the coil to the rear, runs to the nip, down behind the
  robot and onto the ground between the wheels. A reel with a vertical axis (lying flat) would be lower but needs a
  90° twist and a guide that follows the coil radius.
- **Core from PE pipe 315** (cheap, light, smooth for the hose), clamped between the flanges by 6 tie rods inside the
  pipe, so nothing sticks out into the coil. The hose end is fixed to the core with a strap clamp and a closed end cap.
- **Reserve 3 m** stays on the reel so the end clamp is never loaded.
- The hose path (`G.run_points`) is computed from the coil radius: tangent from the coil to the nip, around the bottom
  pinch roller, vertically down, around the guide roller. `hose_check()` gives ≥ 13 mm from the hose to the nearest
  part, the nuts of the bearing bolts inside the plates. **Use button-head bolts or a plastic guide strip there.**

## 6. Pinch rollers

Three jobs for one pair of rollers:

1. **Closing the hose** while the strip is irrigated. The far end of the strip runs up into the robot; without the
   nip the water would also fill the coil (4.5 l per metre of hose on the reel, and the coil would swell against the
   flanges). At 15 kPa a
   flat 121 mm hose needs about 19 N of clamping (10 mm contact band, estimated); the springs give 300 N.
2. **Squeezing** the last water out while winding, back towards the hydrant where the drain valve is open.
3. **Measuring** the hose length: encoder on the bottom roller. Together with the reel angle it gives the coil
   radius, so the controller knows the hose that is left and the winding speed.

The water pressure pulls 69 N on the robot towards the hydrant; the robot holds that with its brakes (grip ≈ 1050 N).

## 7. Drive

- Winding tension 150 N (a tight coil) at a full coil (r 421 mm) needs 63 Nm. The gearmotor gives 30 Nm × 3 × 0.95 =
  86 Nm (× 1.4).
- Maximum reel speed 33 rpm: 0.58 m/s at the smallest coil, so the robot reverses at up to 0.6 m/s while winding.
  The reel sets the pace, the robot follows (current limit on the motor as tension control).
- Laying out: the robot pulls the hose off against 50 N of back tension (motor short-circuited / regenerating), so the
  reel cannot overrun.
- A worm gear holds the reel when the power is off.

## 8. Pump at the ditch

- The system needs only 3.6 m of head at 7.4 m³/h (72 W hydraulic). A 3" petrol pump (class "WB30", 4 kW) then runs
  almost at idle: throttle 0.37, ≈ 0.35 l/h. It is far too big for this. With 24 h a day that is ≈ 7 l of petrol a
  day, 0.5 l per mm per ha.
- **Better:** a small 2" pump, or an electric pump with a battery and solar panel at the ditch (≈ 100 W). Then the
  hydrant can also charge the robot.
- **Needed at the ditch, for autonomy:** a remote start/stop (radio or GSM relay on the engine), a motorised 3-way
  valve (pump → hose / hose → drain), a pressure sensor at the hydrant, a 0.8 mm filter, and a foot valve so the pump
  stays primed.

## 9. Capacity

| | |
| --- | --- |
| Per strip | 124 × 4 m = 496 m², 25 mm, 12.4 m³ |
| Time per strip | 122 min, of which 100 min irrigating (set by the infiltration) |
| 24 h | 11.8 strips, 0.59 ha at 25 mm |
| Sustained | 3.5 mm/day evaporation on ≈ 4.2 ha: one robot can keep about 4 ha of grassland wet in a dry summer |

The infiltration sets the capacity: wet area × infiltration = flow. More capacity needs a longer hose or a second
hose, not a bigger pump. The robot is idle most of the time (it drives 8 min per strip), so it can do other work
between the strips if the hose may stay coupled.

## 10. Stability and axle loads

- Implement 146 kg, centre of gravity at y −205, z 1058 (reel full, hose empty).
- Robot + reel 308 kg, centre of gravity at z 788: tips sideways at 25° and backwards at 30° (static). Grassland
  near ditches is mostly flat; avoid driving across steep ditch banks with a full reel.
- Front axle 139 kg, rear 169 kg: well within 500 kg per axle.
- The reel stands 1.7 m high behind the GNSS antenna (y 575, z 740). It shades a narrow wedge of sky to the rear
  (about ±6° wide, up to ≈ 65° elevation). If the RTK fix suffers, put the antenna on a short mast.

## 11. Checks

| Check | Result |
| --- | --- |
| `check_interference()` (with the robot) | none |
| `check_fit()` (reel turned in 8 steps over a full turn) | none |
| `clearance()` | mount 37.5 mm (foot bolts to the rear lower beam), frame 56 mm, reel 206 mm, drive 117 mm, pinch 144 mm |
| `hose_check()` | hose run ≥ 12.9 mm from the bearing nuts, reel full and empty |
| Animation | robot heading ≤ 17° in the lead curve, reel 3 … 148 m, 62 outlets in the field |

## 12. Parts and cost (estimated, 2026, excl. VAT)

| Part | € |
| --- | --- |
| 3" lay-flat hose PVC 150 m | 375 |
| 65 outlets: take-off grommet, restrictor, flat tail 0.5 m | 130 |
| 2 couplings 3" (Storz or Bauer), end cap, strap clamp | 70 |
| Laser cutting: 2 side plates 6 mm, feet, brackets, motor bracket | 200 |
| Cross tubes, tie tubes, standoffs, welding | 60 |
| PE pipe 315 SDR17 (0.13 m), 2 aluminium flanges Ø900 × 4 | 220 |
| Shaft, 2 weld-on hubs, tie rods, bolts | 80 |
| Bearings: 2 × UCF205, 2 × UCFL204, 2 bushings | 60 |
| 3 PU-coated rollers Ø80, springs, sliding blocks | 170 |
| Worm gearmotor 48 V 350 W + motor driver | 300 |
| Chain 08B, sprockets 12T and 36T | 40 |
| Encoder, controller, radio, box | 200 |
| **Robot side** | **≈ 1,900** |
| At the ditch: motorised 3" 3-way valve, remote start, pressure sensor, filter, suction hose (petrol pump not included) | ≈ 650 |

## 13. Open points

- **Measure the infiltration and the strip width** on the real field. They set the flow and the time per strip.
- **Test the outlets on the reel:** do the take-offs and tails wind flat, do they wear, do they leak when clamped in the
  nip? Option: outlets made in the hose wall with only a slit valve, without a tail.
- **Automatic coupling to the hydrants** (phase 2), so the robot can move to the next hydrant or the next field without
  a person: for example a funnel coupling on a post that the robot drives the hose end into.
- The lead curve over the headland: the empty hose lies in a curve when laid, but moves when it fills. Peg it, or lay
  the lead straight and move the hydrant along a lay-flat main pipe at the ditch.
- Slopes: see section 4.
- Smaller pump (section 8).
