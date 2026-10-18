# Dockweed drill v6: why it is designed this way

v6 keeps the process and the spindle drive of v5 ([../v5/RATIONALE.md](../v5/RATIONALE.md): 800 W gearmotor directly
on the spindle via a jaw coupling, 500 rpm, Ruud-style can Ø 219, fixed high camera, PTO-tube X axis). It changes the
frame, the way the PTO tubes are held, the Z axis and the spindle size.

## 1. Frame of 40 × 40 × 3, PTO tubes bolted between side plates

- **One tube size.** Uprights, cross beams, cross tube and camera mast are all 40 × 40 × 3. That is the size of the
  robot beams, so one length of stock covers it.
- **Side plates instead of support ribs.** In v2–v5 each PTO tube rested on 2 welded ribs at the uprights (x ±250),
  so every sleeve and scraper had to be sawn open (14 mm) to pass the ribs. In v6 the tubes span between two 12 mm
  side plates at x ±700 (span 1376):
  - each tube end has a **welded plug** (the inner lemon profile, 25 mm) **tapped 2 × M10**, and the bolts go in from
    outside through the side plate. Undo 4 bolts and the tube is out, or the carriage slides off the end;
  - the sleeves are now **closed**: stiffer, and dirt can no longer enter through the slot;
  - the side plates are welded to the ends of **2 cross beams 40 × 40 × 3**, one at each tube height, directly behind
    the uprights. Each crossing has **1 × M12** through upright and beam, so the X frame (beams + side plates) can also
    come off the headstock in one piece.
- **Stiffness.** A tube between two plates bends more in the middle than the old tube on two supports with an
  overhang. With the slide at x 0 and treated as simply supported: 0.75 mm down and 1.31 mm in v from the 600 N Z force
  (twist 0.5°). The plug + 2 × M10 + 12 mm plate is closer to fixed (0.19 / 0.33 mm), so the truth lies in between.
  v5 had 0.45 / 0.96 mm at x ±500. For drilling a Ø 180 hole that is good enough. If it is not, a third support in
  the middle (a clamp on the cross beam) costs only the middle stroke.
- **Cross beams:** 438 mm cantilever from the upright to the side plate. With the slide at x +500 they carry
  ≈ 600 N each: 0.78 mm down, 0.57 mm in v, 51 MPa.
- **Gusset.** The headstock gusset is shorter (75 instead of 130 mm), because the M12 of the lower cross beam passes
  at z 760, right where the old gusset ended.

## 2. Z axis: tube on HGR15 rails, actuator beside it

- **Guide as in v2:** Z tube 120 × 60 × 3 with 2 HGR15 rails on its front face, 4 HGH15CA carriages bolted to the X
  slide at the tube heights (300 apart). Without a ball screw between the rails the 23 mm risers of v2 are not needed:
  flat bar 25 × 8 under the rails is enough (−4.7 kg, and the spindle moves 15 mm closer to the tubes).
- **Drive:** electric actuator 24 V (Linak LA36 class), stroke 400, **pin to pin to the left of the Z tube** (x −95).
  - The top pin sits on an **extension of the X slide** (x −150..−40, up to z 1300). The rod eye sits in a bracket at
    the bottom of the Z tube. The actuator pushes the carriage down and lifts it.
  - The actuator only pushes and pulls. The 300 N side force on the cutter goes through the rails (≤ 585 N per
    carriage, C0 15.7 kN). The offset of 95 mm adds ≈ 95 N per carriage, the spindle behind the rails ≈ 160 N.
  - Left, because the X motor sits on the right at z 895–950 behind the slide. The spiral cable moves to the right,
    above the X motor (bracket at z 965 on the slide, top on the Z tube).
  - **Retracted = driving position** (cutter 200 above the ground), extended = 200 deep.
- **Forces:** the Z slide weighs 46 kg. Pushing 600 N into the soil needs only 150 N from the actuator (the weight
  helps). Lifting the slide with the can and pulling out of the soil needs ≈ 660 N. A 1700 N variant has margin 2.6.
- **Speed and current:** ≈ 94 mm/s down, 73 mm/s up (assumed figures). 1.3 A while plunging, 7.7 A while lifting at
  24 V.
