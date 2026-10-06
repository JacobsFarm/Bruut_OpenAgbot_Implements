# Simple liquid fertilizer applicator version 2 (disc + knife): rationale

5 October 2026. Model: `Liquid_Fertilizer_Applicator_Simple_v2.FCStd` (FreeCAD 1.1, generated with `build_lfs2.py`).
Figures come from the model, `lfs2_calc.py` and `lfs2_ground.py`. Where something is assumed or estimated, this is stated.

Version 2 is [version 1](../simple/RATIONALE.md) with **a cutting disc in front of the knife in each row**. The knife alone
cannot cut the roots well in dry, tough sward: it lifts or tears the sward. In v2 a flat disc first cuts through
the sward. The knife runs right behind it in the same plane and only opens the cut. That is the same
principle as the [advanced variant](../advanced/RATIONALE.md), but rigid on a floating toolbar, with
standard parts.

Everything else is the same as v1:
- the headstock with the low pivot;
- the lift frame with cross tube, toolbar and arms;
- the actuator with slotted hole;
- the depth wheels;
- the dosing unit on the headstock (diaphragm pump, pressure regulator 2.0 bar, orifice plates).

The rationale for those is in v1 and is not repeated here.

![overview rear right](previews/1_iso_rear_right.png)

---

## 1. What changes compared with version 1

| | Version 1 (knife only) | **Version 2 (disc + knife)** |
| --- | --- | --- |
| Making the slot | knife cuts by itself, cutting edge 25° backwards | **disc Ø 300 × 4** cuts 45 mm deep, knife at 10° follows 40 mm deep in the cut |
| Gap knife – disc | – | 14 mm; the knife enters the cut 41 mm behind the point where the disc leaves the ground |
| Outflow | approx. 25 mm deep | approx. 27 mm deep |
| Element | 3.9 kg | 9.1 kg (disc 2.1 kg, bearing hub 1.4 kg, disc arm 1.3 kg) |
| Mass implement / lift frame | 75 / 44 kg | 101 / 70 kg |
| Down force | not needed: the knife pulls itself into the ground | **the discs need down force** (estimated 100 N per disc); it comes from the weight of the lift frame (§ 3) |
| Actuator | 1000 N, approx. 25 mm/s: 8 s lifting | **1500 N**, approx. 20 mm/s: 10 s lifting; after 5.1 s discs and knives are out of the ground |
| Lifted, clear of the ground | knives 124 mm | discs 86 mm, knives 177 mm |
| Front axle lifted, empty tank (robot 150 kg) | 492 N | 377 N; with 40 kg ballast 200 N |
| Dimensions (w × l × h) | 906 × 672 × 917 mm | 938 × 639 × 922 mm: the hubs of the outer rows stick out 16 mm beyond the toolbar, still well within the robot width of 978 mm |
| Cost (indicative) | approx. € 595 | **approx. € 915** |

## 2. The element: disc, hub and knife

![disc and knife, side view](previews/8_knife_side.png)

- **Cutting disc**: a flat, hardened coulter disc Ø 300 × 4 with 4-hole mounting. This is a common part for seeders and disc fertilizer applicators.
  - The centre is 105 mm above the ground, so the disc cuts **45 mm** deep.
  - It cuts the roots and the sward before the knife arrives.
- **Bearing hub**: a hub with flange and two bearings (6204-2RS) on an **M20 axle bolt**.
  - The hub sits on one side of the disc; the disc hangs freely from it.
  - That is less work than a fork on both sides. Moreover a fork does not fit next to the depth wheels.
- **Disc arm**: a 60 × 10 strip, welded at an angle under the base plate of the knife holder.
  - The foot runs over the whole length of the base plate, so there is a long weld.
  - The base plate is 20 mm wider on that side (strip 100 × 10).
- **Hub away from the depth wheel**: the hub and the arm are on the side where the depth wheel is not (`disc_side` in `lfs2_params.py`).
  - Rows 2 and 4 have the hub on the inside, rows 1 and 5 on the outside, row 3 on the right.
  - This keeps room between discs, hubs and depth wheels everywhere.
