# Why the mobile refiller with two IBCs is what it is

## Two IBCs, one per liquid

The precision applicator V4 applies two liquids at once (A through the right half of the roller pump, B through the
left), each from its own work tank. A refiller for it must carry both and keep them apart, so each liquid gets its
own IBC, pump, hose, drop pipe and nozzle. Mixing in one tank is not an option: the point of two liquids is that they
are dosed separately (or must not be mixed before they are in the soil).

## A longer frame instead of a wider one

Side by side, two IBCs (1200 wide each when the valve faces sideways) would make a 2.4 m wide robot that no longer
fits the 1 m passes and the farm gates. One behind the other they keep the width of the simple refiller (1200 + the
mast on the left). That needs a frame about 2.1 m long for the two pallets plus a gap for the mast cross tube: the
wheelbase goes from 1000 to 2200 (upper beams 1300 → 2500). Front units, steering, rear units and hub motors stay as
they are; only the beams are longer. IBC A sits 25 mm behind the front stepper-motor plates (as on the simple
refiller), IBC B behind it; the mast stands between them on the left, so the arm reach (1450 to the centre line of the
working robot) is the same as on the simple refiller and the skip pattern and turn geometry stay the same.

## Two nozzles across the arm

The working robot's funnels lie across the robot, 455 mm apart (A right, B left). The working robot stops beside the
refiller with the same heading, its right side towards the refiller, so funnel A is the near one: nozzle A sits
1222.5 from the refiller centre line, nozzle B 1677.5. Both hoses run side by side; B crosses over the arm at the
pivot and runs on the outside, so the A hose can drop straight into its drop pipe without crossing B. The antenna
sits between the nozzles: the RTK position then is the centre line of the working robot.

## The refiller is inside a 6 m U-turn: where exactly

The lengthened refiller is 2.63 m long, inside a U-turn of 6 m (two arcs of R 2.4 m with 1.2 m straight). Where it
stands along the headland decides how close the turning working robot (with the lifted applicator) comes: centred on
the turn it touches the second arc; 3.23 m from the pass the robot leaves gives the largest gap, **169 mm** in plan
view (`tla_plan.min_gap`, outlines of the robot with its applicator and of the refiller with IBCs, mast and hoses),
on the second arc. That is less than the 225 mm of the simple refiller; a larger turning radius or a wider skip
(N = 7) gives more room.

## Not two full IBCs

Four wheels of 500 kg (Quinder datasheet) carry about 2000 kg. Robot (173 kg), bed, mast and pumps (about 120 kg)
and two empty IBCs (116 kg) leave about 1400 kg of liquid: **570 l per IBC** at 1.2 kg/l, the left rear wheel then
carries 498 kg (the mast and both pumps are on the left, IBC B lies further from the middle than A). Two full IBCs
would put 773 kg on that wheel. Traction is the other limit: rolling resistance on grass (8 %) exceeds the continuous
force of the four hub motors above about 270 l per IBC; only short moves on the headland are possible fuller, as
with the simple refiller. Options to carry two full IBCs, not modelled:

- a third axle under the gap between the IBCs (6 wheels: 3000 kg), with the middle wheels free to castor;
- the XL robot (`agbots/agbot design big`, Quinder 16") with the same long frame;
- 2 × 600 l IBCs (1200 × 800 footprint) on the same frame.

## Fill bridge for the trailer

The IBCs are filled through their top. The trailer's arm reaches across the refiller the way it reaches across the
working robot, so the refiller needs two funnels side by side across its width, 455 apart, at one y. The only place
for that is over the gap between the IBCs: a plate on the cage top bars of both IBCs carries the two funnels (rim
z 2060), and a short PP 50 pipe from each funnel over the cage into a DN50 bulkhead fitting drilled into the flat top
of its own IBC (y 90 for A, −230 for B, clear of the straps and cage bars). The trailer lifts its arm 706 mm to put
its nozzles 106 mm over these rims.
