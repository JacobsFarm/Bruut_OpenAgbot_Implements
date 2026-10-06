# Trencher for AgOpenBot "Bruut"

Implement for milling a **shallow channel** in grassland or on maize land, which drains water from a puddle to the ditch. Electrically driven and as simple as possible to build.

Files in this folder:

| File | Contents |
|---|---|
| `trencher_design.py` | Parametric FreeCAD script (all dimensions in `P = dict(...)` at the top) |
| `trencher_bruut.FCStd` | FreeCAD model, shown at 150 mm working depth |
| `trencher_bruut.step` | STEP export (without the robot's reference beams) |
| `render_*.png` | Views |

Rebuild in FreeCAD (Python console):

```python
exec(open(r"F:/veldrobot/aanbouwdelen/trencher/trencher_design.py", encoding="utf-8").read())
```

---

## 1. Requirements

### Functional
| # | Requirement | Value |
|---|---|---|
| F1 | Channel width | 100 – 200 mm (≈ one spade width), standard 150 mm |
| F2 | Channel depth | 100 – 200 mm, adjustable |
| F3 | Channel length per job | typically 10 – 20 m, from puddle to ditch |
| F4 | Ground | grassland (sward with roots), maize land/maize stubble, wet clay and sand |
| F5 | Soil removal | spread the excavated soil next to the channel (do not let it fall back into the channel) |
| F6 | Channel bottom | as smooth as possible, without thresholds, so that the water keeps flowing |
| F7 | Transport | lift the tool completely, at least 150 mm clear above ground level |
| F8 | Control | drive along an AB line of AgOpenGPS/AgOpenBot; lifting, lowering and milling motor on/off from the robot |

### Robot / mounting
| # | Requirement |
|---|---|
| R1 | Fully electric, powered from the robot battery (48 V preferred, 24 V possible, see §5) |
| R2 | Mount without drilling or welding on the robot frame: U-bolts around the rear beam |
| R3 | Light enough that the robot does not tip backwards and the front wheels keep enough grip. Target weight < 80 kg (first model ≈ 110 kg, see §6) |
| R4 | Keep reaction forces small, so that the robot can still drive with limited traction |
| R5 | Can be mounted and removed by one person |

### Construction and maintenance
| # | Requirement |
|---|---|
| B1 | Laser or plasma cut plate parts, with only straight lines and arcs. Weld only where there is no alternative |
| B2 | Standard purchased parts: UCFL flange bearings, 08B-1 chain, BLDC motor with planetary gearbox and a standard linear actuator |
| B3 | Wear parts (knives) replaceable with 2 bolts. The knives are made of Hardox or an old excavator bucket blade |
| B4 | Overload (stone, tree root) must not break anything |

### Safety
| # | Requirement |
|---|---|
| V1 | Disc guarded above and on the right side with a hood. The throwing direction is to the left and away from the robot |
| V2 | Milling motor only runs when the tool is down (angle sensor on the hinge) |
| V3 | The robot's emergency stop also switches off the milling motor. When blocked the motor stops at the current limit |
| V4 | Nobody within 5 m while milling (stones and clods are thrown away) |

---

## 2. Chosen principle: paddle disc ("mini ditch cutter")

Alternatives considered:

| Principle | Advantage | Disadvantage | Verdict |
|---|---|---|---|
| Chain trencher (Ditch Witch) | neat, narrow slot | many wearing parts, high power, soil stays on the edge, expensive | ✗ |
| Towed V-plough / ditch plough | very simple, no motor | needs a lot of draft force (> 2 kN), and the robot does not have that. The sward tears | ✗ |
| Milling drum (narrow rotavator) | standard knives | soil falls back into the channel, works poorly in sward | ✗ |
| **Paddle disc with hood** | cuts and throws in one movement, few parts, small reaction force | a bit more laser work | **✓** |

Operation:
- A **Ø600 × 10 mm disc** (laser) with **6 welded paddles**. On each paddle sits a **replaceable 10 mm knife**, fixed with 2 × M12. The tip diameter is **Ø700**.
- All knives stick out **to the left** from the disc. The disc thus forms the right wall of the channel. As a result the bearing, chain guard and carrier plate can stay **to the right, outside the channel**. At 200 mm depth the hub is still 150 mm above ground level.
- The **knife width determines the channel width**. There will be 3 knife sets: 100, 150 and 200 mm.
- The disc turns **counter-rotating**: the bottom moves with the driving direction. The soil is thus cut from below upwards and thrown over the top. The hood directs the soil **to the left**, away, and an adjustable throwing flap controls the spreading width.
- Because the disc counter-rotates, the tool is pulled slightly into the ground. That helps to hold the depth. The horizontal reaction force is only ±130 N, so the robot hardly has to pull.
- The disc is **rotationally symmetric**: the angle of the carrier arm makes no difference to the channel shape. A simple **hinged arm** is therefore enough, a parallelogram is not needed.

## 3. Construction (see model)

| Group | Parts |
|---|---|
| **Headstock** (fixed on the robot) | front plate 8 mm, 2 side plates 10 mm, upper cross tube Ø42.4, 2 U-bolts M12 around the rear beam, hinge pin Ø25, actuator pin Ø25 |
| **Arm + carrier plate** (one weldment) | hinge bush Ø42.4×5, arm tube 60×60×4, carrier plate 10 mm, actuator lugs with **slotted hole** |
| **Disc** | disc Ø600×10 with lightening holes and welded hub, 6 paddles of 8 mm, 6 knives of 10 mm Hardox |
| **Drive** | BLDC 48 V 1.5 kW 3000 rpm with planetary gearbox i=10 (300 rpm), on the left on the carrier plate above the hood. Chain 08B-1 15T/15T in a narrow chain guard (band 3 mm + lid 6 mm). Shaft Ø35, 2 × UCFL207 |
| **Hood** | 3 mm plate, folded in segments of 15°, with right side wall. Open on the left, with adjustable throwing flap |
| **Depth** | glide shoe 70 mm wide to the right of the channel, at the height of the disc. Holder with a row of holes in steps of 22 mm (~25 mm depth difference) |
| **Lifting** | linear actuator 6000 N, stroke 200 mm (pin-to-pin ≈ 400 → 600 mm), with limit switches and potentiometer |
| **Electrics** | IP65 box with BLDC controller and actuator relay/driver. Angle sensor on the hinge |

### Floating position (the most important simplification)
The lower eye of the actuator sits in a **40 mm slotted hole**. In working position the actuator extends slightly further than needed. The tool then rests with its own weight on the **glide shoe** and follows the ground level. No hydraulics or force control is therefore needed.

## 4. Key figures (from the script)

| Quantity | Value |
|---|---|
| Disc speed | 300 rpm (adjustable via the controller) |
| Tip speed | 11 m/s (enough to throw the soil 1–3 m away) |
| Shaft torque | ≈ 44 Nm, tip force ≈ 125 N continuous (plus flywheel effect of the disc for peaks) |
| Channel cross-section 150×150 | 0.0225 m³ per metre |
| Driving speed while milling | 2 – 4 m/min (adjustable in AgOpenBot) |
| Milling power needed | ≈ 250 – 600 W at 3 m/min (estimate with 200–500 kJ/m³ for grass sward/clay). The 1.5 kW gives ample reserve |
| Bite per knife | ≈ 1.7 mm, so little force per knife and a smooth run |
| 20 m channel | ≈ 7 minutes |
| Arm angle | working position ≈ −4°, lifted ≈ −30° |
| Actuator stroke needed | ≈ 160 mm + 40 mm slot, so a stroke of 200 mm |
| Mass | ≈ 110 kg (first model, not yet optimised) |

## 5. Control / electrical

- **Voltage**: 48 V is preferred (1.5 kW is then ≈ 31 A). At 24 V it becomes ≈ 62 A, which needs thick cables. Take 24 V only if the Bruut has nothing else, and then possibly choose a 1 kW motor.
- **Motor controller** (BLDC, for example a VESC or a simple 48 V controller with PWM input): set a current limit as an "electronic slip clutch". On a current peak or blocking:
  1. the robot stops driving,
  2. the tool goes up 50 mm,
  3. the motor restarts.
- **Actuator**: 12/24/48 V with built-in limit switches. Preferably a type with **potentiometer or Hall feedback**.
- **Angle sensor on the hinge** (potentiometer or magnetic encoder, e.g. AS5600): measures the actual depth and forms the interlock "only turn the cutter when it is down".
- **Link with AgOpenBot**: 3 outputs (lift, lower, milling motor on) and 2 inputs (angle, motor current). For example via the existing ESP32/Teensy machine module ("section control" = cutter on, "hydraulic lift" = lift/lower).

### Phase 2: controlling the fall with RTK (optional)
Water only flows if the channel bottom **slopes down towards the ditch**. With the glide shoe the bottom follows the ground level, and that is usually good enough. If you want a fixed fall (for example 2–5 mm/m), it can be done like this:
- record the RTK height of the robot at the puddle and at the ditch,
- let the actuator (with feedback) control the depth instead of the shoe, so that bottom height = starting height − fall × distance,
- then set the glide shoe higher as a lower limit/safety.

## 6. Open points / to be checked

1. **Dimensions of the Bruut's rear beam.** The model contains an assumption: 60×60 tube at Z = 500–560 mm. Adjust `koker_x(...)` and the U-bolts after measuring.
2. **Battery voltage and capacity of the Bruut** (24 or 48 V?). The motor choice depends on this.
3. **Weight and tipping moment.** The tool hangs ≈ 0.75 m behind the robot. Check the load on the front wheels. Possibly a counterweight at the front, or put the headstock closer to the rear axle.
4. **Reducing weight** (target < 80 kg): headstock plates of 6 mm, disc of 8 mm with larger lightening holes, carrier plate with cut-outs.
5. **Wear resistance of the knives** in sandy soil. Possibly hardfacing or knives with a carbide tip.
6. **Stones**: a shear bolt on the sprocket of the disc (M8, 8.8) as a mechanical back-up for the current limit.
7. **Cutting the sward**: optionally a coulter disc in front of the disc to cut the sward on both sides, so that the edges become neater.
8. **Front shielding**: chain curtain or rubber flap at the front of the hood.
9. **Clods and wet clay**: does the soil stick to the paddles? If necessary a scraper on the hood, or set the knives more at an angle.
10. **Test first** with a wooden/MDF template of the disc and a loose cordless drill or angle grinder motor, so that you can try out speed and knife shape before you order laser parts.

## 7. Build order (proposal)

1. Measure the Bruut's rear beam and adjust the parameters in `trencher_design.py`.
2. Order laser parts: disc, paddles, carrier plate, headstock plates, actuator lugs, hood segments, lid of the chain guard, knives.
3. Welding 1: paddles on the disc and the hub on the disc. Welding 2: hinge bush + arm + carrier plate + lugs.
4. Mount the headstock on the robot with the U-bolts. Hang the arm with the pin. Fit the actuator.
5. Fit bearings, shaft, chain and motor. Fit hood and shoe.
6. Connect electrically, first the emergency stop and the interlock. Then test run without knives.
7. Trial channel in grassland at 100 mm depth. Adjust speed and driving speed, then go deeper.