- **Knife**: the same 50 × 10 strip with M12 pivot bolt and M6 shear bolt as in v1.
  - The knife now stands **10° backwards instead of 25°**. The disc has already cut the roots, so the knife no longer has to cut at an angle; it only opens the cut.
  - A steeper knife can stand closer behind the disc. At the narrowest point the gap is 14 mm; upwards it gets wider.
  - The knife tip is **5 mm less deep** than the disc (40 against 45 mm), just as in the advanced variant. This way the knife runs in the pre-cut slot.
  - The tube sits behind the knife; the outflow is approx. 27 mm deep.
- **Depth wheels**: now stand between disc and knife tip (axle at y = −390). An adjusting pin chooses the depth, as in v1.
  - The wheel position makes little difference for ground following: shifting between y = −350 and −450 changes the standard deviation of the knife depth only from 10.1 to 9.2 mm.
  - The spread comes mainly from the rigid toolbar.
- **Cross tube**: 55 mm further back (y = −420) and centre to centre with the arms.
  - The disc and the disc arm of row 3 run underneath it.
  - The eyes for the actuator housing stick forward to the old pin. The lifting kinematics are therefore the same as v1.

## 3. Down force: the discs have to go in

A knife pulls itself into the ground with its tip. **A disc has to be pressed in with weight.** That is the
main price of version 2.

The moments about the pivot of the lift frame (z = 200) are estimated, see `lfs2_calc.LOADS`:

| Per element | Normal | Heavy sward |
| --- | --- | --- |
| Down force the disc needs for 45 mm | 100 N | 200 N |
| Draft force disc (rolling + cutting) | 30 N | 50 N |
| Draft force knife in the pre-cut slot | 60 N | 125 N |

| Moments about the pivot (5 elements) | Normal | Heavy sward |
| --- | --- | --- |
| Weight of lift frame (70 kg) + suction force of knives, downwards | 276 Nm | 314 Nm |
| Discs pushed upwards | 125 Nm | 250 Nm |
| Draft force of knives and discs | 105 Nm | 206 Nm |
| **Force on the 2 depth wheels together** | **143 N** | **0 N**: the lift frame floats up and the discs do not reach depth |

- **Normally the lift frame itself can deliver up to 137 N per disc.** Without ballast the discs then reach depth and the depth wheels keep ground contact.
- **In hard sward approx. 40–50 kg of ballast is needed.**
  - Use steel plates on the toolbar, fixed with the same U-bolts.
  - 20 kg of ballast gives 192 N per disc, 40 kg gives 246 N.
- **Ballast has a downside.** When lifted it hangs on the robot.
  - With 40 kg of ballast and an empty tank the front axle of a 150 kg robot drops to 200 N. That is just as light as with the advanced variant (188 N).
  - So only put the ballast on the toolbar if the sward demands it, and weigh the robot per axle.
- **Alternative to ballast: two gas springs** between the headstock and the cross tube.
  - While working they press the lift frame down and thus use the weight of the robot.
  - When lifted their force is internal, so the front axle does not get lighter.
  - Disadvantage: the actuator also has to overcome the gas springs and so has to be heavier. This has not been worked out; first measure whether it is needed.
- **Draft force for the robot**:
  - normal 461 N, heavy 875 N;
  - grip with an empty tank approx. 950 N (μ = 0.5).
  - In heavy sward the robot is thus close to its limit.

## 4. Lifting

Lifting works as in v1: working = actuator fully out, lifting = fully in, with a slotted hole for floating.
- The lift frame has become 26 kg heavier. With a 1.5 × margin **1180 N** is needed, so an actuator of **1500 N** (stroke 200).
- Cheap 1500 N actuators reach 10–20 mm/s. Calculated with 20 mm/s:

| Step | Stroke | Time |
| --- | --- | --- |
| free stroke in the slotted hole | 48 mm | 2.4 s |
| discs and knives out of the ground | 102 mm | 5.1 s |
| fully lifted (discs 86 mm, knives 177 mm, wheels 162 mm clear) | 200 mm | 10 s |

The robot stops at the end of the row and waits until the discs and knives are out of the ground. It lowers
while driving.

