# Three-point hitch, A-frame: why it is built this way

## 1. The triangle coupler

- An A-frame (triangle) coupler is the quick hitch seen on many front linkages: the hitch carries a male triangle,
  every implement a female one. The robot drives under the implement with the triangle low, lifts, the sloping legs
  centre the implement and the apex hooks in; a spring latch drops through the lock plate. No pins to line up by hand,
  which suits a robot that has to change implements on its own.
- Size: there is no standard triangle this small, so it is drawn for the robot: 400 mm between the legs at the lower
  pins (about category 0, 500 between the inner faces of the lower arms), 120 mm at the apex, 390 mm high. The legs
  are 40 x 40 x 3, the female plates 6 mm, play 2 mm. The coupler origin (middle of the lower pins) and the lean of
  10 degrees are parameters, so the parallel and lift variants use the same triangle.

## 2. The LA36 in the place of the top link

- A real three-point linkage has 1 degree of freedom (lower links + top link + implement mast form a four-bar): lift
  rods on the lower links set the height, the top link sets the pitch. With only one actuator in the top link
  position the four-bar would be free, so here the lower arms, the cross tube, the pitch brace and the triangle are
  **one rigid lift frame** that turns about the lower pivots. The LA36 runs from a tower on the toolbar to the apex:
  retracting it turns the frame up. The pitch brace (turnbuckle) sets the angle of the triangle on the arms, like the
  top link length on a tractor.
- The price: the implement tilts with the lift (25.6 degrees, rear up). For a cultivator, a ridger or a rake that is
  fine (more ground clearance behind). For implements that must stay level (a sprayer boom, a box, a seeder) take the
  parallel variant, for lifting a machine straight up the lift variant.
- Geometry: lower pivots of the simple hitch (y -820, z 380), lower pins at (-1250, 230), 455 mm arms. 200 mm lift
  needs 25.6 degrees. The LA36 pin on the apex sits 80 mm in front of the triangle: lifted, the triangle top leans
  35 degrees forward and the actuator would otherwise run over the apex. The back fixture on the tower is at
  (-890, 1070): searched so that the stroke 200 covers work + float (575 mm) and lifted (422 mm) with 22 / 25 mm to the
  end stops, with the post face 45 mm in front of the back pin so the housing (37 mm below the spindle on that side)
  clears the post; the motor is on the upper/rear side.
- The housing hangs on the tower and the rod eye runs in a **30 mm slot** in the apex lugs: in work the LA36 stands at
  the middle of the slot and the frame floats -2.5 .. +2.6 degrees (gauge wheels +-27 mm). Lifting first closes the
  slot. The lugs reach only 20 mm towards the tower, so the outer tube end stays clear of them when fully retracted.

## 3. Actuator choice

- The load is small: the frame and cultivator pull 680 .. 900 N on the LA36 (virtual work, `tpa_calc.actuator`);
  the lever arm drops from 337 to 258 mm while lifting. So the fast 20 mm spindle with gear F (1700 N, 72 mm/s
  unloaded, 52 at 1700 N) is enough: about 61 mm/s, 2.5 s to lift, 6.6 A at 24 V. The heavier 12F (2600 N, 32 mm/s)
  would take 5 s.
- The LA36 brakes itself (self-lock 2200 N for 20F), so the hitch stays up without current.
- Order code as in the liquid fertilizer applicator V2 (spindle 20, stroke 200, installation 400, solid eyes):
  `36 200 200 0 0 01 B 6 - 6 1 2 F 3 0400 N C S 0 0 0` (check against the datasheet before ordering).

## 4. What the robot can carry

- Not the actuator but the front axle is the limit: an implement lifted 1.3 m behind the robot centre takes weight off
  the front axle. With the 2 x 20 kg front counterweight ~48 kg can hang in the hitch (cg 150 mm behind the lower pins)
  while 20 % stays on the front axle; without it ~17 kg. With the 34 kg cultivator lifted: front 26 % with, 13 %
  without the counterweight. So this hitch needs the front counterweight, like simple.

## Estimated, not measured

- Robot mass 160 kg and its centre of gravity midway between the axles; least front axle share 20 % to steer
- LA36 speed linear between no load and nominal load (datasheet table), dimensions of the housing and motor from the
  datasheet drawing (motor diameter, gear length, end of the outer tube estimated)
- Tyre grip 0.45, rolling resistance 0.08 on cultivated soil; draft of a duckfoot tine 30 kPa x share width x depth
- cg of a general implement 150 mm behind the lower pins, for the capacity
- Steel 7.85 kg/dm3 for all frame parts, rubber 1.2 kg/dm3 for the gauge wheels
