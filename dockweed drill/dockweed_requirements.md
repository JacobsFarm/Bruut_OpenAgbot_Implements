# Dock weed mill ("pulveriser") for the AgBot / OpenAgbot "Bruut"

Implement that grinds up broad-leaved dock **plant by plant**: a CNC gantry with an X axis (left-right) and a Z axis (up-down). A fast-running cutter hangs from it and grinds up the root crown and the upper taproot. A pot around it keeps the soil in place. A second attachment mows the plant off above ground. Fully electric (48 V), made with easily available parts. The concept was modelled on **Robot Ruud** (WUR / Joost Samsom).

| File | Contents |
|---|---|
| `dockweed_design.py` | Parametric FreeCAD script (all dimensions in `P = dict(...)` at the top) with calculations and export |
| `dockweed_drill.FCStd` | FreeCAD model, shown with the cutter 150 mm deep. Groups: Bok (headstock), X_as (X axis), Z_as (Z axis), Spil (spindle), Pot, Gereedschap (tool), Camera, Elektra (electrics) |
| `dockweed_drill.step` | STEP export, without the reference robot and the environment |
| `dxf/*.dxf` | Cutting contours (laser/plasma) of 15 plate parts |
| `render_*.png` | Views: working position, driving position, mowing and detail of the cutter in the ground |

Rebuild in FreeCAD (Python console):

```python
exec(open(r"F:/veldrobot/aanbouwdelen/dockweed drill/dockweed_design.py", encoding="utf-8").read())
maak_renders()     # optional: redo all images (driving position, mowing, details)
```

View a different position: `build(x_slede=-300, z_frees=280)` (driving position) or `build(gereedschap="maai", z_frees=30)`.

---

## 1. What we learn from Robot Ruud, the conversation with Joost and the BRUUT concept

### Do's

| Do | Source | How in this design |
|---|---|---|
| **High speed**, works like a hand blender and not like a drill. Too slow gives coarse root pieces, which sprout again ("then it actually multiplies") | Joost | 1500 rpm (14 m/s tip speed), adjustable to 3000. Plunging slowly (25 mm/s) gives slices of **0.25 mm** |
| Hole of **~18 cm**, depth **~15 cm**. The sward closes up quickly, re-seeding is not needed and cows do not scratch the small holes open | Joost, WUR article | Cutter Ø180, standard 150 mm deep, max. 200 mm |
| Shred the plant **above and below ground** | Joost | Cutter goes through rosette, root crown and taproot. The pot keeps everything in place |
| With a **clump** with a lot of dock: take out a few plants each time, come back later. Do not blacken 2 m² | Joost | Software: maximum number of treatments per m² per round |
| **Hood + artificial light** for the camera works better than software correction alone | Joost | LED light bar next to the camera. Working at night is possible, possibly an apron as a light hood |
| **Electric**: can be controlled and measured precisely (encoder, current) | Joost | Closed-loop stepper motors, VESC on the spindle |
| **Modular**, simple, first get 60–80 % working | Joost / you | Headstock with clamps, tool with 4 bolts, all dimensions parametric |
| Regrowth is only in the **upper part of the taproot** | Research (see sources) | Minimum ~10 cm, preferably 15 cm. 20 cm if it really has to go |

### Don'ts

| Don't | Why |
|---|---|
| Hydraulics in the field | A burst hose means oil in the land. Kubota, pumps and valve block cost approx. €25,000 for Ruud |
| Turning too slowly (ordinary hydraulic motor, a few hundred rpm) | Coarse pieces, and they sprout again |
| Give the builder a blank mandate or integrate everything | With the second machine it became 3–4× more expensive than budgeted |
| Heavy machines on soft (peat) ground | Ground pressure. That is why also pay attention to the weight of this implement (§8) |
| Milling a clump bare in one go | Drying out and weeds |

### What I took from the BRUUT.STP concept (inspiration folder) and changed

