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
];

export const ideas = [...websiteIdeas, ...moreIdeas.map((i) => ({ ...i, extra: true }))];
