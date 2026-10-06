# Liquid fertilizer applicator (renure): design rationale

4 October 2026. Model: `Liquid_Fertilizer_Applicator.FCStd` (FreeCAD 1.1, generated with `build_lfa.py`).
Figures come from the model and from `lfa_calc.py`. Where something is assumed or estimated, this is stated.

**Revised after the animation (§ 4.11).** The animation over a bumpy strip showed that a toolbar hanging rigidly from the
actuator moves up and down too much: the robot pitches, and the elements hang well over 1.3 m behind the robot centre.
The toolbar now works in **floating position**. There is a slotted hole in the upper suspension of the actuator, the actuator lies
flatter and is turned around, the springs are softer, and the down force comes from the toolbar's own weight.

![overview rear right](previews/1_iso_rear_right.png)

---

## 1. Assignment and starting points

- The liquid has to go into the soil: first cut a small groove, then a small knife follows with a tube behind it that places the liquid in the slot.
- Several elements over 1 metre.
- One ground wheel. When the wheel turns, the liquid flows (pump driven by the wheel).
- First as a stand-alone implement, but fitting the Bruut OpenAgbot: track 750 mm, wheelbase 1000 mm, 40 × 40 box beams with M10 holes on a 50 mm grid, rear axle at 215 mm height.
- Set up differently from the inspiration, but with the lessons from it.

## 2. What I take from the inspiration

| Source | What works | What is different here, and why |
| --- | --- | --- |
| **Light disc fertilizer applicator** (Bartlema / NCOK, demo day Zwartebroek) | The discs drive a roller pump, so the dosing depends on the distance travelled. Light and without electronics. In the photos: two discs on one axle with the pump in the middle, two knives with a hose, on a hoe parallelogram. | In the prototype the same discs have to **cut and drive the pump**. If a disc slips in the sward or clogs up, the dosing changes immediately, and every element has its own pump. Here **one separate ground wheel with spikes** (a measuring wheel) drives **one central 5-channel pump** for the whole toolbar. The discs only have to cut. |
| **Fertilizing robot Fieldworkers** (Sterke Erven) | Element with a spring like a hoe element, 20 cm between the injection tines, light vehicle that works day and night, pump determines the total quantity, task map, buffer tank on the headland. | Taken over: **20 cm row spacing**, **spring load per element** and the light set-up. Different: **disc + knife instead of tines**. In grassland a tine tears the sward open and grass can wind around the tine. A disc cuts the roots first, so the knife follows with little force. The pump is **mechanically driven** instead of electrically: the dosing automatically follows the distance travelled, without a controller. A task map remains possible as an extension (§ 4.7). |

Both sources themselves mention refilling via a docking station. § 4.7 and § 6 show that this is also the key for this implement.

## 3. The design in brief

![side view with ground](previews/3_side_right.png)

1. **Mounting headstock** (2 pieces): top plate on the robot's rear lower beam, M10 through the existing holes.
2. **Parallel linkage** (2 × 2 rods) with an **electric linear actuator**. While working the actuator is fully extended and the **toolbar floats** via a slotted hole (−80 / +68 mm); on the headland the actuator pulls the toolbar up 140 mm.
3. **Toolbar** 60 × 60 × 4, 900 mm long.
4. **5 injection elements** at 200 mm (x = −400, −200, 0, 200, 400). Each element has a Ø 300 cutting disc with depth rings, an 8 mm knife with a stainless steel tube and check valve, and a spring leg.
5. **Ground wheel** Ø 400 with spikes between rows 4 and 5, with a 30T → 15T chain to the pump shaft.
6. **5-channel peristaltic pump** (roller pump) on the toolbar, with filter, manifold and a suction hose with camlock to the tank on the robot.

