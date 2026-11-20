# Dockweed drill v10: why it is designed this way

The brief: "a v10 with v8 as the base, the X axis on round tubes, the motor at the side as in v9 (on the X axis, not on
the middle slide with the drill), the Z axis driven by the actuator, and the idea of the linear guide from the
inspiration folder to guide the drill up and down instead of the round tubes; make the animations, videos and
previews too".

So v10 keeps everything of [v8](../v8/RATIONALE.md) that the brief does not change: process, spindle, 800 W gearmotor
on a Ø 30 spindle in 2 × UCP 206, jaw coupling, Ruud-style can, cutter, Linak LA36, headstock, camera, and the whole X
axis on 2 round tubes Ø 50 × 4 with 3 plain-bush housings.

## 1. What the photos show

The 3 photos in `inspiration/` show a test build against a barn door:

- a galvanised steel C profile as the backbone, with **2 profile rails** (size 15..20, steel, holes every 60 mm) bolted
  along its face;
- a **sled**: a rusty steel plate with its sides bent back round the rails, on carriages that run on the rails; the
  rails are fixed and longer than the sled, the sled moves;
- on the sled the DC gearmotor (standing, shaft down), a horizontal shelf with a square hole for the **jaw coupling**
  (red spider), 2 **UCP pillow blocks** on the face of the sled, a sleeve coupling on the spindle and the drill head at
  the bottom;
- in the middle between the rails, above the sled, a bent bracket with a hole: the attachment of the **linear
  actuator** (a Linak-type actuator stands next to the door).

That is the same drive train as v8 (gearmotor on the spindle, jaw coupling, 2 pillow blocks), only guided by rails and
carriages. v10 takes over the principle: **fixed rails, moving carriages on the sled, actuator in the middle**.

## 2. Z axis on linear rails

- **Rails fixed, carriages on the sled (as the photo).** In v8 the 2 tubes moved with the spindle through housings on
  the slide; at full depth the cutter hung 920 mm below the lower housing. With the rails fixed on the slide and the
  carriages on the sled, the carriages go down with the cutter: the arm from the cut to the lower carriage is always
  430 mm, and the carriages are 390 mm apart. The rails stay above the ground (bottom z 225, can top in the driving
  position z 355, beside them in plan).
- **HGR20 / HGH20CA, not size 15.** The photo looks like size 15. The loads are small for both (lower carriage 526 N
  equivalent at 300 N side force: static safety 53 for size 20, about 32 for size 15). Size 20 is chosen for the field:
  bigger balls, stronger seals and scraper (option "KK" double seal + scraper), more moment capacity per carriage, and
  the rail is stiffer on a beam that is not machined. HGR15 / HGH15CA fits the same layout with 2 mm less in v.
- **Rail beams RHS 50 × 40 × 4 at x ±90 instead of one C profile.** The LA36 has to push in the middle, between the rails
  (photo; v6 showed that an actuator 95 mm off the load line is a problem). Its outer tube (44.5 × 50) needs about
  60 mm between the slide and the sled; with one wide backbone behind the rails that space is not there. Two separate
  beams 50 deep leave the middle free: slide (v 170..182) | rail beams (182..232) with the LA36 tube between them
  (203..253) | rails (232..250) | carriages (to 262) | sled (262..268). The beams hang about 490 mm below the slide; with both
  beams working together the cutter moves 0.74 mm at 300 N side force at full depth, much less than the 1.3 mm of the
  v8 tubes.
- **Fixing:** 4 × M8 per beam from the front through the alu slide, between the X housings (z 725..995), into the front
  wall of the beam (tapped, or rivet nuts). At 300 N side force the most loaded bolt sees 548 N shear (slip limit about
  3600 N) and 266 N tension. The rails are bolted with M5 every 60 mm into the 4 mm back wall (5 threads). Set the first
  rail against a straight edge, align the second to it with a carriage pair as a gauge, shim the beam where it is not
  flat.
