# Three-point hitch, parallel: why it is built this way

## 1. Why a parallel linkage

- The liquid fertilizer applicator hangs its toolbar on a headstock with a parallel linkage and an electric actuator
  with a slot: the toolbar stays level, floats on the elements in work and is lifted at the headland. That is what
  most implements need (seeders, hoes, boom sprayers, rakes, boxes): this variant makes it a general hitch with the
  A-frame triangle as the interface.
- Compared with the a_frame variant (one rigid frame turned by the LA36 in the top link place) the implement does not
  tilt: it goes straight up (203 mm up, 29 mm forward). The price is 4 links and 8 pins instead of 2 arms and a brace.

## 2. Geometry

- The headstock is welded on the rear toolbar of three point hitch/simple (one toolbar for all rear implements; the
  applicator bolts its headstock to the rear beam instead). The link pairs sit at x +-110 (the applicator: +-100) so
  the outer cheeks (x 126..134) stay clear of the hanger webs at x 155.
- Links 300 mm (applicator 260): 200 mm lift with -12 .. +28 degrees. The rear pins are 280 mm apart along the
  triangle, in work 90 and 370 mm up the triangle and 75 mm in front of it; the front pins follow from the work
  angle: (y -867, z 368) under the toolbar and (-818, 644) above it. The links run between their cheeks, the LA36
  between the link pairs.
- The coupler origin in work is the same as in a_frame (y -1250, z 230), so the cultivator hangs at exactly the
  same place.

## 3. LA36 and the slot

- As in the applicator: the diagonal from the top of the headstock to the bottom of the carrier gets shorter when
  the carrier goes up, the housing sits on the moving carrier (motor below, so it stays clear of the triangle) and
  the rod pin runs in a slot in the headstock. The pin positions were searched (scratch script, the same criteria as
  the applicator's RATIONALE 10): slot as short as possible for +-8 degrees of float, the stroke 150 covering work
  (487 mm, pin at the slot end with the carrier at the bottom of the float) and lifted (370 mm) with 13 / 20 mm to the
  end stops. Result: body pin on the carrier 180 mm up the triangle and 45 mm in front of it, slot end at
  (y -780, z 660), slot 31 mm: the carrier floats -40 / +41 mm (applicator: slot 85, float -70 / +68 for disc
  elements on springs; gauge wheels need less).
- The diagonal is flat (33 degrees in work): little stroke per mm of lift, so the force is high at the start of the
  lift: 1306 N with the cultivator. The 16 mm spindle with gear F (2000 N, 60 / 43 mm/s) keeps 35 % margin and lifts
  in 2.4 s; 20F (1700 N) would be at 77 %, 12F (2600 N, as the applicator) would take 3.6 s.
- The back fixture lugs on the carrier reach at most 14 mm towards the actuator: the hex of the back fixture starts
  14.9 mm from the pin.

## 4. What the robot can carry

- The LA36 could lift ~60 kg of implement; the front axle allows ~49 kg (cg 150 mm behind the triangle) with the
  2 x 20 kg front counterweight and ~17 kg without, as in the other variants. With the 34 kg cultivator lifted the
  front axle keeps 26 % with the counterweight, 13 % without.

## Estimated, not measured

- Robot mass 160 kg and its centre of gravity midway between the axles; least front axle share 20 % to steer
- LA36 speed and current linear between no load and nominal load (datasheet table); housing and motor dimensions
  from the datasheet drawing, motor diameter and gear length estimated
- Link cg moves half as far as the carrier (in the virtual work), no friction in the pins
- Tyre grip 0.45, rolling resistance 0.08 on cultivated soil; draft of a duckfoot tine 30 kPa x share width x depth
- cg of a general implement 150 mm behind the triangle, for the capacity
