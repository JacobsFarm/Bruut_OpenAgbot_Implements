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
  // ---------- Transport & general ----------
  // ---------- Measuring & sensors ----------
  // ---------- Cooperation & swarm ----------
];

export const ideas = [...websiteIdeas, ...moreIdeas.map((i) => ({ ...i, extra: true }))];