- **Sled = back plate of the spindle bracket.** A 6 mm plate bent into a U (web 252 wide, flanges 26 forward), like the
  sled in the photo: the flanges stiffen the sled and cover the rails and carriages at the sides against soil thrown by
  the cutter. The spindle bracket of v8 is welded on the back (lower plate, side plates, bearing plate, top plate), so
  the spindle comes out at robot y −938, 16 mm closer to the robot than v8. The DXF has the flat blank with both bends.
- **Friction:** balls and seals together about 26 N while cutting, against about 380 N in the v8 bushes. The LA36 now
  pushes 241 N and lifts 606 N (margin 7.0 / 2.8). Its mean I² back to back drops from 18.6 to 13.1 A² (60 % of the
  allowed 21.2 A²); it is OK from 13.5 s per plant, the cycle is 21.8 s.
- **End stops:** rubber blocks under and above each rail. The LA36 limits the stroke itself (400 mm); the carriages
  stop 6.2 mm above the rail end at full depth and 11.2 mm below the top when driving. The stops only catch a
  carriage if the actuator is taken off.

## 3. X motor at the side

- As v9: the NEMA 23 closed-loop + 5:1 sits **fixed** on a 10 mm bracket welded to the right side plate; the gearbox and
  motor point forward (towards the robot) between the cross beams, the pulley on the gearbox shaft is behind the
  bracket. On the left a tension pulley on an M10 in a slot. The belt (HTD5M 15 mm, about 2.86 m) runs round both
  pulleys at z 910, between the tubes and between the lower and upper X housings; the lower run is clamped on the
  front of the slide.
- The slide carries no motor, pulley or idlers any more (v8 had an omega drive on the slide) and the motor cable does
  not move. The slide is 380 wide (v8: 410); the side plates stay 1470 apart, the pulleys sit at x ±690, just outside
  the X housings at x ±500.
- The motor hangs on the right side plate, so the cross beams carry 2.5 kg more at their cantilever end: 0.54 mm down,
  73 MPa (v8 0.5 mm, 78 MPa with the motor on the slide).
- The side plates now reach to behind the slide (v 190): the inductive limit switch (left) and the rubber end stop
  (right) look at the edge of the slide.

## 4. What it costs

- **Mass 131.2 kg** (v8 127.0). The rail frame (2 RHS, 2 rails, stops, bolts) is 13.7 kg; the Z sled is lighter than
  the v8 Z part (39.2 against 45.0 kg moving in Z) because the tubes, yoke and clamp plate are gone. 75.4 kg moves in x
  (v8 76.2).
- **Axle load** as v8: 37 kg on the front axle when driving (13 %), 59 kg with the battery forward; the lightest front
  wheel is 11.3 kg with the slide at x ±500. Same advice as v8: battery forward, or a counterweight at the front.
- **Dirt:** profile rails are precision parts. They sit 225 mm above the ground, behind the sled flanges and away from
  the can, but the carriages need the double seal and scraper, grease every 100 km of travel (in practice: every
  month) and the rails a wipe with oil after wet work. A bellows over each rail is possible (the beams have room
  below and above).

## 5. Open points (v10)

1. Buy the rails and carriages (HIWIN HG20 or equal) and check H, W, L, the hole pattern and the ratings; set `rail_*`
   and `blk_*`. Size 15 also fits if that is what is in stock (the layout stays, v gets 2 mm shorter).
2. Rail beams: check the flatness of the RHS over 900 mm; mill or shim the rail face if needed. M5 in 4 mm wall:
   check the thread, or use 5 mm wall RHS.
3. Measure the cutter deflection at full depth with 100..300 N side force (1.8 mm calculated at 300 N, of which 1.1 mm
   in the spindle shaft).
4. Belt length and tension slot with the belt you buy (about 2.86 m open length with the clamp).
5. All open points of v8 for the X axis (plugs, Helicoil, tube deflection), the spindle, the LA36 and the can.
