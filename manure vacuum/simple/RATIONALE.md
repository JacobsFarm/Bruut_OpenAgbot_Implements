# Manure vacuum collector (simple): rationale

## Vacuum tank, not a fan

The debris vacuum moves litter in an air stream through a fan-and-screen bin. Manure is a liquid with straw: an air
stream would need a huge flow to carry it, and a screen would clog. A sealed tank under 0.5 bar vacuum instead pulls
the manure up the hose as a liquid (it could lift it 5 m); the pump only moves air, and a float valve shuts the
suction line before the tank is full so the pump stays dry. This is how slurry tankers work.

## Squeegee instead of brush

On a solid floor the manure lies in a thin layer. A rubber lip at the rear of the hood that bends back on the floor
scrapes it together inside the hood, where the suction stub takes it. The front flap rides 40 mm high so the layer
gets in; the castors carry the hood so the lip pressure stays the same.

## Same nozzle, hose and lift as the debris vacuum

The hood, lift, castors and hose are already checked against the steering sweep and the lift poses. The tank's inlet
stub is at the same place as the debris bin's, so the hose is unchanged. Only the brush, its bearings and its motor
are left out.

## Tank size

The standard robot is light. 130 l of manure is 133 kg; with the nozzle in front the full machine is ~476 kg, with
313 kg on the front axle. A bigger tank means fewer trips, but more load on the front wheels and the hub motors; 130 l
fills in ~6 minutes, which keeps the trips to the pit short (60 m). The cycle (collect, drive, dump) repeats ~17 times
a day for 100 cows.

## Emptying

At the pit grid the dump valve opens; the pump can be reversed to push the tank empty in seconds and to blow the hose
clear. The same docking (a fixed position by the pit) also lets a hose rinse the nozzle and the tank.

## Navigation

Indoors there is no RTK: the robot follows the alley with the lidar / UWB approach of the arena leveller, and the
alleys are fixed routes. Cows are slow obstacles; the robot stops and waits.
