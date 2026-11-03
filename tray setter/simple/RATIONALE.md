# Tray setter (simple) - rationale

## Pick and drop instead of a tray-fed carousel

Commercial transplanters let a person put plants in a carousel, or pull whole rows out of special trays. A robot has
no person on it, so the plants must come out of standard plug trays one by one: a small XYZ gantry with a needle
gripper does that with the same parts as a 3D printer or a CNC router (GT2 belts, NEMA17). The plug falls through a
tube to the soil, as in drop-type transplanters, so the gantry never has to reach the ground.

## Under the belly, not at the front

The idea list says front-mounted. Between the wheels the shoes are stiffly held, see the same ground as the wheels and
need no lift (the robot sets the depth); the drop tubes go straight down from the table without bends. The planting
units hang from the belly rails of the drop-on-demand boom, the press wheels behind the shoes stay 77 mm from the rear
tyres.

## Gantry speed sets the pace

One pick-and-drop takes 1.6-3.0 s (Z up/down 140 mm at 600 mm/s, X/Y at 800 mm/s with 4 m/s2, gripping 0.15 s).
Two rows at 300 mm need a plant every 3.1 s at 0.048 m/s, so the robot creeps. That is slow (~780 plants/h, about
what one person with a hand planter does), but the robot works unattended and does not tire. A faster variant would
pick 2 plants at once (one per row) or use a tray shuttle so the gantry only moves short distances.

## Trays

Two 128-cell trays are 256 plants, 38 m of bed, 13 minutes. Somebody has to change them (30 s); an advanced variant
would carry a rack of trays and a tray changer.

## Shoe and press wheels

A runner shoe opens a narrow slot without turning the soil; the boot behind the blade keeps the slot open where the
plug lands. Two press wheels tilted 15 degrees (tops apart) push the slot walls against the plug. Draft ~120 N per
shoe at 60 mm in a seedbed, small for the hub motors.

## Estimated, not measured

- Gantry speed and acceleration, Z speed, gripping time, drop time
- Draft per shoe (120 N), press wheel force (150 N), drive power at 0.048 m/s (220 W), gantry power (40 W)
- Plug and seedling size (25 mm plug, 90 mm leaves), mass per plant (30 g)
- Tray change time (30 s), field efficiency (70 %)
- Robot mass (161.5 kg) and centre of gravity, usable battery energy (2.4 kWh)
- Not modelled: belts and pulleys, the gripper's needle drive, cable chains, a plant sensor in the drop tube, spring
  loading of the press wheels
