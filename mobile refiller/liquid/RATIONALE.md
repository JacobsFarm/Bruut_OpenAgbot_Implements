# Mobile refiller (liquid): why it is built like this

The concept, all uses and the other variants are in the [mobile refiller README](../README.md). This file explains the
choices in the liquid model. Numbers come from `mrl_calc.py` and the model (`build_mrl.py`); estimated values are
listed at the end of the [README](README.md#estimated-not-measured).

## 1. Refill in the turn, not at the farm

The working robot (standard Bruut with the [liquid fertilizer applicator advanced](../../liquid%20fertilizer%20applicator/advanced/))
carries a work tank of about 150 l. At 505 l/ha that lasts 0.29 ha or 81 minutes. Driving to a farm tank 500 m away
and back costs 20 minutes each time: field efficiency 80 % (53 % at 2 km). Every working robot that refills itself also
drives the headland and the track with a full tank.

The turn is the moment the working robot is not working anyway. With a 1 m implement and a smallest turning circle of
2.1 m the Bruut turns with three points (see `agbots/agbot slim`): forward arc R 2.4 m, **straight reverse of 3.8 m along
the headland**, forward arc. That straight is long enough to pump about 25 l while both robots drive, which is what the
working robot uses in two passes of 200 m at 550 l/ha. The working robot stops only to set its wheels straight (which it
does anyway) plus the camera check and the spout going down: about 3 s per turn.

Alternatives that were not chosen:
- **Fill standing still at every turn** (no driving along): simpler control, but 10 s or more of standstill per turn.
  It remains the fallback ("drive to the robot" mode) and the mode for big doses.
- **Hose reel from a fixed tank** (like drag-hose slurry systems): no refiller robot, but a hose across the field is in
  the way of the robot's own turns and of anything else in the field.
- **Bigger tank on the working robot**: more compaction, higher centre of gravity, and the front axle of the working
  robot already becomes light when the implement is lifted ([applicator RATIONALE § 6](../../liquid%20fertilizer%20applicator/advanced/RATIONALE.md)).
  With a refiller the work tank can stay small or even get smaller.

## 2. Where the refiller waits

Outside the turn, beside the straight, with the centre lines 1.45 m apart:
- The corners of the working robot swing up to 0.73 m outside its path in the arcs (R 2.4 m, robot 1.43 m long,
  0.98 m wide). With 1.45 m there is 0.23 m left at that moment and 0.47 m between the robots when they drive side by
  side. The refiller never has to move out of the way.
- On the outside the refiller drives only on the headland (or the farm track along the fence), never in the crop.
- Cost: the headland is about 1.2 m deeper (6.4 m from the field edge instead of 5.2 m).
- The turns alternate between the two ends of the field, so the next turn on this headland is two passes (2 m)
  further. After a refill the refiller is 3.8 m back along the headland: it reverses 5.8 m with its trailer to the
  next spot (8 s), and has minutes to spare.

## 3. A boom with a trolley (polar), not a fixed spout

The relative position of the two robots is never exact: RTK ±2 cm each, the working robot stops a few centimetres
early or late, the refiller lags when the working robot speeds up. The spout must still hit a Ø300 funnel, and keep
hitting it while both drive.

- **Slew + trolley** gives 2 degrees of freedom in the horizontal plane: any point between 0.35 and 1.5 m from the
  column, all round. The working robot can be on either side, in front or behind (drive-to-the-robot mode).
- A slewing boom of fixed length (1 degree of freedom) only reaches a circle; a telescopic boom is heavier and
  harder to seal. A trolley on a **belt linear module** (the same type as the X axis of the [field marker](../../marker/simple/))
  is bought, light (5.5 kg/m), fast and stiff enough: 3 mm deflection at full reach.
- **Worm slew drive** (e.g. a 3" slew drive with a 24 V motor): self-locking, so the boom stays where it is when the
  power is off; 14 Nm is needed to accelerate the boom at 30°/s².
- **Column at the rear, between the two rear lower beams.** There the hose can come up from the pump *inside* the
  column to a swivel at the top: no hose loop around the column, any slew angle. The column base plate and the
  sub-frame under the beams are clamped together by the same 8 × M10 (sandwich), so the beam carries no bending from
  the column alone.
- **Park pointing backwards** over the hitch: nothing sticks out in front of the robot (steering, its own GNSS
  antenna, people walking up to it), and over the trailer the head is still 150 mm above the trailer tank.

## 4. The head: antenna on the spout, camera beside it

- **RTK antenna on the spout axis**, on a short mast on the spout cap. The spout position is then measured directly.
  The alternative (computing the spout from the robot's own antenna, its heading, the slew angle and the trolley
  position) gives 26 mm error per degree of heading at 1.5 m reach, plus boom deflection and play. With the antenna on
  the axis only tilt matters, which the IMU in the head corrects. The antenna moves down with the spout (185 mm), which
  does not change its horizontal position.
- **Camera looking down**, 135 mm along the boom from the spout, at the fiducial plate next to the funnel. Two
  independent measurements (GNSS and vision) must agree before the spout goes down. The tag carries an ID: the
  refiller cannot fill the wrong robot or the wrong product tank.
- **Spout stroke 185 mm** with a 24 V linear actuator. Raised, the lowest part of the head (camera lens) is about
  100 mm above the funnel rim; that is why the boom can be out *before* the working robot arrives and the working robot
  can drive in under it. Lowered, the tip is 64 mm deep in the funnel.
- **Open funnel, no coupling.** A dry-break coupling would be drip-free, but needs millimetre alignment and force, and
  cannot follow while driving. An open funnel Ø300 tolerates 73–125 mm offset and allows filling on the move.
  Against splashing: the nozzle goes into the funnel, a strainer in the neck, and 150 l/min is moderate for 1.5".

## 5. Tank: T-shape with a sump between the beams

- The space inside the frame (between the upper beams x ±305 and the inner lower beams y ±405) is empty on the Bruut.
  A **sump** of 500 × 530 mm hangs down there to 300 mm above the ground: 112 l of the 268 l sits low.
  - Centre of gravity of the liquid at 730 mm instead of about 960 mm for a flat tank of the same volume on top.
  - The pump hangs under the rear beams **below the liquid level**: it is always primed and sucks the sump empty.
- The upper part (860 × 760 × 260) rests on two cradle tubes across the upper beams at y −375 and +275 (on the beam
  holes). They are deliberately not in the middle: the sump goes down between them.
- The front of the tank stays 75 mm behind the stepper-motor plates; the sump stays 107 mm away from the front wheels
  when they steer 30°.
- Rotomoulded PE (6 mm), as standard agricultural tanks: chemically resistant, translucent (level visible). Baffles
  against sloshing are needed in the real tank (not modelled).

## 6. Pump and hose

- **24 V centrifugal transfer pump, 1.5"**, chemical version (PP housing, FKM/EPDM). Static lift from the sump to the
  spout is only 0.77 m; with 5 m of 1.5" hose, swivel, valves and bends the operating point is about 164 l/min at 4.6 m.
  The controller limits it to 150 l/min (splashing in the funnel). Electric power about 370 W.
- A **diaphragm pump** would be self-priming and dose more accurately, but 24 V diaphragm pumps give 10–40 l/min:
  too slow for the turn window. A **peristaltic pump** (as on the applicator) is too slow and heavy at this flow.
- Two **electric ball valves**: one at the sump outlet, one on the line from the trailer. The trailer line is a
  separate hose with a camlock at the hitch (flexible part at the hitch; rigid in the model).
- A **flow meter** after the pump (not modelled) logs litres per refill.

## 7. Trailer: a robot chassis without front wheels, with driven wheels

- The full train weighs about 1 t. The robot's four hub motors give 84 kgf continuous (Quinder 8", 550 W: 44 Nm = 21 kgf per wheel); rolling resistance on a grass
  headland is 80 kgf. With the trailer wheels driven: 126 kgf, **max. grade 5 % instead of 0 %**. The 6 motors also share the peak current when starting.
- The trailer uses the **same parts as the robot**: 4 upper beams, 3 lower beams, 2 rear wheel units with hub motors
  (on the hole grid: the upper beams sit with their centre 350 mm in front of the axle so the wheel-unit bolts are on
  the holes, as at the rear of the robot). Spare parts are shared.
- **Tank centred over the axle** (50 mm in front): the hitch load is small (26 kg full), so it does not overload the
  rear wheels of the robot (204 kg per wheel full; 231 kg with the tank 200 mm forward).
- A-frame drawbar with an eye on a **vertical pin** in a clevis under the robot (behind the rear tyres). The trailer
  can articulate to about 85° before it touches the robot.
- Driven trailer wheels with independent speeds can steer the trailer when reversing: the train can reverse straight
  along the headland to the next turn.
- Parking leg behind the front beam of the trailer.

## 8. What the working robot needs (receiver kit)

- Work tank 147 l on the same cradle tubes as the refiller tank (no sump: the applicator's suction comes from the
  bottom).
- **Funnel Ø300** in the middle of the tank (y −35), rim 1144 mm above the ground, with a strainer in the neck.
- **Fiducial target** 160 × 160 next to the funnel, on the side where the refiller docks.
- **Ultrasonic level sensor** (stops the pump via radio) and a vent; a float valve in the funnel neck as mechanical
  overfill stop (not modelled).
- Cost: the work tank was needed anyway; the kit adds about €150 (funnel, target, sensor).

## 9. Not chosen / later

- **Coupling under pressure** (dry-break, automatic docking cone): for products that may not be open to the air
  (crop protection) this is the better choice, but filling then has to happen standing still.
- **Second pump for transfer trailer → robot tank**: now the pump simply switches its suction to the trailer tank.
- **Rinse water tank** and rinse programme for crop protection.
- **Cover over the funnel** (lid that the spout pushes open) against rain and dust.
