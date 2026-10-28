# Why the field runs are set up this way

## A short field, real speeds

A real field is 100–400 m long. With 12 passes of 200 m the field would be a thin strip on the screen and the robot
an invisible dot, and every turn would come after 4.5 minutes of real time. The runs therefore use a field of
**12 passes × 40 m**: the whole field fits in one camera view, the pattern of the passes and the turns is visible, and
every distance, speed, dose and pump flow is still the real one. Only the playback speed changes (up to 40 × in the
passes, 2–10 × in the turns and while filling), and the caption always shows it.

12 passes is the smallest block of the skip pattern: with a 1 m pass and a turning radius of 2.4 m a U-turn needs
at least 6 m (N = 6), so the order is 1, 7, 2, 8, 3, 9, 4, 10, 5, 11, 6, 12 (as in `mobile refiller/simple`). The
liquid refiller is shown with passes side by side and three-point turns, because that is what it was designed for:
it refills while the working robot reverses along the headland.

## Small amounts per turn

On 40 m passes at 500 l/ha the robot uses 2 l per pass, so a mobile refiller tops up only about 4 l per turn (2 s of
pumping). That is what the model gives, and it is shown as it is. On a real field the amount scales with the length:

| Field length | per pass | per turn on the refiller headland | pump time (IBC 120 l/min / boom 150 l/min) |
| --- | --- | --- | --- |
| 40 m (animation) | 2 l | 4 l | 2.0 s / 1.6 s |
| 100 m | 5 l | 10 l | 5 s / 4 s |
| 200 m | 10 l | 20 l | 10 s / 8 s |
| 400 m | 20 l | 40 l | 20 s / 16 s |

For the IBC refiller the working robot stands still for the pump time plus about 2 s (check and nozzle). For the
boom refiller the pump runs while the working robot reverses (3.8 m at 0.4 m/s, about 10 s), so up to about 25 l
per turn costs no extra standstill; beyond that the robot waits at the end of the reverse.

## The work tank on the precision applicator

The combination V2 had no tank yet: the pump manifold was open at the front. For the field runs it gets the same
kind of work tank and funnel as the receiver kit of the refillers, but shorter: the pump stands on the upper beams
at y −390 and its manifold reaches y −194, so the tank runs from y −150 to 330 (in front of it the stepper plates of
the front wheels start at y 405). 840 × 480 × 260 mm, **95.7 l**; filled to 90 l, so a 200 m field at 500 l/ha
(10 l per pass) could be worked for 8 passes without a refill.

The funnel rim is at the same height as on the refiller receiver kits (z 1144), so all three refillers fit without
changes: the hanging nozzle of the IBC refiller and the station end at z 1250, the raised spout of the boom refiller
at 1265. The funnel itself sits 95 mm further forward than on the receiver kit (y +60 instead of −35), so its rim
stays clear of the pump; the docking points are calculated from this position (`funnel_xy`). The strainer sits at
the bottom of the funnel, 10 mm above the outlet, as on the receiver kits: the spout of the boom refiller goes down
to z 1080, 64 mm into the funnel, and the overlap check found it cutting through a strainer placed halfway up.

## Start level of the station run

The stationary IBC trailer only makes sense when the working robot runs low. On the 40 m field the whole field uses
only 24 l, so a robot starting full would never visit the station. The station run therefore starts with **16 l** in
the tank; after pass 3 there is 10 l left, less than the next two passes plus the 5 l reserve need, so the robot
drives to the station and is filled with 84 l. The rule is the one of the stationary README (visit when the tank
will not last until the next time it passes the station's headland), only the threshold is lower.

The station stands on the headland beside the field (left of pass 1), with its arm towards the field and the nozzle
above the line of the headland straights. The robot comes from its pass with a left arc, drives along the headland
to the station (the last 2 m slowly), is filled, turns round with a forward and a reverse arc (as in
`mobile refiller/stationary`) and drives back along the headland into its next pass. The visit costs about 98 s
here: 44 s standing at the station (84 l) and about 52 s for the detour.

## Playback speed and camera

The speed is chosen per simulation step (fast in the middle of a pass, slow near the field edge, in the turns and
while filling) and then smoothed in both directions with at most a factor 4 per second of video, so the animation
slows down *before* a turn or a refill and not after it. Pumping 84 l at the station is shown faster (the pump time
is compressed to about 4 s of video). The camera blends with the speed between an overview of the field and a view
close to the working robot and the refiller; at the start and the end it shows the whole field. On the headland of
the IBC refiller it looks from the fence side, because the refiller stands between the field and the working robot.

## Rendering outside the MCP

A run has 2,200–2,650 frames. FreeCAD renders each frame in about 0.3–1.5 s, far longer than the MCP time-out, so
`render_fld.py` runs in its own FreeCAD process (`freecad.exe render_fld.py`) and closes it when done. The frames and
their data (`frames.json`) go to a work folder; only the MP4s, GIFs and images go into `previews/`.
