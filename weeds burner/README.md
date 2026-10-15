# Weeds burner (flame weeder) for the Bruut

Kills weed seedlings with heat instead of herbicide or soil movement. Made for **pre-emergence flaming**: a freshly
sown bed is flamed a few days before the crop comes up, so every green seedling is a weed. The soil is not moved, so
no new weed seeds are brought to the surface.

| | Variant | Contents |
| --- | --- | --- |
| [Propane, hood 1.5 m](propane_hood/README.md) | `propane_hood/` | FreeCAD model: insulated hood 1.5 × 0.8 m behind the robot with 6 flat-flame burners (167 kW), two 18 kg forklift cylinders (liquid withdrawal) on the robot, vaporiser coil in the hood, valve train with pilots and flame sensors, hood on two steel swivel castors and a free parallelogram. Calculations (dose, speed, gas, vaporiser, cylinder pressure, standstill, heat to the robot, axle loads), animation on a sown bed, parts list (≈ €3,400); why: [RATIONALE](propane_hood/RATIONALE.md) |

![the flame weeder on the robot](propane_hood/previews/1_work_iso_on_robot.png)

![animation: flaming a sown bed](propane_hood/previews/animation_flaming_bed.gif)

## Concept

1. **Sow, wait, flame.** The weeds come up before the crop (carrot: the crop needs 10–14 days). A few days before the
   crop emerges the robot flames the bed.
2. **Hood.** Under an insulated hood the hot gas stays on the soil for > 1 s; 35 kg/ha of propane is enough for
   seedlings up to 2 leaves.
3. **Liquid gas, evaporated in the hood.** Forklift cylinders deliver liquid; a coil in the flames turns it into gas.
4. **Never standing still with the flames on.** Below 0.2 m/s the valves close; pilots stay lit for the next start.

## Requirements

| | |
| --- | --- |
| Robot | standard Bruut OpenAgbot; plate under the rear beams and a cradle on the upper beams, nothing drilled |
| Width | one bed (1.5 m) |
| Gas | propane, on the robot |
| Use | bare, freshly sown beds; see the safety list in the variant README |

## Options for later

| Option | What it adds |
| --- | --- |
| Band flaming over the rows only | after emergence of tolerant crops (onion, maize): shields between the rows, less gas |
| Camera for the crop | stops flaming where the first crop seedlings show (a glass-plate check, automated) |
| Bigger gas supply | a third cylinder, or a refill station like the [mobile refiller](../mobile%20refiller/) for propane |
| Infrared panels | catalytic radiant panels instead of open flames: quieter, slower |
| Steam or hot water | the same hood with a steam generator: no open flame (more energy per ha) |
