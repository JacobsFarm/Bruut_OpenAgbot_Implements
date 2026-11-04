// Extra implement ideas that came from brainstorming (not on the website list). Merged into `ideas` by data_ideas.mjs.
// Same fields as data_ideas.mjs. No numbers are given unless they come from an existing implement.

export const moreIdeas = [
  // ---------- Crop & soil ----------
  // ---------- Weed & crop protection ----------
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