- **Converter 48 → 24 V, 20 A:** the actuator needs ≈ 7 A, ≈ 10 A when it blocks before the slip clutch. There is
  margin for 24 V sensors and relays.

## 3. Duty cycle: the weak point of an actuator here

Per plant the actuator runs down (2.6 s), plunges (7.2 s), rises while mixing (3.6 s) and goes up (2.6 s): **15.9 s
in a cycle of 23.1 s = 69 %**. LA36-class actuators (and Ewellix CAHB) are rated for **20–25 %** duty, for example
2 min on and 8 min off. At 20 % the machine could treat at most **45 plants per hour**, against 156 that the rest of the
machine can do.

| Option | Duty | Remark |
| --- | --- | --- |
| LA36 / CAHB as modelled | 20–25 % | fine for testing, short sessions; will overheat in continuous work |
| Actuator with a lower load share | somewhat higher | the duty rating is at nominal load; at 150–660 N on a 1700 N unit it runs cooler. Ask Linak for the duty at this load profile before deciding |
| Servo electric cylinder (ball screw + 48 V servo with brake, e.g. Leadshine iSV2 on SFU1610) | 100 % | same mounting points (pin to pin), backdrivable, force from the servo torque |
| Ball screw on the Z tube as in v2 | 100 % | nut on the X slide, screw on the Z tube; needs the 23 mm risers again |

**Advice:** build v6 with the actuator for the field trials (it is simple and robust). For real work plan the
servo cylinder in the same brackets: `act_*` holds the installed length, stroke and pin heights, so a different
cylinder is a parameter change.

## 4. Spindle Ø 30 in 2 × UCP 206

- Ø 30 solid C45 from the spindle flange (welded in) through both bearings into the coupling. The 42.4 × 4 tube of v5
  over the overhang is no longer needed:

| | v6 Ø 30 solid | v5 Ø 20 + tube 42.4 × 4 |
| --- | --- | --- |
| Deflection at 300 N on the cutter (overhang 407) | 1.09 mm | 2.35 mm |
| Stress at the lower bearing | 46 MPa | — |
| Critical speed / cutter | 3180 rpm / 16 % | 2160 rpm / 23 % |
| Lower bearing | 1170 N, UC206 C = 19.5 kN | UC204 |

- **UCP 206:** bolt distance 121, foot 165 long, M14. The spindle bracket is wider (side plates at x ±87.5,
  v5 ±78). The side plates stop 22 mm before the spindle axis and the rear part of the top plate is narrower
  (±84), because the rods and set rings of the can run past there when the can rests on the ground and the cutter goes
  deeper. The can rods stay at x ±100 inside the Ø 219 can.
- **Jaw coupling size 28** (bores 30 and 19, 95 / 190 Nm): size 24 bores to 28 mm at most. Against the motor peak of
  30.6 Nm that is a factor 6.2.

## 5. What it costs

- **Mass 118.5 kg** (v5 102.2): cross beams and side plates (≈ 15 kg together), Z tube with rails
  (≈ 12 kg), actuator (6.3 kg), larger bearings and shaft. The jack of v5 is gone.
- The spindle is at robot y −934 (v5 −886), because the Z tube with rails is deeper than the jack. The rear axle
  carries 228 kg while driving, the front 40 kg (v5 47). With the slide at x ±500 the lightest front wheel has 13 kg.
  Moving the battery forward (63 / 206 kg) is advised.
- Max. down force before a wheel drops below 20 kg: 1230 N at x 0, 1060 N at x ±500 (limit 600 N).
- The can is ≥ 122 mm from the rear tyres (v5 78 mm).

## 6. Open points (v6)

1. Choose the actuator variant (installed length, rod eye, force/speed, duty at this load profile) and set `act_*`.
   Ask Linak or the dealer about the duty cycle (§ 3). Alternatively: servo cylinder.
2. Check UCP 206 and coupling size 28 against the parts bought; set `ucp_*` and `jaw_*`.
3. Plugs in the PTO tubes: weld them square, then drill and tap M10 with the side plate as a jig, so that both ends line up.
4. Measure the deflection of the PTO tubes with the slide in the middle (§ 1); add a middle support if needed.
5. All open points of v5 (motor type plate, 500 rpm in real soil).
