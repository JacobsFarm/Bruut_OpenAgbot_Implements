# Implement ideas

Attachments that are **not worked out
yet**: those from the website's list ([openagbot.com](https://openagbot.com), functionality's.json) and extra ideas from brainstorming (marked in their README). Each folder holds a `README.md` with what the implement does, a first concept, what can be reused from the finished
implements and the open questions, so it can be worked out later in the layout described in [AGENTS.md](../AGENTS.md).

## Soil Cultivation & Weed Control

| Idea | What it does |
|---|---|
| [(Rubber) push blade / grader blade](push_blade/README.md) | Front-mounted or mid-mounted between the front and rear wheels. |
| [Small cultivator](small_cultivator/README.md) | Compact cultivator for soil cultivation in vegetable gardens and light plots. |
| [Single-axis inter-row hoe](inter_row_hoe/README.md) | Hoeing unit with single-axis (left/right) guidance that stays tightly between the rows, for example in maize, so weeds are cut close to the crop without damaging it. |
| [Drop-on-demand boom (coarse droplets)](drop_on_demand_boom/README.md) | Boom with individually controlled injectors that fire single coarse droplets on demand at low pressure. |
| [Grassland aerator](grassland_aerator/README.md) | Improving soil structure and air supply in grassland. |

## Spraying, Fertilizing & Irrigation

| Idea | What it does |
|---|---|
| [Irrigation pump (direct pump)](irrigation_direct_pump/README.md) | Pumping water from ditches for local irrigation or crop spraying (website: Irrigation Pump). |
| [Fertilizer spreader](fertilizer_spreader/README.md) | Precise application and spreading of granular fertilizers. |
| [Lime spreader](lime_spreader/README.md) | Spreading lime to improve soil pH levels and structure. |

## Sowing & Planting

| Idea | What it does |
|---|---|
| [Tray setter](tray_setter/README.md) | Front-mounted unit that takes seedlings out of the tray and sets them out at the right spacing. |
| [Patch seeder](patch_seeder/README.md) | Compact seeder that spreads grass seed onto bare patches in the sward, so damaged spots close up again quickly. |

## Spreading & Bedding

| Idea | What it does |
|---|---|
| [Sawdust spreader](sawdust_spreader/README.md) | Even distribution of sawdust or bedding material in stables. |
| [Straw spreader](straw_spreader/README.md) | Evenly spreading straw, specially designed for use between vegetable rows. |
| [Compost spreader / bin](compost_spreader/README.md) | Transporting compost within the frame structure and spreading it between the crop rows. |

## Power & Drive

| Idea | What it does |
|---|---|
| [Battery pack](battery_pack/README.md) | Additional power supply modules to be installed between the frames. |
| [Generator / engine](generator_engine/README.md) | Generator or combustion engine mounted between the frame as an auxiliary power source for extra electricity or mechanical power. |
| [Solar panels](solar_panels/README.md) | Integrated panels to extend battery life and provide sustainable power during operation. |
| [Heavy-duty electric motors](heavy_duty_motors/README.md) | Electric motors such as the Ego Power+ or Greenworks units to drive implements that need real power, replacing small petrol engines. |
| [Charging robot (mobile charger)](charging_robot/README.md) | A robot on wheels that carries a large battery and charges working robots in the field, so they do not have to return to the shed. |
| [Wireless charging dock](wireless_charging_dock/README.md) | A fixed docking station at the field edge or in the shed where the robot drives up and charges, either with contacts or wirelessly. |

## Transport & General

| Idea | What it does |
|---|---|
| [Broom / sweeper](broom_sweeper/README.md) | Large front-mounted brush or electrically driven radial brush for surface cleaning, as an alternative to the front push blade. |
| [Seat & frame extension](seat_frame_extension/README.md) | Front or rear-mounted seat, with the option to widen the frame tubes at the sides. |
| [Dumper / power barrow](dumper_barrow/README.md) | Motorized wheelbarrow-style bin for transporting and dumping loose materials, also usable as a carrying aid or mini dumper. |
| [Tow hitch](tow_hitch/README.md) | Rear-mounted hitch for pulling trailers and other rolling equipment. |
| [Counterweights](counterweights/README.md) | Ballast weights to improve traction and vehicle balance for heavy tasks. |
| [Hydraulic pump](hydraulic_pump/README.md) | External hydraulic power source for applications where hydraulics are a better option than electricity. |
| [Three-point hitch](three_point_hitch/README.md) | Standard lifting system for attaching various agricultural implements. |
| [Small cabin](small_cabin/README.md) | Protective enclosure or housing for the operator. |
| [Speech speaker](speaker/README.md) | A speaker on the robot that can speak: warnings when the robot approaches, status messages for the operator, instructions in the field, and a way to speak to people near the robot. |
| [Crate and box carrier](crate_carrier/README.md) | Follows a picker or runs a set route and carries full crates from the plant rows to the field edge, so pickers do not have to walk with loads. |
| [Tool and material cart](tool_cart/README.md) | Carries tools, stakes, nets, and water along to where the work is, in the field or in a greenhouse. |
| [Bag trailer](bag_trailer/README.md) | Pulls a small trailer with bags of seed, fertilizer or feed to a fixed point in the field or yard. |

