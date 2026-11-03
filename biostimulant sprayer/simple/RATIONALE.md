# Biostimulant sprayer (simple) - rationale

## Why the spot sprayer as it is

Biostimulants go on the whole field at 100-200 l/ha; no camera is needed. The spot sprayer already has a tank, a
diaphragm pump, a 50-mesh filter, a regulator with bypass return (which also stirs the tank) and a 3.75 m boom that
folds for posts, gates and transport. So it is imported unchanged; only the tips, an aerator and a weather mast are
new. Swapping between spot spraying and biostimulants: change the 15 tips, swap the camera mast for the weather mast
(both bolt to the robot), plug in the air pump. Rinse the tank well between herbicide and living products.

## Tips and pressure

- Living products (bacteria, fungi in compost tea) survive low pressure and low shear best; diaphragm pumps below
  ~4 bar are the usual choice. 1.5 bar is used.
- Compost tea contains particles: through a 50-mesh (0.3 mm) filter they stay below 1/3 of the 0.9 mm orifice of a
  size 02 tip, the usual limit for bridging. Smaller tips (01, 015) would block.
- Twin flat-fan turbulence tips give coarse drops from 1 bar: little drift, and the drops land on the leaves and the
  soil instead of evaporating (UV and drying kill organisms).
- Size 02 at 1.5 bar is 0.56 l/min; at 2 m/s that is 186 l/ha, inside the 100-200 l/ha of the idea. The robot drives
  2 m/s on grassland; for 100 l/ha it would need 3.7 m/s, so lower rates need size 015 tips (only for clear products).

## Aeration

Compost tea turns anaerobic within hours without air; brewers bubble ~0.05-0.1 l of air per litre per minute. A 30
l/min pump on 120 l gives 0.25, also enough to keep seaweed extract and bacteria suspensions mixed. The diffuser ring
lies on the tank floor; the pump sits outside the tank on the strap (dry, easy to service).

## Weather window and logging

Living products need low UV, moist leaves and calm air: spray early in the morning or in the evening. The example May
day gives 11 hours inside the window (wind < 3.5 m/s, 8-25 C, RH > 60 %, no rain), 4-10 h and 18-23 h. The weather
sensor sits on a mast above the tank so it sees free air; its data and the GNSS track go into the pass log, which is
what the idea asks for (compare treated and untreated strips later). Untreated check strips can be planned in the
path planner: the boom simply stays off over them.

## Tank size against field size

120 l = 0.64 ha. With refills from the mobile refiller at the field edge (8 min each) the robot does ~1.5 ha/h; the
battery (2.4 kWh, ~2.3 h at 2 m/s) limits a session to ~3.4 ha, so for larger fields a battery swap or the hybrid
range extender is needed before the tank size matters. A bigger tank would add weight on the upper beams for little
gain.

## Estimated, not measured

- Orifice of the size 02 tip (0.9 mm) and the 1/3 bridging rule; shear limit 4 bar for living organisms
- Robot speed of 2 m/s on grassland and the drive power (450 W per m/s, as for the spot sprayer)
- Weather window limits and the example day; refill time (8 min); field efficiency (80 %)
- Air pump flow (30 l/min) and power (25 W), logger power (15 W)
- Masses of the weather sensor (0.7 kg) and the air pump (1.4 kg); the spot sprayer's own estimates
- Robot mass (161.5 kg) and centre of gravity, usable battery energy (2.4 kWh)
- Not modelled: the tips themselves (same bodies), the logger software, a rinse tank
