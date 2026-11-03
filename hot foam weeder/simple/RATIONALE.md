# Hot foam weeder (simple) - rationale

## Hot foam instead of steam or flame

- **Flame** (the flame weeder) is the cheapest per hectare, but it is a fire risk on dry grass, straw, wood chips and
  next to buildings, fences and parked machines, and it cannot be used in a drought ban.
- **Steam** needs a pressure vessel or a once-through steam generator, and steam condenses and runs off the leaf in a
  second or two.
- **Hot water with foam** (as in Foamstream / Heatweed practice): the water stays below 100 C (no pressure vessel, a
  plain coil heater), and a thin layer of foam (0.3-1 % of a sugar / plant-oil based concentrate) keeps the hot water on
  the leaf and insulates it, so the leaf stays above ~60 C for many seconds. 2 s at that temperature kills seedlings;
  the hood keeps the heat in a while longer. Perennials with deep roots (dock, thistle, couch) regrow and need 3-5
  passes per season, as with flaming.

## Why the flame weeder's hood and the propane

The flame weeder already has a 1.5 m insulated hood on castors, a free parallelogram that lets it follow the ground,
and 2 x 18 kg propane cylinders with liquid withdrawal and a safe valve train. The same hood keeps the steam and foam
warm, and propane is the only practical heat source: 40 kW of heat is ~17 times what the robot's 2.4 kWh battery can
deliver for an hour. So the burners in the hood go out and a foam bar goes in; the propane goes to a boiler instead.

## Boiler: 40 kW coil heater

Hot-water pressure washers use propane or diesel coil heaters of 30-60 kW. 40 kW heats 6.8 l/min from 12 to 96 C.
That sets the work rate: at 0.4 l/m2 over the 1.5 m hood the robot must drive 0.19 m/s (~1000 m2/h). A bigger
boiler would allow more speed but needs more water, and the water is the real limit.

The boiler stands on a rear rack behind the robot, above the parallelogram and the front of the hood: the hot parts
(flue) are away from the cylinders on the robot, and the hot hose to the hood is short (1.3 m). The propane goes
liquid through the flame weeder's excess-flow and main valves to the burner; the burner has its own vaporiser in the
flue and its own regulator and safety valve (as in the pressure-washer heaters).

## Water: 95 l under the belly

The cylinders take the top of the robot, so the tank goes under the belly between the wheels, on the rails of the
drop-on-demand boom. ~95 l fits (x +-280, y +-238, 375 high) with 30 mm to a front tyre at full steering lock and
170 mm ground clearance under the frame (enough for paths, yards and tree rows; not for ridged crops). 95 l is ~240 m2
or ~14 minutes: the robot drives back to a tap, or the mobile refiller meets it. Hot foam is a tool for small areas
(paths, yards, playgrounds, fence lines, around trees and posts), not for whole fields; that matches the idea list.

## Weight

Full, the rear axle carries 61 % (boiler and rack behind it, water and gas in the middle); 136 kg per wheel at most,
far below the 500 kg of the hub motor. The hood (72 kg) rides on its own castors.

## Estimated, not measured

- Boiler: 40 kW into the water, 85 % efficiency, fan power 60 W, mass 38 kg
- Dose 0.4 l/m2, foam share 0.5 %, foam hold time 20 s, lethal time 2 s above ~60 C, hose loss 3 K
- Water temperature in the tank (12 C)
- Drive power at 0.19 m/s with this load (250 W), pump power (110 W), control (25 W)
- Prices: propane 1.6 EUR/kg, foam concentrate 6 EUR/l, water 0.002 EUR/l
- Robot mass (161.5 kg) and centre of gravity, usable battery energy (2.4 kWh)
- Masses of the pump, doser, fittings, hoses and the blanket density
- Not modelled: the boiler's coil and burner inside, the wiring, a drain valve on the tank, a filter before the pump,
  frost protection (drain the coil in winter)