| | BRUUT.STP | This design | Why |
|---|---|---|---|
| Construction | 2 horizontal guides + Z slide, motor on top | Same idea | Good CNC principle |
| Guide | PTO-shaft profile tubes that slide into each other | HGR15 profile rails | Two parallel sliding pairs jam quickly (over-constrained), steel on steel with dirt |
| Cutter shaft | Ø15 mm, ~210 mm free below the bearing (280 mm to the tip) | Ø35 in 2× UCF207 | Ø15 bends ±3 mm at 300 N side force and gets ±190 MPa alternating stress. That breaks through fatigue and vibrates |
| Cutter | 3 small blades, Ø~110 | Cross cutter Ø180 with 4 teeth + centring point | Joost: 18 cm. MEV-Ampferfräse: 180 mm |
| Pot | missing | Pot Ø250, rests with its own weight on the sward | Soil stays in place, and the pot works as protection |

---

## 2. Requirements

### Functional
| # | Requirement | Value |
|---|---|---|
| F1 | Hole / working diameter | Ø180 mm |
| F2 | Milling depth | 0–200 mm adjustable, standard 150 mm, measured from the **actual ground level** (pot sensor) |
| F3 | Speed | 1000–2000 rpm pulverising (standard 1500), up to 3000 rpm mowing |
| F4 | Working width X | 1000 mm (stroke), positioning accuracy ±2 mm |
| F5 | Z stroke | 480 mm: driving position 280 mm above ground level to 200 mm deep |
| F6 | Soil | stays in the hole (pot). No flung stones or clods |
| F7 | Second function | mowing disc for mowing off above ground or short "scalping" just above the ground |
| F8 | Capacity | ±20 s per plant, ≈ 150–180 plants per hour |

### Robot / mounting
| # | Requirement |
|---|---|
| R1 | 48 V from the robot battery |
| R2 | Mount without drilling or welding on the robot frame: **4 cross clamps** on 2 cross beams (40×40 tube) |
| R3 | On the **driven axle** (hub motors). Robot drives with the gantry first while weeding (§8) |
| R4 | Robot stands still while milling. Driving is only allowed when the Z axis is up (interlock) |
| R5 | Downward force < 600 N, so that the robot is not lifted |

### Construction and maintenance
| # | Requirement |
|---|---|
| B1 | Laser or plasma cut plate parts (DXF), only straight lines and arcs |
| B2 | Standard purchased parts: aluminium profile 40×80, HGR15, SFU1610, NEMA 23, UCF207, HTD-5M, BLDC + VESC |
| B3 | Change the tool with **4 bolts M10**. Wear parts (teeth) of Hardox |
| B4 | Overload (stone, tree root) must not break anything: current limit on spindle and axes |

### Safety
| # | Requirement |
|---|---|
| V1 | Spindle only runs when the pot is on or just above the ground |
| V2 | Robot emergency stop = 48 V of the implement off (contactor). VESC brakes, Z motor falls on its brake |
| V3 | People > 5 m (autonomous work). When mowing with the pot raised: rubber flap on the pot rim |

---

## 3. Chosen principle (and the alternatives)

| Choice | Chosen | Alternatives considered |
|---|---|---|
| **Kinematics** | Gantry X + Z, robot = Y (like Ruud) | Swing arm (lighter, but no CNC rectangle). Gantry between the axles (the spindle then runs through the longitudinal beams of the frame, so only ±230 mm of stroke) |
| **X guide** | 2 aluminium profiles 40×80 at 300 mm with HGR15 rails | SBR16 (chrome-plated, forgiving, slightly heavier). Sliding gate rail with roller carriages (dirt cheap and indestructible, but +15 kg). V-slot (too weak) |
| **X drive** | HTD-5M toothed belt 15 mm (steel cord) with omega drive, NEMA 23 + 5:1 | Chain 08B (rust/oil), rack and pinion |
| **Z guide** | Tube 120×60×3 with HGR15 rails | Tube-in-tube with PE glide strips (more robust in dirt, more friction and play) |
| **Z drive** | Ball screw SFU1610 + NEMA 23 closed-loop **with brake** | Linear actuator 1500 N (simple and self-locking, but ~30 mm/s: cycle +10 s) |
| **Spindle** | Direct: motor, jaw coupling, shaft Ø35 in 2× UCF207 | Belt reduction 1:2 (more torque at 1500 rpm, extra parts) |
| **Cutter** | Hardox cross cutter Ø180, 2 levels, 4 teeth, centring point | 2 rotor-head teeth on their own hub (purchased part, heavy). Earth auger (carries soil away, and that is not the intention) |
| **Pot** | Rests with its own weight (≈4 kg) on 2 free rods | Spring-loaded (at 230 mm stroke no room for compression springs) |
| **Mounting side** | Head on the **hub motor side** | Head on the steered side: driven wheels then keep ~25 kg of grip (§8) |