## 5. Ground following compared

![ground following version 2](previews/12_ground_following_comparison.png)

![animation version 2 over the bumpy strip](previews/animation_strip_ground_following.gif)

The same strip, the same robot attitude and the same 80 robot positions as for v1 and the advanced variant.
Settings: v1 knife 40 mm; v2 disc 45 and knife 40 mm; advanced disc 40 and knife 35 mm.

| Working position, 80 positions | Advanced | Version 1 | **Version 2** |
| --- | --- | --- | --- |
| Knife depth, range | 12–64 mm | 4–60 mm | 3–60 mm |
| Knife depth, mean / standard deviation | 41 / 8.5 mm | 35 / 8.4 mm | 33 / 9.5 mm |
| Knife depth between 25 and 55 mm | 93 % | 86 % | 82 % |
| Cut of the disc, range / mean | – | – | 10–67 mm / 41 mm |
| Cut between 25 and 55 mm | – | – | 92 % |
| Knife out of the ground | 0 | 0 | 0 |
| Knife deeper than the cut | – | – | 22 of the 400 row positions, at most 12 mm |
| Knife angle | fixed relative to the arm | 19–28° | 4–13° |

What this shows:
- **The cut follows the ground level as well as the knife in v1.** On average it is 41 mm deep at a setting of 45 mm. The toolbar rests on the highest depth wheel, so everything ends up a few mm shallower than set.
- **The knife is 72 mm behind the depth wheels.** Pitching of the lift frame (−5 to +6°) counts for a bit more there, and so the spread of the knife depth is somewhat larger than in v1.
- **Sometimes the knife goes deeper than the cut.** This happens in 5 % of the row positions, by at most 12 mm. At those spots the knife cuts a few mm into undisturbed ground. That costs some extra draft force, but the knife can manage that with its cutting edge.
- **A pit or bump under one row still comes through fully**, as in v1: the knives of rows 4 and 5 go to 3–4 mm shallow at the pit. That is the price of the rigid toolbar. The advanced variant absorbs this per row with depth rings.

In the animation the panel at the bottom right shows per row the knife depth (bar) and the cut of the disc (line).

## 6. Calculations (summary)

Recalculate with `python lfs2_calc.py`.

| Quantity | Value |
| --- | --- |
| Dosing | same as v1: 1.0 mm plate at 2.0 bar gives 538 l/ha at 0.75 m/s |
| Lever arms about the pivot | weight 350 mm, disc 250 mm, knife tip 391 mm (horizontal) / 240 mm (vertical), depth wheel 320 mm |
| Depth wheels (normal) | 2 × 72 N; force in the pivot 135 N downwards and 450 N draft force |
| Maximum down force per disc without ballast | 137 N (with 20 kg ballast 192 N, with 40 kg 246 N) |
| Ballast for heavy sward | 41 kg (wheels just on the ground), 50 kg (wheels 100 N) |
| M6 (4.6) shear bolt | breaks at 1.6 kN on the knife tip; bending stress in the knife then 116 MPa |
| Floating range | −9.1 / +11.0° (depth wheels −50 / +62 mm) |
| Lifting | 28.6°; actuator 1180 N (incl. 1.5 × margin), 10 s at 20 mm/s |
| Axle load robot 150 kg, tank 150 l | working position rear axle full/empty 2836 / 1335 N; lifted front axle full/empty 641 / 377 N |
| Mass implement / lift frame / element / depth wheel | 101 / 70 / 9.1 / 7.0 kg |

| Robot | Tank relative to rear axle | Front axle lifted, full / empty | Empty, with 40 kg ballast | v1, empty | Advanced, empty |
| --- | --- | --- | --- | --- | --- |
| 150 kg | 300 mm | 906 / 377 N | 200 N | 492 N | 188 N |
| 150 kg | 450 mm | 1171 / 377 N | 200 N | 492 N | 188 N |
| 200 kg | 450 mm | 1416 / 622 N | 445 N | 737 N | 433 N |
| 250 kg | 450 mm | 1662 / 867 N | 690 N | 982 N | 679 N |

