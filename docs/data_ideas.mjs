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
    slug: "seat_frame_extension",
    name: "Seat & frame extension",
    category: "Transport & General",
    does: "Front or rear-mounted seat, with the option to widen the frame tubes at the sides.",
    concept: "A seat on a tube frame so a person can ride on the robot, and side extensions that widen the frame for wider implements. Needs a manual-drive mode and clear operator-safety rules.",
    reuse: "Toolbar and hanger design of the disc brushes; tube sizes from the robot.",
    open: ["Operator weight and the axle loads", "Controls and an emergency stop within reach", "Side-extension width versus stability", "Safety rules for a ridden robot"],
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
