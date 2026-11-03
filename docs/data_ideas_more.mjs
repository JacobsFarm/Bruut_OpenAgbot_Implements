// Extra implement ideas that came from brainstorming (not on the website list). Merged into `ideas` by data_ideas.mjs.
// Same fields as data_ideas.mjs. No numbers are given unless they come from an existing implement.

export const moreIdeas = [
  // ---------- Crop & soil ----------
  // ---------- Weed & crop protection ----------
  {
    slug: "speaker",
    name: "Speech speaker",
    category: "Transport & General",
    does: "A speaker on the robot that can speak: warnings when the robot approaches, status messages for the operator, instructions in the field, and a way to speak to people near the robot.",
    concept: "A weatherproof loudspeaker (or a pair, front and rear) on the top plate or mast with a small amplifier, fed by the robot computer. Text-to-speech for messages such as 'robot is turning', 'tank empty' or 'battery low'; optionally a microphone and a radio link so an operator can speak through the robot. Volume follows the distance to detected people.",
    reuse: "Top-plate pattern and mast mounting of the spot sprayer and the field marker; computer and radio link of the mobile refiller.",
    open: ["Speaker type, power and IP rating", "Languages and voice (text-to-speech engine, offline)", "Which events trigger which messages", "Noise limits near animals (cows, horses) and neighbours", "Microphone and two-way speech"],
  },
  {
    slug: "laser_weeder",
    name: "Laser or UV weed treatment",
    category: "Weed & Crop Protection",
    does: "Kills individual weeds with a laser or a focused UV beam, without chemicals and without moving the soil.",
    concept: "Camera finds the weeds (as in the spot sprayer), a galvo mirror aims the beam at the growing point. Needs a shroud against stray light and an interlock, and mostly works on small seedlings.",
    reuse: "Camera mast and detection of the spot sprayer; shroud and safety interlock ideas of the weeds burner.",
    open: ["Laser class and the safety rules that follow", "Power needed per weed and dwell time", "Working width versus galvo scan area", "Cost compared with a spot sprayer"],
  },
  {
    slug: "pheromone_trap_service",
    name: "Pheromone trap service",
    category: "Weed & Crop Protection",
    does: "Visits insect traps and pheromone dispensers at the field edge: checks them with a camera, counts catches and swaps dispensers on schedule.",
    concept: "A small arm or an XYZ stage that opens a trap, photographs the catch and replaces the lure. The robot stops at stored trap positions.",
    reuse: "XYZ stage and camera ideas of the field marker; trap positions kept like the marker's point list.",
    open: ["Trap types and how they open", "Catch counting by image", "Lure storage and replacement by the robot", "Frequency of visits"],
  },
  // ---------- Livestock & farm ----------
  {
    slug: "chicken_house_robot",
    name: "Chicken house robot",
    category: "Livestock & Farm",
    does: "Drives through a poultry house to turn the litter, collect floor eggs, and check birds and climate with sensors.",
    concept: "A small low variant with a litter-turning tool, a soft-brush egg collector and sensors for ammonia, temperature and humidity. Must be quiet and slow around the birds.",
    reuse: "Disc brush and drive from the brushes; camera and logging from the crop scanner idea.",
    open: ["Robot height and width for a poultry house", "Egg pick-up mechanism that does not break eggs", "Speed and noise near birds", "Cleaning and disinfection"],
  },
  // ---------- Measuring & sensors ----------
  {
    slug: "yield_estimator",
    name: "Yield estimator",
    category: "Measuring & Sensors",
    does: "Counts fruits, heads or plants with a camera and logs them per GPS position, so the harvest can be estimated and planned.",
    concept: "Cameras on a mast or in the row, an image model that counts and sizes the crop, and a yield map per row.",
    reuse: "Global-shutter camera and detection pipeline of the in-row weeder and the spot sprayer.",
    open: ["Crop to count (strawberry, broccoli, apple ...)", "Lighting at night versus day", "Count accuracy and counting error", "Output: map, report or plucking plan"],
  },
  // ---------- Transport & general ----------
  // ---------- Power & infrastructure ----------
  {
    slug: "charging_robot",
    name: "Charging robot (mobile charger)",
    category: "Power & Drive",
    does: "A robot on wheels that carries a large battery and charges working robots in the field, so they do not have to return to the shed.",
    concept: "A support robot like the mobile refiller, with a battery pack and a charging plug on a boom or at a fixed side. The working robot docks at a stop point, or charging happens in the headland turn.",
    reuse: "Docking approach, RTK antenna above the connection and procedure of the mobile refiller; battery pack idea.",
    open: ["Charging connector and automatic plug-in", "Charging power and time", "Battery capacity on the charger robot", "Wireless versus conductive contact"],
  },
  {
    slug: "security_patrol",
    name: "Security camera patrol",
    category: "Measuring & Sensors",
    does: "A mast with camera and thermal imaging that patrols the farm or field at night, reports intruders and keeps an eye on animals and equipment.",
    concept: "Mast with pan/tilt camera, thermal sensor and microphone; the robot drives a set route and alerts on movement. Combines with the speaker for warnings.",
    reuse: "Camera mast of the spot sprayer; speaker idea; solar roof for power.",
    open: ["Camera and thermal sensor choice", "Alert route to the farmer", "Privacy and rules for filming", "Night-time driving and obstacles"],
  },
  // ---------- Cleaning up (own ideas, moved from docs/implement ideas/) ----------
];
