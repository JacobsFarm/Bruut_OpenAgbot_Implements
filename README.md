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
  <img src="around_pole_mower/simple/previews/animation_around_posts.gif" alt="Fence mower going around two posts" width="720"><br>
  <i><a href="around_pole_mower/simple/">Around-pole fence mower</a>: the post pushes the head back and in, it slides around and the spring swings it back behind the post</i>
</p>

<p align="center">
  <img src="weed%20picker/mowing_deck/previews/animation_topping_windrow.gif" alt="Weed picker topping a weed patch into one windrow" width="720"><br>
  <i><a href="weed%20picker/mowing_deck/">Weed picker</a>: two rotors turn inwards and throw the chopped weed into one windrow; the robot slows down in thick weed and raises the cut height while driving</i>
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
| [**Mobile refiller**](mobile%20refiller/) | [liquid](mobile%20refiller/liquid/) | Support robot that brings liquid (and in concept seed, granular fertilizer, water, batteries) to the working robots, so they never leave the field. 268 l T-shaped tank with a pump below the liquid level, slewing boom with a trolley and a spout, RTK antenna on the spout and a camera for confirmation, powered trailer of 246 l (6 driven wheels). Tops up the working robot in the straight reverse of its headland turn while both drive: about 25 l per turn, ≈ 3 s standstill. About €6,000 in parts. The concept README lists all uses and variants (gravity buffer, on a tractor, docking station) |
| [**Around-pole fence mower**](around_pole_mower/) | [simple](around_pole_mower/simple/) | Mows the strip under an electric fence and goes around the posts by itself. Trailing swing arm on a post behind the right rear wheel, held on a rest stop by a spring; a Ø400 nylon-string head (non-conductive, safe on wire and posts) under a guard ring cut from PE pipe 315 slides along each post. 48 V BLDC motor at the root of the arm, V-belt inside the arm to a bought lawn-tractor deck spindle; head 182 mm high, floats on an HDPE skid. ≈ 615 W at 0.5 m/s, 1.8 km of fence per hour, about €575 in parts. Includes the arm dynamics around a post and an animation with grass |
| [**Weed picker**](weed%20picker/) | [mowing deck](weed%20picker/mowing_deck/) | Tops thistles, ragwort and dock above the grass and gathers them in one windrow, no bin. Two rotors with free-swinging blades (Ø510, 990 mm cut) in front of the robot turn inwards and throw the chopped weed out of a centre discharge between the front wheels. Each rotor: a 48 V BLDC motor straight on a lawn-tractor deck spindle; the left rotor runs 24 mm higher so the blades may overlap without timing. Cut height 100–400 mm from a 4000 N actuator on a parallel linkage, with a float link for humps. ≈ 1 kW at 0.5 m/s in scattered weeds, slower in dense patches; 82 kg (counterweight at the rear advised), about €1,040 in parts |
| [Mower unit](mower%20unit/) | notes only | General mower unit |

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
