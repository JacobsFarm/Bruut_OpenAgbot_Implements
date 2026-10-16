# Feed pusher auger V2: FreeCAD model

Feed pusher auger for the Bruut OpenAgbot. It sits at the back of the robot, on the side of the fixed wheel motors.
When pushing feed, the robot drives with the auger first; the steering heads are then at the back.
The auger picks up the pushed-away feed and carries it sideways to the feed fence. There it falls through the open end
plate onto the floor.

- **Hood:** one 2 mm folded sheet with 4 bends, as in the simple version. There is no rolled round trough any more.
- **Drive:** an 800 W gearmotor with a foot (V2, dimensions from `parts/800 watt motor`) on a motor plate on top of the hood. A 10B-1 chain with a tensioner runs
  along the left side plate to the auger.
- **Mounting:** 4 arms, each with 4 × M10 through the 4 holes in the rear flange of the side plates of the rear
  wheel modules.

Why it is designed this way is explained in [RATIONALE.md](RATIONALE.md).

## V2 compared with V1

V2 is V1 (the former `advanced` design) with a different rotor support. No shaft runs through the auger any more:

- **Free end (right, open discharge):** the right end plate is larger (up to the top of the beam and forward to
  v −120). It has a cutout, open at the bottom and front, that the whole auger can pass through. The pin sits on a
  **hanging strap** like the old suspension in the shed: 10 mm with two bent-up lips, bolted with 4 × M12 to the end
  plate above the cutout, with a welded-on Ø25 pin. The bearings sit *in* the auger: 2 × 6205-2RS in a turned bearing
  housing (Ø60.3, same as the core tube) butt-welded to the end of the core tube.
- **Removing the auger:** shear bolt out, 4 nuts off, take off the strap with the pin, slide the auger 200 mm to
  the right off the spigot and through the cutout. The frame stays together.
- **Drive end (left):** the UCF206 stays. Through it runs a stepped **drive bush** (one turned part, C45): Ø30
  journal with the keyway for the 38T sprocket, a Ø60.3 collar against the end of the core tube, and a hollow Ø52
  spigot that runs **200 mm** into the core tube (ID 52.3). One **M6 4.6 shear bolt** through core tube and spigot
  (at x = −640, where the flight is to the side) transmits the torque. It breaks at 252 Nm.
- **Sprockets:** 12T on the Ø19 motor shaft, 38T on the Ø30 journal (10B-1, i = 3.17): auger 95 rpm, 78 Nm nominal.
  See `parts/Kettingwielen` for where to buy them.

![hanging strap with the pin on the right](previews/12_pin_hanger_right.png)

| Drive bush in the core tube (rotor transparent) | Pin and 2 × 6205 in the bearing housing |
| --- | --- |
| ![drive bush](previews/13_drive_bush_inside.png) | ![pin and bearings](previews/14_pin_and_bearings_inside.png) |

![on the robot](previews/9_on_robot_iso.png)

![animation (V1; the rotor change does not affect it): pushing feed along the feed fence, with forces and the robot reaction](../V1/previews/animation_feed_pushing.gif)

## Files

| File | Contents |
| --- | --- |
| `Feed_Pusher_Auger_V2.FCStd` | the model, with the robot model hidden next to it. Generated, so do not edit by hand |
| `Feed_Pusher_Auger_V2.step` | the feed pusher only, in robot coordinates |
| `fpa_params.py` | all dimensions, including the robot interface and the operating parameters |
| `fpa_parts.py` | one function per part; each function returns a `Part` shape |
| `build_fpa.py` | model tree, colors, collision check, clearance to the tires, mass, images, STEP |
| `fpa_calc.py` | capacity, torque, power, shear bolt, chain, deflection, wheel loads, side forces and skew (pure Python) |
| `fpa_feed.py` | feed model: height field in the feeding alley, picking up, transport along the auger and ejection at the fence (Python + numpy) |
| `animate_fpa.py` | animation: robot + feed pusher along the feed fence, with forces per frame |
| `make_gif_fpa.py` | frames to GIF with a caption, a force panel (top view) and the feed distribution along the auger |
| `run_in_freecad.py` | macro: open in FreeCAD and run (F6) to rebuild the model and print the key figures |
| `previews/` | images and the GIF |

## Axes

Same as the robot model: x = right, y = driving direction of the robot (front = +y), z = up, ground = z 0, mm.
The origin is the centre of the robot. The implement is therefore directly in robot coordinates; no offset is needed.

- Auger axis at y = −960 and z = 175. The flight runs up to 15 mm above the floor.
- Feed fence on the +x side: the auger feeds towards +x.
- When pushing feed the robot drives towards −y.

## Rebuilding and using

In FreeCAD's Python console (folder in `sys.path`, or via `run_in_freecad.py`):

