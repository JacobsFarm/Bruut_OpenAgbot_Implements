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
  {
    name: "Push blade", folder: "push blade", category: "Soil Cultivation & Weed Control",
    summary: "Front-mounted dozer / grader blade: pushes feed back to the feed fence, scrapes slurry and snow, grades soil and paths. Covers the manure scraper idea as well.",
    variants: [
      { name: "Simple", folder: "push blade/simple", hero: "push blade/simple/previews/1_iso_front_on_robot.png",
        text: "1100 x 450 moldboard on R700 with a bolted rubber edge (steel edge for soil), angle +-25 degrees on an M30 king pin with a lock pin, two lift arms on a front toolbar under the front lower beams, 24 V 1500 N actuator with a float slot.",
        facts: ["Net push 801 N on dry concrete, 348 N with manure", "Lift 159 mm, clears the steered front tyres by 148 mm", "81 kg"] },
    ] },
  {
    name: "Fertilizer spreader", folder: "fertilizer spreader", category: "Spraying, Fertilizing & Irrigation",
    summary: "Spinning-disc spreader for granular fertilizer (and granular lime with a coarser roller). Dose follows the driving speed and a task map.",
    variants: [
      { name: "Simple", folder: "fertilizer spreader/simple", hero: "fertilizer spreader/simple/previews/1_iso_rear_right_on_robot.png",
        text: "88 l PE hopper over and behind the rear axle on rails on the upper beams, fluted metering roller O80 on a 12 V gearmotor, vaned disc O400 on a 48 V BLDC motor behind the robot with a guard towards the robot. Optional 2 x 20 kg front counterweight.",
        facts: ["Driving width 4.1..6.7 m (500..900 rpm)", "100..541 kg/ha at 1 m/s", "~1.6 ha/h, 130 kg full"] },
    ] },
  {
    name: "Grassland harrow", folder: "grassland harrow", category: "Crop & Soil",
    summary: "Pasture harrow behind the robot: a levelling board spreads molehills and dung pats, two rows of spring tines rake out moss and work in seed. Covers the molehill spreader idea.",
    variants: [
      { name: "Simple", folder: "grassland harrow/simple", hero: "grassland harrow/simple/previews/1_iso_rear_right_on_robot.png",
        text: "1300 mm harrow on two lift arms from a rear toolbar (the push blade geometry, mirrored): angle-iron levelling board, 32 double spring tines O8 (a track every 37.5 mm), floats on the sward, lifted by a 24 V actuator.",
        facts: ["Pull 629 N on grass, grip margin 1.44", "0.56 ha/h at 1.5 m/s", "85 kg"] },
    ] },
  {
    name: "Soil sampler", folder: "soil sampler", category: "Crop & Soil",
    summary: "Takes soil cores at GPS points with a gouge on a ball-screw Z axis in the middle of the robot and collects 40 cores per plot in a cup of a 10-cup carousel.",
    variants: [
      { name: "Simple", folder: "soil sampler/simple", hero: "soil sampler/simple/previews/1_iso_on_robot_park.png",
        text: "SBR20 rails and an SFU1605 ball screw with a NEMA23 on a mast plate between two bridges on the upper beams, O25 gouge with ejector, sprung foot, swing chute and funnel, carousel of 10 cups of 1.3 l.",
        facts: ["0-10 cm grass needs 0.5..0.8 kN, 1.3 kN available", "38 s per core, 25 min per plot", "33 kg"] },
    ] },
  {
    name: "Inter-row hoe", folder: "inter row hoe", category: "Soil Cultivation & Weed Control",
    summary: "Single-axis guided hoe behind the robot for row crops such as maize: two hoe units in the inter-rows behind the wheels, kept on the rows by a camera-steered ball-screw side shift.",
    variants: [
      { name: "Simple", folder: "inter row hoe/simple", hero: "inter row hoe/simple/previews/1_iso_rear_right_on_robot.png",
        text: "Rear toolbar and lift arms of the grassland harrow (3000 N actuator), carrier with 2 HGR15 rails, 8 mm shift plate moved +-75 mm by an SFU1610 ball screw and a closed-loop NEMA23. Two parallelogram units with a gauge wheel O250, a goosefoot 250 and two L-blades (550 mm per inter-row, 100 mm band each side of the row). Camera on a mast above the middle row.",
        facts: ["1.5 m per pass (2 x 750), ~0.43 ha/h at 1 m/s","Pull 764 N at 20 mm, grip margin 1.23","Side shift 80 mm/s, ~119 kg, needs the 2 x 20 kg front counterweight"] },
    ] },
  {
    name: "Grassland aerator", folder: "grassland aerator", category: "Soil Cultivation & Weed Control",
    summary: "Slitter aerator in the middle of the robot, between the axles: a passive roller with star discs cuts slits into grassland, pressed in by frame weight and ballast, both axles sharing the reaction.",
    variants: [
      { name: "Simple", folder: "grassland aerator/simple", hero: "grassland aerator/simple/previews/1_iso_front_right_on_robot.png",
        text: "2 bridges on the upper beams, side arms on pivots outside the steering sweep, roller with 8 stars of 6 slitting knives (O450) in 2 UCFL208 bearings, cross beam with 4 x 20 kg ballast, 24 V 2000 N actuator from a mast on the rear bridge (lifts 14 degrees, can press).",
        facts: ["1.2 m, slits 150 x 236 mm, 70 mm deep","~0.41 ha/h at 1.2 m/s, pull 325 N","201 kg incl. 80 kg ballast, 47 % on the front axle"] },
    ] },
  {
    name: "Three-point hitch", folder: "three point hitch", category: "Transport & General",
    summary: "Category 0 three-point linkage at the rear with two electric lift rods, so standard sub-compact implements can hang on the robot. Drawn with a small 5-tine cultivator, which covers the small cultivator idea.",
    variants: [
      { name: "Simple", folder: "three point hitch/simple", hero: "three point hitch/simple/previews/1_iso_rear_right_on_robot.png",
        text: "Rear toolbar of the grassland harrow with lugs for 2 lower links (50 x 20, O16 pins, 500 spacing), a top link bracket and 2 x 24 V 3000 N actuators as lift rods with a slotted eye (the implement floats). Demo implement: 1.0 m cultivator, 5 S-tines with duckfoot shares, 2 gauge wheels.",
        facts: ["Lower pins 220 .. 425 mm, implement level within 2 degrees","Carries ~56 kg lifted with the 2 x 20 kg counterweight (front axle >= 20 %)","Cultivator: 808 N draft at 40 mm, grip margin 1.29, 0.29 ha/h"] },
    ] },
  {
    name: "Crate carrier", folder: "crate carrier", category: "Transport & General",
    summary: "Flat deck on the upper beams for 8 harvest crates, carried from the rows to the field edge following a picker (UWB) or on an RTK route. The same deck carries tools and material (covers the tool cart idea).",
    variants: [
      { name: "Simple", folder: "crate carrier/simple", hero: "crate carrier/simple/previews/1_iso_rear_right_loaded.png",
        text: "3 bearers across the upper beams, side rails and 18 mm plywood (1300 x 1000, loading height 757), angle guides, divider, mesh headboard in front of the crates, 2 ratchet straps; 2 UWB anchors, a stop/go/follow box and the GNSS antenna moved to a mast above the stack.",
        facts: ["8 crates 600 x 400 x 300 in 2 layers","Apples: 141 kg, 48 % front axle, side tip angle 28 degrees","~107 crates per hour on a 150 m shuttle, 51 kg"] },
    ] },
  {
    name: "Counterweights", folder: "counterweights", category: "Transport & General",
    summary: "Stackable 11 kg ballast plates on the lower cross beams, front and rear, to keep enough load on the front axle with rear implements (and on the rear axle with the push blade).",
    variants: [
      { name: "Simple", folder: "counterweights/simple", hero: "counterweights/simple/previews/1_iso_front_right_on_robot.png",
        text: "Per stack (4 stacks): a 15 mm base plate on the two lower beams with 2 M16 studs, up to 4 plates of 170 x 200 x 50 with open slots that slide on from the side, a clamp bar and 2 knob nuts. Fits together with the push blade and the rear toolbar.",
        facts: ["11 kg per plate, 0..99 kg per axle end","Inter-row hoe: 2 plates per stack front, 5 % -> 21 % front axle","Harrow, hitch, spreader: 1 plate per stack front"] },
    ] },
  {
    name: "Battery pack", folder: "battery pack", category: "Power & Drive",
    summary: "Two exchangeable 48 V LiFePO4 pods (2.56 kWh each) hanging under the upper beams between the wheels: low, centred, and free of all toolbars and decks.",
    variants: [
      { name: "Simple", folder: "battery pack/simple", hero: "battery pack/simple/previews/1_iso_front_right_on_robot.png",
        text: "Per side: 2 hangers (flat bar 40 x 8, M10 through the upper beams) and an aluminium pod with 16 LiFePO4 cells 50 Ah, a 16S BMS, hook strips, latches, handles and an Anderson SB50 connector.",
        facts: ["51.2 V, 2 x 2.56 kWh, 26 kg per pod","Inter-row hoe 1.8 -> 6.0 h, harrow 1.4 -> 4.9 h","~230 N extra grip, 52 mm from the steered tyres"] },
    ] },
  {
    name: "Solar canopy", folder: "solar", category: "Power & Drive",
    summary: "Roof of solar panels on a tube frame above the robot that charges the battery through an MPPT controller and carries the GNSS antenna.",
    variants: [
      { name: "Canopy", folder: "solar", hero: "solar/previews/1_iso.png",
        text: "2 panels 1000 x 1650 mm (320 Wp each, 3 possible) on a steel tube frame: base tubes on the upper beams, 4 posts, top rails and cross members, diagonal struts to the overhangs; MPPT box, GNSS antenna on a mast between the panels.",
        facts: ["640 Wp, ~480 kWh per year (NL)", "2.3 kWh per day in June, 0.2 in December", "91 kg, tips over at ~29 degrees static"] },
    ] },
  {
    name: "Compost spreader", folder: "compost spreader", category: "Spreading & Bedding",
    summary: "Bin on the upper beams with a moving floor belt and a beater behind the robot: top-dresses beds, orchard strips and grassland with compost in an even 1.1 m layer, dose from the belt speed.",
    variants: [
      { name: "Simple", folder: "compost spreader/simple", hero: "compost spreader/simple/previews/1_iso_rear_right_on_robot.png",
        text: "299 l bin (150 kg payload) on 3 bearers, floor belt 920 wide on a UHMW slide bed round 2 drums O100 driven by a 24 V worm gearmotor, slide gate 30..150 mm, paddle beater O280 at 300 rpm on a 48 V 1 kW BLDC with a poly-V belt and a deflector hood.",
        facts: ["1..3 kg/m2, 50..150 m2 per bin, ~1.1 t/h with refilling", "Needs 1 counterweight plate per stack (front axle 33 %)", "190 kg empty, climbs 8 degrees full"] },
    ] },
  {
    name: "Stone picker", folder: "stone picker", category: "Crop & Soil",
    summary: "Mid-mounted under the robot between the axles: a 1 m tine rotor flicks stones over a comb into a sieve basket, on a parallelogram lift; the floor drops open at the heap.",
    variants: [
      { name: "Simple", folder: "stone picker/simple", hero: "stone picker/simple/previews/1_iso_front_right_on_robot.png",
        text: "Rotor O114 with 48 double spring tines (tip radius 150, 20 mm deep) on a 48 V 750 W gearmotor at 250 rpm, comb of 12 mm bars, 40 l basket with a sieve floor (25 mm gaps) opened by a 24 V actuator, frame on 4 swing links outside the wheel line lifted 100 mm by one 1500 N actuator.",
        facts: ["1 m wide, 1200..1700 m2/h, ~1 ha per day","44 kg of stones per basket, front axle 41..45 %, no ballast","92 kg, 525 W rotor"] },
    ] },
  {
    name: "Mulch layer", folder: "mulch layer", category: "Crop & Soil",
    summary: "Category 0 implement for the three-point hitch that lays 1.2 m mulch foil over the bed behind the robot: press wheels push the edges down, angled discs bury them.",
    variants: [
      { name: "Simple", folder: "mulch layer/simple", hero: "mulch layer/simple/previews/1_iso_rear_right_on_robot.png",
        text: "Frame with a 60 x 60 toolbar, A-frame mast and 50 x 50 side beams on the hitch of three point hitch/simple (imported), foil roll O200 x 1200 in open V-holders with a band brake, guide bar, 2 semi-pneumatic press wheels O250 on the edges and 2 concave covering discs O350 at 22 degrees, 50 mm deep.",
        facts: ["12 beds of 100 m per hour, a 1075 m roll lasts ~50 min","Pull 730 N, grip margin 1.51","94 kg with a full roll: needs 3 counterweight plates per front stack"] },
    ] },
  {
    name: "Grass meter", folder: "grass meter", category: "Measuring & Sensors",
    summary: "Maps grass cover while driving: front boom with 2 active NDVI sensors, a lidar and a camera, plus a sledge plate meter between the axles for compressed height and dry matter. Covers the NIR sensor idea.",
    variants: [
      { name: "Simple", folder: "grass meter/simple", hero: "grass meter/simple/previews/1_iso_front_right_on_robot.png",
        text: "Boom 1300 on two flat brackets on the front outer lower beam (above the tyres), 2 active NDVI sensors at x +-550, a lidar and an RGB camera; plate 0.1 m2 at 5 kg/m2 on a 350 mm parallelogram from a post under the upper beams, angle sensor on the pivot, 24 V actuator to lift it.",
        facts: ["4.4 ha/h on 10 m transects, ~35 ha per battery","Plate 0..200 mm, 0.3..0.5 mm resolution","22 kg, stays on with most implements"] },
    ] },
  {
    name: "Soil compaction meter", folder: "soil compaction meter", category: "Measuring & Sensors",
    summary: "Automatic cone penetrometer in the middle of the robot: a ball-screw Z axis pushes an ASABE cone at 30 mm/s to 600 mm, a load cell reads the force; compaction maps per depth layer.",
    variants: [
      { name: "Simple", folder: "soil compaction meter/simple", hero: "soil compaction meter/simple/previews/1_iso_front_right_on_robot.png",
        text: "Bridges, mast, SBR20 rails and SFU1605 screw as the soil sampler (mast z 120..1150 with stays), S-type 2 kN load cell, rod O9.5 x 700 with a 30 degree cone O12.83, sprung foot with a PTFE rod bush and a capacitive moisture probe.",
        facts: ["Up to 10.2 MPa with 70 % of the robot weight","35 s per 600 mm profile, ~47 points per hour","32 kg"] },
    ] },
  {
    name: "Charging dock", folder: "charging dock", category: "Power & Drive",
    summary: "Fixed docking station at the field edge or in the shed: the robot drives in and charges through sprung copper contacts (the contact version of the wireless charging dock idea).",
    variants: [
      { name: "Simple", folder: "charging dock/simple", hero: "charging dock/simple/previews/1_iso_docked.png",
        text: "Robot side: a 3.9 kg contact bracket on the front outer lower beam with 2 sprung copper pads and a pilot pin. Station: base plate with ground anchors, post with a 48 V 1 kW IP65 charger and a roof, an arm back between the front wheels to a PE contact head with 2 wide copper bars and a V-funnel.",
        facts: ["17 A at 54 V, 0.3 W contact loss","Robot 20 -> 100 % in 2 h","Catches 75 mm sideways; 80 kg station"] },
    ] },
  {
    name: "UV-C mildew light", folder: "uv mildew light", category: "Weed & Crop Protection",
    summary: "Reflecting hood with 6 UV-C lamps under the robot between the axles: drives over the bed at night and gives a low UV-C dose against powdery mildew, without chemicals.",
    variants: [
      { name: "Simple", folder: "uv mildew light/simple", hero: "uv mildew light/simple/previews/1_iso_front_right_on_robot.png",
        text: "Aluminium hood 580 x 440 on 4 slotted hangers from 2 bearers on the upper beams, rubber side skirts and brush curtains, 6 compact UV-C tubes (PL-L 55 W class) behind guard wires, ballasts and interlock in a box on the rear bearer.",
        facts: ["200 J/m2 at 0.58 m/s, ~1020 m2/h","489 W, ~4000 m2 per battery","21 kg, 25 mm from the steered tyres"] },
    ] },
  {
    name: "Sawdust spreader", folder: "sawdust spreader", category: "Spreading & Bedding",
    summary: "Bedding spreader for cubicles: a 308 l bin with an auger across the robot feeds a spinner on the right side that throws sawdust, chopped straw or a lime mix into the cubicles from the alley.",
    variants: [
      { name: "Simple", folder: "sawdust spreader/simple", hero: "sawdust spreader/simple/previews/1_iso_front_right_on_robot.png",
        text: "Bin 2 mm with 45 degree walls to a trough on 2 bearers on the upper beams, auger O150 across the robot on a 24 V worm gearmotor, spinner housing outside the right outer upper beam with a O320 disc (4 vanes, 350 rpm) open to the right.",
        facts: ["61 cubicles per fill of sawdust, ~570 per hour","Throws ~1.3 m beyond the wheel line","75 kg empty"] },
    ] },
  {
    name: "Bedding rake", folder: "bedding rake", category: "Livestock & Farm",
    summary: "Cubicle groomer on a side arm: reaches from the alley over the curb, under the divider loops, with a tine rotor along the bed that loosens and levels the bedding in the rear metre of each cubicle.",
    variants: [
      { name: "Simple", folder: "bedding rake/simple", hero: "bedding rake/simple/previews/1_iso_rear_right_in_barn.png",
        text: "Plate bracket with pivot lugs on the right outer upper beam, arm 60 x 40 from a pivot above the beams down past the curb and out over the bed, tine rotor O240 x 970 along the bed on a 48 V 400 W gearmotor, 24 V actuator across the robot top to a crank lifts the arm 40 degrees. A row of cubicles is modelled for the checks.",
        facts: ["Grooms 100..1070 mm behind the curb, 90 mm under the loops","~655 cubicles per hour, ~300 W","37 kg, side tip angle 27 degrees"] },
    ] },
  {
    name: "Dumper barrow", folder: "dumper barrow", category: "Transport & General",
    summary: "Tipping skip on the upper beams: a 353 l steel bin hinged at the rear end of the robot, tipped backwards to 48 degrees by two actuators so the load slides out behind the rear wheels.",
    variants: [
      { name: "Simple", folder: "dumper barrow/simple", hero: "dumper barrow/simple/previews/1_iso_rear_right_on_robot.png",
        text: "3 bearers on the upper beams (rest pads, actuator lugs, hinge lugs), subframe of 2 rails 40 x 40 with hinge bosses and a cross tube, 2 mm bin 900 x 1020 x 350 with a 30 degree rear lip, 2 x 24 V 3000 N actuators (stroke 300).",
        facts: ["150 kg of soil (100 l) or 353 l of chips / green waste","Tips 48 degrees in ~36 s, cg stays in front of the rear axle","72 kg, ~950 kg of soil per hour on 100 m"] },
    ] },
  {
    name: "Biocontrol spreader", folder: "biocontrol spreader", category: "Weed & Crop Protection",
    summary: "Releases predatory mites and parasitic wasps (in bran, vermiculite or sawdust) over two rows: 2 hoppers with metering wheels and a blower that carries the product through hoses to deflector nozzles.",
    variants: [
      { name: "Simple", folder: "biocontrol spreader/simple", hero: "biocontrol spreader/simple/previews/1_iso_front_right_on_robot.png",
        text: "Bearer across the upper beams with 2 PE hoppers of 7.9 l (agitator, NEMA17 metering wheel) over the rows at x +-187.5, a 24 V 60 W centrifugal fan, venturis, hoses O40 and deflector nozzles 450 mm above the ground.",
        facts: ["Predatory mites 2 ml/m2: 0.8 ha per fill","~1350 m2/h, ~12 h per battery","18 kg"] },
    ] },
  {
    name: "Bag trailer", folder: "bag trailer", category: "Transport & General",
    summary: "Two-wheeled trailer on the 50 mm tow ball of the cambridge roll (hitch, coupling and drawbar imported): a plywood deck with boards and a drop tailgate for 12 bags of 25 kg.",
    variants: [
      { name: "Simple", folder: "bag trailer/simple", hero: "bag trailer/simple/previews/1_iso_rear_right_loaded.png",
        text: "Frame of 40 x 40 rails and cross members behind the cbr cross beam and drawbar, plywood deck 1110 x 1410 at 358 mm with side and front boards and a drop tailgate, axle tube on hangers, 2 x 4.00-8 wheels with mudguards.",
        facts: ["12 bags of 25 kg, 24 kg on the ball","Steepest slope loaded: 3.5 deg wet grass, 6.5 dry","110 kg empty"] },
    ] },
  {
    name: "Broom / sweeper", folder: "broom sweeper", category: "Transport & General",
    summary: "Front angle broom on the push blade's toolbar, lift arms and king pin (imported): a roller brush O400 x 1000 under a hood, 48 V belt drive, on 2 castors, angled +-25 degrees to throw the material aside.",
    variants: [
      { name: "Simple", folder: "broom sweeper/simple", hero: "broom sweeper/simple/previews/1_iso_front_on_robot.png",
        text: "Head frame with the swivel plate, cross beam 80 x 60 and 5 mm end plates, PP brush O400 x 1000 in UCFL 208 bearings at 400 rpm, 48 V 1000 W gearmotor with an HTD belt, aluminium hood and rubber flap, 2 swivel castors O125; 3000 N version of the blade actuator.",
        facts: ["~2900 m2/h angled, ~4900 m2 per charge","~910 W brush, rear axle 54 % working","Lifting needs 4..9 counterweight plates; 124 kg"] },
    ] },
  {
    name: "Lime spreader", folder: "lime spreader", category: "Spraying, Fertilizing & Irrigation",
    summary: "Drop spreader for granulated or ground lime: a 178 l V-hopper centred over the robot, a trough auger to a 1.3 m cross auger behind the rear wheels that lets the lime fall through a row of holes inside a rubber dust skirt.",
    variants: [
      { name: "Simple", folder: "lime spreader/simple", hero: "lime spreader/simple/previews/1_iso_rear_right_on_robot.png",
        text: "Rails on the inner upper beams, steel V-hopper down between the beams to a U-trough, trough auger O100 in a tube under the rear lower beams, cross auger O100 x 1300 with 25 outlet holes O20 and flights from the middle outward, 2 x 24 V worm gearmotors, rubber skirt 20 mm above the ground.",
        facts: ["205 kg granulated lime per fill: 0.21 ha at 1000 kg/ha", "Up to 3.5 t/ha, 0.30 ha/h, no dust cloud", "97 kg empty, rear axle 60 % full"] },
    ] },
  {
    name: "Cover crop undersower", folder: "cover crop undersower", category: "Crop & Soil",
    summary: "Sows a cover crop into a standing 2-row crop: a 28 l hopper with 3 fluted metering cells feeds hoses to fishtail deflectors in the free middle inter-row and behind both rear tyres; spring tines on a bar high over the crop cover the seed.",
    variants: [
      { name: "Simple", folder: "cover crop undersower/simple", hero: "cover crop undersower/simple/previews/1_iso_rear_right_in_crop.png",
        text: "Bearer across the upper beams with a PE V-hopper, aluminium metering housing with 3 fluted rollers on one 12 V speed-following shaft, hoses O32 routed over the crop rows, fishtail deflectors 40 mm above the ground, tine bar at 430 mm on 2 hangers under the rear lower beams with 7 spring tines O8.",
        facts: ["Ryegrass 0.43 ha, clover 3.6 ha per fill", "0.22 ha/h, ~1.1 ha per charge", "26 kg; crop rows untouched (checked)"] },
    ] },
  {
    name: "Straw spreader", folder: "straw spreader", category: "Spreading & Bedding",
    summary: "Lays a straw mulch strip in the free middle inter-row: 2 small bales on a slatted floor chain are fed against a spiked shredder drum, the loose straw falls through a chute to a 160 mm outlet between the crop rows.",
    variants: [
      { name: "Simple", folder: "straw spreader/simple", hero: "straw spreader/simple/previews/1_iso_rear_right_in_crop.png",
        text: "2 bearers and 2 rails on the upper beams, slatted floor of 2 chains 08B in UCP 204 shafts with a 24 V gearmotor, aluminium bale chamber, spiked drum O320 at 250 rpm on a 48 V 750 W motor in a 3 mm housing, aluminium chute to z 300.",
        facts: ["260 m of strip per fill at 0.5 kg/m2", "~440 W drum, ~3.5 km of strip per charge", "102 kg empty; crop rows untouched (checked)"] },
    ] },
  {
    name: "Electric weeder", folder: "electric weeder", category: "Weed & Crop Protection",
    summary: "Spot electric weed control in the free middle inter-row: a camera finds weeds, a 5 kV generator switches on a comb of spring-steel fingers only while a weed is under it, the current returns through a coulter disc.",
    variants: [
      { name: "Simple", folder: "electric weeder/simple", hero: "electric weeder/simple/previews/1_iso_front_right_in_crop.png",
        text: "Bearer on the upper beams with the HV box and beacon, post with a parallel-arm lift (24 V actuator), PE holder with 9 spring-steel fingers and rubber curtains, coulter disc O250 as earth return, camera under the inner front lower beam.",
        facts: ["4-leaf weeds at 0.2 m/s: 1.8 kJ per weed", "~3000-3800 weeds per charge", "27 kg; crop rows untouched (checked)"] },
    ] },
  {
    name: "Hydraulic power pack", folder: "hydraulic pump", category: "Transport & General",
    summary: "48 V hydraulic power unit on the rear half: BLDC motor with a 4 cc gear pump (11 l/min, 150 bar), 16 l tank, 2-section solenoid valve block and 2 pairs of ISO-A quick couplers for hydraulic implements.",
    variants: [
      { name: "Simple", folder: "hydraulic pump/simple", hero: "hydraulic pump/simple/previews/1_iso_rear_left_on_robot.png",
        text: "2 bearers and a 5 mm base plate on the upper beams, 16 l steel tank with return filter, BLDC 48 V 3.5 kW with bell housing and group-1 gear pump, motor controller, valve block with relief valve, gauge and 2 double-acting 24 V sections, couplers screwed into its rear face.",
        facts: ["11 l/min, 150 bar: 19-30 kN cylinders", "44 min of full flow at 100 bar per charge", "49 kg + 12 kg oil, rear axle 62 %"] },
    ] },
  {
    name: "Irrigation pump", folder: "irrigation pump", category: "Spraying, Fertilizing & Irrigation",
    summary: "Direct pump from ditches and ponds: a self-priming 1.5\" pump on a 48 V 1.5 kW motor with an 8 m suction hose on a reel, delivering to a Camlock coupling at the rear; mount of the hydraulic power pack.",
    variants: [
      { name: "Simple", folder: "irrigation pump/simple", hero: "irrigation pump/simple/previews/1_iso_rear_left_on_robot.png",
        text: "Bearers and base plate from the hydraulic pack, self-priming centrifugal pump with priming chamber and BLDC 1.5 kW, reel O520 with 8 m of spiral suction hose, rotary union and strainer with foot valve, discharge to a 1.5\" Camlock at the rear edge.",
        facts: ["8.5 m3/h at 3 m lift into a drip line", "10-17 m3 per charge", "62 kg"] },
    ] },
];
