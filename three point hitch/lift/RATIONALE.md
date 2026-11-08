# Three-point hitch, lift mast: why it is built this way

## 1. Straight up and down

- To pick up a machine that stands on its own legs, set it down somewhere else and leave it there, the hitch has to
  go straight up and down: a swinging hitch (a_frame) tilts the machine and moves it along y, so the legs would
  scrape. A parallel linkage (parallel) keeps it level but moves it 29 mm along y and needs the long links. A mast
  with 2 columns does exactly what is needed, with one LA36 straight in line with the travel (no lever: the LA36
  only carries the weight plus the friction).
- The interface stays the A-frame triangle with 10 degrees lean, so the same machines and implements fit all three
  variants.

## 2. Coupling with the triangle

- The male triangle comes from below: with the carriage low the male origin is 60 mm under the female origin of the
  standing machine. Because the triangle gets narrower upwards, the male legs pass between the lips of the female
  while the robot reverses, and the apex passes under the hook. Lifting 60 mm brings the male into the female (the
  sloping legs centre it within the 2 mm play), the hook takes the weight and the spring latch drops into the lock
  plate. Then the machine comes off its legs: 220 mm at the top of the travel.
- Setting down is the same in reverse; the latch is pulled with its T-handle (by hand, or later a small solenoid).

## 3. Mast and carriage

- Fixed columns O50 x 4 with the bushes in the carriage (as dockweed drill v7, but there the tubes move): the mast
  is a closed frame (2 cross tubes, 2 uprights) that hangs on the rear face of the toolbar with 2 brackets at x +-275,
  so the carriage can pass the toolbar height. The hanger webs of the toolbar reach y -890: the columns stand at
  y -940 and the housings start at y -918.
- 300 mm between the 2 housings of a column: the machine hangs ~490 mm behind the columns, so its moment gives a
  force couple of 842 N on the bushes and with a dry iglidur bush (0.15) 253 N of friction, about a third of the
  weight. Longer spacing means less friction but a longer carriage.
- The carriage plate has 3 windows (8 mm instead of a full 10 mm plate) and the housings are tubes instead of
  blocks: the carriage went from 35 to 22 kg.

## 4. LA36

- Stroke 300 (installation 500 + 300 = 800 max): 280 mm travel with 10 mm to both end stops. 20 mm spindle with
  gear F (1700 N, 52 .. 72 mm/s): the 957 N load is 56 %, lifting takes 4.6 s.
- The housing sits on the carriage and the rod goes up to the top cross tube: with the body at the top the mast
  would have to be 300 mm taller. The housing is turned 90 degrees about the spindle (motor along x, the back
  fixture ordered at 90 degrees so its hole stays along x): otherwise its 148 mm depth does not fit between the
  toolbar (y -860) and the carriage plate (y -980).
- The rod pin runs in a 40 mm slot under the top cross: an implement on its own wheels (a roller, a rake) can float
  up that far with the carriage. The top cross sits high enough that the rod eye stays clear at the top of the slot.

## 5. Axle load

- The machine hangs 1.4 m behind the robot centre: lifted, it takes weight off the front axle. With the standard
  2 x 20 kg front counterweight only 15 % remains on the front axle with the 50 kg demo machine; 58 kg of front
  counterweight (6 plates of 11 kg in the counterweights stacks) gives 20 %. Without counterweight the front wheels
  would almost lift (2 %): never lift a machine without the front counterweight.

## Estimated, not measured

- Robot mass 160 kg and its centre of gravity midway between the axles; least front axle share 20 % to steer
- Friction coefficient of the dry iglidur bush on a steel tube 0.15
- LA36 speed and current linear between no load and nominal load (datasheet table); housing and motor dimensions
  from the datasheet drawing, motor diameter and gear length estimated
- Bulk density of the seed in the demo box 0.75 kg/l, PE 0.95 kg/dm3
