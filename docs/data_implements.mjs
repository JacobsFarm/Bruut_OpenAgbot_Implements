// Worked-out implements, taken from the READMEs in this repository.
// Image paths are relative to the repository root. hero = main image of the page.

export const implementsList = [
  {
    name: "Overseeder", folder: "overseeder", category: "Sowing & Planting",
    summary: "Grassland slit seeder. 1 m modules with 8 rows at 125 mm and coupling flanges. A thin disc cuts a 15 mm slot, the seed is placed about 12 mm deep and a sprung press wheel closes the slot. Every row follows the ground on its own arm; two gas springs push the floating lift frame down with robot weight.",
    variants: [
      { name: "Simple", folder: "overseeder/simple", hero: "overseeder/simple/previews/12_work_iso_with_robot.png",
        text: "Angled single disc (7°, Ø300 × 3) with a seed boot in its lee and a depth ring. Gravity-fed seed hopper with a compartment for grass (41 l) and one for fine seed (18 l), each with its own cam roller and a motor that follows the driving speed. Built on the headstock and lift frame of the simple applicator v2.",
        facts: ["8 rows at 125 mm = 1 m per module", "Draft force approx. 335 N (normal)", "Depth within ±3 mm: 94 %", "About €1,675 in parts"] },
      { name: "Advanced", folder: "overseeder/advanced", hero: "overseeder/advanced/previews/12_work_iso_with_robot.png",
        text: "Parallel linkage so the toolbar stays parallel, straight Ø300 × 3 disc with depth rings on both sides, a curved seed coulter directly behind the disc and a press wheel in a fork. Air seeder (62 + 17 l hopper, 12 V fan) on a frame above the rear axle blows the seed through 8 hoses to the coulters.",
        facts: ["8 rows at 125 mm = 1 m per module", "2 gas springs in the slotted hole", "Depth within ±3 mm: 98 %", "About €2,280 in parts"] },
    ] },
  {
    name: "Liquid fertilizer applicator", folder: "liquid fertilizer applicator", category: "Spraying, Fertilizing & Irrigation",
    summary: "Injects liquid fertilizer (such as RENURE) just under the sward, without mist or drift. Five injection elements at 200 mm; each element follows the ground on its own arm.",
    variants: [
      { name: "Simple", folder: "liquid fertilizer applicator/simple", hero: "liquid fertilizer applicator/simple/previews/11_work_iso_with_robot.png",
        text: "Cheap and robust: 5 fixed injection knives with a stainless steel tube, two wheelbarrow wheels as depth wheels, a lift frame with a single low pivot and one cheap linear actuator, a 12 V diaphragm pump with fixed regulator and orifice plates. Only flat bar, tube and standard parts.",
        facts: ["5 knives at 200 mm", "12 V diaphragm pump, dose depends on speed", "About €600 in materials"] },
      { name: "Simple v2", folder: "liquid fertilizer applicator/simple_v2", hero: "liquid fertilizer applicator/simple_v2/previews/11_work_iso_with_robot.png",
        text: "Simple version plus a flat coulter disc Ø300 in front of each knife, cutting 45 mm deep; the knife runs 14 mm behind it in the same plane. Costs 26 kg extra on the lift frame (70 kg), a 1500 N actuator and up to 50 kg of ballast in hard sward.",
        facts: ["Disc + knife per row", "Lift frame 70 kg", "About €915 in materials"] },
      { name: "Advanced", folder: "liquid fertilizer applicator/advanced", hero: "liquid fertilizer applicator/advanced/previews/11_work_iso_with_robot.png",
        text: "Disc, knife, tube and press wheel per element on spring arms; a 5-channel peristaltic pump driven by a worm-gear motor whose speed follows the robot's driving speed, and an electrically lifted parallel linkage that floats while working (slotted hole). No ground wheel.",
        facts: ["5 elements at 200 mm", "89–1,316 l/ha, 18 settings", "Includes ground-following animation"] },
    ] },
  {
    name: "Feed pusher auger", folder: "feed pusher auger", category: "Transport & General",
    summary: "Pushes feed back to the feed fence. Sits at the back of the robot; the robot drives with the auger first. The auger picks up the pushed-away feed and carries it sideways to the fence.",
    variants: [
      { name: "Simple", folder: "feed pusher auger/simple", hero: "feed pusher auger/simple/render_v2_rear.png",
        text: "Cheap version from flat plate and sectional flights; DXF files for the side plate and the flight ring.",
        facts: ["Flat plate + sectional flights", "STEP and DXF files"] },
      { name: "Advanced", folder: "feed pusher auger/advanced", hero: "feed pusher auger/advanced/previews/9_on_robot_iso.png",
        text: "Ø320 auger under a 2 mm folded hood with 4 bends. Foot-mounted gearmotor on top of the hood, 08B-1 chain with tensioner along the left side plate. Mounted with 4 arms on the rear flange holes of the rear wheel modules. Open discharge end. Includes a feed-transport model and a force animation.",
        facts: ["24 V gearmotor with chain drive", "Open discharge end", "Feed-transport model and force animation"] },
    ] },
  {
    name: "Disc brushes", folder: "brushes", category: "Transport & General",
    summary: "Sweeper disc brushes for loose material on concrete. Each brush on its own 48 V worm gearmotor (NMRV063, 550 W); reversing the motors makes a windrow in the middle or spreads material wide. Mounted on an 80 × 80 toolbar under the rear beams with U-bolts. Includes an animation with a particle model.",
    variants: [
      { name: "Double 750", folder: "brushes/simple", hero: "brushes/simple/previews/1_double_750_iso_on_robot.png",
        text: "Two Ø750 brushes (standard). Working width 1.50 m with brushes touching to 1.70 m with 200 mm between them. Spread wide or make a windrow.",
        facts: ["2 × Ø750", "1.50–1.70 m"] },
      { name: "Double 650", folder: "brushes/simple", hero: "brushes/simple/previews/2_double_650_iso_on_robot.png",
        text: "Two Ø650 brushes: the same job, narrower and lighter.",
        facts: ["2 × Ø650", "1.30–1.50 m"] },
      { name: "Single 850", folder: "brushes/simple", hero: "brushes/simple/previews/3_single_850_iso_on_robot.png",
        text: "One Ø850 brush covering the robot's own width, sweeping the strip in front of the robot to one side.",
        facts: ["1 × Ø850", "0.85 m"] },
    ] },
  {
    name: "Dockweed drill", folder: "dockweed drill", category: "Soil Cultivation & Weed Control",
    summary: "Finds a dock plant (broad-leaved dock) and mills out its root on a CNC gantry, chemical-free.",
    variants: [
      { name: "One design", folder: "dockweed drill", hero: "dockweed drill/render_front_left.png",
        text: "Dock removal mill on a two-axis CNC gantry. Renders, animations, DXF and STEP files. An older single-script design (dockweed_design.py).",
        facts: ["Animation and close-up GIFs", "DXF and STEP files"] },
    ] },
  {
    name: "Trencher", folder: "trencher", category: "Soil Cultivation & Weed Control",
    summary: "Wheel trencher for cutting narrow trenches.",
    variants: [
      { name: "One design", folder: "trencher", hero: "trencher/render_left_rear.png",
        text: "Wheel trencher mounted on the Bruut. Renders and STEP export. An older single-script design (trencher_design.py).",
        facts: ["Renders and STEP export"] },
    ] },
  {
    name: "Field marker", folder: "marker", category: "Measuring & Sensors",
    summary: "Stakes out points from a coordinate list (piles, posts, planting positions, plot corners). The robot stops roughly behind the point; an XYZ stage puts a spray-paint head exactly on it.",
    variants: [
      { name: "Simple", folder: "marker/simple", hero: "marker/simple/previews/1_work_iso_on_robot.png",
        text: "Three bought linear modules: X 800 mm belt module, Y 200 mm and Z 300 mm ball screws. Paint head: upside-down marking-spray can in a PVC drain pipe pushed by a servo; sprung PVC 110 shroud with an inductive sensor finds the ground. Second GNSS antenna on a mast straight above the nozzle.",
        facts: ["Robot may stop ±100 mm off", "NEMA 23 closed-loop motors", "About €1,450 in parts", "Concept lists flag, peg, punch and soil-probe heads"] },
    ] },
  {
    name: "Mobile refiller", folder: "mobile refiller", category: "Spraying, Fertilizing & Irrigation",
    summary: "Support robot that brings liquid (and in concept seed, granular fertilizer, water, batteries) to the working robots, so they never leave the field.",
    variants: [
      { name: "Liquid", folder: "mobile refiller/liquid", hero: "mobile refiller/liquid/previews/1_iso_refiller_with_trailer.png",
        text: "268 l T-shaped tank with a pump below the liquid level, a slewing boom with a trolley and a spout, an RTK antenna on the spout and a camera for confirmation, and a powered trailer of 246 l (6 driven wheels). Tops up the working robot in the straight reverse of its headland turn while both drive.",
        facts: ["About 25 l per turn, ≈ 3 s standstill", "Pump 150 l/min", "About €6,000 in parts"] },
      { name: "Simple (IBC)", folder: "mobile refiller/simple", hero: "mobile refiller/simple/previews/1_iso_refiller_ibc.png",
        text: "A standard 1000 l IBC set on with pallet forks, pump under the IBC, a fixed mast with a hanging hose and the RTK antenna above the nozzle. The working robot skips passes so every turn is a U-turn; the refiller stands inside the turn and the robot stops ≈ 13 s under the nozzle; 1 m further per refill.",
        facts: ["Standard 1000 l IBC", "No boom, trailer or camera", "About €1,650 in parts"] },
      { name: "Stationary: IBC trailer", folder: "mobile refiller/stationary/ibc_trailer", hero: "mobile refiller/stationary/ibc_trailer/previews/1_1_iso_1ibc.png",
        text: "Single-axle trailer for one or two 1000 l IBCs, parked on the headland by a tractor. Control box (pump, battery, controller, RTK receiver, radio) on the A-frame drawbar and a mast with swinging arm, drop pipe, drip-stop nozzle and RTK antenna straight above the nozzle.",
        facts: ["1 or 2 IBCs", "120 l per visit", "The working robot drives to it"] },
      { name: "Stationary: flat wagon", folder: "mobile refiller/stationary/flat_wagon", hero: "mobile refiller/stationary/flat_wagon/previews/1_iso_flat_wagon.png",
        text: "Standard two-axle flat bale wagon (8 × 2.48 m) with 6 IBCs, two across. Only two holes in the deck and two box hangers; suction header along the deck, control box under the deck, mast on a skid at the rear left corner.",
        facts: ["6 IBCs", "Pump 0.8 m below the IBC bottoms", "Wagon itself unchanged"] },
      { name: "Stationary: three-point frame", folder: "mobile refiller/stationary/three_point", hero: "mobile refiller/stationary/three_point/previews/1_iso_three_point.png",
        text: "Welded frame on four legs for one 1000 l IBC, picked up on a category 2 three-point linkage and set down on the headland. The mast doubles as the hitch tower; control box under the platform.",
        facts: ["1 IBC", "Category 2 three-point", "Pump 535 mm below the IBC bottom"] },
    ] },
  {
    name: "Around-pole fence mower", folder: "around_pole_mower", category: "Mowing",
    summary: "Mows the strip under an electric fence and goes around the posts by itself.",
    variants: [
      { name: "Simple", folder: "around_pole_mower/simple", hero: "around_pole_mower/simple/previews/1_iso_on_robot.png",
        text: "Trailing swing arm on a post behind the right rear wheel, held on a rest stop by a spring. A Ø400 nylon-string head under a PE-pipe guard ring slides around each post. 48 V BLDC motor at the root of the arm, V-belt inside the arm to a bought lawn-tractor deck spindle; head 182 mm high on an HDPE skid. No sensor, no actuator, no software.",
        facts: ["≈ 615 W at 0.5 m/s", "1.8 km of fence per hour", "About €575 in parts", "Arm dynamics and animation with grass"] },
    ] },
  {
    name: "Weed picker", folder: "weed picker", category: "Mowing",
    summary: "Tops thistles, ragwort and dock above the grass and gathers them in one windrow, no bin. Ragwort in particular has to leave the field.",
    variants: [
      { name: "Mowing deck", folder: "weed picker/mowing_deck", hero: "weed picker/mowing_deck/previews/1_iso_on_robot.png",
        text: "Twin-rotor mowing deck in front of the robot: two rotors with free-swinging blades (Ø510, 990 mm cut) turn inwards and throw the chopped weed out of a centre opening as a windrow ≈ 320 mm wide. Each rotor: 48 V BLDC motor on a lawn-tractor deck spindle; the left rotor runs 24 mm higher. Cut height 100–400 mm from a 4000 N actuator on a parallel linkage, with a float link for humps.",
        facts: ["≈ 1 kW at 0.5 m/s", "82 kg (rear counterweight advised)", "About €1,040 in parts", "Animation in a weed patch"] },
    ] },
  {
    name: "Sickle bar mower", folder: "sickle bar mower", category: "Mowing",
    summary: "Mows grass with double-knife cutter bars instead of rotating blades: a clean cut at low power, the grass left lying in a swath to dry. The bars follow the ground on their shoes.",
    variants: [
      { name: "Triple", folder: "sickle bar mower/triple", hero: "sickle bar mower/triple/previews/1_work_iso_on_robot.png",
        text: "Three double-knife bars: 1.25 m in front of the robot on a parallel linkage with a float link and a roll pin, and two 1.0 m wings in the middle of the frame on a mid frame under the top beams. Each bar: upper and lower knife (50 mm pitch, stroke 50, 600 rpm), a crank gearbox with two cranks 180° apart so the knife forces cancel, and a 48 V 1000 W BLDC motor. The wings fold up with a 4000 N actuator each; the anchor slides in a slot so they float with the ground.",
        facts: ["3.25 m working width", "≈ 2.2 kW mowing at 1 m/s, 1.0 ha/h", "210 kg, 163 kg on the shoes while mowing", "About €3,200 in parts"] },
    ] },
  {
    name: "Irrigation", folder: "irrigation", category: "Spraying, Fertilizing & Irrigation",
    summary: "Irrigates grassland by flooding at low pressure from a pump at the ditch: little energy, no wind drift, no evaporation in the air.",
    variants: [
      { name: "Stationary pump + hose reel", folder: "irrigation/stationary + roller", hero: "irrigation/stationary + roller/previews/1_full_reel_iso_on_robot.png",
        text: "The robot carries a reel with 150 m of 3\" lay-flat hose, lays it out empty, the petrol pump at the ditch floods a 4 m strip (outlets every 2 m), the hose runs empty and the robot winds it up again. Pinch rollers keep the reel dry and squeeze the last water out.",
        facts: ["7.4 m³/h at 0.17 bar, CU ≈ 99 %", "122 min per 500 m² strip at 25 mm", "146 kg, about €1,900 in parts"] },
    ] },
  {
    name: "Spot sprayer", folder: "spotspray unit", category: "Soil Cultivation & Weed Control",
    summary: "Sprays weeds plant by plant instead of the whole field. A camera in front finds the weeds; the boom behind opens only the nozzles above a plant.",
    variants: [
      { name: "Folding 3.75 m boom", folder: "spotspray unit/boom", hero: "spotspray unit/boom/previews/1_work_iso_on_robot.png",
        text: "Wide-angle global-shutter camera on a mast (1.48 m, 55° down) sees the whole strip from 1.8 m ahead; 2.65 s later 15 PWM nozzles at 250 mm on a stainless pipe open above the plant. Centre section 1.25 m and two 1.25 m wings that fold up in 3.2 s with a 24 V actuator each, also in the field. 120 l tank and diaphragm pump on the robot.",
        facts: ["≈ 20 l/ha at 5 % weed cover, 1.1 ha/h", "91 kg", "About €3,580 in parts", "Animation with docks and a fence post"] },
    ] },
  {
    name: "In-row weeder", folder: "in row weeder", category: "Soil Cultivation & Weed Control",
    summary: "Hoes inside two rows of broccoli (375 mm apart, wheels in the inter-rows). Camera under the front beams finds the plants 0.84 s ahead; knives swing out around each plant.",
    variants: [
      { name: "Finger, 2 rows", folder: "in row weeder/finger", hero: "in row weeder/finger/previews/1_work_iso_on_robot.png",
        text: "Two row units under the belly on parallelograms with gauge wheels in the robot's wheel track. A NEMA 23 closed-loop stepper with a 10:1 gearbox swings a 220 mm arm with a spring-steel finger and a flat knife 20 mm deep. Out in 98 ms, back in 148 ms; never closer than 50 mm to a stem.",
        facts: ["0.5 m/s, 6,400 plants/h", "55 kg", "About €2,240 in parts"] },
      { name: "Double arms", folder: "in row weeder/double_arm", hero: "in row weeder/double_arm/previews/1_work_iso_on_robot.png",
        text: "Two knives per row (4 steppers) that open to both sides of each plant and close behind it, timed by the real distance to the stem. Each knife moves only 78 mm: out in 89 ms, back in 118 ms.",
        facts: ["90 % of the row band outside the safe zones hoed", "68 kg", "About €2,820 in parts"] },
    ] },
  {
    name: "Belt rake", folder: "bandrake", category: "Soil Cultivation & Weed Control",
    summary: "Band rake in front of the robot: a rubber belt with 15 tine bars around two drums (1.52 m working width). Combs weed seedlings out of nursery beds between young trees or rakes moss and thatch out of grassland into one windrow.",
    variants: [
      { name: "Electric", folder: "bandrake/electric", hero: "bandrake/electric/previews/1_work_iso_on_robot.png",
        text: "48 V 750 W gearmotor with a 20:1 planetary gearbox on the right drum. Two swivel castors on 24 V actuators carry the 110 kg rake, set the depth and lift it 100 mm for the headland; a free parallelogram pushes it.",
        facts: ["Comb mode 0.6 m/s, rake mode 1.2 m/s, 0.49 ha/h", "About €2,380 in parts", "Tine forces and animation"] },
    ] },
  {
    name: "Weeds burner (flame weeder)", folder: "weeds burner", category: "Soil Cultivation & Weed Control",
    summary: "Pre-emergence flame weeder for freshly sown beds (carrot, onion, beetroot, parsnip): kills the emerged seedlings without moving the soil.",
    variants: [
      { name: "Propane hood", folder: "weeds burner/propane_hood", hero: "weeds burner/propane_hood/previews/1_work_iso_on_robot.png",
        text: "Insulated 1.5 × 0.8 m hood behind the robot with 6 flat-flame burners (13 kg/h, 167 kW). Two 18 kg forklift cylinders with liquid withdrawal on the robot, a vaporiser coil in the hood, two main solenoid valves in series, a motorised regulator, pilots with igniters and flame sensors; the valves close at once when the robot stops.",
        facts: ["34 kg/ha at 0.7 m/s, 0.84 ha per filling", "Gas ≈ €55/ha", "131 kg empty, about €3,400 in parts"] },
    ] },
];
