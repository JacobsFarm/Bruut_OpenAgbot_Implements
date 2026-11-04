# Debris vacuum (simple): why it is built like this

## Clean-air fan on the bin

A fan in the dirty air stream (as in a leaf vacuum with a shredder impeller) is cheap but glass shards and cans wear
and break the impeller and make it unbalanced. Here the fan sucks the air out of the bin through a screen: the
litter drops in the bin where the air slows down, and only air passes the fan. It costs a sealed bin and a screen,
but the impeller lasts.

## Hose speed 22 m/s, O125

An item is carried safely when the air is ~1.8x faster than its terminal speed. The heaviest item per area is a piece
of PV glass (50 x 50 x 3.2 mm, 20 g, ~10.9 m/s), so 22 m/s is enough for everything on the list. O125 passes a crushed
can, a cup and a 0.5 l PET bottle; a bigger hose needs proportionally more air and power. A lower speed would save
power (it goes with v^3) but lose the glass.

## Brush in the nozzle

Under the flaps the air only reaches ~8 m/s over a 1 m wide slot: enough for cups and butts lying loose, not for a can
or a shard in the sward. The brush roller (O200, 400 rpm, 8 mm into the grass) flicks them up into the nozzle, where
the air takes them to the outlet. It also keeps the nozzle from having to sit very low (it rides 40 mm up on the
castors, the flaps 10-25 mm).

## Power: ~1.4 kW, so a range extender for big jobs

The fan takes ~910 W, the brush ~240 W and the drive ~300 W with a half-full bin: ~1.3 h per 1.9 kWh charge, ~0.34 ha.
That is the physics of moving 0.27 m3/s at 1.7 kPa. For a festival site (several ha) run the robot with the
[hybrid range extender](../../Hybrid/) (3 kW generator) or swap battery packs; a smaller hose or nozzle would not pick
up the glass.

## Nozzle on the magnet-sweeper head

The magnet sweeper already has a head frame on the king pin with brackets that hold a 1100 mm wide box 70 mm in front
of the beam, clear of the broom castors when they swivel round. The nozzle uses the same bolt pattern, so the head
frame and castors are shared.

## Bin on the upper beams

The bin sits between the axles (y -380..370), clear of the front steering stacks (y 405) and the rear frame bolts
(y -416), on cross bars bolted into the grid holes of the upper beams at y +-325. A full bin (60 kg) shifts the load
to the rear a little (rear 55 %). The fan and motor make it 1.46 m high.

## Estimated, not measured

- Loss factors of the nozzle (2.0), bends (1.0) and bin (1.0), friction of the corrugated hose (0.04), screen 400 Pa
- Fan and motor efficiency (0.5), fan and motor mass (9 + 4.5 kg), gearmotor mass (7.5 kg)
- Item masses, drag areas and drag coefficients, the conveying factor 1.8
- Bristle force on the sward (60 N per m), friction (0.6), windage of the brush (30 W)
- Bulk density of litter (60 kg/m3) and glass shards (1300 kg/m3), litter left per ha (25 kg), bin payload (60 kg)
- Rolling resistance of the robot (0.06) and the castors (0.08) on grass; robot mass and battery energy
- Not modelled: liner bag, door latches, dust filter on the fan outlet, wear lining in the nozzle and hose bends