**A CNC trick:** the pot sensor works as the *probe* of a CNC mill. With `G38.2` the Z lowers until the pot feels the sward. That height is the ground level, and from there the cutter goes exactly 150 mm deeper. Bumps and pits in the land therefore make no difference.

---

## 4. Construction (see model)

| Group | Parts |
|---|---|
| **Headstock** (fixed on the robot) | 2 support arms tube 40×40×3 (630 long) on 2 cross beams of the robot with **4 cross clamps** (plates 90×90×5 + 4× M10×100). 2 uprights 50×50×3, 2 braces 25×25×2 |
| **X axis** | 2× aluminium profile 40×80 L=1300 (centres 760 and 1060 above ground level), with M8 + T-nut on the uprights. 2× HGR15 rail with 4 carriages HGH15CA. End plates aluminium 10 mm. X slide aluminium 10 mm 300×420. Toothed belt HTD-5M 15 mm with belt clamps outside the end plates. Pulley 20T + 2 idlers. NEMA 23 closed-loop + planetary gearbox 5:1. Inductive limit switch, rubber end stop |
| **Z axis** | Z slide tube 120×60×3, L=950, with 2 aluminium risers 25×23 and 2 HGR15 rails. 4 carriages HGH15CA on the X slide. SFU1610 with BK12/BF12, nut housing on the X slide. NEMA 23 closed-loop with brake on top of the slide |
| **Spindle bracket** (orange, weldment) | Back plate 6 mm with rivet nuts M10 on the Z slide. Lower bearing plate 8 mm (with arms to the pot rods), upper bearing plate 6 mm, motor plate 8 mm, 2 side plates 5 mm with windows |
| **Spindle** | BLDC 48 V 1.5 kW 3000 rpm. Jaw coupling Ø65. Shaft Ø35 C45 with welded flange Ø110 (4× M10 on pitch circle 80). 2× UCF207 (bearing distance 160) |
| **Pot** | Stainless steel pot Ø250×150, 2 mm wall, lid 3 mm, rubber edge strip and shaft seal. 2 rods Ø16 with adjusting rings, sliding through PE bushings. Inductive sensor M12 "ground contact" at the adjusting ring |
| **Tool 1** | Pulverising cutter: lower cross Hardox 10 mm with 4 teeth (10×18×26), upper cross turned 45°, core tube 48.3×5, flange 10 mm, centring point 60 mm |
| **Tool 2** | Mowing disc Ø200×4 with 3 hinged robot-mower blades (tip circle Ø230), core tube, flange. In the model it lies loose next to the robot |
| **Camera** | Mast and arm aluminium 30×30 on the X slide (the camera moves along). Industrial USB3 camera 320 mm in front of the spindle, LED light bar |
| **Electrics** | IP65 box on the left upright (VESC, 2 stepper drivers, ESP32-FluidNC, DC/DC, fuse, emergency stop relay). Cable chain on the upper profile |

---

## 5. Which 48 V motor?

**Specification:** BLDC (brushless) **48 V, 1.5–2 kW, ±3000 rpm nominal**, with **Hall sensors**, a **keyed shaft** (Ø14–19 mm) and flange mounting. At least IP54. In practice this is the same class as the motor of the trencher (there with a planetary gearbox). One motor type for several implements means exchanging spare parts.

- **Directly on the spindle, without reduction.** Pulverising at 1500 rpm gives the nominal torque (4.8 Nm), so ±750 W continuous and ±1.5 kW briefly (VESC 2× current). Mowing goes at full speed, 3000 rpm.
- **Controlled by a VESC** (e.g. Flipsky 75100), via the same CAN control that is already in your repo (`VESC/`, `vesc_can.py`).
  - control the speed exactly,
  - **current limit as an electronic slip clutch** (stone, thick root),
  - measure current. With that you adjust the plunge speed: a lot of current means lowering more slowly.
  - active braking: the spindle stands still in < 2 s.