## Measuring & Sensors

| Idea | What it does |
|---|---|
| [Grass meter / crop scanner](grass_meter/README.md) | Measuring grass and crop height and health to create task maps for nitrogen or phosphate. |
| [Soil compaction meter](soil_compaction_meter/README.md) | Measuring and mapping soil density at specific data points. |
| [NIR sensor (NDVI & crop status)](nir_sensor/README.md) | Near-infrared sensor that measures the NDVI of the crop while driving. |
| [Yield estimator](yield_estimator/README.md) | Counts fruits, heads or plants with a camera and logs them per GPS position, so the harvest can be estimated and planned. |
| [Disease and pest scout](disease_scout/README.md) | Looks at the leaves close up, finds disease and pest damage early and stores a photo per plant with its position. |
| [Soil moisture sensor placer](soil_moisture_placer/README.md) | Places wireless soil moisture sensors at set GPS points, reads them out and picks them up again. |
| [Fence voltage meter](fence_voltage_meter/README.md) | Measures the voltage and current of the electric fence while driving along it and maps where the voltage drops. |
| [Windbreak and tree-row inspector](windbreak_inspector/README.md) | Drives along hedgerows, windbreaks and orchard rows and logs gaps, damage, dead trees and growth with a camera. |
| [Security camera patrol](security_patrol/README.md) | A mast with camera and thermal imaging that patrols the farm or field at night, reports intruders and keeps an eye on animals and equipment. |

## Cooperation & Swarm Operation

| Idea | What it does |
|---|---|
| [Drone combination](drone_combination/README.md) | The robot works together with a drone as a mobile base station. |
| [Swarm operation (multiple robots per field)](swarm_operation/README.md) | Several Bruut units work the same field as one swarm. |

## Crop & Soil

| Idea | What it does |
|---|---|
| [Soil sampler](soil_sampler/README.md) | Pushes a sampling probe into the soil at GPS points and keeps each sample in a numbered tube, so a field can be sampled on a grid without a person walking it. |
| [Stone picker](stone_picker/README.md) | Picks stones out of grassland or a seedbed and carries them to a bin, which is then emptied at the field edge. |
| [Molehill spreader](molehill_spreader/README.md) | Spreads molehills flat in grassland before mowing or overseeding, so the mower stays clean and the sward closes again. |
| [Mole and tunnel mapper](mole_mapper/README.md) | Finds and maps molehills (and with a probe, mole tunnels) so they can be treated or spread flat later. |
| [Cover crop undersower](cover_crop_undersower/README.md) | Sows a cover crop (green manure) in a crop that is already standing, between the rows. |
| [Mulch / foil layer](mulch_layer/README.md) | Lays mulch foil or paper along the rows, pressing the edges into the soil, to suppress weeds and keep moisture. |

## Weed & Crop Protection

| Idea | What it does |
|---|---|
| [UV-C light for mildew control](uv_mildew_light/README.md) | Drives UV-C lamps along the rows, shining between and over the plants at night, to suppress powdery mildew and other fungal diseases without chemicals. |
| [Laser or UV weed treatment](laser_weeder/README.md) | Kills individual weeds with a laser or a focused UV beam, without chemicals and without moving the soil. |
| [Electric weed control](electric_weeder/README.md) | Applies a high-voltage current through weeds with an electrode, between rows or in the row, to kill the plant including its root. |
| [Hot steam / hot foam weeder](steam_foam_weeder/README.md) | Kills weeds with hot steam or hot foam under a light hood, as an alternative to the flame weeder. |
| [Biological-control spreader](biocontrol_spreader/README.md) | Releases beneficial organisms (parasitic wasps, predatory mites, nematodes) at set points or lines in the crop. |
| [Pheromone trap service](pheromone_trap_service/README.md) | Visits insect traps and pheromone dispensers at the field edge: checks them with a camera, counts catches and swaps dispensers on schedule. |

## Livestock & Farm

| Idea | What it does |
|---|---|
| [Fence inspector](fence_inspector/README.md) | Drives along the fence, checks the electric fence, reports breaks and shorts and straightens leaning posts. |
| [Drinking trough check](drinker_check/README.md) | Visits drinking troughs, measures the water level, tops it up and reports dirt or damage with a camera. |
| [Manure scraper / slurry pusher](manure_scraper/README.md) | Scrapes or pushes manure and slurry on stable floors and walkways toward a drain or gutter. |
| [Bedding rake](bedding_rake/README.md) | Rakes and levels bedding (straw, sawdust, wood chips) in loose housing, stables and paddocks. |
| [Chicken house robot](chicken_house_robot/README.md) | Drives through a poultry house to turn the litter, collect floor eggs, and check birds and climate with sensors. |

Already worked out (in the folders next to this one): overseeder, liquid fertilizer applicator, feed pusher auger, disc brushes
(broom), dockweed drill (CNC weed driller), trencher, spot sprayer (atomising boom), in-row weeder (finger weeders), around-pole
mower (mowing arm), weed picker, irrigation (hose reel), field marker, mobile refiller, belt rake and weeds burner.
