# Compost spreader (simple): why it is built this way

## Bin on top, spread behind

- The robot straddles the bed with the wheels in the paths (x +-375): between the tyres there is only 650 mm. A layer
  1.1 m wide spread in front of or under the robot would be driven over, so the compost leaves **behind** the rear
  axle, from a beater at y -1040 (tyre back at y -715).
- The bin uses the space the crate carrier uses: on the upper beams, from the rear end to y 333, 72 mm short of the
  front steering stacks (they start at y 405 and reach z 1032). The bin top (z 1160) stays behind them, so the steering
  plates and motors stay free and the GNSS dome (y 575) keeps a clear sky forwards.
- 3 bearers across the upper beams (as the crate carrier) at y 180, -20 and -330, clear of the frame bolts of the rear
  units (y -584..-416, up to z 705). The side plates stand on angle feet bolted to the bearer ends.

## Moving floor instead of a screw

- Damp compost bridges over a screw or an opening in a hopper bottom. A **moving floor belt** under the whole bin
  carries the full load out, the way muck spreaders and feed wagons do: no bridging, no slope needed in the bin, so the
  bin stays low (cg of the load at z 995).
- Belt 920 wide on a UHMW-PE slide bed, drums O100. The rear drum drives (it pulls the loaded top run), the front drum
  sits in take-up slots. A 24 V worm gearmotor 60:1 with a 1:4 chain step gives up to 30 mm/s; with a full bin the
  belt needs ~444 N pull (belt on the bed mu 0.25, compost on the side walls), 24 Nm on the drum, ~27 W.
- Rubber skirts from the side plates onto the belt edges stop compost running under the plates.

## Dose = belt speed x gate

- The slide gate sets the layer height on the belt (30..150 mm), set by hand with 2 star knobs; the robot then sets
  the belt speed from the driving speed and a task map: q = rho x fill x gate width x opening x belt speed.
- The three jobs (1, 2 and 3 kg/m2) all come out at a gate of 80..100 mm and ~23 mm/s of belt (80 % of top speed),
  so one gate setting per compost type is enough; the belt does the fine control.

## Beater

- A tube rotor with 28 paddles at 300 rpm (tip 4.4 m/s) breaks up lumps and throws the compost back into a hood that
  turns it down onto the bed. Low tip speed keeps the throw short: the layer lands within ~1.1 m width behind the
  robot, no wide spread pattern as with a spinning disc.
- Power from muck spreaders: ~0.6 kJ/kg to break up and throw, plus ~150 W idle: 680..810 W at 0.9..1.1 kg/s. A 48 V
  1 kW BLDC (as used on other implements) with a poly-V belt 1:5 to the rotor, under a guard on the right.

## Payload, ballast and slopes

- 150 kg is the payload taken for the top of the robot (as for the crate carrier, estimated). With moist green compost
  (600 kg/m3) that is 250 l of the 299 l bin. Dry compost fills the bin at 135 kg; rotted manure reaches 150 kg at 200 l.
- The spreader itself is 190 kg (4 mm side plates, belt 18 kg, drums, beater 44 kg) with its cg behind the rear axle
  (y -513), because the beater must be behind the tyres. Without ballast the front axle keeps only 22..25 %: too little
  for steering on grass. **1 plate per stack of the counterweights** (66 kg) brings it to 33..35 %.
- Full with ballast the robot weighs 566 kg. The hub motors (4 x 55 Nm continuous) climb 8 degrees continuously, 12
  degrees empty; on steeper fields fill the bin half. Side tip angle 26.7 degrees (cg 746 mm high).
- This is the heaviest implement so far; a lighter build (aluminium side plates, a thinner belt) is the first thing to
  look at in an advanced version.

## Capacity

One bin covers 150 m2 of grassland at 1 kg/m2, 75 m2 of orchard strip at 2 kg/m2 or 50 m2 of bed at 3 kg/m2. With a
4 minute refill from a heap (front loader or a pallet fork on a yard tractor) and 80 m to and from the heap that is
~1.1 t per hour, 400..1100 m2 per hour. Energy is small (46..57 Wh per bin, 33..41 bins per battery): the limit is the
refilling, not the battery. Pairs well with the [mobile refiller](../../mobile%20refiller/) idea of a support vehicle.

## Estimated, not measured

- Robot mass 160 kg, cg (0, 0, 380); payload rating 150 kg on top
- Bulk densities of the composts (400..750 kg/m3), fill factor of the belt under the gate 0.85
- Friction: belt on UHMW 0.25, compost on steel 0.5, lateral pressure ratio 0.4
- Beater energy 0.6 kJ/kg and idle 150 W (from muck spreader figures), spread width 1.1 m
- Masses of the gearmotors, motor and bearings; the belt drawn flat (no cleats)
- Refill time 4 min and 80 m travel per load; hub motor 55 Nm continuous, rolling resistance 0.06
- Ballast position (y 500, z 700) of the counterweights
