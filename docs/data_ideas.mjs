// Implement ideas taken from the website (functionality's.json) that are not worked out in FreeCAD yet.
// Used by build_docs.mjs to write "implement ideas/<slug>/README.md" and the idea pages of the document.
// "does" = the function as described on the website; "concept" = first thoughts on how to build it on the Bruut;
// "reuse" = existing implements/parts to start from; "open" = what has to be decided or measured before building.

import { moreIdeas } from "./data_ideas_more.mjs";

const websiteIdeas = [
  // ---------- Soil cultivation & weed control ----------
  {
    slug: "drop_on_demand_boom",
    name: "Drop-on-demand boom (coarse droplets)",
    category: "Soil Cultivation & Weed Control",
    does: "Boom with individually controlled injectors that fire single coarse droplets on demand at low pressure. Every droplet is placed straight onto the weed, which practically eliminates drift and cuts chemical usage to a fraction of a conventional spray pass.",
    concept: "Same carrier as the spot sprayer (camera mast in front, boom behind), but with drop-on-demand valves instead of PWM flat-fan nozzles. Droplets are fired at the detected plant position, so the boom needs a finer position resolution along the boom than 250 mm.",
    reuse: "Camera mast, tank, pump, folding boom and control box of the spot sprayer (spotspray unit/boom).",
    open: ["Injector type, droplet size and firing rate", "Injector pitch along the boom", "Aiming accuracy at 0.5 m/s: time from camera to droplet", "Product types and viscosity the injectors can handle"],
  },
  // ---------- Spraying, fertilizing & irrigation ----------
  {
    slug: "irrigation_direct_pump",
    name: "Irrigation pump (direct pump)",
    category: "Spraying, Fertilizing & Irrigation",
    does: "Pumping water from ditches for local irrigation or crop spraying (website: Irrigation Pump). In the repo this is the not-yet-worked-out variant \"direct pump\" of the irrigation implement: pump on the robot, water from a tank, a ditch or a hydrant.",
    concept: "Instead of a petrol pump staying at the ditch, a pump on the robot feeds a hose or a short boom directly. Water comes from a tank on a trailer or a hydrant at the field edge.",
    reuse: "Reel, pinch rollers and outlets of irrigation/stationary + roller; the mobile refiller for tank supply.",
    open: ["Pump mass on the robot versus pump at the ditch", "Hose or boom as distributor", "Water supply: tank, hydrant or ditch", "Comparison of energy and capacity with the stationary-pump variant"],
  },
  {
    slug: "lime_spreader",
    name: "Lime spreader",
    category: "Spraying, Fertilizing & Irrigation",
    does: "Spreading lime to improve soil pH levels and structure.",
    concept: "Like the fertilizer spreader, but with a coarser metering roller or belt for powdery or granular lime and a covered outlet against dust. Large dose per hectare means large hopper volume, so reloading logistics matter.",
    reuse: "Fertilizer spreader hopper and metering; mobile refiller for reloading.",
    open: ["Dose per hectare and hopper volume", "Dust control and flow behaviour of damp lime", "Reloading: how often per hectare?"],
  },
  // ---------- Sowing & planting ----------
  {
    slug: "tray_setter",
    name: "Tray setter",
    category: "Sowing & Planting",
    does: "Front-mounted unit that takes seedlings out of the tray and sets them out at the right spacing.",
    concept: "A magazine of trays above the front beams, a gripper or pin-picker takes one seedling per cycle and plants it in a dibbled hole. Spacing by the robot's odometry; the robot stops or crawls per plant.",
    reuse: "XYZ stage idea of the field marker for positioning; camera and odometry of the in-row weeder.",
    open: ["Tray type and plug size", "Pick-and-place mechanism and cycle time", "Planting depth and soil closing", "Tray reloading, again from a refiller?"],
  },
  // ---------- Spreading & bedding ----------
  {
    slug: "straw_spreader",
    name: "Straw spreader",
    category: "Spreading & Bedding",
    does: "Evenly spreading straw, specially designed for use between vegetable rows.",
    concept: "A bale rack or bin with a shredding and metering unit that drops straw as a narrow strip between rows, for weed suppression and moisture. Width limited to the inter-row space of 375 mm rows (the wheels run in the inter-rows).",
    reuse: "Row geometry of the in-row weeder; metering from the sawdust spreader.",
    open: ["Bale handling or loose straw bin", "Strip width and thickness between rows", "Blocking of the metering unit by long straw"],
  },
  // ---------- Power & drive ----------
  {
    slug: "generator_engine",
    name: "Generator / engine",
    category: "Power & Drive",
    does: "Generator or combustion engine mounted between the frame as an auxiliary power source for extra electricity or mechanical power.",
    concept: "A small generator (range extender) on a vibration-damped frame between the beams, charging the 48 V bus. Exhaust and fuel placement are the main design problems.",
    reuse: "Frame mounting like the battery pack; the irrigation petrol pump is another engine use.",
    open: ["Generator power class and mass", "Vibration isolation and noise", "Fuel tank and exhaust placement", "Charging strategy with the battery"],
  },
  {
    slug: "heavy_duty_motors",
    name: "Heavy-duty electric motors",
    category: "Power & Drive",
    does: "Electric motors such as the Ego Power+ or Greenworks units to drive implements that need real power, replacing small petrol engines.",
    concept: "A standard interface plate for battery-powered garden-tool motors (their battery or the robot's bus via adapter), with a belt or shaft output to an implement. Gives a ready, cheap drive where a bought motor is easier than a custom 48 V BLDC.",
    reuse: "Motor plates and V-belt drives of the around-pole mower and the weed picker.",
    open: ["Which motors: brands, power, output shaft type", "Supply: own battery or the robot's 48 V", "Interface plate and quick-change mounting", "Protection against dust and water"],
  },
  // ---------- Transport & general ----------
  {
    slug: "broom_sweeper",
    name: "Broom / sweeper",
    category: "Transport & General",
    does: "Large front-mounted brush or electrically driven radial brush for surface cleaning, as an alternative to the front push blade.",
    concept: "A cylindrical (radial) brush across the front with a 48 V motor and height adjustment. The disc brushes already exist for the rear; a roller brush at the front sweeps material sideways or into a collector.",
    reuse: "Disc brushes (brushes/simple): motors, toolbar and mounting; push blade as the alternative.",
    open: ["Radial brush diameter, length and bristle type", "Sweep direction and collector", "Height and pressure control", "Dust control"],
  },
  {
    slug: "seat_frame_extension",
    name: "Seat & frame extension",
    category: "Transport & General",
    does: "Front or rear-mounted seat, with the option to widen the frame tubes at the sides.",
    concept: "A seat on a tube frame so a person can ride on the robot, and side extensions that widen the frame for wider implements. Needs a manual-drive mode and clear operator-safety rules.",
    reuse: "Toolbar and hanger design of the disc brushes; tube sizes from the robot.",
    open: ["Operator weight and the axle loads", "Controls and an emergency stop within reach", "Side-extension width versus stability", "Safety rules for a ridden robot"],
  },
  {
    slug: "hydraulic_pump",
    name: "Hydraulic pump",
    category: "Transport & General",
    does: "External hydraulic power source for applications where hydraulics are a better option than electricity.",
    concept: "A 48 V motor-pump set with a small tank and valve block, with quick couplings at the front and rear for hydraulic implements. Useful for high force at slow speed where linear actuators are too weak.",
    reuse: "Motor and mounting from the heavy-duty motors idea; hydraulics from the irrigation reel (which has its own).",
    open: ["Flow and pressure class", "Tank size and cooling", "Coupling standard for implements"],
  },
  {
    slug: "small_cabin",
    name: "Small cabin",
    category: "Transport & General",
    does: "Protective enclosure or housing for the operator.",
    concept: "A light cabin or canopy on the frame with a seat. Only meaningful together with the seat and frame extension.",
    reuse: "Seat & frame extension; top-plate pattern.",
    open: ["Weight and centre of gravity", "Entry and exit, visibility", "Rollover protection"],
  },
  // ---------- Measuring & sensors ----------
  // ---------- Cooperation & swarm ----------
  {
    slug: "drone_combination",
    name: "Drone combination",
    category: "Cooperation & Swarm Operation",
    does: "The robot works together with a drone as a mobile base station. The drone flies out from the platform, maps the plot from above and passes its imagery straight to the robot, which converts it into a driving and treatment plan. The drone charges and swaps batteries on the robot, so the pair can keep scouting and working alternately for a full day without anyone coming out to the field.",
    concept: "A landing platform on the robot's top plate with a charging contact or battery-swap mechanism, a data link to the robot computer and a way to align the drone on landing (RTK or visual markers). The plan generation reuses the task-map pipeline of the crop scanner.",
    reuse: "Top-plate pattern; solar panel roof as an alternative platform; task-map pipeline of the grass meter and NIR sensor.",
    open: ["Platform size and landing aid", "Charging versus battery swap", "Weather limits for flying and landing", "Regulations for autonomous flights"],
  },
  {
    slug: "swarm_operation",
    name: "Swarm operation (multiple robots per field)",
    category: "Cooperation & Swarm Operation",
    does: "Several Bruut units work the same field as one swarm. The job is split into sections, the robots divide the passes among themselves and keep each other informed of position, progress and battery state, so they never overlap or cross. Capacity scales simply with the number of units instead of with machine size, work continues when one unit drops out, and the light platforms keep soil compaction low.",
    concept: "Mostly software: a job planner that splits the field into passes, shared position and progress messages over a radio link, collision avoidance by reserved corridors, and hand-over of a pass when one unit drops out. The mobile refiller already works with a working robot, which is a two-unit special case.",
    reuse: "The pass pattern of the mobile refiller (simple) and the headland-turn animations of the agbot slim.",
    open: ["Communication link and message set", "Pass allocation and re-allocation", "Collision and crossing rules", "Charging and refilling logistics for many units"],
  },
];

export const ideas = [...websiteIdeas, ...moreIdeas.map((i) => ({ ...i, extra: true }))];