- **Where to find:** "48V 1500W/2000W BLDC motor 3000 rpm hall keyed shaft". These are go-kart/e-motor motors (e.g. types sold as *MY1020D*/*Kunray*). There are also industrial 110 mm BLDC motors with a round or square flange. Note: choose a version with a **keyed shaft**, not just a sprocket pressed on it. Also ask about the IP class.
- **Do not:**
  - brushed motor (MY1020 brushed): possible as a budget option, but brushes wear and you have no speed measurement,
  - open outrunner/RC motor: dirt and water,
  - e-bike hub motor: too slow,
  - angle grinder: 230 V,
  - hydraulic motor: see the don'ts.
- **Too weak in the trial?** Take 2 kW, or put a 1:2 belt in between (HTD-8M), but then you mow at a maximum of 1500 rpm.

---

## 6. Tools and method

**Pulverising (tool 1), cycle per plant**
1. Camera (moving along on the X slide) and AI find the plant. The robot stops with the plant under the spindle line (RTK/odometry).
2. `X` to the plant. Spindle at 1500 rpm.
3. `G38.2` Z down until the pot touches the sward. That is the ground level.
4. Plunge to 150 mm at 25 mm/s: the root is cut into slices of ±0.25 mm.
5. 1 s of running on, then **rotating upwards** (mixes once more). Only then does the pot come loose from the ground.
6. Rapid to driving position, spindle brakes. Robot drives on.

```gcode
G90 G0 X420            ; spindle above the plant
; spindle on via VESC (CAN) 1500 rpm
G38.2 Z-300 F3000      ; lower until pot sensor switches = ground level
G91 G1 Z-150 F1500     ; plunge 150 mm, 25 mm/s
G4 P1                  ; 1 s of running on
G1 Z150 F3000          ; back to ground level, rotating
G90 G0 Z0              ; driving position
; spindle off (VESC brakes)
```

**Mowing / short milling (tool 2)**
- Changing: 4 bolts M10 (spanner 17), reachable from below through the pot.
- Lower until the pot touches the ground: the blades are then **30 mm** above ground level. Lowering further (the pot slides up) gives a lower cut, down to "scalping" at 0–10 mm.
- Large rosette or flowering stems: at 2–3 positions next to each other (shift X, move the robot slightly). Goal: **mow off flowering stems before the seed is ripe**. One plant can produce tens of thousands of seeds that stay viable for years.

---

## 7. Key figures (from the script)

| Quantity | Value |
|---|---|
| Spindle pulverising | 1500 rpm, tip speed 14 m/s, 750 W nominal / 1.5 kW peak |
| Spindle mowing | 3000 rpm, tip Ø230: 36 m/s |
| Plunge 25 mm/s | 0.25 mm per tooth: slices that no longer sprout |
| Hole Ø180×150 | 3.8 litres of soil. Cutting energy 2–8 kJ, so 0.3–1.3 kW average over 6 s |
| Energy per plant | ≈ 2–3 Wh (spindle + axes). 1000 plants ≈ 2–3 kWh |
| Z axis | SFU1610 + 3 Nm: 1700 N max. Software limit ~600 N. Rapid 100 mm/s |
| X axis | 5:1 + 20T: holding force ~900 N, rapid 200 mm/s |
| Cycle | ≈ 22 s per plant, ≈ **165 plants/hour** (MEV-Ampferfräse with tractor and driver: 50–200 holes/hour at 10 kW) |
| Spindle shaft Ø35 | 300 N side force: 0.4 mm deflection, 25 MPa. Critical speed ~5000 rpm (mowing = 60 %) |
| Mass of implement | **≈ 91 kg**: spindle 23, X axis 21, Z axis 20, headstock 14, electrics 5, pot 4, cutter 2.5, camera 1.6 |
| Moving mass | X ≈ 59 kg, Z ≈ 48 kg |

---

## 8. Weight distribution of the robot (important!)

91 kg at ±0.4 m in front of an axle, on a robot of ±150 kg with a 0.7 m wheelbase, is a lot. The script calculates it (assumption robot 150 kg, centre of gravity midway between the axles):

| Situation | Axle on the gantry side | Far axle |
|---|---|---|
| Robot without implement | 75 kg | 75 kg |
| Gantry on the **steered** side | 216 kg (steered) | **25 kg on the hub motors**: no grip, ✗ |
| Gantry on the **hub motor side** | 216 kg (driven) | 25 kg (steered): steering gets light |
| Same + **battery on the far side** | 184 kg (driven) | 57 kg (steered) ✓ |

**Therefore:**
- Mount the gantry on the **hub motor side** (for you now the rear with the tow hitch).
- Let the robot drive **with that side first** while weeding. That is rear-wheel steering, and at low speed no problem.
- Put the **battery on the far side**. A 2nd battery there is useful counterweight: twice as long working.
- Maximum ±1170 N downward force before the gantry axle lifts off. Limit the Z force to ±600 N for that reason.
- Adjust `robot_massa` and `robot_zw_y` in the script as soon as you have weighed the robot (2 scales under the axles).
- A **4WD** AgBot (on your GitHub) also solves it.

Making it lighter for version 2 (±10 kg): spindle bracket in aluminium (−4 kg), X stroke 800 mm (−2 kg), use the robot's camera (−1.6 kg), smaller clamp plates.

---

## 9. Control and electrical

- **48 V** from the robot via a 63 A fuse and a contactor in the **emergency stop loop**.
- **Spindle:** VESC 75/100 via CAN to the Jetson. Current ±31 A at 1.5 kW, peaks 60 A. Cable 10 mm², short.
- **X and Z:** NEMA 23 closed-loop 3 Nm. ⚠️ A "48 V" battery is **54–58 V** when full, while many NEMA 23 drivers (HBS57/CL57T) only go to ±50 V. Two solutions:
  - a **DC/DC 48→36/24 V** (±10 A) for the drivers,
  - or drivers up to 80 V. The same type as your HBS86H for the steering motors is also possible; then check whether the encoder fits.
- **Controller:** ESP32 with **FluidNC** (e.g. MKS DLC32, or an ESP32 with external drivers). G-code via USB from the Jetson. Homing with inductive sensors (X-min, Z-top), probe input = pot sensor.
- **Interlocks:**
  - spindle only on below a safe Z,
  - robot only drives if Z-home is active,
  - stepper driver alarm (blocking) means: spindle off, 50 mm up, try again. After 3× skip and log the position.
- **Camera:** your own camera with YOLO model on the Jetson, plus LED light bar 48 V (or 12 V via DC/DC). Working at night gives constant light. If it disappoints in daylight: a light apron around the camera view (tip from Joost).
- **Cables to the Z slide** (spindle motor, Z motor, sensor): second cable chain or a spiral cable along the slide (not yet drawn).

---

## 10. Parts list and cost (indicative, 2026, incl. VAT)

| Part | Quantity | Where | € approx. |
|---|---|---|---|
| Aluminium profile 40×80 slot 8, 1300 mm (cut to size) | 2 | Motedis, Dold, Kanya, 123-3D | 50–70 |
| HGR15 rail + 2 carriages HGH15CA, 1300 mm | 2 sets | AliExpress, Amazon, Dold | 70–100 |
| HGR15 rail + 2 carriages, 850 mm | 2 sets | same | 50–70 |
| SFU1610 L≈950 + nut, BK12/BF12, nut housing, coupling | 1 set | AliExpress | 45–70 |
| NEMA 23 closed-loop 3 Nm + driver (X) | 1 | StepperOnline, AliExpress | 60–80 |
| NEMA 23 closed-loop 3 Nm **with brake** + driver (Z) | 1 | StepperOnline | 90–120 |
| Planetary gearbox NEMA 23, 5:1 | 1 | StepperOnline | 35–50 |
| HTD-5M 15 mm PU steel cord 1.5 m + pulley 20T + 2 idlers | 1 | AliExpress, belt dealer | 25–40 |
| BLDC 48 V 1.5–2 kW 3000 rpm, Hall, keyed shaft | 1 | see §5 | 120–250 |
| VESC 75/100 | 1 | Flipsky, AliExpress | 130–200 |
| UCF207 + jaw coupling + shaft Ø35 C45 (and turning work) | 1 set | bearing dealer, agricultural, steel dealer | 70–110 |
| Pot: stainless steel tube or pan Ø250 (or steel tube Ø244.5), rods Ø16, PE bushings, adjusting rings | 1 | DIY store, steel dealer, Action/IKEA pan | 30–60 |
| Inductive sensors M12 | 4 | AliExpress, Conrad | 15–30 |
| ESP32 FluidNC board | 1 | AliExpress | 30–60 |
| E-box IP65, DC/DC, fuse, contactor, cable glands, cable chain, cable | 1 | Conrad, Kiwi, AliExpress | 100–150 |
| Camera + LED bar (if the robot camera is not used) | 1 | — | 50–150 |
| Steel: tubes (40×40×3, 50×50×3, 25×25×2, 120×60×3) + laser parts (DXF) incl. Hardox | — | steel dealer, online laser cutter | 150–250 |
| Bolts, T-nuts, rivet nuts, paint | — | — | 50–80 |
| **Total** | | | **≈ €1,300 – 1,900** |

For comparison: Ruud cost approx. €25,000 at the time for the motor, pumps and valve block alone.

**Budget version (±€1,000):** Z with a linear actuator (500 mm, 1500 N, IP65, Hall) instead of spindle + stepper with brake. Brushed 48 V motor with a simple controller instead of BLDC + VESC. Slower and less feedback, but you can test the principle with it perfectly well.

---

## 11. Open points / to be checked

1. **Measure the robot.** The model contains assumptions from `parameters.scad`: tube 40×40×2, longitudinal beams at X = ±375, cross beams at Y = −20 and −470, axles at −150 and −850, top of frame 644 mm. Adjust `P`.
2. **Weigh the robot** and determine the centre of gravity (§8). Then adjust `robot_massa` and `robot_zw_y`.
3. **Determine speed and plunge speed in the trial** (see §12): 1000 / 1500 / 2000 rpm × 15 / 25 / 40 mm/s. After 6–8 weeks count how many come back. Joost had ±20 %.
4. **Cutter shape**: does wet clay/peat stick to the crosses? If necessary fewer arms, or set the teeth at more of an angle.
5. **Stones**: VESC current limit + closed-loop alarm. Possibly a shear pin in the flange.
6. **Sealing of X rails**: splash guard above the upper profile. Grease the rails regularly (HGR is sensitive to rust).
7. **Work out cable chain/spiral cable** for the Z slide.
8. **Hole pattern of carriages and motors** on X slide and Z slide: mark from the real purchased parts (not in the DXF).
9. **Mowing with the pot raised**: rubber flap on the pot rim against flying pebbles.
10. **Software**: maximum number of plants per m² per round (do not make a clump bare), and a log with RTK position per treated plant (then you can go back after 6 weeks for the check).

---

## 12. Build and test order (proposal)

1. **Test the process first, without the gantry.** Build the spindle bracket with motor, VESC, cutter and pot on a wooden stand or on a drill press/lifting device. Mill 20–30 plants at different speeds and plunge speeds. Log the current (VESC) and mark the spots. This is the biggest uncertain point and only costs ±€400.
2. Measure and weigh the robot. Adjust parameters and run the model again.
3. Order laser parts (DXF folder), profiles cut to size, purchased parts.
4. Mount headstock + X axis (align profiles straight and parallel: first fix one rail, align the second with the carriage running along).
5. Z axis + spindle bracket, then electrics: emergency stop and interlocks first. Test run without cutter.
6. Set up FluidNC: homing, probe (pot sensor), current limits. Test the G-code cycle by hand.
7. Link with the Jetson: camera → plant position → robot stops → G-code. First on loose plants, then on a field.
8. After 6–8 weeks: count regrowth and adjust speed/depth.

---

### Sources
- Conversation with Joost Samsom (inspiration/gesprek met joost samson.txt) and WUR article "Ruud weet wel weg met ridderzuring" (Frits van Evert): cutter up to 15 cm, high speed, hole ~18 cm.
- MEV GmbH (Austria), Ampferfräse for tractor/loader: hole Ø180 × 250 mm, ±10 kW hydraulic, 50–200 holes/hour, ±80 kg (product page mev.co.at, via search engine; the page gave a 404 when fetched)
- Regrowth of *Rumex* root fragments (only the upper part of the root sprouts; at least the upper ~9 cm, strictly up to 20 cm removed) — https://www.researchgate.net/publication/344660399 and https://www.sciencedirect.com/science/article/pii/S0570178318300241
- AgBot/OpenAgbot "Bruut": https://github.com/JacobsFarm/Bruut_OpenAgbot (`CAD_designs/config/parameters.scad`, `setup/information/Specs hardware/`)