| Characteristic | Value |
| --- | --- |
| Working width | 1.0 m (5 rows × 200 mm) |
| Working depth | 40 mm (disc), knife tip 35 mm, outflow approx. 27 mm below ground level |
| Dosing | 89 to 1316 l/ha in 18 settings (§ 4.7), standard 505 l/ha |
| Capacity | 0.36 ha/h at 1 m/s (theoretical) |
| Down force | approx. 133 N per element, from the toolbar's own weight (floating position) |
| Ground following | toolbar floats −80 / +68 mm, each element within that still −32 / +66 mm |
| Lift height | 140 mm: knife 57 mm, disc 68 mm and ground wheel 88 mm clear of the ground |
| Dimensions | 906 × 1037 × 860 mm (w × l × h), within the robot width of 978 mm |
| Mass (model) | 107 kg, of which 83 kg moves along when lifting |

**Operation.** The robot lowers the toolbar; the actuator goes fully out. The depth rings come onto the ground, the discs go 40 mm into the sward and the ground wheel touches the ground. The toolbar then rests on the elements and the ground wheel and floats along with the ground level, even when the robot pitches or rolls. While driving the ground wheel turns the pump. Each row gets a fixed quantity per metre, which enters the slot via the knife and the tube. On the headland the actuator pulls the toolbar up. The ground wheel then comes loose, the pump stands still and the check valves keep the hoses filled.

## 4. Design choices

### 4.1 Working width and row spacing

- **5 rows at 200 mm** gives exactly 1 m working width, equal to the 20 cm that Fieldworkers uses. In grassland the fertilizer is then spread over narrow strips, without having more elements than necessary (each element needs down force, see § 6).
- The implement is 906 mm wide and stays **within the robot width** (978 mm over the wheel brackets). The toolbar only has to run to the outer clamp; the working width stays 1 m because each row serves a 200 mm strip.
- The clamps slide along the toolbar. A different row spacing (for example 4 × 250 mm) only needs different values in `row_x`.

### 4.2 Cutting: thin disc with depth rings

![element](previews/8_unit_side.png)

- **Disc Ø 300 × 3 mm**, smooth and ground, made of drill steel. A small, thin disc has a smaller contact area in the soil and therefore needs less down force. That is the most important point for a light robot (§ 6).
- **Depth rings Ø 220** on both sides of the disc. Working depth = (300 − 220) / 2 = **40 mm**. The rings roll on the ground, so each element follows the ground level by itself, independent of how the robot tilts. Other depth: change the rings (Ø 240 gives 30 mm, Ø 200 gives 50 mm).
- The rings **press the sward next to the cut downwards**, so that it does not lift and the cut stays clean. Down force that is left over goes via the rings to the ground.
- This means **no separate depth wheel per element** is needed. The element is only 55 mm wide; with 200 mm row spacing and the ground wheel between the rows there is no room for a depth wheel anyway.

### 4.3 Knife and injection tube

- The knife sits **behind the disc, in the same plane**: 8 mm thick, 30 mm wide, Hardox 450.
- The **knife tip is 5 mm higher than the bottom of the disc** (35 mm deep). The knife only opens the pre-cut slot and does not cut new roots. That costs little draft force and little down force.
- The front edge **slopes 14.5° forward** (tip first). The knife therefore pulls itself into the slot and takes over part of the required down force. The depth rings limit the depth.
- The **gap between knife and disc is at least 7 mm**, approx. 70 mm above ground level. It works as a scraper for the disc and is too narrow for roots to jam in (check this in practice, § 7).
- **Stainless steel 316 tube 8 × 1** directly behind the knife. It lies in the lee of the knife, so that no soil rubs against it, and the **outflow is approx. 27 mm deep**, behind the knife tip where the slot is still open.
- **Check valve (approx. 0.5 bar)** on top of the tube. The hoses stay filled, so dosing starts immediately after lowering, and nothing drips after lifting.
- The knife is held with 2 bolts between the fork plates and is quick to replace. Option: make one of the two a shear bolt.
- **The slot stays open**: there is no press wheel. With ammonium-containing products a small press wheel per row can lower the emissions. Room has been kept behind the knife for this.

### 4.4 Suspension of the element: one pivot and a spring leg

![element detail](previews/6_unit_detail.png)