## 7. Bill of materials and cost (indicative)

Prices in euros excl. VAT, bought individually (2026 price level, not quoted). Compared with v1 the following are added:

| Group | Contents | approx. € |
| --- | --- | --- |
| Discs | 5 flat coulter discs Ø 300 × 4, hardened, 4-hole | 125 |
| Hubs | 5 bearing hubs with 4-hole flange (2 × 6204-2RS), M20 axle bolts, rings | 160 |
| Extra steel | 5 disc arms strip 60 × 10 (approx. 330 mm), wider base plates (approx. 7 kg) | 20 |
| Actuator | 1500 N instead of 1000 N | 15 |
| **Total v2** | v1 (€ 595) + the above | **approx. € 915** |

The rest of the bill of materials and the cutting list are in [v1 § 3.7 and § 7](../simple/RATIONALE.md). Changes to the cutting list:
- base plate of knife holder: strip 100 × 10 × 115 instead of 80 × 10 × 100;
- disc arm: 5 × strip 60 × 10, approx. 330 mm (sloping part + foot);
- cross tube: at y = −420, the eyes 60 mm longer.

Keep spares: as in v1, plus 1 disc and 2 bearings 6204-2RS.

## 8. Risks and test plan (in addition to v1)

| Risk | Measure / test |
| --- | --- |
| The discs do not reach depth (too little down force) | **Build one element first** and measure the down force at 45 mm depth, on wet and dry grassland, with weights or a spring scale. Then choose the ballast (0–50 kg) and check that the front axle does not get too light when lifted. |
| The front axle gets too light with ballast | Ballast only in hard sward; weigh the robot per axle. Alternative: gas springs (§ 3). |
| Grass or roots jam between disc and knife | The gap is 14 mm: narrow enough as a scraper, but assess it in the trial. If necessary move the knife 5 mm forward (`knife_pivot`) or a scraper on the disc arm. |
| The knife runs beside the cut under side load | The disc hangs on one side from the hub. Play in the hub or a bent arm shifts the cut. At every refill check that knife and disc are in one line. |
| Bearing wear in the hubs | Bearings 6204-2RS with dust seal; replace when the disc has play. |
| The disc clogs with mud | A flat, sharp disc usually keeps itself clean. In sticky soil a scraper on the disc arm. |
| Lifting takes 10 s | Robot stops at the end of the row; after 5 s everything is out of the ground. |

The other risks are the same as [v1 § 8](../simple/RATIONALE.md): dose follows the speed, clogging of the
plates, shear bolt, interlock reversing/sharp steering, low ground clearance of the headstock.

## 9. Model and files

| File | Contents |
| --- | --- |
| `Liquid_Fertilizer_Applicator_Simple_v2.FCStd` | the model in working position (robot reference hidden) |
| `lfs2_params.py` | all dimensions; new: disc, hub, disc arm, `disc_side`, `knife_depth` |
| `lfs2_kin.py` | kinematics, plus the gap between knife and disc (`disc_knife_gap`) |
| `lfs2_parts.py` | one function per part; new: `disc`, `disc_hub`, `disc_stub`, `disc_arm` |
| `build_lfs2.py` | model tree, lifting (`build(psi=...)`), interference check, mass, images |
| `lfs2_calc.py` | dosing, forces on the lift frame with discs (`LOADS`), ballast, lifting, axle load, cost |
| `lfs2_ground.py` | ground following: cut of the disc, knife depth, knife deeper than the cut |
| `plot_ground2.py` | comparison chart (`previews/12_ground_following_comparison.png`) |
| `ground_advanced_reference.json`, `ground_simple_v1_reference.json` | knife depth of the advanced variant and of v1 at the same positions |
| `animate_lfs2.py` / `make_gif_lfs2.py` | animation behind the robot model and the GIF |
| `run_in_freecad.py` | macro: rebuild in FreeCAD (F6) |

`build_lfs2.check_interference()` gives 0 hits in all positions: working position, both limits of the floating range and
lifted, with the robot reference included. `animate_lfs2.check_fit()` gives 0 hits against the real robot model.
