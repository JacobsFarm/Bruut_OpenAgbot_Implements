# Implement ideas

Attachments that are **not worked out
yet**: those from the website's list ([openagbot.com](https://openagbot.com), functionality's.json) and extra ideas from brainstorming (marked in their README). Each folder holds a `README.md` with what the implement does, a first concept, what can be reused from the finished
implements and the open questions, so it can be worked out later in the layout described in [AGENTS.md](../AGENTS.md).

## Soil Cultivation & Weed Control

| Idea | What it does |
|---|---|
| [Drop-on-demand boom (coarse droplets)](drop_on_demand_boom/README.md) | Boom with individually controlled injectors that fire single coarse droplets on demand at low pressure. |

## Sowing & Planting

| Idea | What it does |
|---|---|
| [Tray setter](tray_setter/README.md) | Front-mounted unit that takes seedlings out of the tray and sets them out at the right spacing. |

## Power & Drive

| Idea | What it does |
|---|---|
| [Generator / engine](generator_engine/README.md) | Generator or combustion engine mounted between the frame as an auxiliary power source for extra electricity or mechanical power. |
| [Heavy-duty electric motors](heavy_duty_motors/README.md) | Electric motors such as the Ego Power+ or Greenworks units to drive implements that need real power, replacing small petrol engines. |
| [Charging robot (mobile charger)](charging_robot/README.md) | A robot on wheels that carries a large battery and charges working robots in the field, so they do not have to return to the shed. |

## Transport & General

| Idea | What it does |
|---|---|
| [Seat & frame extension](seat_frame_extension/README.md) | Front or rear-mounted seat, with the option to widen the frame tubes at the sides. |
| [Small cabin](small_cabin/README.md) | Protective enclosure or housing for the operator. |
| [Speech speaker](speaker/README.md) | A speaker on the robot that can speak: warnings when the robot approaches, status messages for the operator, instructions in the field, and a way to speak to people near the robot. |

## Cooperation & Swarm Operation

| Idea | What it does |
|---|---|
| [Drone combination](drone_combination/README.md) | The robot works together with a drone as a mobile base station. |
| [Swarm operation (multiple robots per field)](swarm_operation/README.md) | Several Bruut units work the same field as one swarm. |

## Crop & Soil

| Idea | What it does |
|---|---|
| [Mole and tunnel mapper](mole_mapper/README.md) | Finds and maps molehills (and with a probe, mole tunnels) so they can be treated or spread flat later. |

## Weed & Crop Protection

| Idea | What it does |
|---|---|
| [Laser or UV weed treatment](laser_weeder/README.md) | Kills individual weeds with a laser or a focused UV beam, without chemicals and without moving the soil. |
| [Hot steam / hot foam weeder](steam_foam_weeder/README.md) | Kills weeds with hot steam or hot foam under a light hood, as an alternative to the flame weeder. |
| [Pheromone trap service](pheromone_trap_service/README.md) | Visits insect traps and pheromone dispensers at the field edge: checks them with a camera, counts catches and swaps dispensers on schedule. |

## Livestock & Farm

| Idea | What it does |
|---|---|
| [Fence inspector](fence_inspector/README.md) | Drives along the fence, checks the electric fence, reports breaks and shorts and straightens leaning posts. |
| [Drinking trough check](drinker_check/README.md) | Visits drinking troughs, measures the water level, tops it up and reports dirt or damage with a camera. |
| [Manure scraper / slurry pusher](manure_scraper/README.md) | Scrapes or pushes manure and slurry on stable floors and walkways toward a drain or gutter. |
| [Chicken house robot](chicken_house_robot/README.md) | Drives through a poultry house to turn the litter, collect floor eggs, and check birds and climate with sensors. |

## Measuring & Sensors

| Idea | What it does |
|---|---|
| [Yield estimator](yield_estimator/README.md) | Counts fruits, heads or plants with a camera and logs them per GPS position, so the harvest can be estimated and planned. |
| [Disease and pest scout](disease_scout/README.md) | Looks at the leaves close up, finds disease and pest damage early and stores a photo per plant with its position. |
| [Soil moisture sensor placer](soil_moisture_placer/README.md) | Places wireless soil moisture sensors at set GPS points, reads them out and picks them up again. |
| [Fence voltage meter](fence_voltage_meter/README.md) | Measures the voltage and current of the electric fence while driving along it and maps where the voltage drops. |
| [Windbreak and tree-row inspector](windbreak_inspector/README.md) | Drives along hedgerows, windbreaks and orchard rows and logs gaps, damage, dead trees and growth with a camera. |
| [Security camera patrol](security_patrol/README.md) | A mast with camera and thermal imaging that patrols the farm or field at night, reports intruders and keeps an eye on animals and equipment. |

Already worked out (in the folders next to this one): overseeder, liquid fertilizer applicator, feed pusher auger, disc brushes
(broom), dockweed drill (CNC weed driller), trencher, spot sprayer (atomising boom), in-row weeder (finger weeders), around-pole
mower (mowing arm), weed picker, irrigation (hose reel), field marker, mobile refiller, belt rake, weeds burner,
push blade (also the manure scraper job), fertilizer spreader, grassland harrow (molehill spreader), soil sampler, inter-row hoe, grassland aerator, three-point hitch (with the small cultivator), crate carrier (also the tool cart), counterweights, battery pack, solar canopy, compost spreader, stone picker, mulch layer, grass meter (NIR sensor), soil compaction meter, charging dock, UV-C mildew light, sawdust spreader, bedding rake, dumper barrow, biocontrol spreader, bag trailer, broom sweeper (angle broom on the push-blade lift), lime spreader (drop auger), cover crop undersower, straw spreader (bale shredder), electric weeder (spot HV comb), hydraulic power pack and irrigation pump (direct pump).

Covered elsewhere: the tow hitch (50 mm tow ball) and the patch seeder (drop seeder that a camera switches on over
bare soil) are in [overseeding/](../overseeding/) (cambridge roll and overseeder).