- Each element hangs from **one pivot** (Ø 20 pin) behind the toolbar. The arm consists of two laser-cut 6 mm fork plates. The disc sits between them on an axle supported on both sides, so there is no skewed load on the bearing.
- **Spring leg**: compression spring Ø 35, wire 5 mm, free length 160 mm, **soft: c ≈ 4 N/mm** (assumed spring).
  - In floating position the toolbar's weight determines the down force: (813 N − 150 N ground wheel) / 5 ≈ **133 N per element**.
  - The springs distribute that weight over the elements. A soft spring keeps the force per element equal, even if one element is on a bump and another in a pit. In the animation the force stayed between 107 and 169 N.
  - With the lower spring seat (nut on the spring rod) you set **how high the toolbar floats**. On flat ground the arm is then at 2.7°, with the toolbar 11 mm above the design height.
- **Stone protection**: the arm can go up 60 mm. The spring then goes to 95 mm; it is solid at about 50 mm.
- The **adjusting nut on top of the spring rod is also the lower stop**. The arm can drop 8° (32 mm at the disc); when lifting it hangs from the nut.
- **Why no parallelogram per element**, as with hoe elements and the Steketee suspension in the inspiration? That is four extra hinges per element, and it gets heavier and longer. The disadvantage of one pivot is that the knife tilts about the disc when the arm turns, and also when the robot pitches (the toolbar stays parallel to the robot).
  - In the animation the **knife depth therefore varied from 12 to 64 mm** at a fixed disc depth of 40 mm.
  - A parallelogram per element removes the part caused by the arm angle; the pitching of the robot remains.
  - Whether that spread matters for the placement of the fertilizer has to be shown by the field trial (§ 7).

### 4.5 Drive: one ground wheel, a chain and the pump on the same shaft

![drive](previews/7_drive_detail.png)

