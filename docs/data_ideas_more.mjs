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
  {
    slug: "power_harrow",
    source: CATALOGUE,
    name: "Power harrow / rotary tiller",
    category: "Crop & Soil",
    does: "Driven tines or blades work the top soil into a seedbed, or loosen the soil between vines and trees. Seen on vineyard and orchard robots (Slopehelper power harrow, Pellenc RX-20, Naïo Ted) and small electric tractors.",
    concept: "A narrow rear-mounted rotor with vertical tines (power harrow) or L-blades (rotary tiller) and a crumbler roller that sets the depth, driven by a geared electric motor. Lifted by a linear actuator like the grassland harrow. Works in strips, so the power stays within what the robot can supply.",
    reuse: "Rear mount and lift of the grassland harrow; gearmotor and chain drive of the dockweed drill; power supply from the battery pack or hybrid range extender.",
    open: ["Working width versus available power and traction", "Rotor speed, tine type and working depth", "Draft and reaction forces on a light robot", "Stones: overload protection of the rotor"],
  },
  {
    slug: "flail_mulcher",
    source: CATALOGUE,
    name: "Flail mulcher",
    category: "Crop & Soil",
    does: "Shreds prunings, tough grass, stubble and crop residues between rows instead of only cutting them. Seen on orchard and vineyard robots (Slopehelper drum mulcher, XAG RM80, Bonsai OMC AR500).",
    concept: "A rear-mounted flail rotor with Y-knives or hammers in a closed housing with a rear roller that sets the cutting height. Belt-driven from a strong electric motor. A swing-out side section could also reach under the tree row.",
    reuse: "Housing, belt drive and height setting of the mower unit (mowing deck); motor options of the heavy-duty electric motors; swing-out arm of the around-pole fence mower.",
    open: ["Power needed for prunings versus grass", "Rotor speed, knife type and stone throw protection", "Width that fits the row spacing", "Mass on the rear and balance with counterweights"],
  },
  // Sowing & planting
  // Weed & crop protection
  {
    slug: "orchard_air_sprayer",
    source: CATALOGUE,
    name: "Air-assisted orchard sprayer",
    category: "Spraying, Fertilizing & Irrigation",
    does: "Sprays the canopy of fruit trees, vines or hedges with an air stream that carries the droplets into the leaves, and switches nozzles off where there is no canopy. Seen on GUSS, LJ-Tech S500Pro, MQ Agritech M200 and Smart Apply.",
    concept: "A tank on the upper beams, an axial fan at the rear with a ring of nozzles, or two vertical towers with cross-flow fans. A lidar or camera measures the canopy per height section and switches each nozzle section on and off.",
    reuse: "Tank, pump and control box of the spot sprayer; nozzle switching of the drop-on-demand boom; canopy sensing of the windbreak and tree-row inspector.",
    open: ["Fan power and air volume versus battery", "Tank size versus mass and the robot's payload", "Drift: tower or tunnel version, canopy sensing", "Height of the trees to reach"],
  },
  // Livestock & farm
  {
    slug: "feed_mixer_wagon",
    source: CATALOGUE,
    name: "Feed mixing and distribution wagon",
    category: "Livestock & Farm",
    does: "Loads, weighs and mixes a ration and lays it along the feed fence several times a day. Seen on the Lely Vector, DeLaval OptiWagon, GEA DairyFeed F4500, Kuhn Aura and Trioliet Triomatic.",
    concept: "A small mixing bin with a vertical auger on the upper beams and a discharge door or cross conveyor at the side. Loads at a feed kitchen (loaded by hand or from a hopper), weighs on load cells and drives along the feed fence on the same route as the feed pusher.",
    reuse: "Auger and side discharge of the feed pusher auger; load cell weighing of the mobile refiller; route along the feed fence of the feed pusher.",
    open: ["Bin volume versus mass and stability", "Mixing power of a vertical auger on a battery", "Loading: feed kitchen, hopper or by hand", "Feeding small groups (calves, young stock) versus the whole herd"],
  },
  {
    slug: "fresh_grass_harvester",
    source: CATALOGUE,
    name: "Fresh grass harvester (zero grazing)",
    category: "Livestock & Farm",
    does: "Mows fresh grass in the field, loads it and brings it to the feed fence, several times a day. Seen on the Lely Exos.",
    concept: "A front sickle bar or disc mower, a short pick-up belt or auger that lifts the swath into a container on the robot, and an unloading floor or tipping container at the feed fence. Small loads, many trips.",
    reuse: "Sickle bar mower; belt rake for the pick-up; dumper barrow or bag trailer for the container; feed pusher route at the barn.",
    open: ["Load per trip versus mass and the field's bearing capacity", "Pick-up of fresh, heavy grass", "Unloading at the feed fence", "Trips per day for a given number of cows"],
  },
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
