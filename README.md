# Bruut Implements

Open-source implements (attachments) for the **[Bruut OpenAgbot](https://github.com/JacobsFarm/Bruut_OpenAgbot)**, an open-source agricultural field robot. Want to know more about the project? Go to **[openagbot.com](https://openagbot.com)**.

Every design is parametric: change a number, rebuild, and the whole model follows. They are built in FreeCAD from Python scripts, come with the calculations behind them and, for the advanced variants, an animation on the robot. Everything bolts onto the 50 mm hole grid of the robot's chassis beams.

<p align="center">
  <img src="dockweed%20drill/animation_dockweed_drill.gif" alt="Dockweed drill removing a dock plant" width="720"><br>
  <i>Dockweed drill: finds a dock plant and mills out its root</i>
</p>

**Jump to:** [Gallery](#gallery) · [Animations](#animations) · [Implements](#implements) · [Build it yourself](#build-it-yourself) · [Related](#related)

## Gallery

<table>
  <tr>
    <td align="center" width="50%">
      <a href="overseeder/"><img src="overseeder/advanced/previews/12_work_iso_with_robot.png" alt="Overseeder, advanced variant"></a><br>
      <b><a href="overseeder/advanced/">Overseeder (advanced)</a></b><br>8-row slit seeder with an air seeder
    </td>
    <td align="center" width="50%">
      <a href="overseeder/"><img src="overseeder/simple/previews/12_work_iso_with_robot.png" alt="Overseeder, simple variant"></a><br>
      <b><a href="overseeder/simple/">Overseeder (simple)</a></b><br>Angled discs with a gravity hopper
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="liquid%20fertilizer%20applicator/advanced/"><img src="liquid%20fertilizer%20applicator/advanced/previews/11_work_iso_with_robot.png" alt="Liquid fertilizer applicator"></a><br>
      <b><a href="liquid%20fertilizer%20applicator/">Liquid fertilizer applicator</a></b><br>Disc and knife units on spring arms
    </td>
    <td align="center">
      <a href="dockweed%20drill/"><img src="dockweed%20drill/render_front_left.png" alt="Dockweed drill"></a><br>
      <b><a href="dockweed%20drill/">Dockweed drill</a></b><br>Finds a dock plant and mills out its root
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="trencher/"><img src="trencher/render_left_rear.png" alt="Trencher"></a><br>
      <b><a href="trencher/">Trencher</a></b><br>Wheel trencher for cutting narrow trenches
    </td>
    <td align="center">
      <a href="feed%20pusher%20auger/advanced/"><img src="feed%20pusher%20auger/advanced/previews/9_on_robot_iso.png" alt="Feed pusher auger"></a><br>
      <b><a href="feed%20pusher%20auger/advanced/">Feed pusher auger</a></b><br>Pushes feed back to the feed fence
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="brushes/simple/"><img src="brushes/simple/previews/1_double_750_iso_on_robot.png" alt="Disc brushes, 2 x 750 mm"></a><br>
      <b><a href="brushes/">Disc brushes</a></b><br>2 × Ø650/750: windrow or spread wide
    </td>
    <td align="center">
      <a href="brushes/simple/"><img src="brushes/simple/previews/3_single_850_iso_on_robot.png" alt="Disc brush, 1 x 850 mm"></a><br>
      <b><a href="brushes/simple/">Disc brush Ø850</a></b><br>Sweeps the robot's own width to one side
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="marker/simple/"><img src="marker/simple/previews/1_work_iso_on_robot.png" alt="Field marker on the robot"></a><br>
      <b><a href="marker/">Field marker</a></b><br>Marks GPS points with paint, via an XYZ stage
    </td>
    <td align="center">
      <a href="marker/simple/"><img src="marker/simple/previews/7_head_detail.png" alt="Field marker paint head"></a><br>
      <b><a href="marker/simple/">Field marker paint head</a></b><br>Spray can, servo and a sprung shroud that senses the ground
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="mobile%20refiller/liquid/"><img src="mobile%20refiller/liquid/previews/1_iso_refiller_with_trailer.png" alt="Mobile refiller with trailer"></a><br>
      <b><a href="mobile%20refiller/">Mobile refiller</a></b><br>Support robot: 515 l, boom with spout, powered trailer
    </td>
    <td align="center">
      <a href="mobile%20refiller/liquid/"><img src="mobile%20refiller/liquid/previews/7_docked_iso.png" alt="Mobile refiller docked next to the working robot"></a><br>
      <b><a href="mobile%20refiller/liquid/">Mobile refiller, docked</a></b><br>RTK antenna on the spout, camera checks the funnel
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="mobile%20refiller/simple/"><img src="mobile%20refiller/simple/previews/1_iso_refiller_ibc.png" alt="Simple mobile refiller with a standard IBC"></a><br>
      <b><a href="mobile%20refiller/simple/">Mobile refiller (simple)</a></b><br>Standard 1000 l IBC, pump, mast with a hanging hose
    </td>
    <td align="center">
      <a href="mobile%20refiller/simple/"><img src="mobile%20refiller/simple/previews/8_refill_iso.png" alt="Working robot stopped under the nozzle in its U-turn"></a><br>
      <b><a href="mobile%20refiller/simple/">Mobile refiller (simple), refill</a></b><br>Inside the U-turn: the working robot stops under the nozzle
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="mobile%20refiller/stationary/ibc_trailer/"><img src="mobile%20refiller/stationary/ibc_trailer/previews/2_7_refill_iso.png" alt="Stationary refill station on an IBC trailer"></a><br>
      <b><a href="mobile%20refiller/stationary/">Stationary refill station</a></b><br>IBC trailer (1 or 2 IBCs): the working robot drives to it
    </td>
    <td align="center">
      <a href="mobile%20refiller/stationary/flat_wagon/"><img src="mobile%20refiller/stationary/flat_wagon/previews/1_iso_flat_wagon.png" alt="Stationary refill station on a flat wagon with six IBCs"></a><br>
      <b><a href="mobile%20refiller/stationary/">Stationary refill station, flat wagon</a></b><br>6 IBCs on a standard bale wagon; also a three-point frame
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="around_pole_mower/simple/"><img src="around_pole_mower/simple/previews/1_iso_on_robot.png" alt="Around-pole fence mower on the robot"></a><br>
      <b><a href="around_pole_mower/">Around-pole fence mower</a></b><br>String head under the electric fence, swings around the posts
    </td>
    <td align="center">
      <a href="around_pole_mower/simple/"><img src="around_pole_mower/simple/previews/6_belt_drive_cover_off.png" alt="Fence mower arm with the cover off"></a><br>
      <b><a href="around_pole_mower/simple/">Fence mower arm</a></b><br>48 V motor, V-belt in the arm, deck spindle, PE guard ring
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="weed%20picker/mowing_deck/"><img src="weed%20picker/mowing_deck/previews/1_iso_on_robot.png" alt="Weed picker on the robot in front of a weed patch"></a><br>
      <b><a href="weed%20picker/">Weed picker</a></b><br>Twin-rotor mowing deck: cuts thistles, ragwort and dock into one windrow
    </td>
    <td align="center">
      <a href="weed%20picker/mowing_deck/"><img src="weed%20picker/mowing_deck/previews/8_linkage_actuator.png" alt="Weed picker linkage and actuator"></a><br>
      <b><a href="weed%20picker/mowing_deck/">Weed picker linkage</a></b><br>Parallel linkage, actuator with float link: cut height 100–400 mm
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="irrigation/stationary%20+%20roller/"><img src="irrigation/stationary%20+%20roller/previews/1_full_reel_iso_on_robot.png" alt="Irrigation hose reel on the robot"></a><br>
      <b><a href="irrigation/">Irrigation hose reel</a></b><br>150 m lay-flat hose, laid out empty, floods a 4 m strip at 0.17 bar
    </td>
    <td align="center">
      <a href="irrigation/stationary%20+%20roller/"><img src="irrigation/stationary%20+%20roller/previews/7_pinch_detail.png" alt="Pinch rollers of the hose reel"></a><br>
      <b><a href="irrigation/stationary%20+%20roller/">Hose reel pinch rollers</a></b><br>Clamp the hose shut while irrigating, squeeze it empty while winding
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="spotspray%20unit/boom/"><img src="spotspray%20unit/boom/previews/1_work_iso_on_robot.png" alt="Spot sprayer with a 3.75 m boom on the robot"></a><br>
      <b><a href="spotspray%20unit/">Spot sprayer</a></b><br>Camera in front, 120 l tank, 3.75 m boom with 15 PWM nozzles
    </td>
    <td align="center">
      <a href="spotspray%20unit/boom/"><img src="spotspray%20unit/boom/previews/5_folded_iso_rear.png" alt="Spot sprayer with both wings folded up"></a><br>
      <b><a href="spotspray%20unit/boom/">Spot sprayer, wings folded</a></b><br>Each 1.25 m wing folds up in 3.2 s, also in the field
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="in%20row%20weeder/finger/"><img src="in%20row%20weeder/finger/previews/1_work_iso_on_robot.png" alt="In-row finger weeder under the robot"></a><br>
      <b><a href="in%20row%20weeder/">In-row finger weeder</a></b><br>2 rows of broccoli, a stepper-driven finger per row, camera under the robot
    </td>
    <td align="center">
      <a href="in%20row%20weeder/finger/"><img src="in%20row%20weeder/finger/previews/6_knives_from_above_out_and_in.png" alt="In-row weeder knives from above"></a><br>
      <b><a href="in%20row%20weeder/finger/">In-row weeder knives</a></b><br>One knife out beside a plant, the other in the row line
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="bandrake/electric/"><img src="bandrake/electric/previews/1_work_iso_on_robot.png" alt="Electric belt rake in front of the robot"></a><br>
      <b><a href="bandrake/">Electric belt rake</a></b><br>1.5 m, 48 V drive, castors on actuators: one windrow from outside to inside
    </td>
    <td align="center">
      <a href="bandrake/electric/"><img src="bandrake/electric/previews/9_nursery_bed_iso.png" alt="Belt rake in a nursery bed"></a><br>
      <b><a href="bandrake/electric/">Belt rake in a nursery bed</a></b><br>Combs out weed seedlings between young trees
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="weeds%20burner/propane_hood/"><img src="weeds%20burner/propane_hood/previews/1_work_iso_on_robot.png" alt="Propane flame weeder behind the robot"></a><br>
      <b><a href="weeds%20burner/">Flame weeder</a></b><br>Hooded 1.5 m, 6 burners, 2 × 18 kg propane on the robot
    </td>
    <td align="center">
      <a href="weeds%20burner/propane_hood/"><img src="weeds%20burner/propane_hood/previews/3_flames_through_the_hood.png" alt="Flames under the hood"></a><br>
      <b><a href="weeds%20burner/propane_hood/">Flame weeder, flames</a></b><br>Pre-emergence: burns the seedlings on a freshly sown bed
    </td>
  </tr>
</table>

## Animations

The advanced designs are animated on the real robot model, with the loads and forces calculated per frame.

<p align="center">
  <img src="liquid%20fertilizer%20applicator/advanced/previews/animation_strip_ground_following.gif" alt="Ground-following animation of the liquid fertilizer applicator" width="720"><br>
  <i><a href="liquid%20fertilizer%20applicator/advanced/">Liquid fertilizer applicator</a>: every element follows the bumpy ground on its own arm</i>
</p>

<p align="center">
  <img src="feed%20pusher%20auger/advanced/previews/animation_feed_pushing.gif" alt="Feed pushing animation with forces on the robot" width="720"><br>
  <i><a href="feed%20pusher%20auger/advanced/">Feed pusher auger</a>: pushing feed back to the fence, with the forces on the auger and the robot's reaction</i>
</p>

<p align="center">
  <img src="brushes/simple/previews/animation_windrow_double_750.gif" alt="Disc brushes making a windrow" width="720"><br>
  <i><a href="brushes/simple/">Disc brushes</a>: two Ø750 brushes turn inwards and sweep a layer of loose material into a windrow</i>
</p>

<p align="center">
  <img src="marker/simple/previews/animation_staking_out.gif" alt="Field marker staking out three points" width="720"><br>
  <i><a href="marker/simple/">Field marker</a>: the robot stops a few centimetres off, the stage puts the nozzle exactly on each point</i>
</p>

<p align="center">
  <img src="mobile%20refiller/liquid/previews/animation_refill_in_turn.gif" alt="Mobile refiller topping up the working robot in its headland turn" width="720"><br>
  <i><a href="mobile%20refiller/">Mobile refiller</a>: tops up the working robot in the straight part of its turn, while both drive</i>
</p>

<p align="center">
  <img src="mobile%20refiller/simple/previews/animation_refill_in_u_turn.gif" alt="Simple mobile refiller topping up the working robot in the middle of its U-turn" width="720"><br>
  <i><a href="mobile%20refiller/simple/">Mobile refiller (simple)</a>: the working robot skips passes and turns in one go; it stops under the hanging nozzle in the middle of the U-turn, and the refiller moves 1 m per refill</i>
</p>

<p align="center">
  <img src="around_pole_mower/simple/previews/animation_around_posts.gif" alt="Fence mower going around two posts" width="720"><br>
  <i><a href="around_pole_mower/simple/">Around-pole fence mower</a>: the post pushes the head back and in, it slides around and the spring swings it back behind the post</i>
</p>

<p align="center">
  <img src="weed%20picker/mowing_deck/previews/animation_topping_windrow.gif" alt="Weed picker topping a weed patch into one windrow" width="720"><br>
  <i><a href="weed%20picker/mowing_deck/">Weed picker</a>: two rotors turn inwards and throw the chopped weed into one windrow; the robot slows down in thick weed and raises the cut height while driving</i>
</p>

<p align="center">
  <img src="irrigation/stationary%20+%20roller/previews/animation_one_strip.gif" alt="Irrigation hose reel: one strip laid out, irrigated, drained and wound" width="720"><br>
  <i><a href="irrigation/stationary%20+%20roller/">Irrigation hose reel</a>: the robot lays the empty hose, the pump at the ditch floods a 4 m strip, the hose runs empty and the robot winds it up again</i>
</p>

<p align="center">
  <img src="spotspray%20unit/boom/previews/animation_spot_spraying.gif" alt="Spot sprayer spraying dock and folding a wing for a post" width="720"><br>
  <i><a href="spotspray%20unit/boom/">Spot sprayer</a>: the camera finds the docks, only the nozzles above a plant open; the right wing folds up for a fence post</i>
</p>

<p align="center">
  <img src="in%20row%20weeder/finger/previews/animation_in_row_weeding.gif" alt="In-row weeder: the fingers swing out around every broccoli plant" width="720"><br>
  <i><a href="in%20row%20weeder/finger/">In-row finger weeder</a>: the camera finds the broccoli, each stepper swings its knife out around every plant and back into the row line</i>
</p>

<p align="center">
  <img src="in%20row%20weeder/double_arm/previews/animation_double_arm_weeding.gif" alt="In-row weeder with double arms opening around every plant" width="720"><br>
  <i><a href="in%20row%20weeder/double_arm/">In-row weeder, double arms</a>: two knives per row open to both sides of every plant and close behind it, each on its own stepper</i>
</p>

<p align="center">
  <img src="bandrake/electric/previews/animation_raking_windrow.gif" alt="Belt rake raking moss and thatch into one windrow" width="720"><br>
  <i><a href="bandrake/electric/">Electric belt rake</a>: the tines carry the litter and the previous pass's windrow to the left into one windrow; at the headland the castor actuators lift the rake</i>
</p>

<p align="center">
  <img src="weeds%20burner/propane_hood/previews/animation_flaming_bed.gif" alt="Flame weeder flaming a sown bed" width="720"><br>
  <i><a href="weeds%20burner/propane_hood/">Flame weeder</a>: six burners under the hood kill the seedlings on a sown bed; when the robot stops only the pilot flames stay on</i>
</p>

## Implements

| Implement | Variants | What it does |
|---|---|---|
| [**Overseeder**](overseeder/) | [simple](overseeder/simple/) · [advanced](overseeder/advanced/) | Grassland slit seeder. 1 m modules with 8 rows at 125 mm and coupling flanges. Cuts a 15 mm slot, places seed about 12 mm deep and closes the slot with a sprung press wheel. Simple: angled single disc, gravity hopper, about €1,675 in parts. Advanced: parallel linkage, depth bands, curved seed coulter and an air seeder, about €2,280 |
| [**Liquid fertilizer applicator**](liquid%20fertilizer%20applicator/) | [simple](liquid%20fertilizer%20applicator/simple/) · [simple v2](liquid%20fertilizer%20applicator/simple_v2/) · [advanced](liquid%20fertilizer%20applicator/advanced/) | Injects liquid fertilizer into the soil. Simple: fixed knives, two gauge wheels and a 12 V pump, about €600 in parts. Simple v2: adds a cutting disc in front of each knife, about €900. Advanced: disc and knife units on spring arms, a ground-wheel-driven 5-channel peristaltic pump and a parallel linkage |
| [**Feed pusher auger**](feed%20pusher%20auger/) | [simple](feed%20pusher%20auger/simple/) · [advanced](feed%20pusher%20auger/advanced/) | Pushes feed back to the feed fence. Simple: cheap version from flat plate and sectional flights. Advanced: Ø320 auger under a folded 2 mm hood, 24 V gearmotor with chain drive, open discharge end. Includes a feed-transport model and a force animation |
| [**Disc brushes**](brushes/) | [simple](brushes/simple/) (2 × Ø650, 2 × Ø750, 1 × Ø850) | Sweeper disc brushes for loose material on concrete. Each brush on its own 48 V worm gearmotor; reverse the motors and the pair makes a windrow in the middle or spreads material wide. Units slide on U-bolts along an 80 × 80 toolbar under the rear beams. Includes an animation with a particle model of the material |
| [**Dockweed drill**](dockweed%20drill/) | one design | Dock (broad-leaved dock) removal mill on a CNC gantry. Renders, animations, DXF and STEP files |
| [**Trencher**](trencher/) | one design | Wheel trencher for narrow trenches. Renders and STEP export |
| [**Field marker**](marker/) | [simple](marker/simple/) | Stakes out points from a coordinate list (piles, posts, planting positions, plot corners). The robot stops roughly behind the point; an XYZ stage from bought linear modules puts a spray-paint head exactly on it, with a GNSS antenna on a mast straight above the nozzle. Sprung spray shroud senses the ground. About €1,450 in parts. The concept README lists flag, peg, punch and soil-probe heads and 20 more functions |
| [**Mobile refiller**](mobile%20refiller/) | [liquid](mobile%20refiller/liquid/) · [simple](mobile%20refiller/simple/) · [stationary](mobile%20refiller/stationary/) | Support robot that brings liquid (and in concept seed, granular fertilizer, water, batteries) to the working robots, so they never leave the field. Liquid: 268 l T-shaped tank with a pump below the liquid level, slewing boom with a trolley and a spout, RTK antenna on the spout and a camera for confirmation, powered trailer of 246 l (6 driven wheels). Tops up the working robot in the straight reverse of its headland turn while both drive: about 25 l per turn, ≈ 3 s standstill. About €6,000 in parts. Simple: a standard 1000 l IBC set on with pallet forks, pump under the IBC, fixed mast with a hanging hose and the RTK antenna above the nozzle. The working robot skips passes so that every turn is a U-turn; the refiller stands inside the turn and the working robot stops ≈ 13 s under the nozzle; 1 m further per refill. About €1,650 in parts. Stationary: refill stations that stand on the headland (IBC trailer for 1 or 2 IBCs, three-point frame, 6 IBCs on a standard flat wagon), each with its own control box (pump, motor, battery, RTK receiver) and the RTK antenna above the nozzle; the working robot drives to them for 120 l per visit. The concept README lists all uses and variants (gravity buffer, on a tractor, docking station) |
| [**Around-pole fence mower**](around_pole_mower/) | [simple](around_pole_mower/simple/) | Mows the strip under an electric fence and goes around the posts by itself. Trailing swing arm on a post behind the right rear wheel, held on a rest stop by a spring; a Ø400 nylon-string head (non-conductive, safe on wire and posts) under a guard ring cut from PE pipe 315 slides along each post. 48 V BLDC motor at the root of the arm, V-belt inside the arm to a bought lawn-tractor deck spindle; head 182 mm high, floats on an HDPE skid. ≈ 615 W at 0.5 m/s, 1.8 km of fence per hour, about €575 in parts. Includes the arm dynamics around a post and an animation with grass |
| [**Weed picker**](weed%20picker/) | [mowing deck](weed%20picker/mowing_deck/) | Tops thistles, ragwort and dock above the grass and gathers them in one windrow, no bin. Two rotors with free-swinging blades (Ø510, 990 mm cut) in front of the robot turn inwards and throw the chopped weed out of a centre discharge between the front wheels. Each rotor: a 48 V BLDC motor straight on a lawn-tractor deck spindle; the left rotor runs 24 mm higher so the blades may overlap without timing. Cut height 100–400 mm from a 4000 N actuator on a parallel linkage, with a float link for humps. ≈ 1 kW at 0.5 m/s in scattered weeds, slower in dense patches; 82 kg (counterweight at the rear advised), about €1,040 in parts |
| [**Irrigation**](irrigation/) | [stationary pump + hose reel](irrigation/stationary%20+%20roller/) | Irrigates grassland by flooding at low pressure from a petrol pump at the ditch. The robot carries a reel with 150 m of 3" lay-flat hose, lays it out empty over the field, and after the gift winds it up empty again: it never carries water. Outlets every 2 m (3.5 mm restrictor, flat drop tail) flood a 4 m strip with 7.4 m³/h at 0.17 bar, CU ≈ 99 % on level ground. Pinch rollers keep the reel dry while irrigating and squeeze the hose while winding. 122 min per strip of 500 m² at 25 mm; one robot keeps about 4 ha wet in a dry summer. 146 kg, about €1,900 in parts on the robot. Includes the hydraulics and an animation of one strip |
| [**Spot sprayer**](spotspray%20unit/) | [folding boom](spotspray%20unit/boom/) | Sprays weeds plant by plant. A wide-angle global-shutter camera on a mast in front of the robot (1.48 m, 55° down) sees the whole 3.75 m strip from 1.8 m ahead; 2.65 s later the boom behind the robot opens only the nozzles above the plant. 15 clamp-on PWM nozzle bodies at 250 mm on a stainless wet pipe, 40° flat fans at 400 mm. Centre section 1.25 m, two 1.25 m wings that fold up in 3.2 s with a 24 V actuator each, also in the field for posts and trees. 120 l tank on the robot, diaphragm pump with bypass under the rear beams; the GNSS antenna moves to the mast top. ≈ 20 l/ha at 5 % weed cover, 1.1 ha/h; 91 kg, about €3,580 in parts. Includes an animation with docks and a fence post |
| [**In-row weeder**](in%20row%20weeder/) | [finger, 2 rows](in%20row%20weeder/finger/) · [double arms](in%20row%20weeder/double_arm/) | Hoes inside two rows of broccoli (375 mm apart, the wheels in the inter-rows). Two row units under the belly, each on a parallelogram with a gauge wheel in the robot's wheel track: a NEMA 23 closed-loop stepper with a 10:1 gearbox swings a 220 mm arm with a spring-steel finger and a flat knife 20 mm deep. Between the plants the knife is in the row line; it swings out in 98 ms before each plant and back in 148 ms after it, never closer than 50 mm to a stem. A global-shutter camera with LED bars under the front beams finds the plants 0.84 s ahead. 0.5 m/s, 6,400 plants/h; 55 kg, about €2,240 in parts. Double arms: two knives per row (4 steppers) that open to both sides of each plant and close behind it, timed by the real distance to the stem: 90 % of the row band outside the safe zones hoed, 68 kg, about €2,820. Includes the stepper move, the zone around each plant and animations |
| [**Belt rake**](bandrake/) | [electric](bandrake/electric/) | Band rake in front of the robot: a 260 mm rubber belt with 15 tine bars around two drums (1.52 m working width), 48 V 750 W gearmotor on the drive drum, swath board at the left end. Combs weed seedlings out of nursery beds between young trees (10 mm deep, 0.6 m/s) or rakes moss and thatch out of grassland from the outside inwards into one windrow (1.2 m/s, 0.49 ha/h). Two swivel castors on 24 V actuators carry the 110 kg rake, set the depth and lift it 100 mm for the headland, so the robot never carries it; a free parallelogram pushes it. About €2,380 in parts. Includes the tine forces, side force on the robot and an animation |
| [**Weeds burner**](weeds%20burner/) | [propane hood](weeds%20burner/propane_hood/) | Pre-emergence flame weeder for freshly sown beds: an insulated 1.5 × 0.8 m hood behind the robot with 6 flat-flame burners (13 kg/h, 167 kW), 34 kg/ha at 0.7 m/s. Two 18 kg forklift cylinders with liquid withdrawal on the robot, a vaporiser coil inside the hood, two main solenoid valves, a motorised regulator, pilots with igniters and flame sensors; the valves close at once when the robot stops. The hood rides on two steel swivel castors, pulled by a free parallelogram, with a heat shield towards the robot. 0.84 ha per filling, gas ≈ €55/ha; 131 kg empty, about €3,400 in parts. Includes dose, gas supply, safety and an animation |
| [Mower unit](mower%20unit/) | notes only | General mower unit |

**Not worked out yet:** [implement ideas/](implement%20ideas/) holds one folder with a `README.md` per attachment from the website's list that has no model yet. **Overview document** with every implement and variant on its own page: [docs/bruut_implements.pdf](docs/bruut_implements.pdf) ([HTML](docs/bruut_implements.html)), generated with `node docs/build_docs.mjs --pdf`.

Each folder holds its own requirements and notes (`*_requirements.md`, `README.md`, `RATIONALE.md` or `info.txt`). `RATIONALE.md` explains why the dimensions and choices are what they are.

## Build it yourself

1. Install [FreeCAD](https://www.freecad.org/) 1.1.
2. Open a variant folder, for example `feed pusher auger/advanced/`, and run `run_in_freecad.py` in FreeCAD. It rebuilds the model and prints the key numbers.
3. Change a dimension in the `*_params.py` file and run it again. Never edit the `.FCStd` by hand: it is generated.

What is in a variant folder:

| File | Contents |
|---|---|
| `*_params.py` | all dimensions, including the interface to the robot |
| `*_parts.py` | one function per part |
| `build_*.py` | model tree, colors, interference check, mass, renders, STEP export |
| `*_calc.py` | the calculations (capacity, forces, torque, springs, axle loads) |
| `animate_*.py`, `make_gif_*.py` | animation on the robot and the GIF |
| `previews/` | renders and animations |

The robot model itself lives in the [Bruut_OpenAgbot](https://github.com/JacobsFarm/Bruut_OpenAgbot) project. AI agents: see [AGENTS.md](AGENTS.md) for the workflow.

## Related

- **Robot design:** [JacobsFarm/Bruut_OpenAgbot](https://github.com/JacobsFarm/Bruut_OpenAgbot), the base robot these implements mount on
- **Website:** [openagbot.com](https://openagbot.com)

## Notes

- Models are stored as `.FCStd` (FreeCAD) with `.step` exports where available.
- `inspiration/` folders and `agbots/` (the base robot models and their comparison) are excluded from the repository via `.gitignore`.
- Code comments, docstrings and the older dockweed drill and trencher scripts are still partly in Dutch.
- Licensed under the terms in [LICENSE](LICENSE).