- **Ground wheel Ø 400** with 16 spikes (rim Ø 360 × 40, galvanised steel), at x = 312, between rows 4 and 5. It runs on ground between two slots and thus not in a slot. It overlaps 7 mm with the inner edge of the track of the right rear wheel; that has little influence.
- The **wheel arm rotates about the same axis as the driven sprocket**. When the wheel moves up and down, the chain length stays the same. A chain tensioner is only needed to change sprockets.
- A **torsion spring around the shaft** presses the wheel onto the ground; the spikes prevent slip.
- **Chain 08B-1 (1/2")**, 30T on the wheel and 15T on the pump shaft, 90 links. The pump therefore turns 2 × as fast as the wheel.
- An **M18 inductive sensor** counts the teeth of the 15T sprocket. With that the robot sees that the pump is turning (chain breakage or a blocked wheel), knows speed and area, and can stop if the pump stands still while driving.
- The arm can drop 12° (approx. 60 mm), so that the wheel stays on the ground even in a pit; in the animation it never lost contact.
- **Lifting is stopping**: when lifted the ground wheel hangs 88 mm above the ground, so the pump stands still without a switch or valve.
- Approx. 40 mm has been kept free between the pump coupling and the left bearing for an **electromagnetic clutch**, in case you later want to switch locally on/off without lifting.

### 4.6 Pump: 5-channel peristaltic

- **Each row has its own hose in the same pump head**, so the distribution stays equal, even if one outlet has more resistance. With one pump and a manifold block the liquid goes the way of least resistance and a blocked row goes unnoticed.
- **Positive displacement pump**: the quantity per revolution is practically independent of pressure and viscosity.
- **Only the hose touches the liquid.** That makes the pump suitable for corrosive products (acidic air scrubber liquid, ammonium-containing mineral concentrate). There are no valves or shaft seals, the pump is self-priming and may run dry.
- At standstill the hose is pinched shut, so nothing siphons out of the tank.
- Difference from the inspiration: there a roller pump per element sits on the disc axle. Here one pump head for all rows is fixed on the toolbar. The hoses do not move along with the elements, except the last piece to the valve.
- **Output**: roller track r = 35 mm, pump hose 6.4 × 1.6 mm, gives **6.0 ml per revolution per channel** (fill factor 0.85 assumed; to be calibrated). At 1 m/s the pump turns at 101 rpm, well within the range of hose pumps.
- Disadvantage: the pump hose wears. Keep a spare set and choose the hose material for the product.

### 4.7 Setting the dosing

Dose [l/ha] = i · V · 10 000 / (O · a), with i = z<sub>wheel</sub> / z<sub>pump shaft</sub>, V = stroke volume per channel [l],
O = effective rolling circumference of the ground wheel (1.19 m assumed, to be calibrated) and a = row spacing (0.2 m).

| Pump hose (inner Ø) | 15/24T (i 0.62) | 20/18T (1.11) | 24/15T (1.60) | **30/15T (2.0)** | 36/15T (2.40) | 40/12T (3.33) |
| --- | --- | --- | --- | --- | --- | --- |
| 4.8 mm (3.4 ml/rev) | 89 | 158 | 227 | 284 | 341 | 474 |
| **6.4 mm (6.0 ml/rev)** | 158 | 281 | 404 | **505** | 606 | 842 |
| 8.0 mm (9.4 ml/rev) | 247 | 439 | 632 | 790 | 947 | 1316 |

- **The driving speed does not change the dosing.** Even when slowing down for turns or obstacles the number of litres per hectare stays the same. At 505 l/ha and 1 m/s, 0.61 l/min goes through each row.
- **Calibrating**: with the toolbar lifted, turn the ground wheel by hand 20 revolutions (approx. 24 m) and catch the five outlets in measuring cups. That gives the dose and the distribution per row (target ±5 %). Measure the rolling circumference in the field over 50 m.
- **What this means for renure.** As an indication, always have the product analysed: mineral concentrate contains approx. 6 to 9 kg N/m³ and liquid fertilizer (UAN, 28 to 30 % N) approx. 360 to 390 kg N/m³. Air scrubber liquid varies strongly.
  - At 505 l/ha mineral concentrate gives **3 to 5 kg N/ha per pass**; a normal application therefore needs several m³ per ha.
  - UAN has to go on the lowest setting (89 l/ha, approx. 32 to 35 kg N/ha).
  - The limit for diluted renure is therefore not the applicator but the **tank capacity and refilling**. That fits the idea of small, frequent applications and a docking station.
- **Task map as an extension**: replace the chain to the pump shaft with a small motor with reduction and use the ground wheel with the sensor as an encoder. Pump, hoses and elements stay the same.

### 4.8 Lifting and floating: parallelogram, slotted hole and electric actuator

- **Parallelogram** with 260 mm rods (30 × 30 × 3 tube, Ø 16 pins). The toolbar stays parallel to the robot.
- **Floating position.** The upper pin of the actuator sits in an **85 mm slotted hole** in the mounting headstock, along the axis of the actuator.
  - While working the actuator is **fully extended (440 mm)**. The pin can then slide freely in the slotted hole, so that the toolbar can float between **−80 and +68 mm** around the design height.
  - The toolbar rests on the elements and the ground wheel. If the robot pitches or rolls, the toolbar follows the ground and not the robot.
  - Before lifting the actuator retracts. The pin comes to the bottom of the slotted hole and takes the toolbar along up to 140 mm.
  - The control is simple: working position = actuator out, lifting = actuator in. No force or position control is needed.
- **Why float** (from the animation, § 4.11)? A robot with a 1 m wheelbase already pitches 1.5 to 2.5° on an undulation of ±14 mm.
  - The elements hang well over 1.3 m behind the robot centre. With a fixed toolbar they therefore move **±40 to 60 mm** up and down relative to the ground.
  - That is more than the spring arms can cope with: in the first simulation they were on their stop half of the time and the knife sometimes came out of the ground.
- **Actuator**: 24 V, stroke 150 mm, installed length approx. 290 mm, at least 1500 N (design 2500 N), IP66, limit switches.
  - It is **turned around**: the housing with the parallel motor is at the bottom on the rear frame, and the thin rod slides through the slotted hole at the top.
  - This keeps the motor housing clear of the slotted-hole plates. The plates are 27 mm apart, so that the rod (Ø 25) fits between them.
  - It lies **flat, approx. 35°**: 0.58 mm stroke per mm lift height in working position and 0.91 in lifted position. Only this way do 140 mm of lift and ~60 mm of downward floating fit together within 150 mm of stroke.
  - Lifted it is at 298 mm. Lifting force approx. **1170 N** including a 30 % margin.
  - Choose a fast version (≥ 40 mm/s at ~1200 N), so that lifting takes approx. 3 s.
- Why electric: the robot is electric and has no hydraulics.

![lifted, with robot reference](previews/9_lifted_side_with_robot.png)

### 4.9 Mounting on the robot

![on the robot (reference)](previews/11_work_iso_with_robot.png)

- **Mounting headstock**: 8 mm top plate on the rear lower beam (`chassis_beam_1` rear_outer), 2 × M10 per side through the existing holes at x = ±125 and ±175, with a clamp plate underneath. A back plate against the beam takes the tilting moment; the cheeks carry the pins of the parallelogram.
- The inner cheeks **extend above the robot beam**, to a cross tube at 800 mm height. That tube carries the slotted-hole plates of the actuator.
- The headstock lies between |x| = 62 and 200 mm. That keeps it clear of the wheel brackets (from |x| = 261), of the upper beams (|x| = 305 to 445) and of the wooden blocks. **The robot does not have to be modified.**
- The model contains a **hidden reference of the robot rear** (`Robot_reference`). In working position and lifted position no part overlaps with the robot or with each other (check `build_lfa.check_interference()`, 0 hits).
- In the animation document the **real robot model** from `agbot design` was also checked: 0 overlap (`animate_lfa.check_fit()`).
- Coordinates: implement y − 575 = robot y. Otherwise all axes are the same as the robot model.
- **Why at the rear and not between the axles?** Between the axles the weight distribution is most favourable (§ 6). But between the wheel brackets there is only 522 mm of room, and at most 2 rows fit there.

### 4.10 Materials

- **Frame**: S355, powder coated. Laser cut: mounting headstock 8 mm, fork plates 6 mm, element shield 10 mm. Toolbar: 60 × 60 × 4 tube.
- **Knife**: Hardox 450, or steel with a carbide tip.
- **Disc**: hardened drill steel disc (as on seeding and tillage machines).
- **Wet parts**: stainless steel 316 for tubes and valves, PP or PVDF for the fittings, PVC or PE hose. Pump hose of Norprene or PharMed; check the chemical resistance for the chosen product.
- Flush with water after use; this can be done at the docking station.

### 4.11 Ground following tested: animation over a bumpy strip

![animation](previews/animation_strip_ground_following.gif)

`animate_lfa.py` hangs the applicator behind the real robot model and drives 6.3 m over a strip with:
- a long undulation (±14 mm, wavelength 2.6 m);
- a cross slope that alternates;
- two molehills, two pits and a 20 mm cross ridge.

Per frame:
- the robot rests with its four wheels on the ground level (pitching up to 2.5°, rolling up to 1.7°);
- the toolbar drops until the ground carries its weight;
- each element and the ground wheel find their own arm angle at which the depth ring or wheel touches the ground.

The cycle: start lifted, lower while driving away, work at 0.75 m/s, lift and stop.

| Result (working position, 78 frames) | Fixed toolbar (first design) | Floating position (now) |
| --- | --- | --- |
| Toolbar height relative to design | fixed | −58 to +59 mm (range −80 / +68) |
| Spring travel of elements | −24 to +68 mm | −32 to +22 mm |
| Element on a stop | 78 times | 2 times |
| Knife depth | −28 to 59 mm (knife sometimes out of the ground) | 12 to 64 mm |
| Force per element | strongly varying | 107 to 169 N |
| Ground wheel off the ground | 11 frames | 0 frames |

## 5. Calculations (summary)

Recalculate with `import lfa_calc; lfa_calc.report()`. Masses from `build_lfa.mass_properties()`.

| Quantity | Value |
| --- | --- |
| Pump stroke volume (6.4 mm hose) | 6.0 ml/rev per channel |
| Standard ratio / dose | 30/15T, i = 2.0, 505 l/ha |
| Flow per row at 1 m/s | 0.61 l/min |
| Pump speed at 1 m/s | 101 rpm |
| Chain | 08B-1, 90 links |
| Spring (c 4 N/mm): design position / force | 127 mm / 133 N |
| Down force per element (floating position) | approx. 133 N; arm angle 2.7°, toolbar 11 mm above design |
| Floating range of toolbar / spring travel of element | −80 / +68 mm; −32 / +66 mm |
| Spring length at 60 mm stone deflection | 95 mm (solid approx. 50 mm) |
| Total ground pressure (5 elements + ground wheel) | 813 N (weight of the moving part) |
| Actuator working / lifted, slotted hole | 440 / 298 mm, slotted hole 85 mm |
| Ratio working / lifted, lifting force | 0.58 / 0.91 mm per mm, 1170 N |
| Mass implement / moving part / one arm | 107 kg / 83 kg / 7.0 kg |

## 6. Weight distribution of the robot: the main point of attention

The elements press on the ground 805 mm behind the rear axle. The centre of gravity of the implement is 555 mm behind the rear axle.

- **While working (floating position)** the ground carries the moving part (813 N). The robot only carries the mounting headstock and the horizontal draft force.
  - The rear axle is therefore **not** relieved.
  - With a fixed toolbar and extra down force via the actuator, as in the first design, the down force actually lifted the rear of the robot.
- **Lifted** the whole implement hangs behind the rear axle, and then the **front axle becomes light**. The front wheels steer, so on the headland in turns that is the critical moment. That has not changed.

Assumption, because the robot weight is not known: robot 150 kg with the centre of gravity 500 mm in front of the rear axle, and a tank of 150 l (1.2 kg/l).

| Robot | Tank relative to rear axle | Rear axle while working, tank full / empty | Max. ground pressure (rear axle ≥ 600 N), full / empty | Front axle lifted, full / empty |
| --- | --- | --- | --- | --- |
| 150 kg | 300 mm | 2132 / 895 N | 1662 / 977 N | 718 / **188 N** |
| 150 kg | 450 mm | 1867 / 895 N | 1515 / 977 N | 983 / **188 N** |
| 200 kg | 450 mm | 2112 / 1141 N | 1651 / 1113 N | 1228 / 433 N |
| 250 kg | 450 mm | 2357 / 1386 N | 1787 / 1249 N | 1473 / 679 N |

Conclusions:

1. **Weigh the robot per axle.** This is the first thing to confirm; enter the values in `lfa_calc.ROBOT`.
2. **Put the tank between the axles**, approx. 450 mm in front of the rear axle.
3. **The floating position (813 N) stays below the limit in all cases.** More down force is possible with two gas springs between headstock and rear frame (constant force over the floating stroke) or with weights on the toolbar.
   - Then stick to the "max. ground pressure" column. With a 150 kg robot and an empty tank there is only approx. 160 N of room left.
   - With extra down force also raise the spring seats, otherwise the elements push against their upper stop.
4. If the robot weighs less than approx. 200 kg, the front axle becomes too light when the implement is lifted. Solutions: **approx. 25 kg of front ballast**, or 4 elements at 250 mm (approx. 10 kg less).

## 7. Risks and test plan

| Risk | Measure / test |
| --- | --- |
| Required down force in the sward (dry spring or summer) unknown; 133 N per element may be too little | **Build one element first** and measure the down force at 40 mm depth with a spring scale or weights, on wet and dry grassland. Too little: gas springs or weights on the toolbar, within the limit of § 6. Only then build five. |
| Knife depth varies due to robot pitching (12–64 mm in the animation) | In the field trial measure the placement (dye); if necessary a parallelogram per element or the knife closer to the disc axis. |
| Robot too light or wrongly balanced | Measure axle weights, place tank and ballast (§ 6). |
| Wear of pin and slotted hole | Hardened pin and a replaceable wear strip in the slotted hole; the slotted hole moves at every bump. |
| Ground wheel slips or sinks | Spikes, torsion spring; calibrate the rolling circumference in the field; the sensor sees standstill. |
| Grass or roots jam between disc and knife | Assess the 7 mm gap in the trial; if necessary a scraper or a smaller gap. |
| Blockage of tube or valve | 80 mesh filter before the manifold; each channel has its own pump hose, so a blocked row builds up pressure and shows up when calibrating. |
| Wear of the pump hose | Spare set; replace according to running hours (the sensor counts revolutions). |
| Reversing or sharp steering with the knives in the ground | Software interlock: lift first before reversing and before sharp turns. |
| Stones | Arm deflects 60 mm; optionally a shear bolt in the knife. |
| Ammonia emission from an open slot | Outflow at 27 mm depth behind the knife; optionally a press wheel per row. |
| Corrosion | Stainless steel 316 and plastic for wet parts; flush at the dock. |

## 8. Bill of materials (main groups)

| Group | Contents | Mass (model) |
| --- | --- | --- |
| Mounting headstock | 2 × top, clamp and back plate, 4 cheeks (inner cheeks extending), 2 cross tubes, slotted-hole plates (85 mm), 4 × M10, 4 pins Ø 16 | 15.5 kg |
| Parallelogram | 4 rods 30 × 30 × 3 with bushings | 4.0 kg |
| Lifting device | linear actuator 24 V, 2500 N, stroke 150, mounted turned around | 4.3 kg |
| Toolbar and rear frame | tube 60 × 60 × 4 × 900, 4 frame plates, cross tube with actuator eye, 4 pins | 10.2 kg |
| Drive and pump | 5-channel roller pump, support, filter, manifold, shaft Ø 20, 2 × UCFL204, 15T sprocket, coupling, torsion spring, M18 sensor, 25 mm suction hose with camlock | 13.5 kg |
| Ground wheel arm | arm, wheel Ø 400 with spikes, axle, 30T sprocket, chain 08B-1 | 8.4 kg |
| 5 × element | clamp plates with 4 × M12, shield, spring plate, pivot pin, 2 fork plates, disc Ø 300 with hub, 2 depth rings Ø 220, knife 8 mm, stainless steel tube 8 × 1, check valve, spring leg | 5 × 10.1 kg |
| Hoses | 5 × PVC 8 × 12 mm | 0.3 kg |
| **Total** | | **107 kg** |

Purchased parts: pump head (multi-channel cassette pump, or self-built: rotor with 3 rollers on 2 bearings, 5 hoses side by side), actuator, 2 × UCFL204, 08B-1 sprockets (standard 15T/30T plus a change set 12/18/24T and 15/20/24/36/40T), chain with tensioner, 5 discs with hub, 10 depth rings (plus change sets Ø 200/240), 5 compression springs Ø 35 × 5 × 160 (c ≈ 4 N/mm), 5 check valves, 80 mesh filter, 1" camlock. Optional: 2 gas springs for extra down force.

## 9. Model and files

| File | Contents |
| --- | --- |
| `Liquid_Fertilizer_Applicator.FCStd` | the model in working position (robot reference hidden) |
| `lfa_params.py` | all dimensions, including the robot interface |
| `lfa_parts.py` | one function per part |
| `build_lfa.py` | model tree, colors, lifting (`build(lift=140)`), interference check, mass, images |
| `lfa_calc.py` | dosing, spring, down force, floating position, actuator, axle load |
| `animate_lfa.py` | animation behind the robot model over a bumpy strip (ground following) |
| `make_gif_lfa.py` | frames to GIF with a caption and a "ground following" panel |
| `run_in_freecad.py` | macro: rebuild in FreeCAD (F6) |
| `previews/` | images 1 to 11 and `animation_strip_ground_following.gif` |

See `README.md` for regenerating, lifting and checking.