```python
import build_fpa
build_fpa.build()                        # builds, saves FCStd and STEP (robot hidden)
build_fpa.build(show_robot=True, save_path=None, step_path=None)
build_fpa.check_interference()           # overlap among parts and with the robot (must be empty)
build_fpa.clearance()                    # smallest distance of hood / flap / arms to the rear tires
build_fpa.mass_properties()              # mass and centre of gravity
build_fpa.render_all()                   # all images in previews/, save, STEP
```

```python
import fpa_calc
fpa_calc.report()                        # key figures
fpa_calc.robot_reaction(-80, 40)         # wheel loads, side forces, skew at 80 N sideways and 40 N backwards
fpa_calc.axle_loads()                    # axle loads without/with feed pusher and counterweight
```

## Animation

Builds a separate document `FPA_V2_on_robot_animation` with:

- the robot model from `agbots/agbot design` (those files are not modified);
- the feed pusher;
- a concrete floor and a feed fence with a kerb;
- a strip of feed that the cows have pushed away.

That strip lies 600 to 950 mm from the fence, at about 24 kg/m. It has a spot where feed has already been eaten and a clump of 10 kg.

Per frame (8 per second, with 5 sub-steps):
- **Feed:** the feed model picks up feed at the front of the flight and carries it in 25 mm cells to the fence,
  limited by the capacity. Anything more is pushed ahead of the auger. At the fence it falls onto the floor
  and settles into an edge.
- **Auger:** from the mass in the auger follow the torque, the power and the motor current.
- **Forces on the robot:** the side force away from the fence (red) and the pushing force against the driving direction.
- **Robot:** according to `fpa_calc.robot_reaction` the load changes per wheel. The side force of the floor differs per
  wheel (blue). The robot runs a fraction skew, because the rear wheels are fixed, and the front wheels steer against it.
- **Speed control:** above 18 A motor current the robot drives slower, to a minimum of 25 % of the driving speed.

```python
import animate_fpa
animate_fpa.build()
animate_fpa.play()                       # live, animate_fpa.stop()
animate_fpa.summary()                    # range of mass, torque, current, forces, skew, speed
animate_fpa.render_all(r"C:\temp\fpa_frames")
import make_gif_fpa
make_gif_fpa.main(r"C:\temp\fpa_frames", r"previews\animation_feed_pushing.gif")
make_gif_fpa.main(r"C:\temp\fpa_frames", r"previews\animation_feed_pushing_clean.gif", overlay=False)  # without text
```

Driving plan, control and camera are at the top of `animate_fpa.py` (`SPEED`, `I_SET`, `I_MAX`, `CAM_A/B/C`).
The feed is in `fpa_feed.FeedField._init_windrow`.

## Model tree

```
Feed_pusher (feed_pusher_auger)
  Mount          4 arms (adapter plate on the wheel bracket flange + gusset + end plate with slotted holes) and bolts
  Frame          2 mm hood, 80x80x3 beam with end plates, left side plate, right end plate with auger cutout (open discharge),
                 folded angles, rubber flap + clamp strip, PE glide shoe, motor plate
  Bearings       UCF206 left; right: hanging strap (10 mm, 2 lips) + welded Ø25 pin + 4 × M12, 2 × 6205-2RS
  Drive          800 W gearmotor with foot, Ø19 h6 output shaft + key 6x6, 12T sprocket, 10B-1 chain, tensioner, chain guard
  Auger_rotor    drive bush (Ø30 journal + key 8x7, Ø52 × 200 spigot), core tube with bearing housing, Ø320 flight pitch 260,
                 M6 shear bolt, 38T sprocket (rotates along)
  Counterweight  2 blocks of 20 kg on the front lower beam
Robot (hidden in the FCStd; for checking only)
```

## Estimated, not measured

- Robot: 150 kg with the centre of gravity in the middle (same as the liquid fertilizer applicator).
- Feed: bulk density 280 kg/m³, friction 0.5 on concrete, auger resistance factor λ = 4 (CEMA, fibrous).
- Auger: transport efficiency 0.65 and maximum fill factor 0.6.
- Tires: tire stiffness 0.12 per degree per N of wheel load and grip 0.6.
- Gearmotor (V2, 800 W): mass 9 kg, output 300 rpm (not on the drawing, check the type plate), foot width 90 and cross
  hole distance 70 (M8), body Ø105 and nose shape estimated from the photo. Length 260, gearbox Ø120, shaft Ø19 h6 + key 6,
  35 out, 64 above the foot, foot 115 with holes 80 apart are from the drawing.
- Robot bracket: the dimensions of the flange holes come from `agbot_parts.side_plate`.
- V2: radial load on the pin (own weight + half the circumferential force at the starting torque); 6205 C0 = 7.8 kN
  from the catalogue; shear strength of the M6 4.6 bolt taken as 0.6 × Rm.

See RATIONALE § 6.
