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
  {
    slug: "arena_leveller",
    source: CATALOGUE,
    name: "Riding arena leveller",
    category: "Crop & Soil",
    does: "Levels and loosens the footing of a horse riding arena at night, so it is ready every morning. Seen on Fraunhofer ARA (tracked arena robot).",
    concept: "A rear tool frame with a row of loosening tines, a levelling board and a small roller or mesh, driven over the arena in a fixed RTK or lidar pattern (indoor arenas have no RTK). The depth and board height are set by a linear actuator.",
    reuse: "Levelling board, tines and lift of the grassland harrow; push blade for moving sand back from the edges; lidar ideas of the chicken house robot for indoor navigation.",
    open: ["Navigation in an indoor arena without RTK", "Footing types (sand, sand with fibres, wood chips) and the depth to work", "Edges and corners along the arena wall", "Watering the footing at the same time"],
  },
  // Sowing & planting
  {
    slug: "precision_seeder",
    source: CATALOGUE,
    name: "Precision seeder (single seed)",
    category: "Sowing & Planting",
    does: "Sows row crops (beet, maize, vegetables) seed by seed and records the RTK position of every seed, so a later weeding pass can hoe around each plant before it is even visible. Seen on FarmDroid FD20 and Fendt Xaver.",
    concept: "Two to four seeding units on a toolbar behind the robot, each with a small hopper, a vacuum or finger metering disc driven by its own stepper, a coulter and a press wheel. The controller logs each seed drop with the RTK position and time.",
    reuse: "Toolbar and parallelogram units of the inter-row hoe; metering motor and hopper of the overseeder; position logging and odometry timing of the cauliflower applicator; in-row weeder for the follow-up pass.",
    open: ["Metering principle (vacuum, finger, cell wheel) per crop", "Accuracy of the logged seed position at the working speed", "Depth control and soil closing", "Row spacing and number of units per pass"],
  },
  // Weed & crop protection
  {
    slug: "insect_vacuum",
    source: CATALOGUE,
    name: "Insect vacuum / beetle catcher",
    category: "Weed & Crop Protection",
    does: "Sucks or knocks pest insects off the crop instead of spraying: lygus bugs in strawberries, Colorado beetles and larvae in potatoes. Seen on the Agrobot Bug Vacuum and the Fieldworkers Colorado beetle catcher.",
    concept: "A hood over one or two rows with an air flow that pulls the insects off the plants into a catch box with a fine screen (or a fan that kills them), with flexible strips that shake the plants. For beetles: brushes or beaters that knock them into a tray below the canopy.",
    reuse: "Fan, hose and bin of the debris vacuum; row hood and strip curtains of the potato disease scout.",
    open: ["Air speed that lifts the insects without damaging the crop or flowers", "Catch box, killing method and emptying", "Fan power and battery use per hectare", "Effect on beneficial insects"],
  },
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
    slug: "manure_vacuum",
    source: CATALOGUE,
    name: "Manure vacuum collector",
    category: "Livestock & Farm",
    does: "Sucks fresh manure from a solid barn floor into a tank and empties it at a drain or pit, instead of pushing it. Seen on the Lely Discovery Collector, Hetwin Avenger Pickup, Schauer Enro Collect and JOZ Barn-E.",
    concept: "A low tank on the upper beams, a vacuum pump and a wide suction nozzle with a rubber squeegee at the front. The robot drives a fixed route through the barn and drives to a dump point, where a valve at the bottom of the tank opens.",
    reuse: "Nozzle and fan or pump layout of the debris vacuum; route driving and squeegee of the push blade (slurry scraping); mobile refiller docking for the dump point.",
    open: ["Vacuum pump type that handles slurry with straw", "Tank volume versus mass and the floor's grip", "Navigation in a barn with cows (no RTK under the roof)", "Emptying point and cleaning"],
  },
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
    slug: "concentrate_dispenser",
    source: CATALOGUE,
    name: "Concentrate dispenser on the feed table",
    category: "Livestock & Farm",
    does: "Doses concentrates or minerals on the feed along the fence while pushing feed, to draw cows to the fence. Seen on the Euromilk EM Lizard and Schauer Faro.",
    concept: "One or two small hoppers on the feed pusher with a metering auger driven by a stepper, dropping a thin line on the pushed feed. Dose per metre or per feeding place is set in the route.",
    reuse: "Feed pusher auger (carrier and route); metering auger and hopper of the overseeder or fertilizer spreader.",
    open: ["Hopper size and filling", "Dose accuracy per metre at the driving speed", "Moisture and caking of the concentrate", "Link with the herd management system"],
  },
  {
    slug: "calf_milk_taxi",
    source: CATALOGUE,
    name: "Calf milk taxi",
    category: "Livestock & Farm",
    does: "Brings warm milk to the calves in their hutches or pens and doses each calf's portion, so the farmer does not have to carry buckets. Inspired by the automatic calf feeders such as the Lely Calm.",
    concept: "An insulated milk tank with a heater and a stirrer on the upper beams, a pump and a dosing nozzle on a short arm at the side. The robot drives along the hutches on a stored route and stops at each one to dose the set amount into the bucket.",
    reuse: "Tank and pump of the liquid fertilizer applicator; flow dosing of the mobile refiller; stop-and-dose positioning of the field marker.",
    open: ["Hygiene: cleaning the tank, pump and hoses after every round", "Keeping the milk at drinking temperature", "Dose per calf and identifying the calf or hutch", "Mixing milk powder on board or filling from a calf milk kitchen"],
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
  {
    slug: "barn_pressure_washer",
    source: CATALOGUE,
    name: "Barn pressure washer",
    category: "Livestock & Farm",
    does: "Cleans pens, walls and floors with a high-pressure water jet when the barn is empty, around the clock. Seen on the Envirologic Evo Cleaner (pig barns).",
    concept: "A pressure washer pump on board (water by hose or from a tank) and a nozzle on a small arm with two axes that follows a taught pattern per pen. The robot moves from pen to pen on a stored route.",
    reuse: "Arm and axes of the weed picker or field marker; tank and pump of the mobile refiller; motor options of the heavy-duty electric motors.",
    open: ["Water supply: hose reel or tank", "Waterproofing of the robot and its electronics", "Arm reach for walls and partitions", "Navigation in a wet, empty barn"],
  },
  // Transport & general
  {
    slug: "landscaping_tools",
    source: CATALOGUE,
    name: "Hedge trimmer, edger and leaf blower",
    category: "Transport & General",
    does: "Trims hedges, cuts lawn edges along paths and blows leaves into a windrow, without a gardener walking along. Seen on the Electric Sheep Verdie.",
    concept: "A side arm with two axes that carries a hedge trimmer bar, swapped for an edger disc at ground level, and a separate blower nozzle at the front. The robot follows the hedge or path edge with a camera or a stored RTK line.",
    reuse: "Arm and swing-out of the around-pole fence mower; following a line of plants of the windbreak and tree-row inspector; garden-tool motors of the heavy-duty electric motors; broom sweeper for picking up the windrow.",
    open: ["Arm reach and height for hedges", "Detecting the hedge face and the path edge", "Safety of the trimmer bar near people", "Blower power and noise"],
  },
  {
    slug: "line_marker",
    source: CATALOGUE,
    name: "Sports field line marker",
    category: "Transport & General",
    does: "Paints the lines of sports fields (football, hockey) from a stored layout, with only a few minutes of setup. Seen on the Turf Tank Two.",
    concept: "A paint tank on the robot, a small pump and a spray nozzle with a shield, mounted at a known point under the robot. The robot drives the lines on RTK; the nozzle switches on and off at the ends. A field layout is placed on two measured corners, like the AB line.",
    reuse: "Paint marking and point list of the field marker; pump and nozzle of the spot sprayer; RTK antenna offset of the robot.",
    open: ["Line accuracy at the nozzle (antenna offset, tilt)", "Paint type, nozzle and line width", "Drawing curves (centre circle, penalty arc)", "Field templates and the user interface"],
  },
  {
    slug: "weeding_bed",
    source: CATALOGUE,
    name: "Weeding bed (lying platform)",
    category: "Transport & General",
    does: "Carries one or more workers lying face down just above the crop, so they can weed or harvest by hand without bending, while the robot creeps along the bed. Seen on the Fieldworkers Weed-E.",
    concept: "A wide frame on the upper beams with padded lying boards and a sun canopy, the people facing down over the rows. The robot drives very slowly in a straight line; a hand button on each board stops or starts it.",
    reuse: "Frame extensions, seat and canopy of the seat, canopy and frame extension; solar canopy; stop button and slow driving of the crate carrier (following a picker).",
    open: ["Number of workers and frame width over the beds", "Speed control by the workers and safety stops", "Comfort: height above the crop, padding, shade", "Mass of the people versus the robot's payload"],
  },
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
