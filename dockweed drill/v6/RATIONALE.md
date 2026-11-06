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

## 2. Z axis: two upright PTO tubes, LA36 and spindle in the middle

The first v6 had a Z tube 120 × 60 × 3 on 2 HGR15 rails with the actuator pin to pin to the left of it. That layout
put the actuator 95 mm off the load line, needed rails and carriages as bought parts, and used an assumed actuator. It
is now:

- **Guide: 2 PTO inner tubes standing upright** at x ±64 (49 × 39.5 × 4.5, the same profile as the X axis), long
  axis (49) in v. They move with the Z carriage and slide through **2 × 2 sleeves** of the outer tube (57.5 × 48 × 4,
  100 long) on the back of the X slide, at the heights of the X tubes (z 760 and 1060, 300 apart). The lemon profile
  cannot turn, so the spindle bracket stays square without rails. Same stock and the same scrapers and grease
  nipples as the X axis.
  - The sleeves sit in **steel saddle blocks** (x ±38, from the slide to the centre of the sleeve, welded round the
    sleeve), each held with 4 × M8 from behind into the slide. The M8 of the X sleeves are now countersunk in the
    slide, so its back face is flat for the saddles.
  - At the bottom the tubes have a **welded plug tapped 2 × M10** and are bolted from below into a **10 mm lower
    yoke**; 60 mm higher a **10 mm clamp plate** with lemon holes holds them square. Both plates are welded to the
    back plate of the spindle bracket. The tubes have to be bare between z+502 and z+1318 (the part that runs through
    the sleeves over the 400 stroke), so there is no top yoke: it would also hit the actuator housing.
  - **Why x ±64:** the actuator housing (76 wide) needs the tubes at least 38 mm from the middle; the X gearbox at
    x 90..150 behind the slide limits it from the other side. Both have 6 mm clearance; the sleeves themselves are
    above or below the gearbox.
- **Drive: Linak LA36** from `parts/actuator`: 24 V, 1700 N, 20 mm spindle, gear F 1:18, stroke 400, back fixture and
  rod eye solid Ø 12.2. Built-in length from the datasheet: 250 + stroke = 650.
  - **In the middle, at x 0, between the tubes**, 19 mm in front of the back plate of the spindle bracket. The Z force
    now has no lever about the v axis (the old 95 mm offset is gone). The ground reaction on the spindle is 124 mm behind
    the actuator; that couple goes into the sleeves (≈ 124 N each at 600 N).
  - The back fixture hangs in a clevis on a tab in the middle of the X slide (pin at z 1420), the rod eye in a
    bracket welded to the back plate of the spindle bracket. The housing (148 high, 112 behind the spindle axis) points
    backwards, over the spindle motor. In the driving position (highest) it is 10 mm above the motor.
  - **Retracted = driving position**, as Linak advises (less vacuum in the housing, so less water ingress).
- **Forces:** sleeves are not rails, so there is friction. With μ 0.15 and 300 N side force on the cutter the sleeves
  take 585 / 435 N per tube and give ≈ 380 N friction. Plunging with 600 N on the cutter then needs 545 N from the
  actuator, lifting 705 N. The LA36 gives 1700 N (margin 3.1 / 2.4) and self-locks up to 2200 N.
- **Stiffness:** the tubes overhang 490 mm below the lower sleeve at 150 deep. At 300 N side force the cutter moves
  2.3 mm sideways and 1.7 mm in v (spindle bracket taken as rigid), tube stress 30–35 MPa. Good enough for a Ø 180
  hole; if not, put the lower sleeves lower on an extension of the slide.
- **Speed and current** (datasheet curves): 66 mm/s down, 64 mm/s up; 4.9 A while plunging, 5.7 A lifting, 12.4 A at
  1700 N + 20 %. The 20 A converter is enough.
- The spiral cable runs from a bracket above the X motor (x 135) to a cap on top of the right tube.

## 3. Duty cycle: the weak point of an actuator here

Per plant the actuator runs down (3.0 s), plunges (7.2 s), rises while mixing (3.6 s) and goes up (3.0 s): **16.8 s
in a cycle of 24.0 s = 70 %**. The LA36 datasheet allows **20 %** at full load for strokes up to 600 mm (4 min on, 16
min off, 40 °C); Ewellix CAHB is similar. At 20 % the machine could treat at most **43 plants per hour**, against 150
that the rest of the machine can do.

| Option | Duty | Remark |
| --- | --- | --- |
| LA36 as modelled | 20 % | fine for testing, short sessions; will overheat in continuous work |
| Actuator with a lower load share | somewhat higher | the duty rating is at nominal load; at 545–705 N on a 1700 N unit it runs cooler. Ask Linak for the duty at this load profile before deciding |
| Servo electric cylinder (ball screw + 48 V servo with brake, e.g. Leadshine iSV2 on SFU1610) | 100 % | same mounting points (pin to pin), backdrivable, force from the servo torque |
| Ball screw between the Z tubes | 100 % | nut on the yoke, screw in a bearing on the slide tab; same place as the actuator |

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

- **Mass 122.9 kg** (v5 102.2; with the HGR15 rails 118.5): cross beams and side plates (≈ 15 kg together), Z guide
  tubes (7.9 kg) with 4 sleeves in steel saddle blocks (the saddles are the heavy part, ≈ 7 kg; they can be made as
  bent plate later), LA36 (6.0 kg), larger bearings and shaft. The jack of v5 is gone.
- The spindle stays at robot y −934 (v5 −886): the actuator sits in the space the Z tube had. The rear axle carries
  234 kg while driving, the front 39 kg (v5 47). With the slide at x ±500 the lightest front wheel has 12 kg. Moving
  the battery forward (62 / 211 kg) is advised.
- Max. down force before a wheel drops below 20 kg: 1265 N at x 0, 1110 N at x ±500 (limit 600 N).
- The can is ≥ 122 mm from the rear tyres (v5 78 mm).

## 6. Open points (v6)

1. LA36 order code along the lines of 36 200 400 0 A 01 B … (20 mm spindle, stroke 400, analogue Hall feedback for the
   position, B = 24 V with slip clutch): check the code with the dealer, and ask Linak about the duty cycle at this load profile (§ 3).
   Measure the delivered actuator (outer tube, back pin to housing) and set `act_*`. Alternatively: servo cylinder.
2. Z sleeves: ream or hone them to a sliding fit on the tubes, and check the friction (μ 0.15 assumed). If the cutter
   deflects too much sideways (2.3 mm at 300 N), move the lower sleeves lower.
3. Check UCP 206 and coupling size 28 against the parts bought; set `ucp_*` and `jaw_*`.
4. Plugs in the PTO tubes: weld them square, then drill and tap M10 with the side plate as a jig, so that both ends line up.
5. Measure the deflection of the PTO tubes with the slide in the middle (§ 1); add a middle support if needed.
6. All open points of v5 (motor type plate, 500 rpm in real soil).
