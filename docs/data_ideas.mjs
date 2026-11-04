// Implement ideas taken from the website (functionality's.json) that are not worked out in FreeCAD yet.
// Used by build_docs.mjs to write "implement ideas/<slug>/README.md" and the idea pages of the document.
// "does" = the function as described on the website; "concept" = first thoughts on how to build it on the Bruut;
// "reuse" = existing implements/parts to start from; "open" = what has to be decided or measured before building.

import { moreIdeas } from "./data_ideas_more.mjs";

const websiteIdeas = [
  // ---------- Soil cultivation & weed control ----------
  // ---------- Spraying, fertilizing & irrigation ----------
  // ---------- Sowing & planting ----------
  // ---------- Spreading & bedding ----------
  // ---------- Power & drive ----------
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
  // ---------- Measuring & sensors ----------
  // ---------- Cooperation & swarm ----------
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
