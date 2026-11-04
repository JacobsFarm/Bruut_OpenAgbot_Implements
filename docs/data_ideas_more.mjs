// Extra implement ideas from brainstorming and from the robot catalogue (F:/side_projecten/Agbots_website). Merged into `ideas` by data_ideas.mjs.
// Same fields as data_ideas.mjs. No numbers are given unless they come from an existing implement.

const CATALOGUE = "Source: the robot catalogue (F:/side_projecten/Agbots_website): a function that other robots do and the Bruut has no implement or idea for yet.";

export const moreIdeas = [
  // ---------- Crop & soil ----------
  // ---------- Weed & crop protection ----------
  // ---------- Livestock & farm ----------
  // ---------- Measuring & sensors ----------
  // ---------- Transport & general ----------
  // ---------- Power & infrastructure ----------
  // ---------- Cleaning up (own ideas, moved from docs/implement ideas/) ----------

  // ---------- From the robot catalogue (Agbots_website): functions other robots do that the Bruut has no implement for ----------
  // Crop & soil
  // Sowing & planting
  // Weed & crop protection
  // Livestock & farm
  // Transport & general
  // Harvesting
  {
    slug: "asparagus_harvester",
    source: CATALOGUE,
    name: "Asparagus harvester",
    category: "Transport & General",
    does: "Finds white asparagus spears that push up through the ridge, cuts them below the surface and lifts them out. Seen on the AVL Compact S9000 and the Inaho harvesting robot.",
    concept: "A module that straddles one ridge, with a camera or a sensor that detects spear tips breaking the plastic or soil, a narrow cutting and gripping tool on a vertical axis that goes into the ridge, and a crate on the robot. The robot creeps along the ridge.",
    reuse: "Vertical axis and drill head layout of the dockweed drill; camera hood of the potato disease scout; crate carrier deck for the harvested spears.",
    open: ["Detecting spears before they reach the light", "Cut depth and closing the ridge again", "Cycle time per spear versus the robot's speed", "Working under the plastic film"],
  },
];
